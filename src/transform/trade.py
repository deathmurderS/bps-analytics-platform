"""Transformation logic for Foreign Trade data.

Builds dimension and fact DataFrames for the trade domain from
staging records produced by the BPS Foreign Trade extractor.

Grain: one row = one commodity × one country × one port × one period.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class TradeTransformer:
    """Build trade dimensions and fact DataFrames from staging data."""

    def build_fact_trade(
        self,
        trade_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Build the fact_trade table from staging data.

        Expected staging columns:
            trade_type, commodity_code, country_code, port_code,
            period, value_usd, net_weight_kg

        Returns:
            DataFrame with columns:
                date_key, product_key, country_key, port_key,
                trade_type, value_usd, net_weight_kg
        """
        df = trade_df.copy()

        # Ensure required columns exist
        required = [
            "trade_type",
            "commodity_code",
            "country_code",
            "port_code",
            "period",
            "value_usd",
            "net_weight_kg",
        ]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert period (e.g., "2023" or "2023-01") to date_key
        df["date_key"] = df["period"].apply(
            lambda p: self._period_to_date_key(p)
        )

        # Keys
        df["product_key"] = df["commodity_code"]
        df["country_key"] = df["country_code"]
        df["port_key"] = df["port_code"]

        # Numeric conversions
        df["value_usd"] = pd.to_numeric(df["value_usd"], errors="coerce")
        df["net_weight_kg"] = pd.to_numeric(
            df["net_weight_kg"], errors="coerce"
        )

        # Select fact columns
        fact_columns = [
            "date_key",
            "product_key",
            "country_key",
            "port_key",
            "trade_type",
            "value_usd",
            "net_weight_kg",
        ]
        fact_df = df[fact_columns].copy()

        return fact_df

    @staticmethod
    def _period_to_date_key(period: str) -> int:
        """Convert a BPS period string to a date key.

        Supports:
        - "2023" -> 20230101
        - "2023-01" -> 20230101
        - "2023-01-01" -> 20230101
        """
        if not period:
            return 0
        parts = period.strip().split("-")
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        return year * 10000 + month * 100 + day

    def build_dim_product(
        self,
        product_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Build dim_product from product records.

        Args:
            product_records: List of dicts with keys:
                product_code, product_name

        Returns:
            DataFrame with columns: product_key, product_code, product_name
        """
        records = [
            {
                "product_key": str(rec.get("product_code")),
                "product_code": str(rec.get("product_code")),
                "product_name": rec.get("product_name"),
            }
            for rec in product_records
        ]
        return pd.DataFrame(records)

    def build_dim_country(
        self,
        country_records: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Build dim_country from country records.

        Args:
            country_records: List of dicts with keys:
                country_code, country_name

        """
        records = [
            {
                "country_key": str(rec.get("country_code")),
                "country_code": str(rec.get("country_code")),
                "country_name": rec.get("country_name"),
            }
            for rec in country_records
        ]
        return pd.DataFrame(records)

    def build_dim_trade_flow(self) -> pd.DataFrame:
        """Build the dim_trade_flow dimension.

        Provides the export/import flow dimensions.
        """
        return pd.DataFrame(
            [
                {"trade_flow": "ekspor", "flow_name": "Ekspor"},
                {"trade_flow": "impor", "flow_name": "Impor"},
            ]
        )