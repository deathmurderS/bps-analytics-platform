"""Glossary extractor for BPS WebAPI."""

from typing import Any, Dict, List

from src.extract.bps_api import BPSAPIClient


class GlossaryExtractor:
    """Extract glossary/glosarium data from BPS API.

    Glosarium provides definitions, concepts, classifications, units,
    and data sources for indicators.
    """

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch(self, **extra_params: Any) -> Dict[str, Any]:
        """Fetch glossary data with optional filtering parameters."""
        return self.client.get_glossary(**extra_params)

    @staticmethod
    def parse_glossary(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse glossary response into a list of glossary records."""
        data = response.get("data", [])
        records: List[Dict[str, Any]] = []

        for item in data:
            records.append(
                {
                    "glossary_id": item.get("id"),
                    "indicator_name": item.get("nama_indikator"),
                    "concept": item.get("konsep"),
                    "definition": item.get("definisi"),
                    "classification": item.get("klasifikasi"),
                    "measure": item.get("ukuran"),
                    "unit": item.get("satuan"),
                    "data_source": item.get("sumber_data"),
                }
            )
        return records