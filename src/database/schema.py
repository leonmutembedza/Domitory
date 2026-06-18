from src.database.db import DatabaseConnection

# Database schema definitions and index management.

_CREATE_ROOMS = """
CREATE TABLE IF NOT EXISTS rooms (
    id   INT          NOT NULL,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
);
"""

_CREATE_STUDENTS = """
CREATE TABLE IF NOT EXISTS students (
    id       INT          NOT NULL,
    name     VARCHAR(200) NOT NULL,
    birthday TIMESTAMP    NOT NULL,
    sex      CHAR(1)      NOT NULL,
    room_id  INT          NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_students_room
        FOREIGN KEY (room_id) REFERENCES rooms (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
"""


# Index DDL

_INDEXES = [
    (
        "idx_students_room_id",
        "CREATE INDEX IF NOT EXISTS idx_students_room_id " "ON students (room_id);",
    ),
    (
        "idx_students_room_birthday",
        "CREATE INDEX IF NOT EXISTS idx_students_room_birthday "
        "ON students (room_id, birthday);",
    ),
    (
        "idx_students_sex",
        "CREATE INDEX IF NOT EXISTS idx_students_sex " "ON students (room_id, sex);",
    ),
]


class SchemaManager:
    """
    Creates and manages the database schema required by the application.

    Responsible for creating tables and performance indexes.
    """

    def __init__(self, conn: DatabaseConnection) -> None:
        """
        Initialize the schema manager.

        Args:
            conn: Active database connection manager.
        """
        self._conn = conn

    def apply(self) -> None:
        """
        Create database tables and indexes if they do not already exist.

        The operation is idempotent and can be executed multiple times
        without affecting existing schema objects.
        """
        with self._conn.cursor() as cur:
            cur.execute(_CREATE_ROOMS)
            cur.execute(_CREATE_STUDENTS)

        with self._conn.cursor() as cur:
            for _, stmt in _INDEXES:
                cur.execute(stmt)

    def index_ddl(self) -> list[str]:
        """
        Return the SQL statements used to create indexes.

        Returns:
            List of index creation statements.
        """
        return [stmt for _, stmt in _INDEXES]
