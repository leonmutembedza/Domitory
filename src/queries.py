from __future__ import annotations

from src.db import DatabaseConnection

# ---------------------------------------------------------------------------

_SQL_ROOMS_STUDENT_COUNT = """
SELECT
    r.id                    AS room_id,
    r.name                  AS room_name,
    COUNT(s.id)             AS student_count
FROM rooms r
LEFT JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY r.id;
"""

# ---------------------------------------------------------------------------

_SQL_5_YOUNGEST_ROOMS = """
SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM AGE(CURRENT_TIMESTAMP, s.birthday))
            / (365.25 * 24 * 60 * 60)
        )::numeric,
        2
    ) AS avg_age_years
FROM rooms r
JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY avg_age_years ASC
LIMIT 5;
"""

# ---------------------------------------------------------------------------

_SQL_5_BIGGEST_AGE_DIFF = """
SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(
        (
            EXTRACT(EPOCH FROM (MAX(s.birthday) - MIN(s.birthday)))
            / (365.25 * 24 * 60 * 60)
        )::numeric,
        2
    ) AS age_diff_years
FROM rooms r
JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY age_diff_years DESC
LIMIT 5;
"""

# ---------------------------------------------------------------------------

_SQL_MIXED_SEX_ROOMS = """
SELECT
    r.id AS room_id,
    r.name AS room_name,
    COUNT(DISTINCT s.sex) AS sex_count
FROM rooms r
JOIN students s ON s.room_id = r.id
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) > 1
ORDER BY r.id;
"""

# ---------------------------------------------------------------------------

class QueryRepository:
    """Executes analytical queries and returns plain dictionaries."""

    def __init__(self, conn: DatabaseConnection) -> None:
        self._conn = conn

    def rooms_with_student_count(self) -> list[dict]:
        return self._run(_SQL_ROOMS_STUDENT_COUNT)

    def five_rooms_youngest_avg_age(self) -> list[dict]:
        return self._run(_SQL_5_YOUNGEST_ROOMS)

    def five_rooms_largest_age_diff(self) -> list[dict]:
        return self._run(_SQL_5_BIGGEST_AGE_DIFF)

    def mixed_sex_rooms(self) -> list[dict]:
        return self._run(_SQL_MIXED_SEX_ROOMS)

    # ------------------------------------------------------------------
    def _run(self, sql: str) -> list[dict]:
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._coerce(row) for row in rows]

    @staticmethod
    def _coerce(row: dict) -> dict:
        from decimal import Decimal

        return {
            key: float(value) if isinstance(value, Decimal) else value
            for key, value in row.items()
        }

# ---------------------------------------------------------------------------