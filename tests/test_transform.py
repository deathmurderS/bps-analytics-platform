"""Tests for the transform module and raw storage."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.raw.storage import RawStorage
from src.transform.economic import EconomicTransformer


class TestEconomicTransformer:
    """Test the economic transformer."""

    def _make_staging_df(self):
        """Create a staging DataFrame for testing."""
        return pd.DataFrame(
            {
                "variable_id": ["145", "145", "145"],
                "region_id": ["1100", "1200", "1300"],
                "year": [2023, 2023, 2024],
                "value": [100.5, 200.3, 300.1],
            }
        )

    def test_build_fact_economic(self):
        """Should build fact table from staging data."""
        staging_df = self._make_staging_df()
        transformer = EconomicTransformer()
        fact_df = transformer.build_fact_economic(staging_df)

        expected_columns = {"date_key", "region_key", "indicator_key", "value", "year"}
        assert expected_columns.issubset(set(fact_df.columns))
        assert len(fact_df) == 3

        # Date key should be YYYY0101 format
        assert fact_df.iloc[0]["date_key"] == 20230101
        assert fact_df.iloc[2]["date_key"] == 20240101

        # Keys should be set correctly
        assert fact_df.iloc[0]["indicator_key"] == "145"
        assert fact_df.iloc[0]["region_key"] == "1100"

    def test_build_fact_economic_missing_column(self):
        """Should raise error if required column is missing."""
        staging_df = self._make_staging_df().drop(columns=["value"])
        transformer = EconomicTransformer()

        with pytest.raises(ValueError, match="value"):
            transformer.build_fact_economic(staging_df)

    def test_build_dim_date(self):
        """Should build the date dimension."""
        transformer = EconomicTransformer()
        dim_date = transformer.build_dim_date([2022, 2023, 2024])

        assert len(dim_date) == 3
        assert list(dim_date["year"]) == [2022, 2023, 2024]
        assert list(dim_date["date_key"]) == [20220101, 20230101, 20240101]
        assert list(dim_date["month_name"]) == ["January", "January", "January"]
        assert list(dim_date["period_type"]) == ["YEAR", "YEAR", "YEAR"]

    def test_build_dim_region(self):
        """Should build the region dimension."""
        transformer = EconomicTransformer()
        regions = [
            {"region_code": "1100", "region_name": "ACEH"},
            {"region_code": "1200", "region_name": "SUMATERA UTARA"},
        ]
        dim_region = transformer.build_dim_region(regions)

        assert len(dim_region) == 2
        assert list(dim_region["region_code"]) == ["1100", "1200"]
        assert list(dim_region["region_key"]) == ["1100", "1200"]

    def test_build_dim_indicator(self):
        """Should build the indicator dimension."""
        transformer = EconomicTransformer()
        indicators = [
            {
                "indicator_code": "145",
                "indicator_name": "PDRB ADHK",
                "subject_name": "Ekonomi",
                "unit": "Miliar Rupiah",
                "frequency": "Tahunan",
            }
        ]
        dim_indicator = transformer.build_dim_indicator(indicators)

        assert len(dim_indicator) == 1
        assert dim_indicator.iloc[0]["indicator_key"] == "145"
        assert dim_indicator.iloc[0]["indicator_name"] == "PDRB ADHK"


class TestRawStorage:
    """Test the raw storage module."""

    def test_save_and_load(self, tmp_path):
        """Should save a raw response and load it back."""
        storage = RawStorage(base_dir=tmp_path)
        data = {"status": "200", "data": [{"kode": "1100", "nama": "ACEH"}]}

        saved_path = storage.save(
            data,
            source="domain",
            dataset="prov",
        )

        assert saved_path.exists()
        loaded = storage.load(saved_path)
        assert loaded == data

    def test_path_structure(self, tmp_path):
        """Should create the expected directory structure."""
        storage = RawStorage(base_dir=tmp_path)
        data = {"test": "value"}

        saved_path = storage.save(
            data,
            source="dynamic_data",
            dataset="pdrb",
        )

        # Path should be: {base}/bps/dynamic_data/pdrb/YYYY/MM/DD/response.json
        parts = saved_path.parts
        assert parts[-1] == "response.json"
        assert "bps" in parts
        assert "dynamic_data" in parts
        assert "pdrb" in parts

    def test_list_files(self, tmp_path):
        """Should list saved raw files."""
        storage = RawStorage(base_dir=tmp_path)

        storage.save({"a": 1}, source="domain", dataset="prov")
        storage.save({"b": 2}, source="domain", dataset="kab")

        files = storage.list_files(source="domain")
        assert len(files) == 2

        all_files = storage.list_files()
        assert len(all_files) == 2

    def test_list_files_empty(self, tmp_path):
        """Should return empty list for no files."""
        storage = RawStorage(base_dir=tmp_path)
        assert storage.list_files() == []