
from src.db import DatabaseConnection

# App
# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Index DDL
# ---------------------------------------------------------------------------

_INDEXES = [

    (
        "idx_students_room_id",
        "CREATE INDEX IF NOT EXISTS idx_students_room_id "
        "ON students (room_id);",
    ),
    
    (
        "idx_students_room_birthday",
        "CREATE INDEX IF NOT EXISTS idx_students_room_birthday "
        "ON students (room_id, birthday);",
    ),
 
    (
        "idx_students_sex",
        "CREATE INDEX IF NOT EXISTS idx_students_sex "
        "ON students (room_id, sex);",
    ),
]

# ---------------------------------------------------------------------------

class SchemaManager:

    def __init__(self, conn: DatabaseConnection) -> None:
        self._conn = conn

    def apply(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(_CREATE_ROOMS)
            cur.execute(_CREATE_STUDENTS)

        with self._conn.cursor() as cur:
            for name, stmt in _INDEXES:
                cur.execute(stmt)

    def index_ddl(self) -> list[str]:
        return [stmt for _, stmt in _INDEXES]

# ---------------------------------------------------------------------------
