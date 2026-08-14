"""Transformation logic for metadata (SIMDASI + Glosarium).

Builds the dim_dataset and dim_glossary dimension tables from
SIMDASI and Glosarium API responses.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class MetadataTransformer:
    """Build metadata dimension DataFrames from SIMDASI and Glosarium data."""

    def build_dim_dataset(
        self,
        simdasi_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Build the dim_dataset dimension table from SIMDASI records.

        Args:
            simdasi_records: List of dicts with keys:
                table_id, table_code, title, subject, unit, frequency

        Returns:
            DataFrame with columns:
                dataset_key, table_id, table_code, title, subject,
                available_years, source_system
        """
        records = []
        for idx, record in enumerate(simdasi_records):
            records.append(
                {
                    "dataset_key": idx + 1,
                    "table_id": record.get("table_id"),
                    "table_code": record.get("table_code"),
                    "title": record.get("title"),
                    "subject": record.get("subject"),
                    "available_years": record.get("available_years"),
                    "source_system": "BPS",
                }
            )
        return pd.DataFrame(records)

    def build_dim_glossary(
        self,
        glossary_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Build the dim_glossary dimension table from Glosarium records.

        Args:
            glossary_records: List of dicts with keys:
                glossary_id, indicator_name, concept, definition,
                classification, measure, unit, data_source

        Returns:
            DataFrame with columns:
                glossary_key, glossary_id, indicator_name, concept,
                definition, classification, measure, unit, data_source,
                endpoint
        """
        records = []
        for idx, record in enumerate(glossary_records):
            records.append(
                {
                    "glossary_key": idx + 1,
                    "glossary_id": record.get("glossary_id"),
                    "indicator_name": record.get("indicator_name"),
                    "concept": record.get("concept"),
                    "definition": record.get("definition"),
                    "classification": record.get("classification"),
                    "measure": record.get("measure"),
                    "unit": record.get("unit"),
                    "data_source": record.get("data_source"),
                    "endpoint": "glosarium",
                }
            )
        return pd.DataFrame(records)

    def enrich_indicator_with_glossary(
        self,
        dim_indicator: pd.DataFrame,
        glossary_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Enrich the dim_indicator table with glossary definitions.

        Matches indicators to glossary entries by name (case-insensitive).

        Args:
            dim_indicator: Existing dim_indicator DataFrame.
            glossary_records: List of glossary dicts.

        Returns:
            Enriched dim_indicator DataFrame with additional columns:
                concept, definition, classification, measure, data_source
        """
        df = dim_indicator.copy()

        # Build a lookup from glossary records
        glossary_lookup: Dict[str, Dict[str, Any]] = {}
        for record in glossary_records:
            name = str(record.get("indicator_name", "")).strip().lower()
            if name:
                glossary_lookup[name] = record

        # Add enrichment columns
        df["concept"] = None
        df["definition"] = None
        df["classification"] = None
        df["measure"] = None
        df["data_source"] = None

        # Match by indicator name
        for idx, row in df.iterrows():
            indicator_name = str(row.get("indicator_name", "")).strip().lower()
            if indicator_name in glossary_lookup:
                record = glossary_lookup[indicator_name]
                df.at[idx, "concept"] = record.get("concept")
                df.at[idx, "definition"] = record.get("definition")
                df.at[idx, "classification"] = record.get("classification")
                df.at[idx, "measure"] = record.get("measure")
                df.at[idx, "data_source"] = record.get("data_source")

        return df