"""Raw layer storage for original API responses."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from src.config.settings import settings


class RawStorage:
    """Store original API responses as JSON files.

    Raw layer serves as the source of truth for reprocessing. Files are
    organized by date to preserve the retrieval timeline.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.raw_data_dir

    def _build_path(
        self,
        source: str,
        dataset: str,
        timestamp: datetime | None = None,
    ) -> Path:
        """Construct the storage path for a raw response.

        Layout: {base}/bps/{source}/{dataset}/{YYYY}/{MM}/{DD}/response.json
        """
        ts = timestamp or datetime.now()
        path = (
            self.base_dir
            / "bps"
            / source
            / dataset
            / str(ts.year)
            / f"{ts.month:02d}"
            / f"{ts.day:02d}"
        )
        return path

    def save(
        self,
        data: Dict[str, Any],
        source: str,
        dataset: str,
        timestamp: datetime | None = None,
    ) -> Path:
        """Save a raw API response to disk as JSON.

        Args:
            data: The API response (dict) to save.
            source: Source name (e.g., 'dynamic_data', 'domain').
            dataset: Dataset identifier (e.g., 'pdrb' or a variable code).
            timestamp: Optional timestamp; defaults to now.

        Returns:
            The path where the file was saved.
        """
        path = self._build_path(source, dataset, timestamp)
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / "response.json"

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return file_path

    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load a raw API response from disk."""
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def list_files(self, source: str | None = None) -> list[Path]:
        """List all raw response files, optionally filtered by source."""
        search_root = self.base_dir / "bps"
        if source:
            search_root = search_root / source

        if not search_root.exists():
            return []

        return sorted(search_root.rglob("response.json"))