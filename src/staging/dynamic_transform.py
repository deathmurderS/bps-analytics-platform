"""Staging transformation for dynamic data responses.

Converts the nested JSON structure from the BPS API into a tabular
format suitable for validation and loading into the warehouse.

The BPS dynamic data response has this structure:
{
    "variable": [...],
    "vervar": [...],
    "infotabel": {...},
    "datacontent": [
        ["2023", "value1", "value2", ...],
        ["2024", "value1", "value2", ...],
        ...
    ]
}

IMPORTANT: The values in each datacontent row map to regions in the
order of the domain list. For example, if the domain is '0000'
(national), the values correspond to all provinces in order. If the
domain is '1100' (Aceh), the values correspond to all regencies in
Aceh in order.

To correctly map values to regions, the transformer needs the list of
region codes that correspond to the domain. This can be obtained from
the Domain API or from the response metadata.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class DynamicDataTransformer:
    """Transform BPS dynamic data JSON into a tabular DataFrame."""

    def __init__(
        self,
        response: Dict[str, Any],
        region_codes: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            response: The BPS API response dict.
            region_codes: List of region codes corresponding to the
                domain. The order must match the order of values in
                each datacontent row. If None, region_id will be
                set to None (caller must resolve later).
        """
        self.response = response
        self.region_codes = region_codes

    def extract_metadata(self) -> Dict[str, Any]:
        """Extract table metadata from the response."""
        info = self.response.get("infotabel", {})
        table = info.get("tabel", {})
        return {
            "table_id": table.get("id"),
            "table_code": table.get("kode"),
            "table_name": table.get("nama"),
            "subject": table.get("subjek"),
            "unit": table.get("satuan"),
            "frequency": table.get("periode"),
        }

    def extract_variables(self) -> List[Dict[str, Any]]:
        """Extract variable definitions."""
        variables = self.response.get("variable", [])
        return [
            {
                "variable_id": var.get("id"),
                "variable_name": var.get("label"),
                "variable_description": var.get("description"),
            }
            for var in variables
        ]

    def extract_vertical_variables(self) -> List[Dict[str, Any]]:
        """Extract vertical variable definitions."""
        vervars = self.response.get("vervar", [])
        return [
            {
                "vervar_id": var.get("id"),
                "vervar_name": var.get("label"),
                "vervar_description": var.get("description"),
                "vervar_unit": var.get("unit"),
            }
            for var in vervars
        ]

    def to_tabular(self) -> pd.DataFrame:
        """Convert the datacontent into a long-format DataFrame.

        The datacontent is a list of rows where the first element is
        the year and the remaining elements are values for each region.

        Value-to-region mapping:
        - If region_codes is provided, values map to regions in order.
        - If vervars exist, values map to (region, vervar) combinations.

        Returns:
            DataFrame with columns:
                variable_id, region_id, year, value
                (plus vervar_id if vertical variables exist)
        """
        datacontent = self.response.get("datacontent", [])
        variables = self.extract_variables()
        vervars = self.extract_vertical_variables()

        # Determine the number of value columns per row
        # Each row: [year, value1, value2, ...]
        # The number of values should match the number of regions
        # (or regions * vervars if vervars exist)
        records: List[Dict[str, Any]] = []

        for row in datacontent:
            if not row:
                continue

            year = row[0]
            values = row[1:]

            # If there are vertical variables, each value corresponds
            # to a combination of region and vervar
            if vervars:
                for idx, value in enumerate(values):
                    region_idx = idx // len(vervars) if vervars else idx
                    vervar_idx = idx % len(vervars) if vervars else 0

                    region_id = None
                    if self.region_codes and region_idx < len(self.region_codes):
                        region_id = self.region_codes[region_idx]

                    records.append(
                        {
                            "variable_id": variables[0].get("variable_id")
                            if variables
                            else None,
                            "vervar_id": vervars[vervar_idx].get("vervar_id")
                            if vervars
                            else None,
                            "region_id": region_id,
                            "year": year,
                            "value": value,
                        }
                    )
            else:
                for idx, value in enumerate(values):
                    region_id = None
                    if self.region_codes and idx < len(self.region_codes):
                        region_id = self.region_codes[idx]

                    records.append(
                        {
                            "variable_id": variables[0].get("variable_id")
                            if variables
                            else None,
                            "vervar_id": None,
                            "region_id": region_id,
                            "year": year,
                            "value": value,
                        }
                    )

        df = pd.DataFrame(records)

        if not df.empty:
            # Type conversions
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df["value"] = pd.to_numeric(df["value"], errors="coerce")

        return df

    def transform(self) -> Dict[str, Any]:
        """Run the full transformation and return all components."""
        return {
            "metadata": self.extract_metadata(),
            "variables": self.extract_variables(),
            "vertical_variables": self.extract_vertical_variables(),
            "data": self.to_tabular(),
        }