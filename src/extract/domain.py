"""Domain data extractor for BPS WebAPI."""

from typing import Any, Dict, List

from src.extract.bps_api import BPSAPIClient


class DomainExtractor:
    """Extract domain data (provinces, regencies, etc.) from BPS API."""

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch_provinces(self) -> Dict[str, Any]:
        """Fetch list of provinces."""
        return self.client.get_domain("prov")

    def fetch_regencies(self) -> Dict[str, Any]:
        """Fetch list of regencies/cities."""
        return self.client.get_domain("kab")

    def fetch_districts(self) -> Dict[str, Any]:
        """Fetch list of districts."""
        return self.client.get_domain("kec")

    def fetch_villages(self) -> Dict[str, Any]:
        """Fetch list of villages."""
        return self.client.get_domain("desa")

    def parse_domain_list(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse domain response into a list of region records.

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
        data = response.get("data", [])
        records: List[Dict[str, Any]] = []

        for item in data:
            records.append(
                {
                    "region_code": item.get("kode"),
                    "region_name": item.get("nama"),
                }
            )

        return records