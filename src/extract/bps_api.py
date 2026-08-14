"""Base BPS WebAPI client for making HTTP requests."""

from typing import Any, Dict, Optional

import requests

from src.config.settings import settings


class BPSAPIError(Exception):
    """Raised when the BPS API returns an error."""


class BPSAPIClient:
    """HTTP client for the BPS WebAPI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or settings.bps_api_key
        self.base_url = base_url or settings.bps_api_base_url
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "BPS API key is required. Set BPS_API_KEY in your .env file."
            )

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform a GET request to the BPS API."""
        url = f"{self.base_url}/{endpoint}"
        request_params = dict(params or {})
        request_params["key"] = self.api_key

        try:
            response = requests.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise BPSAPIError(
                f"HTTP error {response.status_code} for {url}: {response.text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise BPSAPIError(f"Request failed for {url}: {exc}") from exc

        return response.json()

    def get_domain(self, domain_type: str = "prov") -> Dict[str, Any]:
        """Fetch domain data (e.g., provinces, regencies)."""
        return self._get("domain", {"type": domain_type})

    def get_dynamic_data(
        self,
        model: str = "data",
        domain: Optional[str] = None,
        var: Optional[str] = None,
        th: Optional[str] = None,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """Fetch dynamic data from the BPS API.

        Args:
            model: API model (e.g., 'data').
            domain: Domain code (e.g., '1100' for a province).
            var: Variable ID(s), comma-separated.
            th: Period (e.g., '2023' or '2023,2024').
            **extra_params: Additional query parameters (e.g., 'vervar').
        """
        params: Dict[str, Any] = {"model": model}
        if domain:
            params["domain"] = domain
        if var:
            params["var"] = var
        if th:
            params["th"] = th
        params.update(extra_params)
        return self._get("list", params)

    def get_simdasi(
        self,
        table_id: Optional[str] = None,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """Fetch SIMDASI metadata for a table."""
        params: Dict[str, Any] = {}
        if table_id:
            params["id"] = table_id
        params.update(extra_params)
        return self._get("simdasi", params)

    def get_glossary(self, **extra_params: Any) -> Dict[str, Any]:
        """Fetch glossary data."""
        return self._get("glosarium", extra_params)