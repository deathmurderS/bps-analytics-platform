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

        Handles the actual BPS API response structure:
        {
            "status": "OK",
            "data-availability": "available",
            "data": [
                {"page": 1, "pages": 1, "total": 34},  # pagination info
                [
                    {"domain_id": "1100", "domain_name": "Aceh", ...},
                    ...
                ]
            ]
        }

        Also handles:
        - Direct list responses
        - Dict responses with {"data": [...]} structure
        - Legacy format with {"kode": "...", "nama": "..."} items
        """
        # Handle if response is already a list
        if isinstance(response, list):
            data = response
        else:
            # Handle dict response with "data" key
            data = response.get("data", []) if isinstance(response, dict) else []

        # Extract the actual domain list from the response
        # The BPS API returns [pagination_info, [domain_items]]
        domain_items: List[Any] = []
        for item in data:
            if isinstance(item, list):
                # This is the actual list of domain items
                domain_items = item
                break
            elif isinstance(item, dict) and "domain_id" in item:
                # Direct dict item
                domain_items.append(item)
            elif isinstance(item, dict) and "kode" in item:
                # Legacy format
                domain_items.append(item)

        records: List[Dict[str, Any]] = []

        for item in domain_items:
            if isinstance(item, dict):
                # Handle both actual BPS format (domain_id/domain_name)
                # and legacy format (kode/nama)
                region_code = item.get("domain_id") or item.get("kode")
                region_name = item.get("domain_name") or item.get("nama")
                records.append(
                    {
                        "region_code": region_code,
                        "region_name": region_name,
                    }
                )

        return records
