import unittest
from unittest.mock import Mock

from src.database.schema import SchemaManager


class TestSchemaManager(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.schema = SchemaManager(self.conn)

    def test_apply(self):

        cursor1 = Mock()
        cursor2 = Mock()

        self.conn.cursor.side_effect = [
            Mock(
                __enter__=Mock(return_value=cursor1),
                __exit__=Mock(return_value=None),
            ),
            Mock(
                __enter__=Mock(return_value=cursor2),
                __exit__=Mock(return_value=None),
            ),
        ]

        self.schema.apply()

        self.assertEqual(cursor1.execute.call_count, 2)

        self.assertGreater(cursor2.execute.call_count, 0)

    def test_index_ddl(self):

        ddl = self.schema.index_ddl()

        self.assertEqual(len(ddl), 3)

        self.assertTrue(all(stmt.startswith("CREATE INDEX") for stmt in ddl))
