"""Real BPS data extraction script.

This script runs the pipeline against the actual BPS WebAPI to:
1. Fetch real BPS data
2. Load it into the warehouse
3. Build the Data Marts
4. Output summary statistics that can be documented in real_insights.md

Usage:
    python scripts/extract_real_data.py \\
        [--domain 0000] [--var 145] [--th 2020,2021,2022,2023,2024] \\
        [--dataset pdrb_nasional]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.settings import settings
from src.extract.bps_api import BPSAPIClient
from src.extract.domain import DomainExtractor
from src.extract.dynamic_data import DynamicDataExtractor
from src.quality.validators import DataQualityValidator
from src.raw.storage import RawStorage
from src.staging.dynamic_transform import DynamicDataTransformer
from src.transform.economic import EconomicTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def extract_real_data(
    domain: str,
    var: str,
    periods: str,
    dataset_name: str,
) -> Dict[str, object]:
    """Run real BPS data extraction and return summary."""
    logger.info("=" * 60)
    logger.info("REAL BPS DATA EXTRACTION")
    logger.info("=" * 60)

    # Step 1: Validate API key
    settings.validate()
    logger.info(f"API key present: {bool(settings.bps_api_key)}")

    # Step 2: Initialize clients
    client = BPSAPIClient()
    extractor = DynamicDataExtractor(client)
    domain_extractor = DomainExtractor(client)
    storage = RawStorage()
    validator = DataQualityValidator()

    # Step 3: Fetch dynamic data
    logger.info(f"Fetching var={var}, domain={domain}, periods={periods}")
    response = extractor.fetch(
        domain=domain,
        var=var,
        periods=periods,
    )

    status = response.get("status")
    variables = response.get("variable", [])
    datacontent = response.get("datacontent", [])
    logger.info(f"  Status: {status}")
    logger.info(f"  Variables: {len(variables)}")
    logger.info(f"  Data rows: {len(datacontent)}")

    if not datacontent:
        logger.error("  No data returned. Check your variable ID and domain.")
        return {"success": False, "error": "No data from API"}

    # Step 4: Save raw response
    raw_file = storage.save(
        response,
        source="dynamic_data",
        dataset=dataset_name,
    )
    logger.info(f"Raw response saved: {raw_file}")

    # Step 5: Fetch region codes
    try:
        if domain and domain != "0000":
            domain_response = domain_extractor.fetch_regencies()
        else:
            domain_response = domain_extractor.fetch_provinces()
        regions = domain_extractor.parse_domain_list(domain_response)
        region_codes = [str(r["region_code"]) for r in regions]
        logger.info(f"Region codes fetched: {len(region_codes)}")
    except Exception as exc:
        logger.warning(f"Could not fetch region codes: {exc}")
        region_codes = None

    # Step 6: Transform to staging
    transformer = DynamicDataTransformer(response, region_codes=region_codes)
    staged = transformer.transform()
    df = staged["data"]
    metadata = staged["metadata"]
    logger.info(f"Staged rows: {len(df)}")

    # Step 7: Data quality
    result = validator.validate(df, context="real-data-extraction")
    print(f"\n{result.summary()}\n")

    if not result.passed:
        logger.error("Data quality checks failed.")
        return {"success": False, "error": "Data quality failed"}

    # Step 8: Build summary for real_insights.md
    summary: Dict[str, object] = {
        "success": True,
        "indicator_name": variables[0].get("label") if variables else "Unknown",
        "variable_id": var,
        "unit": metadata.get("unit"),
        "frequency": metadata.get("frequency"),
        "table_name": metadata.get("table_name"),
        "table_id": metadata.get("table_id"),
        "periods": periods,
        "domain": domain,
        "regions": len(region_codes or []),
        "total_records": len(df),
        "years_available": sorted(df["year"].unique().tolist()),
        "raw_file": str(raw_file),
    }

    # National values by year
    national_values = {}
    for year in df["year"].unique():
        year_df = df[df["year"] == year]
        national_values[int(year)] = round(year_df["value"].sum(), 6)
    summary["national_values"] = national_values

    # Region values for latest year
    latest_year = max(df["year"])
    latest_df = df[df["year"] == latest_year]
    region_values = {}
    for _, row in latest_df.iterrows():
        region_values[str(row["region_id"])] = round(float(row["value"]), 6)
    summary["latest_year_region_values"] = region_values
    summary["latest_year"] = int(latest_year)

    logger.info("=" * 60)
    logger.info("EXTRACTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Indicator: {summary['indicator_name']}")
    logger.info(f"Period: {periods}")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Raw file: {raw_file}")

    return summary


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Extract real BPS data")
    parser.add_argument("--domain", default="0000", help="BPS domain code")
    parser.add_argument("--var", required=True, help="BPS variable ID")
    parser.add_argument("--th", required=True, help="Periods (comma-separated)")
    parser.add_argument("--dataset", required=True, help="Dataset name")
    args = parser.parse_args()

    result = extract_real_data(
        domain=args.domain,
        var=args.var,
        periods=args.th,
        dataset_name=args.dataset,
    )

    if result.get("success"):
        logger.info("\n✅ Real data extraction successful.")
        logger.info("Use the output above to populate docs/real_insights.md")
    else:
        logger.error(f"\n❌ Extraction failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()