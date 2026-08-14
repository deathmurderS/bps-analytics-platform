"""Tests for the data quality validators."""

import pandas as pd
import pytest

from src.quality.validators import DataQualityValidator, ValidationResult


class TestDataQualityValidator:
    """Test the data quality validator."""

    def _make_valid_df(self):
        """Create a valid DataFrame for testing."""
        return pd.DataFrame(
            {
                "variable_id": ["145", "145", "145"],
                "region_id": ["1100", "1200", "1300"],
                "year": [2023, 2023, 2023],
                "value": [100.5, 200.3, 300.1],
            }
        )

    def test_valid_data_passes(self):
        """Valid data should pass all checks."""
        df = self._make_valid_df()
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert len(result.checks) > 0

    def test_missing_required_column_fails(self):
        """Missing required column should fail."""
        df = self._make_valid_df().drop(columns=["value"])
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "required_columns"][0]
        assert check["status"] == "FAIL"

    def test_empty_dataset_fails(self):
        """Empty dataset should fail."""
        df = pd.DataFrame(
            columns=["variable_id", "region_id", "year", "value"]
        )
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "empty_dataset"][0]
        assert check["status"] == "FAIL"

    def test_missing_values_fail(self):
        """Missing values should fail."""
        df = self._make_valid_df()
        df.loc[0, "value"] = None
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "missing_values"][0]
        assert check["status"] == "FAIL"

    def test_duplicates_fail(self):
        """Duplicate rows should fail."""
        df = self._make_valid_df()
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "duplicates"][0]
        assert check["status"] == "FAIL"

    def test_invalid_numeric_fails(self):
        """Non-numeric values should fail."""
        df = pd.DataFrame(
            {
                "variable_id": ["145", "145", "145"],
                "region_id": ["1100", "1200", "1300"],
                "year": [2023, 2023, 2023],
                "value": ["100.5", "not_a_number", "300.1"],
            }
        )
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "numeric_value"][0]
        assert check["status"] == "FAIL"

    def test_invalid_year_fails(self):
        """Invalid year should fail."""
        df = pd.DataFrame(
            {
                "variable_id": ["145", "145", "145"],
                "region_id": ["1100", "1200", "1300"],
                "year": ["2023", "invalid", "2023"],
                "value": [100.5, 200.3, 300.1],
            }
        )
        validator = DataQualityValidator()
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "period"][0]
        assert check["status"] == "FAIL"

    def test_invalid_region_codes_fail(self):
        """Invalid region codes should fail when allowed codes provided."""
        df = self._make_valid_df()
        validator = DataQualityValidator(
            allowed_region_codes=["1100", "1200"]
        )
        result = validator.validate(df)

        assert result.passed is False
        check = [c for c in result.checks if c["check"] == "region_codes"][0]
        assert check["status"] == "FAIL"

    def test_negative_values_warn(self):
        """Negative values should produce a warning but not fail."""
        df = self._make_valid_df()
        df.loc[0, "value"] = -100.5
        validator = DataQualityValidator()
        result = validator.validate(df)

        # Negative values are a WARN, not a FAIL
        assert result.passed is True
        check = [c for c in result.checks if c["check"] == "negative_values"][0]
        assert check["status"] == "WARN"

    def test_summary_output(self):
        """Summary should be a non-empty string."""
        df = self._make_valid_df()
        validator = DataQualityValidator()
        result = validator.validate(df)

        summary = result.summary()
        assert isinstance(summary, str)
        assert "Data Quality Validation Results" in summary
        assert "PASSED" in summary