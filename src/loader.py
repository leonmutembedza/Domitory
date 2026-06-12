from __future__ import annotations

import json
from pathlib import Path

from src.db import DatabaseConnection


class DataLoader:

    def __init__(self, conn: DatabaseConnection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    def load_rooms(self, path: str | Path) -> int:
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

    # ------------------------------------------------------------------
    @staticmethod
    def _read_json(path: str | Path) -> list[dict]:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
