"""ETL pipeline orchestration for the BPS Data Warehouse.

This module provides a command-line pipeline that orchestrates the
full flow: API extraction → raw storage → staging → data quality →
transformation → load to PostgreSQL.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.config.settings import settings
from src.extract.bps_api import BPSAPIClient
from src.extract.domain import DomainExtractor
from src.extract.dynamic_data import DynamicDataExtractor
from src.extract.glossary import GlossaryExtractor
from src.extract.simdasi import SIMDASIExtractor
from sqlparse import split
from src.load.postgres import PostgresLoader
from src.quality.validators import DataQualityValidator
from src.raw.storage import RawStorage
from src.staging.dynamic_transform import DynamicDataTransformer
from src.transform.economic import EconomicTransformer
from src.transform.metadata import MetadataTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the end-to-end ETL pipeline."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        var: Optional[str] = None,
        periods: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or settings.bps_api_key
        self.domain = domain
        self.var = var
        self.periods = periods
        self.dataset_name = dataset_name or f"var{var or 'unknown'}"

        # Components
        self.client = BPSAPIClient(api_key=self.api_key)
        self.extractor = DynamicDataExtractor(self.client)
        self.domain_extractor = DomainExtractor(self.client)
        self.simdasi_extractor = SIMDASIExtractor(self.client)
        self.glossary_extractor = GlossaryExtractor(self.client)
        self.storage = RawStorage()
        self.validator = DataQualityValidator()
        self.transformer = EconomicTransformer()
        self.metadata_transformer = MetadataTransformer()
        self.loader = PostgresLoader()

    def run(self) -> None:
        """Run the full pipeline."""
        logger.info("=" * 60)
        logger.info("BPS DATA WAREHOUSE PIPELINE")
        logger.info("=" * 60)

        # Step 1: Extract
        logger.info(
            f"Step 1/7: Extracting data from BPS API "
            f"(domain={self.domain}, var={self.var}, periods={self.periods})"
        )
        response = self.extractor.fetch(
            domain=self.domain,
            var=self.var,
            periods=self.periods,
        )
        logger.info(f"  Response status: {response.get('status')}")
        logger.info(f"  Variables: {len(response.get('variable', []))}")
        logger.info(f"  Data rows: {len(response.get('datacontent', []))}")

        # Step 2: Save raw
        logger.info(f"Step 2/7: Saving raw response to: {self.storage.base_dir}")
        raw_path = self.storage.save(
            response,
            source="dynamic_data",
            dataset=self.dataset_name,
        )
        logger.info(f"  Saved to: {raw_path}")

        # Step 3: Stage
        logger.info("Step 3/7: Transforming to staging format")
        # Fetch region codes for the domain to map values correctly
        region_codes = self._fetch_region_codes()
        staging_transformer = DynamicDataTransformer(
            response,
            region_codes=region_codes,
        )
        staged = staging_transformer.transform()
        df = staged["data"]
        metadata = staged["metadata"]
        variables = staged["variables"]
        logger.info(f"  Staged rows: {len(df)}")
        logger.info(f"  Staged columns: {list(df.columns)}")

        if df.empty:
            logger.error("  No data rows found in response. Aborting.")
            sys.exit(1)

        # Check if region_id is populated
        if df["region_id"].isnull().all():
            logger.warning(
                "  WARNING: region_id is null for all rows. "
                "Values cannot be mapped to regions correctly."
            )

        # Step 4: Data quality
        logger.info("Step 4/7: Running data quality checks")
        result = self.validator.validate(df, context=f"var={self.var}")
        print(f"\n{result.summary()}\n")

        if not result.passed:
            logger.error("  Data quality checks failed. Aborting pipeline.")
            sys.exit(1)
        logger.info("  Data quality checks passed.")

        # Step 5: Transform to dimensional model
        logger.info("Step 5/7: Building dimensional model")
        years = sorted(df["year"].unique().tolist())
        fact_df = self.transformer.build_fact_economic(df)
        dim_date = self.transformer.build_dim_date(years)
        dim_indicator = self._build_dim_indicator(variables, metadata)
        dim_region = self._build_dim_region()
        logger.info(f"  Fact rows: {len(fact_df)}")
        logger.info(f"  Date dimension rows: {len(dim_date)}")
        logger.info(f"  Indicator dimension rows: {len(dim_indicator)}")
        logger.info(f"  Region dimension rows: {len(dim_region)}")

        # Step 5b: Metadata (SIMDASI + Glosarium)
        logger.info("Step 5b/7: Extracting metadata (SIMDASI + Glosarium)")
        dim_dataset, dim_glossary, glossary_records = self._extract_metadata()
        logger.info(f"  Dataset metadata rows: {len(dim_dataset)}")
        logger.info(f"  Glossary rows: {len(dim_glossary)}")

        # Enrich dim_indicator with glossary definitions
        if glossary_records:
            dim_indicator = self.metadata_transformer.enrich_indicator_with_glossary(
                dim_indicator,
                glossary_records,
            )
            logger.info("  Enriched dim_indicator with glossary definitions")

        # Step 6: Load to PostgreSQL
        logger.info("Step 6/7: Loading to PostgreSQL")
        self.loader.create_schemas(["raw", "staging", "warehouse", "mart"])

        # Create tables if they don't exist
        self._create_tables()

        # Load dimensions (idempotent)
        logger.info("  Loading dim_date (upsert)...")
        self.loader.upsert_dataframe(
            dim_date,
            table_name="dim_date",
            schema="warehouse",
            conflict_columns=["date_key"],
        )

        logger.info("  Loading dim_indicator (upsert)...")
        self.loader.upsert_dataframe(
            dim_indicator,
            table_name="dim_indicator",
            schema="warehouse",
            conflict_columns=["indicator_key"],
        )

        logger.info("  Loading dim_region (upsert)...")
        self.loader.upsert_dataframe(
            dim_region,
            table_name="dim_region",
            schema="warehouse",
            conflict_columns=["region_key"],
        )

        # Load metadata dimensions (idempotent)
        if not dim_dataset.empty:
            logger.info("  Loading dim_dataset (upsert)...")
            self.loader.upsert_dataframe(
                dim_dataset,
                table_name="dim_dataset",
                schema="warehouse",
                conflict_columns=["dataset_key"],
            )

        if not dim_glossary.empty:
            logger.info("  Loading dim_glossary (upsert)...")
            self.loader.upsert_dataframe(
                dim_glossary,
                table_name="dim_glossary",
                schema="warehouse",
                conflict_columns=["glossary_key"],
            )

        # Load fact (idempotent)
        logger.info("  Loading fact_economic (upsert)...")
        self.loader.upsert_dataframe(
            fact_df,
            table_name="fact_economic",
            schema="warehouse",
            conflict_columns=["date_key", "region_key", "indicator_key"],
            update_columns=["value"],
        )

        # Load Data Marts
        logger.info("  Building Data Marts...")
        self._build_marts()

        # Step 7: Verify
        logger.info("Step 7/7: Verifying load")
        fact_count = self.loader.verify_row_count("fact_economic")
        date_count = self.loader.verify_row_count("dim_date")
        region_count = self.loader.verify_row_count("dim_region")
        indicator_count = self.loader.verify_row_count("dim_indicator")
        dataset_count = self.loader.verify_row_count("dim_dataset")
        glossary_count = self.loader.verify_row_count("dim_glossary")
        logger.info(f"  fact_economic: {fact_count} rows")
        logger.info(f"  dim_date: {date_count} rows")
        logger.info(f"  dim_region: {region_count} rows")
        logger.info(f"  dim_indicator: {indicator_count} rows")
        logger.info(f"  dim_dataset: {dataset_count} rows")
        logger.info(f"  dim_glossary: {glossary_count} rows")

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    def _fetch_region_codes(self) -> Optional[List[str]]:
        """Fetch region codes for the current domain.

        For national data (domain='0000'), fetches all province codes.
        For a specific province, fetches all regency codes.
        For other levels, fetches the appropriate domain list.

        Returns:
            List of region codes in the order they appear in the
            datacontent values, or None if the domain list cannot
            be fetched.
        """
        try:
            if self.domain and self.domain != "0000":
                # For a specific province, fetch regencies
                response = self.domain_extractor.fetch_regencies()
            else:
                # For national, fetch provinces
                response = self.domain_extractor.fetch_provinces()

            regions = self.domain_extractor.parse_domain_list(response)
            return [str(r["region_code"]) for r in regions]
        except Exception as exc:
            logger.warning(f"  Could not fetch region codes: {exc}")
            return None

    def _extract_metadata(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
        """Extract SIMDASI and Glosarium metadata.

        Returns:
            Tuple of (dim_dataset, dim_glossary, glossary_records).
            Empty DataFrames if metadata cannot be fetched.
        """
        # SIMDASI
        dim_dataset = pd.DataFrame()
        try:
            simdasi_response = self.simdasi_extractor.fetch_all()
            simdasi_metadata = self.simdasi_extractor.parse_table_metadata(
                simdasi_response
            )
            if simdasi_metadata:
                # Add available years from the current dataset
                simdasi_metadata["available_years"] = self.periods
                dim_dataset = self.metadata_transformer.build_dim_dataset(
                    [simdasi_metadata]
                )
                logger.info(f"  SIMDASI metadata: {simdasi_metadata.get('title')}")
        except Exception as exc:
            logger.warning(f"  Could not fetch SIMDASI metadata: {exc}")

        # Glosarium
        dim_glossary = pd.DataFrame()
        glossary_records: List[Dict[str, Any]] = []
        try:
            glossary_response = self.glossary_extractor.fetch()
            glossary_records = self.glossary_extractor.parse_glossary(
                glossary_response
            )
            if glossary_records:
                dim_glossary = self.metadata_transformer.build_dim_glossary(
                    glossary_records
                )
                logger.info(f"  Glosarium entries: {len(glossary_records)}")
        except Exception as exc:
            logger.warning(f"  Could not fetch Glosarium: {exc}")

        return dim_dataset, dim_glossary, glossary_records

    def _build_dim_indicator(
        self,
        variables: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> pd.DataFrame:
        """Build the dim_indicator DataFrame from staged variables.

        The aggregation_method column is part of the semantic layer:
        it defines how the indicator should be aggregated nationally.
        Default is 'SUM'. Could be 'AVG' for average-based indicators
        or 'N/A' for rates/indices that should not be aggregated.
        """
        records = []
        for var in variables:
            records.append(
                {
                    "indicator_key": str(var.get("variable_id")),
                    "indicator_code": str(var.get("variable_id")),
                    "indicator_name": var.get("variable_name"),
                    "subject_name": metadata.get("subject"),
                    "category_name": None,
                    "unit": metadata.get("unit"),
                    "frequency": metadata.get("frequency"),
                    "concept": None,
                    "definition": None,
                    "classification": None,
                    "measure": None,
                    "data_source": None,
                    "aggregation_method": "SUM",
                }
            )
        return pd.DataFrame(records)

    def _build_dim_region(self) -> pd.DataFrame:
        """Build the dim_region DataFrame from the Domain API.

        Fetches the province list and maps region codes to names.
        For national data (domain='0000'), creates a single national row.
        """
        if self.domain and self.domain != "0000":
            # Try to fetch province list to map region codes
            try:
                response = self.domain_extractor.fetch_provinces()
                regions = self.domain_extractor.parse_domain_list(response)
                records = [
                    {
                        "region_key": str(r["region_code"]),
                        "region_code": str(r["region_code"]),
                        "region_name": r["region_name"],
                        "province_name": r["region_name"],
                        "regency_name": None,
                        "district_name": None,
                    }
                    for r in regions
                ]
                return pd.DataFrame(records)
            except Exception as exc:
                logger.warning(f"  Could not fetch domain list: {exc}")
                # Fall back to a minimal region record
                return pd.DataFrame(
                    [
                        {
                            "region_key": str(self.domain),
                            "region_code": str(self.domain),
                            "region_name": f"Region {self.domain}",
                            "province_name": None,
                            "regency_name": None,
                            "district_name": None,
                        }
                    ]
                )
        else:
            # National data
            return pd.DataFrame(
                [
                    {
                        "region_key": "0000",
                        "region_code": "0000",
                        "region_name": "INDONESIA",
                        "province_name": "INDONESIA",
                        "regency_name": None,
                        "district_name": None,
                    }
                ]
            )

    def _table_is_empty(self, table_name: str) -> bool:
        """Check if a warehouse table is empty."""
        try:
            return self.loader.verify_row_count(table_name) == 0
        except Exception:
            return True

    def _table_exists(self, schema: str, table: str) -> bool:
        """Check if a table exists in the given schema.

        Uses PostgreSQL's to_regclass function which returns NULL
        if the relation doesn't exist.
        """
        from sqlalchemy import text

        try:
            with self.loader.connect().connect() as conn:
                res = conn.execute(
                    text("SELECT to_regclass(:qualified) IS NOT NULL AS exists"),
                    {"qualified": f"{schema}.{table}"},
                )
                return bool(res.scalar())
        except Exception:
            return False

    def _create_tables(self) -> None:
        """Create warehouse tables if they don't exist.

        Executes each SQL file as a single script to preserve statement
        order (CREATE TABLE before CREATE INDEX), which prevents
        UndefinedTable errors when an index references a table.
        """
        sql_dir = Path(__file__).resolve().parent.parent / "sql" / "ddl"

        # Execute in dependency order: schemas first, then dimensions, then facts
        file_order = ["schemas.sql", "dimensions.sql", "facts.sql"]

        for filename in file_order:
            sql_file = sql_dir / filename
            if not sql_file.exists():
                logger.warning(f"  SQL file not found: {sql_file}")
                continue

            sql_content = sql_file.read_text()
            try:
                # Execute the entire file as a script
                # exec_driver_sql handles multi-statement scripts correctly
                self.loader.execute_sql(sql_content)
                logger.info(f"  Executed DDL file: {filename}")
            except Exception as exc:
                logger.error(f"  Failed executing {filename}: {exc}")
                # Fail fast to avoid subsequent UndefinedTable errors
                raise

            # After facts.sql, verify critical tables exist
            if filename == "facts.sql":
                missing = []
                for table in ["fact_economic", "fact_trade"]:
                    if not self._table_exists("warehouse", table):
                        missing.append(table)
                if missing:
                    raise RuntimeError(
                        f"DDL executed but tables missing in warehouse: {missing}"
                    )

    def _build_marts(self) -> None:
        """Build Data Mart materialized views.

        Reads the SQL from sql/mart/marts.sql and executes it.
        The marts are designed to answer specific business questions
        (see docs/business_questions.md).
        """
        mart_sql_path = (
            Path(__file__).resolve().parent.parent / "sql" / "mart" / "marts.sql"
        )

        if not mart_sql_path.exists():
            logger.warning(f"  Mart SQL file not found: {mart_sql_path}")
            return

        sql_content = mart_sql_path.read_text()

        # Execute the entire script - preserves statement order
        try:
            self.loader.execute_sql(sql_content)
            logger.info("  Executed marts.sql script")
        except Exception as exc:
            logger.error(f"  Failed executing mart SQL: {exc}")
            raise


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="BPS Data Warehouse ETL Pipeline"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="BPS domain code (e.g., 1100 for ACEH, or 0000 for national)",
    )
    parser.add_argument(
        "--var",
        required=True,
        help="BPS variable ID (e.g., 145)",
    )
    parser.add_argument(
        "--th",
        required=True,
        help="Period(s), e.g., 2020 or 2020,2021,2022",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Dataset name for raw storage (default: var{var})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="BPS API key (overrides .env)",
    )

    args = parser.parse_args()

    pipeline = Pipeline(
        api_key=args.api_key,
        domain=args.domain,
        var=args.var,
        periods=args.th,
        dataset_name=args.dataset,
    )
    pipeline.run()


if __name__ == "__main__":
    main()