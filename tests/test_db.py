import unittest
from unittest.mock import Mock, patch

from src.database.db import DatabaseConfig, DatabaseConnection


class TestDatabaseConfig(unittest.TestCase):

    @patch.dict(
        "os.environ",
        {
            "PG_HOST": "localhost",
            "PG_PORT": "5432",
            "PG_USER": "postgres",
            "PG_PASSWORD": "secret",
            "PG_DB": "students",
        },
    )
    def test_reads_environment_variables(self):
        config = DatabaseConfig()

        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.user, "postgres")
        self.assertEqual(config.password, "secret")
        self.assertEqual(config.dbname, "students")

    def test_explicit_arguments_override_environment(self):
        config = DatabaseConfig(
            host="dbserver", port=9999, user="admin", password="pw", database="testdb"
        )

        self.assertEqual(config.host, "dbserver")
        self.assertEqual(config.port, 9999)
        self.assertEqual(config.user, "admin")
        self.assertEqual(config.password, "pw")
        self.assertEqual(config.dbname, "testdb")


class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        self.config = DatabaseConfig(
            host="localhost",
            port=5432,
            user="postgres",
            password="secret",
            database="students",
        )

    @patch("src.database.db.psycopg2.connect")
    def test_connect_establishes_connection(self, mock_connect):
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        db = DatabaseConnection(self.config)

        db.connect()

        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            user="postgres",
            password="secret",
            dbname="students",
        )

        self.assertEqual(db._conn, mock_conn)
        self.assertFalse(mock_conn.autocommit)

    def test_close_does_nothing_when_connection_is_none(self):
        db = DatabaseConnection(self.config)

        db.close()

    def test_close_closes_open_connection(self):
        db = DatabaseConnection(self.config)

        mock_conn = Mock()
        mock_conn.closed = False

        db._conn = mock_conn

        db.close()

        mock_conn.close.assert_called_once()

    def test_close_does_not_close_already_closed_connection(self):
        db = DatabaseConnection(self.config)

        mock_conn = Mock()
        mock_conn.closed = True

        db._conn = mock_conn

        db.close()

        mock_conn.close.assert_not_called()

    def test_cursor_raises_runtime_error_without_connection(self):
        db = DatabaseConnection(self.config)

        with self.assertRaises(RuntimeError):
            with db.cursor():
                pass

    def test_cursor_commits_on_success(self):
        db = DatabaseConnection(self.config)

        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        db._conn = mock_conn

        with db.cursor() as cur:
            cur.execute("SELECT 1")

        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_cursor.close.assert_called_once()

    def test_cursor_rolls_back_on_exception(self):
        db = DatabaseConnection(self.config)

        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        db._conn = mock_conn

        with self.assertRaises(ValueError):
            with db.cursor():
                raise ValueError("boom")

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_cursor.close.assert_called_once()

    def test_cursor_dictionary_mode_uses_real_dict_cursor(self):
        db = DatabaseConnection(self.config)

        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        db._conn = mock_conn

        with patch("src.database.db.RealDictCursor") as mock_real_dict:
            with db.cursor(dictionary=True):
                pass

            mock_conn.cursor.assert_called_once_with(cursor_factory=mock_real_dict)

    @patch("src.database.db.psycopg2.connect")
    def test_create_schema_if_needed_database_exists(self, mock_connect):
        admin_conn = Mock()

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)

        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_cursor)
        mock_context.__exit__ = Mock(return_value=None)

        admin_conn.cursor.return_value = mock_context

        mock_connect.return_value = admin_conn

        db = DatabaseConnection(self.config)

        db.create_schema_if_needed("students")

        self.assertEqual(mock_cursor.execute.call_count, 1)

        mock_cursor.execute.assert_called_with(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("students",)
        )

        admin_conn.close.assert_called_once()

    @patch("src.database.db.psycopg2.connect")
    def test_create_schema_if_needed_creates_missing_database(self, mock_connect):
        admin_conn = Mock()

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None

        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_cursor)
        mock_context.__exit__ = Mock(return_value=None)

        admin_conn.cursor.return_value = mock_context

        mock_connect.return_value = admin_conn

        db = DatabaseConnection(self.config)

        db.create_schema_if_needed("new_database")

        self.assertEqual(mock_cursor.execute.call_count, 2)

        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("new_database",)
        )

        mock_cursor.execute.assert_any_call('CREATE DATABASE "new_database"')

        admin_conn.close.assert_called_once()

    @patch("src.database.db.psycopg2.connect")
    def test_create_schema_connects_to_postgres_database(self, mock_connect):
        admin_conn = Mock()
        mock_connect.return_value = admin_conn

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)

        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_cursor)
        mock_context.__exit__ = Mock(return_value=None)

        admin_conn.cursor.return_value = mock_context

        db = DatabaseConnection(self.config)

        db.create_schema_if_needed("students")

        mock_connect.assert_called_with(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            dbname="postgres",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
