"""SIMDASI metadata extractor for BPS WebAPI."""

from typing import Any, Dict

from src.extract.bps_api import BPSAPIClient


class SIMDASIExtractor:
    """Extract SIMDASI metadata (table definitions, MFD regions) from BPS API."""

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch_table(self, table_id: str) -> Dict[str, Any]:
        """Fetch SIMDASI metadata for a specific table."""
        return self.client.get_simdasi(table_id=table_id)

    def fetch_all(self) -> Dict[str, Any]:
        """Fetch all SIMDASI tables."""
        return self.client.get_simdasi()

    @staticmethod
    def parse_table_metadata(response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key table metadata from a SIMDASI response."""
        data = response.get("data", [])
        if not data:
            return {}

        first = data[0]
        return {
            "table_id": first.get("id"),
            "table_code": first.get("kode"),
            "title": first.get("judul"),
            "subject": first.get("subjek"),
            "unit": first.get("satuan"),
            "frequency": first.get("periode"),
        }