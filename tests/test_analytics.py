"""Phase 4A — Analytical Validation Tests.

Verifies that Data Mart calculations are analytically correct and
that data remains consistent from source → warehouse → mart.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.quality.validators import DataQualityValidator
from src.staging.dynamic_transform import DynamicDataTransformer
from src.transform.economic import EconomicTransformer

FIXTURE_DIR = Path(__file__).parent / "fixtures"

REGION_CODES = ["1100", "1200", "1300", "1400"]
REGION_NAMES = {
    "1100": "ACEH",
    "1200": "SUMATERA UTARA",
    "1300": "SUMATERA BARAT",
    "1400": "RIAU",
}


@pytest.fixture
def bps_response():
    """Load the realistic BPS dynamic data response fixture."""
    fixture_path = FIXTURE_DIR / "bps_dynamic_response.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def staging_df(bps_response):
    """Build the staging DataFrame from the fixture."""
    transformer = DynamicDataTransformer(bps_response, region_codes=REGION_CODES)
    return transformer.to_tabular()


@pytest.fixture
def fact_df(staging_df):
    """Build the fact DataFrame from staging data."""
    transformer = EconomicTransformer()
    return transformer.build_fact_economic(staging_df)


class TestDataMartCalculations:
    """Verify Data Mart analytical correctness."""

    def test_indicator_trend_national_value(self, staging_df):
        """Q1: National value should be the SUM of all regions.

        For PDRB (a stock/total indicator), the national value is
        the sum of all provincial values.
        """
        # Expected national values per year from fixture
        # 2020: 126.51 + 508.83 + 32.75 + 1.05 = 669.14
        # 2021: 128.94 + 519.07 + 33.42 + 1.07 = 682.50
        # 2022: 133.45 + 536.12 + 34.58 + 1.10 = 705.25

        for year, expected in [(2020, 669.14), (2021, 682.50), (2022, 705.25)]:
            year_df = staging_df[staging_df["year"] == year]
            national_value = year_df["value"].sum()
            assert round(national_value, 2) == expected

    def test_indicator_trend_growth_rate(self, staging_df):
        """Q1: Growth rate should be (current - previous) / previous * 100."""
        # Get national values
        values_by_year = {}
        for year in [2020, 2021, 2022]:
            year_df = staging_df[staging_df["year"] == year]
            values_by_year[year] = year_df["value"].sum()

        # 2021 growth: (682.50 - 669.14) / 669.14 * 100 = 1.9965...%
        expected_growth = (
            (values_by_year[2021] - values_by_year[2020])
            / values_by_year[2020]
            * 100
        )
        assert round(expected_growth, 2) == 2.00

        # 2022 growth: (705.25 - 682.50) / 682.50 * 100 = 3.333...%
        expected_growth = (
            (values_by_year[2022] - values_by_year[2021])
            / values_by_year[2021]
            * 100
        )
        assert round(expected_growth, 2) == 3.33

    def test_regional_performance_rank(self, staging_df):
        """Q2: Regional rank should order regions by value descending."""
        # For year 2020
        year_df = staging_df[staging_df["year"] == 2020]
        ranked = year_df.sort_values("value", ascending=False)

        expected_order = ["1200", "1100", "1300", "1400"]  # by value desc
        actual_order = ranked["region_id"].tolist()

        assert actual_order == expected_order

        # Verify rank values
        # SUMATERA UTARA (1200) has highest value → rank 1
        assert ranked.iloc[0]["region_id"] == "1200"
        # RIAU (1400) has lowest value → rank 4
        assert ranked.iloc[-1]["region_id"] == "1400"

    def test_regional_growth_calculation(self, staging_df):
        """Q3: Regional growth should be per-region YoY change."""
        # ACEH (1100):
        # 2020: 126.51, 2021: 128.94
        # Growth = (128.94 - 126.51) / 126.51 * 100 = 1.9207...%
        aceh_2020 = staging_df[
            (staging_df["year"] == 2020) & (staging_df["region_id"] == "1100")
        ]["value"].iloc[0]
        aceh_2021 = staging_df[
            (staging_df["year"] == 2021) & (staging_df["region_id"] == "1100")
        ]["value"].iloc[0]

        growth = (aceh_2021 - aceh_2020) / aceh_2020 * 100
        assert round(growth, 2) == 1.92

        # SUMATERA UTARA (1200):
        # 2020: 508.83, 2021: 519.07
        # Growth = (519.07 - 508.83) / 508.83 * 100 = 2.0124...%
        sumut_2020 = staging_df[
            (staging_df["year"] == 2020) & (staging_df["region_id"] == "1200")
        ]["value"].iloc[0]
        sumut_2021 = staging_df[
            (staging_df["year"] == 2021) & (staging_df["region_id"] == "1200")
        ]["value"].iloc[0]

        growth = (sumut_2021 - sumut_2020) / sumut_2020 * 100
        assert round(growth, 2) == 2.01

    def test_economic_overview_region_count(self, staging_df):
        """Q4: Region count should equal distinct regions per year."""
        for year in [2020, 2021, 2022]:
            year_df = staging_df[staging_df["year"] == year]
            region_count = year_df["region_id"].nunique()
            assert region_count == 4  # All 4 regions in fixture

    def test_region_count_consistency(self, staging_df):
        """All years should have the same number of regions."""
        counts = staging_df.groupby("year")["region_id"].nunique()
        assert len(counts) == 3  # 3 years
        assert (counts == 4).all()  # All years have 4 regions


class TestReconciliation:
    """Verify data consistency from source → warehouse → mart."""

    def test_fact_preserves_source_values(self, staging_df, fact_df):
        """Every value in fact should match the staging source."""
        # Merge on keys to compare values
        # fact_df has: date_key, region_key, indicator_key, value, year
        # staging_df has: variable_id, vervar_id, region_id, year, value
        merged = fact_df.merge(
            staging_df,
            left_on=["year", "region_key", "indicator_key"],
            right_on=["year", "region_id", "variable_id"],
            suffixes=("_fact", "_staging"),
            how="left",
        )

        assert len(merged) == len(fact_df)

        # All values should match
        for idx, row in merged.iterrows():
            assert round(float(row["value_fact"]), 6) == round(
                float(row["value_staging"]), 6
            )

    def test_no_null_values_in_fact(self, fact_df):
        """Fact table should not contain null values."""
        assert fact_df["value"].notna().all()
        assert fact_df["date_key"].notna().all()
        assert fact_df["region_key"].notna().all()
        assert fact_df["indicator_key"].notna().all()

    def test_grain_uniqueness(self, fact_df):
        """Grain: one row = one indicator × one region × one period."""
        # No duplicate combinations of (date_key, region_key, indicator_key)
        key_combos = fact_df[["date_key", "region_key", "indicator_key"]]
        assert key_combos.duplicated().sum() == 0

    def test_date_keys_valid(self, fact_df):
        """Date keys should be valid YYYY0101 format."""
        for date_key in fact_df["date_key"]:
            year = date_key // 10000
            month_day = date_key % 10000
            assert month_day == 101  # Always Jan 1
            assert 1900 <= year <= 2200  # Reasonable year range

    def test_region_codes_valid(self, fact_df):
        """Region codes should match the expected set."""
        valid_regions = set(REGION_CODES)
        assert set(fact_df["region_key"].unique()) == valid_regions

    def test_indicator_keys_consistent(self, staging_df, fact_df):
        """Indicator keys should be consistent between staging and fact."""
        staging_keys = set(staging_df["variable_id"].astype(str).unique())
        fact_keys = set(fact_df["indicator_key"].astype(str).unique())
        assert staging_keys == fact_keys

    def test_sum_reconciliation(self, staging_df, fact_df):
        """Sum of all fact values should match sum of all staging values."""
        staging_sum = staging_df["value"].sum()
        fact_sum = fact_df["value"].sum()
        assert round(staging_sum, 6) == round(fact_sum, 6)


class TestDataQualityOnReconciliation:
    """Verify data quality is maintained through the pipeline."""

    def test_validator_passes_on_staging(self, staging_df):
        """Data quality checks should pass on the staging data."""
        validator = DataQualityValidator()
        result = validator.validate(staging_df, context="analytics-validation")
        assert result.passed is True

    def test_validator_passes_on_fact(self, fact_df):
        """Data quality checks should pass on the fact data."""
        # Fact has different columns; use custom validator
        validator = DataQualityValidator(
            required_columns=["date_key", "region_key", "indicator_key", "value"],
            numeric_columns=["value"],
        )
        result = validator.validate(fact_df, context="fact-validation")

        # The required columns are all present and populated
        assert result.passed is True