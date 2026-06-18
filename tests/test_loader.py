import json
import tempfile
import unittest
from unittest.mock import MagicMock

from src.ingestion.loader import DataLoader


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        self.conn = MagicMock()
        self.loader = DataLoader(self.conn)

    def test_read_json(self):
        data = [{"id": 1, "name": "Room A"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name

        result = DataLoader._read_json(path)

        self.assertEqual(result, data)

    def test_load_rooms(self):
        rows = [
            {"id": 1, "name": "Room A"},
            {"id": 2, "name": "Room B"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rows, f)
            path = f.name

        cursor = MagicMock()

        self.conn.cursor.return_value.__enter__.return_value = cursor

        count = self.loader.load_rooms(path)

        self.assertEqual(count, 2)

        cursor.executemany.assert_called_once_with(
            "INSERT INTO rooms (id, name) VALUES (%s, %s) " "ON CONFLICT DO NOTHING",
            [
                (1, "Room A"),
                (2, "Room B"),
            ],
        )

    def test_load_students(self):
        rows = [
            {
                "id": 1,
                "name": "John",
                "birthday": "2000-01-01T00:00:00.000",
                "sex": "M",
                "room": 1,
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rows, f)
            path = f.name

        cursor = MagicMock()

        self.conn.cursor.return_value.__enter__.return_value = cursor

        count = self.loader.load_students(path)

        self.assertEqual(count, 1)

        cursor.executemany.assert_called_once_with(
            "INSERT INTO students "
            "(id, name, birthday, sex, room_id) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            [
                (
                    1,
                    "John",
                    "2000-01-01 00:00:00",
                    "M",
                    1,
                )
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
