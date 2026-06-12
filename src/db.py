from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
load_dotenv()

# ---------------------------------------------------------------------------

class DatabaseConfig:

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self.host = host or os.getenv("PG_HOST", "localhost")
        self.port = int(port or os.getenv("PG_PORT", 5435))
        self.user = user or os.getenv("PG_USER", "postgres")
        self.password = password or os.getenv("PG_PASSWORD", "postgres")
        self.dbname = database or os.getenv("PG_DB", "postgres")

# ---------------------------------------------------------------------------

class DatabaseConnection:
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._conn: connection | None = None

    def connect(self) -> None:

        self._conn = psycopg2.connect(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            dbname=self._config.dbname,
        )

        self._conn.autocommit = False

    def close(self) -> None:

        if self._conn and not self._conn.closed:
            self._conn.close()

    @contextmanager
    def cursor(self, dictionary: bool = False) -> Generator:
        """Create cursor with automatic commit/rollback."""

        if self._conn is None:
            raise RuntimeError("Call connect() before using cursor().")

        cursor_factory = RealDictCursor if dictionary else None
        cur = self._conn.cursor(cursor_factory=cursor_factory)

        try:
            yield cur
            self._conn.commit()

        except Exception:
            self._conn.rollback()
            raise

        finally:
            cur.close()

    def create_schema_if_needed(self, database: str) -> None:
        admin_conn = psycopg2.connect(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            dbname="postgres"
        )

        admin_conn.autocommit = True

        try:
            with admin_conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (database,)
                )

                if cur.fetchone() is None:
                    cur.execute(f'CREATE DATABASE "{database}"')

        finally:
            admin_conn.close()

# ---------------------------------------------------------------------------