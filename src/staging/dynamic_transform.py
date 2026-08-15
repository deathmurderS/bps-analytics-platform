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

## BPS API v2 Format

The actual BPS API v2 returns `datacontent` as a dict with encoded keys:
{
    "datacontent": {
        "210019243212262": 5.46,
        "130019243211761": 8.12,
        ...
    }
}

The key format is: `{vervar_id}{var_id}{turvar_id}{tahun_id}{turtahun_id}`
- vervar_id (4 digits): region code (e.g., 1100 = ACEH)
- var_id (3 digits): variable ID (e.g., 192)
- turvar_id (3 digits): vertical variable (e.g., 432 = Perkotaan)
- tahun_id (3 digits): year reference (e.g., 117 = 2021)
- turtahun_id (2 digits): period type (e.g., 61 = Semester 1, 63 = Tahunan)

The `tahun` list maps tahun_id to actual year labels.
The `turvar` list maps turvar_id to vertical variable labels.
The `turtahun` list maps turtahun_id to period type labels.
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
        """Extract table metadata from the response.

        Handles both v1 format (infotabel.tabel) and v2 format
        (var list with val/label/unit/subj).
        """
        info = self.response.get("infotabel", {})
        table = info.get("tabel", {})
        if table:
            return {
                "table_id": table.get("id"),
                "table_code": table.get("kode"),
                "table_name": table.get("nama"),
                "subject": table.get("subjek"),
                "unit": table.get("satuan"),
                "frequency": table.get("periode"),
            }

        # v2 format: use var list metadata
        variables = self.response.get("var", [])
        if variables:
            first_var = variables[0]
            return {
                "table_id": first_var.get("val"),
                "table_code": None,
                "table_name": first_var.get("label"),
                "subject": first_var.get("subj"),
                "unit": first_var.get("unit"),
                "frequency": None,
            }

        return {
            "table_id": None,
            "table_code": None,
            "table_name": None,
            "subject": None,
            "unit": None,
            "frequency": None,
        }

    def extract_variables(self) -> List[Dict[str, Any]]:
        """Extract variable definitions.

        Handles both v1 format (variable list with id/label)
        and v2 format (var list with val/label).
        """
        variables = self.response.get("variable", [])
        if not variables:
            variables = self.response.get("var", [])
        return [
            {
                "variable_id": var.get("id") or var.get("val"),
                "variable_name": var.get("label"),
                "variable_description": var.get("description") or var.get("def"),
            }
            for var in variables
        ]

    def extract_vertical_variables(self) -> List[Dict[str, Any]]:
        """Extract vertical variable definitions.

        Handles both v1 format (vervar list with id/label)
        and v2 format (turvar list with val/label).
        """
        vervars = self.response.get("vervar", [])
        if not vervars:
            vervars = self.response.get("turvar", [])
        return [
            {
                "vervar_id": var.get("id") or var.get("val"),
                "vervar_name": var.get("label"),
                "vervar_description": var.get("description"),
                "vervar_unit": var.get("unit"),
            }
            for var in vervars
        ]

    def _build_year_map(self) -> Dict[str, str]:
        """Build a map of tahun_id to actual year label."""
        tahun_list = self.response.get("tahun", [])
        return {str(t.get("val")): t.get("label") for t in tahun_list}

    def _build_turtahun_map(self) -> Dict[str, str]:
        """Build a map of turtahun_id to period type label."""
        turtahun_list = self.response.get("turtahun", [])
        return {str(t.get("val")): t.get("label") for t in turtahun_list}

    def _decode_v2_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Decode a BPS API v2 datacontent key.

        Key format: {vervar_id}{var_id}{turvar_id}{tahun_id}{turtahun_id}
        - vervar_id: 4 digits (region code)
        - var_id: 3 digits (variable ID)
        - turvar_id: 3 digits (vertical variable)
        - tahun_id: 3 digits (year reference)
        - turtahun_id: 2 digits (period type)

        Returns:
            Dict with decoded components, or None if key is malformed.
        """
        if len(key) != 15:
            return None

        return {
            "vervar_id": key[0:4],
            "var_id": key[4:7],
            "turvar_id": key[7:10],
            "tahun_id": key[10:13],
            "turtahun_id": key[13:15],
        }

    def to_tabular(self) -> pd.DataFrame:
        """Convert the datacontent into a long-format DataFrame.

        Handles both:
        - v1 format: datacontent is a list of rows [year, value1, value2, ...]
        - v2 format: datacontent is a dict with encoded keys

        Returns:
            DataFrame with columns:
                variable_id, region_id, year, value
                (plus vervar_id if vertical variables exist)
        """
        datacontent = self.response.get("datacontent", [])
        variables = self.extract_variables()
        vervars = self.extract_vertical_variables()

        # Build lookup maps for v2 format
        year_map = self._build_year_map()
        turtahun_map = self._build_turtahun_map()

        records: List[Dict[str, Any]] = []

        # Handle v2 format: datacontent is a dict with encoded keys
        if isinstance(datacontent, dict):
            for key, value in datacontent.items():
                decoded = self._decode_v2_key(str(key))
                if not decoded:
                    continue

                # Map tahun_id to actual year
                year_label = year_map.get(decoded["tahun_id"], decoded["tahun_id"])
                try:
                    year = int(year_label)
                except (ValueError, TypeError):
                    year = None

                # Map turtahun_id to period type
                period_type = turtahun_map.get(
                    decoded["turtahun_id"], decoded["turtahun_id"]
                )

                records.append(
                    {
                        "variable_id": decoded["var_id"],
                        "vervar_id": decoded["turvar_id"],
                        "region_id": decoded["vervar_id"],
                        "year": year,
                        "value": value,
                        "period_type": period_type,
                    }
                )

        # Handle v1 format: datacontent is a list of rows
        elif isinstance(datacontent, list):
            for row in datacontent:
                if not row or not isinstance(row, (list, tuple)):
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
                                "period_type": None,
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
                                "period_type": None,
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