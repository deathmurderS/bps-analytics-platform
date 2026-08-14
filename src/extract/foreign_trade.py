"""Foreign Trade data extractor for BPS WebAPI.

The BPS Foreign Trade API provides export/import data including
commodities, countries, ports, values, and weights.

> ⚠️ **IMPORTANT**: The endpoint `"exim"` used in `fetch_trade()` must be
> validated against the actual BPS WebAPI documentation at:
> https://webapi.bps.go.id/documentation/
>
> This module provides the client infrastructure and parser structure.
> The endpoint name and parameter format must be confirmed with the
> official BPS API documentation before running against production data.
>
> Field names in `parse_trade_records()` follow the documented BPS trade
> response structure (kode_barang, nama_barang, kode_negara, etc.).
>
> ⚠️ Until the real endpoint is confirmed, this module works with the
> test fixture at `tests/fixtures/bps_trade_response.json`.
"""

from typing import Any, Dict, List

from src.extract.bps_api import BPSAPIClient


class ForeignTradeExtractor:
    """Extract foreign trade data from the BPS API."""

    def __init__(self, client: BPSAPIClient) -> None:
        self.client = client

    def fetch_trade(
        self,
        trade_type: str = "ekspor",
        period: str = "",
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """Fetch foreign trade data.

        Args:
            trade_type: Type of trade ('eks' for export, 'imp' for import).
            period: Period(s), e.g., '2023' or '2023,2024'.
            **extra_params: Additional parameters (commodity, country, port).
        """
        params: Dict[str, Any] = {"type": trade_type}
        if period:
            params["periode"] = period
        params.update(extra_params)
        return self.client._get("exim", params)

    def parse_trade_records(
        self,
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Parse foreign trade response into records.

        Response structure follows BPS trade data:
        Each record contains commodity, country, port, value, and weight.

        Note: The exact response keys depend on the actual BPS API.
        This parses based on documented structure.
        """
        data = response.get("data", [])
        records: List[Dict[str, Any]] = []

        for item in data:
            records.append(
                {
                    "trade_type": item.get("jenis"),
                    "commodity_code": item.get("kode_barang"),
                    "commodity_name": item.get("nama_barang"),
                    "country_code": item.get("kode_negara"),
                    "country_name": item.get("nama_negara"),
                    "port_code": item.get("kode_pelabuhan"),
                    "port_name": item.get("nama_pelabuhan"),
                    "period": item.get("periode"),
                    "value_usd": item.get("nilai"),
                    "net_weight_kg": item.get("berat_bersih"),
                }
            )
        return records