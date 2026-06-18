from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

load_dotenv()


class DatabaseConfig:
    """
    Stores PostgreSQL connection settings.

    Configuration values can be provided explicitly or loaded
    from environment variables.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        """
        Initialize database configuration.

        Args:
            host: Database host name or IP address.
            port: Database port number.
            user: Database user name.
            password: Database password.
            database: Database name.
        """
        self.host = host or os.getenv("PG_HOST")
        self.port = int(port or os.getenv("PG_PORT", 0))
        self.user = user or os.getenv("PG_USER")
        self.password = password or os.getenv("PG_PASSWORD")
        self.dbname = database or os.getenv("PG_DB")


class DatabaseConnection:
    """
    Manages PostgreSQL database connections and transactions.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Initialize the database connection manager.

        Args:
            config: Database connection configuration.
        """
        self._config = config
        self._conn: connection | None = None

    def connect(self) -> None:
        """
        Establish a connection to the PostgreSQL database.

        Raises:
            psycopg2.Error: If the connection cannot be established.
        """
        self._conn = psycopg2.connect(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            dbname=self._config.dbname,
        )

        self._conn.autocommit = False

    def close(self) -> None:
        """
        Close the database connection if it is open.
        """
        if self._conn and not self._conn.closed:
            self._conn.close()

    @contextmanager
    def cursor(self, dictionary: bool = False) -> Generator:
        """
        Create a database cursor.

        Automatically commits transactions when the operation
        succeeds and rolls back when an exception occurs.

        Args:
            dictionary: If True, return rows as dictionaries.

        Yields:
            PostgreSQL cursor object.

        Raises:
            RuntimeError: If no database connection exists.
        """
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
        """
        Create a database if it does not already exist.

        Connects to the PostgreSQL administrative database and
        checks whether the specified database exists.

        Args:
            database: Name of the database to create.
        """
        admin_conn = psycopg2.connect(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            dbname="postgres",
        )

        admin_conn.autocommit = True

        try:
            with admin_conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))

                if cur.fetchone() is None:
                    cur.execute(f'CREATE DATABASE "{database}"')

        finally:
            admin_conn.close()
