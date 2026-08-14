"""Tests for the Foreign Trade domain (Phase 5)."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.extract.foreign_trade import ForeignTradeExtractor
from src.transform.trade import TradeTransformer

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def trade_response():
    """Load the Foreign Trade response fixture."""
    fixture_path = FIXTURE_DIR / "bps_trade_response.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def trade_df(trade_response):
    """Parse trade response into a DataFrame."""
    extractor = ForeignTradeExtractor(client=None)  # type: ignore
    records = extractor.parse_trade_records(trade_response)
    return pd.DataFrame(records)


class TestForeignTradeExtractor:
    """Test the foreign trade extractor."""

    def test_parse_trade_records(self, trade_response):
        """Should parse trade response into records."""
        extractor = ForeignTradeExtractor(client=None)  # type: ignore
        records = extractor.parse_trade_records(trade_response)

        assert len(records) == 5
        assert records[0]["trade_type"] == "ekspor"
        assert records[0]["commodity_code"] == "15111000"
        assert records[0]["commodity_name"] == "Crude Palm Oil"
        assert records[0]["country_code"] == "CN"
        assert records[0]["country_name"] == "China"
        assert records[0]["port_code"] == "ID-BEL"
        assert records[0]["port_name"] == "Belawan"
        assert records[0]["period"] == "2023"
        assert records[0]["value_usd"] == "1250000.50"
        assert records[0]["net_weight_kg"] == "2500000.00"

    def test_parse_empty(self):
        """Should handle empty data."""
        extractor = ForeignTradeExtractor(client=None)  # type: ignore
        records = extractor.parse_trade_records({"data": []})
        assert records == []


class TestTradeTransformer:
    """Test the trade transformer."""

    def test_build_fact_trade(self, trade_df):
        """Should build the fact_trade table."""
        transformer = TradeTransformer()
        fact_df = transformer.build_fact_trade(trade_df)

        assert len(fact_df) == 5
        expected_columns = {
            "date_key", "product_key", "country_key", "port_key",
            "trade_type", "value_usd", "net_weight_kg",
        }
        assert expected_columns.issubset(set(fact_df.columns))

        # Verify date keys
        assert 20230101 in fact_df["date_key"].values
        assert 20240101 in fact_df["date_key"].values

        # Verify values converted to numeric
        assert fact_df["value_usd"].dtype in ["float64", "int64"]
        assert fact_df["net_weight_kg"].dtype in ["float64", "int64"]

        # Verify keys
        assert set(fact_df["product_key"].unique()) == {"15111000", "10059090"}
        assert set(fact_df["country_key"].unique()) == {"CN", "IN", "US", "BR"}
        assert set(fact_df["port_key"].unique()) == {"ID-BEL", "ID-TPP"}

    def test_missing_column_raises(self, trade_df):
        """Should raise error if required column is missing."""
        invalid_df = trade_df.drop(columns=["value_usd"])
        transformer = TradeTransformer()
        with pytest.raises(ValueError, match="value_usd"):
            transformer.build_fact_trade(invalid_df)

    def test_period_to_date_key(self):
        """Verify period conversion."""
        assert TradeTransformer._period_to_date_key("2023") == 20230101
        assert TradeTransformer._period_to_date_key("2023-01") == 20230101
        assert TradeTransformer._period_to_date_key("2023-01-01") == 20230101
        assert TradeTransformer._period_to_date_key("") == 0

    def test_build_dim_product(self):
        """Should build the product dimension."""
        transformer = TradeTransformer()
        products = [
            {"product_code": "15111000", "product_name": "Crude Palm Oil"},
            {"product_code": "10059090", "product_name": "Maize (Corn)"},
        ]
        dim_product = transformer.build_dim_product(products)

        assert len(dim_product) == 2
        assert dim_product.iloc[0]["product_key"] == "15111000"
        assert dim_product.iloc[0]["product_name"] == "Crude Palm Oil"

    def test_build_dim_country(self):
        """Verify the country dimension."""
        transformer = TradeTransformer()
        countries = [
            {"country_code": "CN", "country_name": "China"},
            {"country_code": "US", "country_name": "United States"},
        ]
        dim_country = transformer.build_dim_country(countries)

        assert len(dim_country) == 2
        assert dim_country.iloc[0]["country_key"] == "CN"
        assert dim_country.iloc[0]["country_name"] == "China"

    def test_build_dim_trade_flow(self):
        """Verify the trade flow dimension."""
        transformer = TradeTransformer()
        dim_flow = transformer.build_dim_trade_flow()

        assert len(dim_flow) == 2
        assert dim_flow.iloc[0]["trade_flow"] == "ekspor"
        assert dim_flow.iloc[1]["trade_flow"] == "impor"


class TestTradeDataMartCalculations:
    """Verify trade mart analytical correctness."""

    def test_export_trend(self, trade_df):
        """Export total for 2023 should be sum of export values."""
        transformer = TradeTransformer()
        fact_df = transformer.build_fact_trade(trade_df)

        exports_2023 = fact_df[
            (fact_df["date_key"] == 20230101)
            & (fact_df["trade_type"] == "ekspor")
        ]
        total_export = exports_2023["value_usd"].sum()
        # 1250000.50 + 980000.25 = 2230000.75
        assert round(total_export, 2) == 2230000.75

    def test_import_trend(self, trade_df):
        """Import total for 2023 should be sum of import values."""
        transformer = TradeTransformer()
        fact_df = transformer.build_fact_trade(trade_df)

        imports_2023 = fact_df[
            (fact_df["date_key"] == 20230101)
            & (fact_df["trade_type"] == "impor")
        ]
        total_import = imports_2023["value_usd"].sum()
        # 450000.75 + 320000.00 = 770000.75
        assert round(total_import, 2) == 770000.75

    def test_commodity_ranking(self, trade_df):
        """CPO should be the top export commodity."""
        transformer = TradeTransformer()
        fact_df = transformer.build_fact_trade(trade_df)

        # CPO exports: 2230000.75 (2023) + 1350000 (2024)
        cpo_export = fact_df[
            (fact_df["product_key"] == "15111000")
            & (fact_df["trade_type"] == "ekspor")
        ]["value_usd"].sum()
        assert round(cpo_export, 2) == 3580000.75

    def test_trade_balance(self, trade_df):
        """Trade balance for 2023 should be exports - imports."""
        transformer = TradeTransformer()
        fact_df = transformer.build_fact_trade(trade_df)

        exports = fact_df[
            (fact_df["date_key"] == 20230101)
            & (fact_df["trade_type"] == "ekspor")
        ]["value_usd"].sum()

        imports = fact_df[
            (fact_df["date_key"] == 20230101)
            & (fact_df["trade_type"] == "impor")
        ]["value_usd"].sum()

        balance = exports - imports
        # 2230000.75 - 770000.75 = 1460000.00
        assert round(balance, 2) == 1460000.00