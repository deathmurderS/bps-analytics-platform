"""Data quality validators for the staging layer."""

from typing import Any, Dict, List, Optional

import pandas as pd


class ValidationResult:
    """Result of a data quality validation run."""

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []
        self.passed: bool = True

    def add_check(
        self,
        name: str,
        status: str,
        details: Any = None,
    ) -> None:
        """Add a validation check result.

        Only 'FAIL' status causes the overall validation to fail.
        'WARN' and 'INFO' statuses do not fail the validation.
        """
        self.checks.append(
            {
                "check": name,
                "status": status,
                "details": details,
            }
        )
        if status == "FAIL":
            self.passed = False

    def summary(self) -> str:
        """Return a human-readable summary of the validation."""
        lines = ["Data Quality Validation Results:"]
        for check in self.checks:
            lines.append(f"  [{check['status']}] {check['check']}: {check['details']}")
        lines.append(f"Overall: {('PASSED' if self.passed else 'FAILED')}")
        return "\n".join(lines)


class DataQualityValidator:
    """Validate staging DataFrames for data quality issues.

    Validates:
    - Missing values
    - Duplicate observations
    - Invalid numeric values
    - Invalid period formats
    - Empty dataset
    """

    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        numeric_columns: Optional[List[str]] = None,
        allowed_region_codes: Optional[List[str]] = None,
    ) -> None:
        self.required_columns = required_columns or [
            "variable_id",
            "region_id",
            "year",
            "value",
        ]
        self.numeric_columns = numeric_columns or ["value"]
        self.allowed_region_codes = allowed_region_codes

    def validate(
        self,
        df: pd.DataFrame,
        context: Optional[str] = None,
    ) -> ValidationResult:
        """Run all validation checks on the DataFrame."""
        result = ValidationResult()
        if context:
            result.add_check(
                "context",
                "INFO",
                context,
            )

        # 1. Required columns check
        missing_cols = [c for c in self.required_columns if c not in df.columns]
        if missing_cols:
            result.add_check(
                "required_columns",
                "FAIL",
                f"missing columns {missing_cols}",
            )
        else:
            result.add_check(
                "required_columns",
                "PASS",
                f"all required columns present: {self.required_columns}",
            )

        if missing_cols:
            return result

        # 2. Empty dataset check
        if df.empty:
            result.add_check(
                "empty_dataset",
                "FAIL",
                "dataset has no rows",
            )
            return result
        result.add_check(
            "empty_dataset",
            "PASS",
            f"dataset has {len(df)} rows",
        )

        # 3. Missing values check
        missing = df[self.required_columns].isnull().sum()
        missing_total = missing.sum()
        if missing_total > 0:
            missing_details = missing[missing > 0].to_dict()
            result.add_check(
                "missing_values",
                "FAIL",
                f"{missing_total} missing values: {missing_details}",
            )
        else:
            result.add_check(
                "missing_values",
                "PASS",
                "no missing values in required columns",
            )

        # 4. Duplicate check
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            result.add_check(
                "duplicates",
                "FAIL",
                f"{duplicate_count} duplicate rows found",
            )
        else:
            result.add_check(
                "duplicates",
                "PASS",
                "no duplicate rows found",
            )

        # 5. Numeric conversion and value checks
        for col in self.numeric_columns:
            if col in df.columns:
                # Check if column can be converted to numeric
                clean_col = pd.to_numeric(df[col], errors="coerce")
                failed_conversions = clean_col.isnull().sum() - df[col].isnull().sum()
                if failed_conversions > 0:
                    result.add_check(
                        f"numeric_{col}",
                        "FAIL",
                        f"{failed_conversions} values could not be converted to numeric",
                    )
                else:
                    result.add_check(
                        f"numeric_{col}",
                        "PASS",
                        "all values are numeric",
                    )

        # 6. Invalid period check
        if "year" in df.columns:
            years = pd.to_numeric(df["year"], errors="coerce")
            invalid_years = years.isnull().sum()
            # Reasonable year range check
            out_of_range = ((years < 1900) | (years > 2200)).sum()
            if invalid_years > 0 or out_of_range > 0:
                result.add_check(
                    "period",
                    "FAIL",
                    f"{invalid_years} invalid years, {out_of_range} out of range",
                )
            else:
                result.add_check(
                    "period",
                    "PASS",
                    f"years range: {int(years.min())} - {int(years.max())}",
                )

        # 7. Region code check
        if self.allowed_region_codes and "region_id" in df.columns:
            invalid_regions = df[
                ~df["region_id"].astype(str).isin(self.allowed_region_codes)
            ]
            if not invalid_regions.empty:
                result.add_check(
                    "region_codes",
                    "FAIL",
                    f"{len(invalid_regions)} rows with invalid region codes: "
                    f"{invalid_regions['region_id'].unique().tolist()[:10]}",
                )
            else:
                result.add_check(
                    "region_codes",
                    "PASS",
                    "all region codes are valid",
                )

        # 8. Negative value check (for indicators where negative is invalid)
        if "value" in df.columns:
            value_numeric = pd.to_numeric(df["value"], errors="coerce")
            if value_numeric.notna().all():
                negative_values = (value_numeric < 0).sum()
                if negative_values > 0:
                    result.add_check(
                        "negative_values",
                        "WARN",
                        f"{negative_values} negative values found (may be valid depending on indicator)",
                    )
                else:
                    result.add_check(
                        "negative_values",
                        "PASS",
                        "no negative values found",
                    )
            else:
                result.add_check(
                    "negative_values",
                    "SKIP",
                    "value column contains non-numeric data; skipped",
                )

        return result