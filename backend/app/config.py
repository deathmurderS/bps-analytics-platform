"""Backend configuration from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Project root .env (BPS/.env) — backend is started from backend/ so cwd .env is often missing
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILES = (
    Path(__file__).resolve().parents[1] / ".env",
    _PROJECT_ROOT / ".env",
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://localhost:5432/bps_dw"
    cors_origins: str = "http://localhost:3000"

    model_config = {
        "env_file": _ENV_FILES,
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()