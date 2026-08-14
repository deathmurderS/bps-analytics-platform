"""PostgreSQL loader for warehouse tables."""

from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config.settings import settings


class PostgresLoader:
    """Load DataFrames into the PostgreSQL warehouse."""

    def __init__(self, connection_url: Optional[str] = None) -> None:
        self.connection_url = connection_url or settings.postgres_url
        self.engine: Engine = create_engine(self.connection_url)

    def connect(self) -> Engine:
        """Return the SQLAlchemy engine."""
        return self.engine

    def execute_sql(self, sql: str) -> None:
        """Execute raw SQL statement."""
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def load_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str,
        if_exists: str = "append",
        index: bool = False,
    ) -> None:
        """Load a DataFrame into a PostgreSQL table.

        Args:
            df: DataFrame to load.
            table_name: Target table name.
            schema: Target schema (e.g., 'warehouse').
            if_exists: 'append', 'replace', or 'fail'.
            index: Whether to write the index as a column.
        """
        # Create schema if it doesn't exist
        self.execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        df.to_sql(
            name=table_name,
            con=self.engine,
            schema=schema,
            if_exists=if_exists,
            index=index,
        )

    def upsert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str,
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> int:
        """Upsert a DataFrame into a PostgreSQL table using INSERT ... ON CONFLICT.

        This makes the pipeline idempotent: running the same data twice
        will not create duplicates or fail on unique constraints.

        Args:
            df: DataFrame to upsert.
            table_name: Target table name.
            schema: Target schema (e.g., 'warehouse').
            conflict_columns: Columns that define the unique constraint
                (e.g., ['date_key', 'region_key', 'indicator_key']).
            update_columns: Columns to update on conflict. If None,
                defaults to all non-conflict columns in the DataFrame.

        Returns:
            Number of rows upserted.
        """
        if df.empty:
            return 0

        # Create schema if it doesn't exist
        self.execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        # Ensure table exists
        df.head(0).to_sql(
            name=table_name,
            con=self.engine,
            schema=schema,
            if_exists="append",
            index=False,
        )

        # Determine columns to update on conflict
        if update_columns is None:
            update_columns = [
                col for col in df.columns if col not in conflict_columns
            ]

        if not update_columns:
            # No columns to update - use DO NOTHING
            conflict_action = "DO NOTHING"
        else:
            update_set = ", ".join(
                f'"{col}" = EXCLUDED."{col}"' for col in update_columns
            )
            conflict_action = f"DO UPDATE SET {update_set}"

        conflict_target = ", ".join(f'"{col}"' for col in conflict_columns)

        # Build the INSERT statement
        columns = ", ".join(f'"{col}"' for col in df.columns)
        placeholders = ", ".join(f":{col}" for col in df.columns)

        sql = f"""
            INSERT INTO {schema}.{table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_target}) {conflict_action}
        """

        # Convert DataFrame to records
        records = df.to_dict(orient="records")

        with self.engine.begin() as conn:
            for record in records:
                # Convert numpy types to native Python types
                clean_record = {
                    k: (None if pd.isna(v) else v.item() if hasattr(v, "item") else v)
                    for k, v in record.items()
                }
                conn.execute(text(sql), clean_record)

        return len(records)

    def create_schemas(self, schemas: List[str]) -> None:
        """Ensure that required schemas exist."""
        for schema in schemas:
            self.execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    def truncate_table(self, table_name: str, schema: str = "warehouse") -> None:
        """Truncate a table before re-loading."""
        with self.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {schema}.{table_name} RESTART IDENTITY CASCADE"))

    def verify_row_count(
        self,
        table_name: str,
        schema: str = "warehouse",
    ) -> int:
        """Return the number of rows in a table."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {schema}.{table_name}")
            )
            return result.scalar_one()

    def load_mart(self, sql_or_view: str, mart_name: str) -> None:
        """Create a materialized view in the mart schema."""
        self.execute_sql(f"CREATE SCHEMA IF NOT EXISTS mart")
        self.execute_sql(f"DROP MATERIALIZED VIEW IF EXISTS mart.{mart_name} CASCADE")
        self.execute_sql(
            f"CREATE MATERIALIZED VIEW mart.{mart_name} AS {sql_or_view}"
        )

    def close(self) -> None:
        """Dispose of the engine."""
        self.engine.dispose()