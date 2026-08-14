"""Transformation logic for economic indicators into dimensional model.

Converts staging DataFrames into dimensions and fact tables suitable
for loading into the PostgreSQL warehouse.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class EconomicTransformer:
    """Build dimension and fact DataFrames from staging data.

    Grain: one row = one indicator × one region × one period.
    """

    def __init__(
        self,
        region_codes: Optional[List[str]] = None,
        region_names: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Args:
            region_codes: List of valid region codes for filtering.
            region_names: Mapping of region_code -> region_name.
        """
        self.region_codes = region_codes
        self.region_names = region_names or {}

    def build_fact_economic(
        self,
        staging_df: pd.DataFrame,
        indicator_code: Optional[str] = None,
    ) -> pd.DataFrame:
        """Build the fact_economic table from staging data.

        Expected staging columns:
            variable_id, region_id, year, value

        Args:
            staging_df: Staging DataFrame.
            indicator_code: Optional indicator code to tag rows.

        Returns:
            DataFrame with columns:
                date_key, region_key, indicator_key, value
        """
        df = staging_df.copy()

        # Ensure required columns exist
        required = ["variable_id", "region_id", "year", "value"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert year to a date key (e.g., YYYY0101 or YYYY0701 for mid-year)
        df["date_key"] = df["year"].astype(int) * 10000 + 101

        # Use variable_id as indicator_key (will be linked in SQL)
        df["indicator_key"] = df["variable_id"]

        # Use region_id as region_key (will be linked in SQL)
        df["region_key"] = df["region_id"]

        # Filter to selected columns
        fact_columns = [
            "date_key",
            "region_key",
            "indicator_key",
            "value",
            "year",
        ]
        fact_df = df[fact_columns].copy()

        return fact_df

    def build_dim_date(self, years: List[int]) -> pd.DataFrame:
        """Build the dim_date dimension table.

        For annual data, the date_key represents the reference period
        (e.g., 20200101 for year 2020). The period_type column
        documents that this is an annual reference period, not an
        actual observation date.

        Args:
            years: List of years to include.

        Returns:
            DataFrame with columns:
                date_key, full_date, year, quarter, month, month_name,
                period_type
        """
        records: List[Dict[str, Any]] = []

        for year in years:
            records.append(
                {
                    "date_key": year * 10000 + 101,
                    "full_date": pd.Timestamp(year=year, month=1, day=1),
                    "year": year,
                    "quarter": 1,
                    "month": 1,
                    "month_name": "January",
                    "period_type": "YEAR",
                }
            )

        return pd.DataFrame(records)

    def build_dim_region(self, region_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Build the dim_region dimension table.

        Args:
            region_records: List of dicts with keys:
                region_code, region_name, province_name (optional),
                regency_name (optional), district_name (optional).

        Returns:
            DataFrame with columns:
                region_key, region_code, region_name, province_name,
                regency_name, district_name
        """
        df = pd.DataFrame(region_records)
        if "region_key" not in df.columns:
            df["region_key"] = df["region_code"]
        return df

    def build_dim_indicator(
        self,
        indicator_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Build the dim_indicator dimension table.

        Args:
            indicator_records: List of dicts with keys:
                indicator_code, indicator_name, subject_name (optional),
                category_name (optional), unit (optional), frequency (optional).

        Returns:
            DataFrame with columns:
                indicator_key, indicator_code, indicator_name,
                subject_name, category_name, unit, frequency
        """
        df = pd.DataFrame(indicator_records)
        if "indicator_key" not in df.columns:
            df["indicator_key"] = df["indicator_code"]
        return df