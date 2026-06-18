from __future__ import annotations

from src.database.db import DatabaseConnection

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


class QueryRepository:
    """
    Executes analytical SQL queries against the dormitory database.

    Query results are returned as plain Python dictionaries.
    """

    def __init__(self, conn: DatabaseConnection) -> None:
        """
        Initialize the repository.

        Args:
            conn: Active database connection manager.
        """
        self._conn = conn

    def rooms_with_student_count(self) -> list[dict]:
        """
        Retrieve all rooms and the number of students assigned to each.

        Returns:
            List of dictionaries containing room information and
            student counts.
        """
        return self._run(_SQL_ROOMS_STUDENT_COUNT)

    def five_rooms_youngest_avg_age(self) -> list[dict]:
        """
        Retrieve the five rooms with the lowest average student age.

        Returns:
            List of dictionaries containing room information and
            average ages.
        """
        return self._run(_SQL_5_YOUNGEST_ROOMS)

    def five_rooms_largest_age_diff(self) -> list[dict]:
        """
        Retrieve the five rooms with the largest age difference
        between their youngest and oldest residents.

        Returns:
            List of dictionaries containing room information and
            age differences.
        """
        return self._run(_SQL_5_BIGGEST_AGE_DIFF)

    def mixed_sex_rooms(self) -> list[dict]:
        """
        Retrieve rooms occupied by students of more than one sex.

        Returns:
            List of dictionaries describing mixed-sex rooms.
        """
        return self._run(_SQL_MIXED_SEX_ROOMS)

    def _run(self, sql: str) -> list[dict]:
        """
        Execute a query and return the result set.

        Args:
            sql: SQL statement to execute.

        Returns:
            Query results converted to standard Python types.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._coerce(row) for row in rows]

    @staticmethod
    def _coerce(row: dict) -> dict:
        """
        Convert database-specific numeric types into standard
        Python types suitable for serialization.

        Args:
            row: Database result row.

        Returns:
            Dictionary with converted values.
        """
        from decimal import Decimal

        return {
            key: float(value) if isinstance(value, Decimal) else value
            for key, value in row.items()
        }
