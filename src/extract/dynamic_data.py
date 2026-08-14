"""Dynamic Data extractor for BPS WebAPI."""

from typing import Any, Dict, List

from src.extract.bps_api import BPSAPIClient


class DynamicDataExtractor:
    """Extract dynamic data from BPS API.

    Dynamic data responses contain variables, vertical variables,
    metadata, and data content.
    """

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch(
        self,
        domain: str,
        var: str,
        periods: str,
        vervar: str = "",
        model: str = "data",
    ) -> Dict[str, Any]:
        """Fetch dynamic data for a given domain, variable, and period.

        Args:
            domain: Domain code (e.g., '1100' for Aceh province).
            var: Variable ID(s) comma-separated.
            periods: Period(s) e.g., '2023' or '2023,2024'.
            vervar: Vertical variable ID (optional).
            model: API model (default 'data').
        """
        extra_params: Dict[str, Any] = {}
        if vervar:
            extra_params["vervar"] = vervar

        return self.client.get_dynamic_data(
            model=model,
            domain=domain,
            var=var,
            th=periods,
            **extra_params,
        )

    @staticmethod
    def parse_variables(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the variable definitions from a dynamic data response."""
        variables = response.get("variable", [])
        records: List[Dict[str, Any]] = []

        for var in variables:
            records.append(
                {
                    "variable_id": var.get("id"),
                    "variable_name": var.get("label"),
                    "variable_description": var.get("description"),
                }
            )
        return records

    @staticmethod
    def parse_vertical_variables(
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Parse vertical variable definitions from a dynamic data response."""
        vervars = response.get("vervar", [])
        records: List[Dict[str, Any]] = []

        for var in vervars:
            records.append(
                {
                    "vervar_id": var.get("id"),
                    "vervar_name": var.get("label"),
                    "vervar_description": var.get("description"),
                    "vervar_unit": var.get("unit"),
                }
            )
        return records

    @staticmethod
    def parse_datacontent(
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Parse the data content into tabular records.

        The data content is typically a list of lists where the first
        element is the year and the remaining elements are the values
        for each region.
        """
        datacontent = response.get("datacontent", [])
        regions = response.get("infotabel", {}).get("tabel", {}).get("nama", "")
        records: List[Dict[str, Any]] = []

        for row in datacontent:
            if not row:
                continue
            year = row[0]
            values = row[1:]
            records.append(
                {
                    "year": year,
                    "values": values,
                    "region_names": regions,
                }
            )
        return records