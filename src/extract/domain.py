"""Domain data extractor for BPS WebAPI."""

from typing import Any, Dict, List, Union

from src.extract.bps_api import BPSAPIClient


class DomainExtractor:
    """Extract domain data (provinces, regencies, etc.) from BPS API."""

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch_provinces(self) -> Union[Dict[str, Any], List[Any]]:
        """Fetch list of provinces."""
        return self.client.get_domain("prov")

    def fetch_regencies(self) -> Union[Dict[str, Any], List[Any]]:
        """Fetch list of regencies/cities."""
        return self.client.get_domain("kab")

    def fetch_districts(self) -> Union[Dict[str, Any], List[Any]]:
        """Fetch list of districts."""
        return self.client.get_domain("kec")

    def fetch_villages(self) -> Union[Dict[str, Any], List[Any]]:
        """Fetch list of villages."""
        return self.client.get_domain("desa")

    def parse_domain_list(
        self,
        response: Union[Dict[str, Any], List[Any]],
    ) -> List[Dict[str, Any]]:
        """Parse domain response into a list of region records.

        Handles both dict responses with {"data": [...]} structure
        and direct list responses.

        The BPS domain response typically has the structure:
        {
            "status": "200",
            "data-availability": "available",
            "data": [
                {"kode": "1100", "nama": "ACEH"},
                ...
            ]
        }
        """
        # Handle if response is already a list
        if isinstance(response, list):
            data = response
        else:
            # Handle dict response with "data" key
            data = response.get("data", []) if isinstance(response, dict) else []

        records: List[Dict[str, Any]] = []

        for item in data:
            if isinstance(item, dict):
                records.append(
                    {
                        "region_code": item.get("kode"),
                        "region_name": item.get("nama"),
                    }
                )

        return records
