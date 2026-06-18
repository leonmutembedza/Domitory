import unittest
from decimal import Decimal
from unittest.mock import MagicMock, Mock

from src.repository.queries import QueryRepository


class TestQueryRepository(unittest.TestCase):

    def setUp(self):
        self.conn = MagicMock()
        self.repo = QueryRepository(self.conn)

    def test_run_query(self):

        cursor = MagicMock()

        cursor.fetchall.return_value = [{"room_id": 1, "avg_age": Decimal("22.3")}]

        self.conn.cursor.return_value.__enter__.return_value = cursor

        result = self.repo._run("SELECT 1")

        cursor.execute.assert_called_once_with("SELECT 1")

        self.assertEqual(result, [{"room_id": 1, "avg_age": 22.3}])

    def test_coerce_decimal(self):

        row = {"room_id": 1, "avg_age": Decimal("22.3")}

        result = QueryRepository._coerce(row)

        self.assertEqual(result, {"room_id": 1, "avg_age": 22.3})

    def test_rooms_with_student_count(self):

        self.repo._run = Mock(return_value=["ok"])

        result = self.repo.rooms_with_student_count()

        self.repo._run.assert_called_once()

        self.assertEqual(result, ["ok"])

    def test_five_rooms_youngest_avg_age(self):

        self.repo._run = Mock(return_value=["ok"])

        result = self.repo.five_rooms_youngest_avg_age()

        self.repo._run.assert_called_once()

        self.assertEqual(result, ["ok"])

    def test_five_rooms_largest_age_diff(self):

        self.repo._run = Mock(return_value=["ok"])

        result = self.repo.five_rooms_largest_age_diff()

        self.repo._run.assert_called_once()

        self.assertEqual(result, ["ok"])

    def test_mixed_sex_rooms(self):

        self.repo._run = Mock(return_value=["ok"])

        result = self.repo.mixed_sex_rooms()

        self.repo._run.assert_called_once()

        self.assertEqual(result, ["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
