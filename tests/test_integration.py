"""Integration tests using a realistic BPS API response fixture.

These tests verify that the full transformation pipeline works
correctly with the actual structure of BPS API responses, not just
hand-crafted test data.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.quality.validators import DataQualityValidator
from src.staging.dynamic_transform import DynamicDataTransformer
from src.transform.economic import EconomicTransformer

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def bps_response():
    """Load the realistic BPS dynamic data response fixture."""
    fixture_path = FIXTURE_DIR / "bps_dynamic_response.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def region_codes():
    """Region codes matching the order of values in the fixture.

    The fixture has 4 values per year, corresponding to 4 provinces:
    ACEH (1100), SUMATERA UTARA (1200), SUMATERA BARAT (1300), RIAU (1400)
    """
    return ["1100", "1200", "1300", "1400"]


class TestIntegrationWithRealBPSStructure:
    """Integration tests using the realistic BPS fixture."""

    def test_full_staging_pipeline(self, bps_response, region_codes):
        """Verify the full staging transformation with real BPS structure."""
        transformer = DynamicDataTransformer(bps_response, region_codes=region_codes)
        result = transformer.transform()

        # Metadata extraction
        assert result["metadata"]["table_id"] == "1234"
        assert result["metadata"]["table_code"] == "T-001"
        assert result["metadata"]["table_name"] == (
            "PDRB Atas Dasar Harga Konstan Menurut Provinsi"
        )
        assert result["metadata"]["subject"] == "Ekonomi"
        assert result["metadata"]["unit"] == "Miliar Rupiah"
        assert result["metadata"]["frequency"] == "Tahunan"

        # Variables extraction
        assert len(result["variables"]) == 1
        assert result["variables"][0]["variable_id"] == "145"
        assert result["variables"][0]["variable_name"] == (
            "PDRB Atas Dasar Harga Konstan"
        )

        # Data transformation
        df = result["data"]
        assert len(df) == 12  # 3 years × 4 regions
        assert list(df.columns) == [
            "variable_id",
            "vervar_id",
            "region_id",
            "year",
            "value",
        ]

        # Verify region mapping is correct
        # Year 2020, region 1100 (ACEH) should have value 126.51
        row_2020_aceh = df[
            (df["year"] == 2020) & (df["region_id"] == "1100")
        ]
        assert len(row_2020_aceh) == 1
        assert row_2020_aceh.iloc[0]["value"] == 126.51

        # Year 2020, region 1200 (SUMATERA UTARA) should have value 508.83
        row_2020_sumut = df[
            (df["year"] == 2020) & (df["region_id"] == "1200")
        ]
        assert len(row_2020_sumut) == 1
        assert row_2020_sumut.iloc[0]["value"] == 508.83

        # Year 2022, region 1400 (RIAU) should have value 1.10
        row_2022_riau = df[
            (df["year"] == 2022) & (df["region_id"] == "1400")
        ]
        assert len(row_2022_riau) == 1
        assert row_2022_riau.iloc[0]["value"] == 1.10

        # Verify all years are present
        assert sorted(df["year"].unique().tolist()) == [2020, 2021, 2022]

        # Verify all regions are present
        assert sorted(df["region_id"].unique().tolist()) == [
            "1100",
            "1200",
            "1300",
            "1400",
        ]

    def test_data_quality_on_real_structure(self, bps_response, region_codes):
        """Verify data quality checks pass on realistic BPS data."""
        transformer = DynamicDataTransformer(bps_response, region_codes=region_codes)
        df = transformer.to_tabular()

        validator = DataQualityValidator()
        result = validator.validate(df, context="integration-test")

        assert result.passed is True
        summary = result.summary()
        assert "PASSED" in summary

    def test_fact_building_from_real_structure(self, bps_response, region_codes):
        """Verify fact table building from realistic BPS data."""
        transformer = DynamicDataTransformer(bps_response, region_codes=region_codes)
        df = transformer.to_tabular()

        economic = EconomicTransformer()
        fact_df = economic.build_fact_economic(df)

        assert len(fact_df) == 12
        assert fact_df["date_key"].nunique() == 3  # 3 years
        assert fact_df["region_key"].nunique() == 4  # 4 regions
        assert fact_df["indicator_key"].nunique() == 1  # 1 variable

        # Verify date keys
        assert 20200101 in fact_df["date_key"].values
        assert 20210101 in fact_df["date_key"].values
        assert 20220101 in fact_df["date_key"].values

    def test_dimension_building_from_real_structure(self, bps_response, region_codes):
        """Verify dimension building from realistic BPS data."""
        transformer = DynamicDataTransformer(bps_response, region_codes=region_codes)
        result = transformer.transform()
        df = result["data"]

        economic = EconomicTransformer()
        years = sorted(df["year"].unique().tolist())
        dim_date = economic.build_dim_date(years)

        assert len(dim_date) == 3
        assert list(dim_date["year"]) == [2020, 2021, 2022]

    def test_region_mapping_without_codes(self, bps_response):
        """Verify behavior when region codes are not provided."""
        transformer = DynamicDataTransformer(bps_response, region_codes=None)
        df = transformer.to_tabular()

        # Without region codes, region_id should be None
        assert df["region_id"].isnull().all()
        assert len(df) == 12  # Still transforms all values

    def test_vervar_mapping(self):
        """Verify vervar (vertical variable) mapping logic."""
        response = {
            "variable": [{"id": "1", "label": "Penduduk", "description": ""}],
            "vervar": [
                {"id": "1", "label": "Laki-laki", "description": "", "unit": "orang"},
                {"id": "2", "label": "Perempuan", "description": "", "unit": "orang"},
            ],
            "infotabel": {"tabel": {"id": "1", "kode": "T", "nama": "Test"}},
            "datacontent": [
                ["2020", "100", "95", "200", "190"],
            ],
        }
        region_codes = ["1100", "1200"]
        transformer = DynamicDataTransformer(response, region_codes=region_codes)
        df = transformer.to_tabular()

        # 1 year × 2 regions × 2 vervars = 4 rows
        assert len(df) == 4

        # Region 1100, vervar 1 (Laki-laki) = 100
        row = df[
            (df["region_id"] == "1100") & (df["vervar_id"] == "1")
        ]
        assert row.iloc[0]["value"] == 100

        # Region 1100, vervar 2 (Perempuan) = 95
        row = df[
            (df["region_id"] == "1100") & (df["vervar_id"] == "2")
        ]
        assert row.iloc[0]["value"] == 95

        # Region 1200, vervar 1 (Laki-laki) = 200
        row = df[
            (df["region_id"] == "1200") & (df["vervar_id"] == "1")
        ]
        assert row.iloc[0]["value"] == 200

        # Region 1200, vervar 2 (Perempuan) = 190
        row = df[
            (df["region_id"] == "1200") & (df["vervar_id"] == "2")
        ]
        assert row.iloc[0]["value"] == 190