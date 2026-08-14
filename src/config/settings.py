"""Application configuration settings loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Centralized configuration for the BPS Data Warehouse project."""

    def __init__(self) -> None:
        # BPS API
        self.bps_api_key: str = os.getenv("BPS_API_KEY", "")
        self.bps_api_base_url: str = os.getenv(
            "BPS_API_BASE_URL", "https://webapi.bps.go.id/v1/api"
        )

        # PostgreSQL
        self.postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db: str = os.getenv("POSTGRES_DB", "bps_dw")
        self.postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
        self.postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")

        # Raw data storage
        self.raw_data_dir: Path = Path(
            os.getenv("RAW_DATA_DIR", str(PROJECT_ROOT / "data" / "raw"))
        )

    @property
    def postgres_url(self) -> str:
        """Build SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def validate(self) -> None:
        """Validate that required settings are present."""
        if not self.bps_api_key:
            raise ValueError(
                "BPS_API_KEY is not set. "
                "Please copy .env.example to .env and set your API key."
            )


# Singleton instance
settings = Settings()