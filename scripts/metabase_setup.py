"""Metabase automated dashboard setup.

This script configures Metabase programmatically via its API:
1. Creates/connects to the PostgreSQL database
2. Creates dashboard cards using the SQL queries from sql/dashboard/
3. Creates the main analytical dashboard

Usage:
    python scripts/metabase_setup.py [--metabase-url URL] [--email EMAIL] [--password PASS]
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

METABASE_URL = "http://localhost:3000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "adminpassword"
DASHBOARD_NAME = "BPS Economic Intelligence"

DASHBOARD_SQL_DIR = Path(__file__).resolve().parent.parent / "sql" / "dashboard"


class MetabaseSetup:
    """Automate Metabase dashboard configuration."""

    def __init__(
        self,
        base_url: str = METABASE_URL,
        email: str = ADMIN_EMAIL,
        password: str = ADMIN_PASSWORD,
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "bps_dw",
        db_user: str = "postgres",
        db_password: str = "postgres",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.db_config = {
            "host": db_host,
            "port": db_port,
            "dbname": db_name,
            "user": db_user,
            "password": db_password,
        }
        self.session_token: Optional[str] = None

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request to the Metabase API."""
        url = f"{self.base_url}/api{path}"
        headers = {}
        if self.session_token:
            headers["X-Metabase-Session"] = self.session_token
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str) -> Dict[str, Any]:
        """Send a GET request to the Metabase API."""
        url = f"{self.base_url}/api{path}"
        headers = {"X-Metabase-Session": self.session_token} if self.session_token else {}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def wait_for_ready(self, max_retries: int = 60) -> None:
        """Wait for Metabase to be ready."""
        logger.info(f"Waiting for Metabase at {self.base_url}...")
        for attempt in range(max_retries):
            try:
                resp = requests.get(f"{self.base_url}/api/health", timeout=5)
                if resp.status_code == 200 and resp.json().get("status") == "ok":
                    logger.info("  Metabase is ready.")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        raise TimeoutError("Metabase did not become ready in time")

    def setup(self) -> None:
        """Run the full Metabase setup."""
        self.wait_for_ready()

        # Step 1: Setup admin user (first-time setup)
        self._setup_admin()

        # Step 2: Find or create PostgreSQL database
        db_id = self._get_or_create_database()

        # Step 3: Create dashboard cards from SQL files
        card_ids = self._create_cards_from_sql(db_id)

        # Step 4: Create the dashboard with cards
        dashboard_id = self._create_dashboard(card_ids)

        logger.info(f"\n✅ Dashboard created: {DASHBOARD_NAME}")
        logger.info(f"   URL: {self.base_url}/dashboard/{dashboard_id}")

    def _setup_admin(self) -> None:
        """Set up the admin user (first-time setup)."""
        # Check if setup has already been done
        try:
            setup_token_resp = requests.get(
                f"{self.base_url}/api/session/properties", timeout=10
            )
            token_data = setup_token_resp.json()
            setup_token = token_data.get("setup-token")

            if setup_token and setup_token != "none":
                logger.info("Setting up admin user...")
                self._post(
                    "/setup",
                    {
                        "token": setup_token,
                        "user": {
                            "first_name": "Admin",
                            "last_name": "User",
                            "email": self.email,
                            "password": self.password,
                            "site_name": "BPS Data Warehouse",
                        },
                        "database": None,
                        "invites": [],
                    },
                )
                logger.info("  Admin user created.")
        except Exception as exc:
            logger.warning(f"  Setup check failed: {exc}")

        # Login
        logger.info("Logging in...")
        session = self._post(
            "/session",
            {"username": self.email, "password": self.password},
        )
        self.session_token = session.get("id")
        if not self.session_token:
            raise RuntimeError("Failed to get session token")
        logger.info("  Logged in successfully.")

    def _get_or_create_database(self) -> int:
        """Get existing PostgreSQL database or create one."""
        logger.info("Configuring database connection...")
        databases = self._get("/database")
        for db in databases.get("data", []):
            if db.get("name") == "bps_dw":
                logger.info(f"  Database found: ID={db['id']}")
                return db["id"]

        db = self._post(
            "/database",
            {
                "name": "bps_dw",
                "engine": "postgres",
                "details": self.db_config,
            },
        )
        logger.info(f"  Database created: ID={db['id']}")
        return db["id"]

    def _create_cards_from_sql(self, db_id: int) -> List[int]:
        """Create dashboard cards from the SQL files."""
        logger.info("Creating dashboard cards...")
        card_ids: List[int] = []

        sql_files = sorted(DASHBOARD_SQL_DIR.glob("*.sql"))

        for sql_file in sql_files:
            name = sql_file.stem.replace("_", " ").title()
            sql = sql_file.read_text()

            # Only create the first query from each file
            first_query = sql.split(";")[0].strip()

            try:
                card = self._post(
                    "/card",
                    {
                        "name": name,
                        "display": self._get_display_type(sql_file.name),
                        "dataset_query": {
                            "database": db_id,
                            "type": "native",
                            "native": {
                                "query": first_query,
                                "template-tags": {},
                            },
                        },
                        "visualization_settings": {},
                    },
                )
                card_ids.append(card["id"])
                logger.info(f"  Card created: {name} (ID={card['id']})")
            except Exception as exc:
                logger.warning(f"  Could not create card {name}: {exc}")

        return card_ids

    def _get_display_type(self, filename: str) -> str:
        """Determine Metabase display type from filename."""
        if "trend" in filename:
            return "line"
        if "regional" in filename:
            return "table"
        if "kpi" in filename or "overview" in filename:
            return "scalar"
        if "metadata" in filename:
            return "table"
        return "table"

    def _create_dashboard(self, card_ids: List[int]) -> int:
        """Create the dashboard and add cards to it."""
        logger.info("Creating dashboard...")
        dashboard = self._post(
            "/dashboard",
            {
                "name": DASHBOARD_NAME,
                "description": "BPS Statistical & Economic Intelligence Dashboard",
            },
        )
        dashboard_id = dashboard["id"]
        logger.info(f"  Dashboard created: ID={dashboard_id}")

        # Add cards to dashboard in a grid layout
        for idx, card_id in enumerate(card_ids):
            col = 0 if idx % 2 == 0 else 8
            row = idx // 2 * 4
            try:
                self._post(
                    f"/dashboard/{dashboard_id}/cards",
                    {
                        "cardId": card_id,
                        "col": col,
                        "row": row,
                        "sizeX": 8,
                        "sizeY": 4,
                    },
                )
            except Exception as exc:
                logger.warning(f"  Could not add card {card_id}: {exc}")

        return dashboard_id


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Metabase automated dashboard setup")
    parser.add_argument("--metabase-url", default=METABASE_URL)
    parser.add_argument("--email", default=ADMIN_EMAIL)
    parser.add_argument("--password", default=ADMIN_PASSWORD)
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", type=int, default=5432)
    parser.add_argument("--db-name", default="bps_dw")
    parser.add_argument("--db-user", default="postgres")
    parser.add_argument("--db-password", default="postgres")
    args = parser.parse_args()

    setup = MetabaseSetup(
        base_url=args.metabase_url,
        email=args.email,
        password=args.password,
        db_host=args.db_host,
        db_port=args.db_port,
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password,
    )
    setup.setup()


if __name__ == "__main__":
    main()