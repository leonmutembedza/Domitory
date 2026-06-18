from __future__ import annotations

import json
from pathlib import Path

from src.database.db import DatabaseConnection

# Data loading utilities for importing room and student records.


class DataLoader:
    """
    Loads room and student data from JSON files into the database.
    """

    def __init__(self, conn: DatabaseConnection) -> None:
        """
        Initialize the data loader.

        Args:
            conn: Active database connection manager.
        """
        self._conn = conn

    def load_rooms(self, path: str | Path) -> int:
        """
        Load room records from a JSON file.

        Args:
            path: Path to the rooms JSON file.

        Returns:
            Number of room records processed.
        """
        rows = self._read_json(path)
        records = [(r["id"], r["name"]) for r in rows]

        with self._conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO rooms (id, name) VALUES (%s, %s) "
                "ON CONFLICT DO NOTHING",
                records,
            )

        return len(records)

    def load_students(self, path: str | Path) -> int:
        """
        Load student records from a JSON file.

        Args:
            path: Path to the students JSON file.

        Returns:
            Number of student records processed.
        """
        rows = self._read_json(path)

        records = [
            (
                s["id"],
                s["name"],
                s["birthday"].replace("T", " ").split(".")[0],
                s["sex"],
                s["room"],
            )
            for s in rows
        ]

        with self._conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO students "
                "(id, name, birthday, sex, room_id) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT DO NOTHING",
                records,
            )

        return len(records)

    @staticmethod
    def _read_json(path: str | Path) -> list[dict]:
        """
        Read and parse a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            List of dictionaries loaded from the file.
        """
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
