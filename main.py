from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db import DatabaseConfig, DatabaseConnection
from src.schema import SchemaManager
from src.loader import DataLoader
from src.queries import QueryRepository
from src.serializer import SerializerFactory


# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("dormitory")


# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Dormitory Pipeline"
    )

    p.add_argument("--students", required=True,
                   help="Path to students JSON file")
    p.add_argument("--rooms", required=True,
                   help="Path to rooms JSON file")

    p.add_argument(
        "--format",
        required=True,
        choices=SerializerFactory.supported_formats(),
        help="Output format: json | xml"
    )

    p.add_argument(
        "--output",
        default=None,
        help="Output file path (default: output/report.<format>)"
    )

    # Database arguments
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", default=5435, type=int)
    p.add_argument("--user", default="postgres")
    p.add_argument("--password", default="postgres")
    p.add_argument("--database", default="postgres")

    return p


# ---------------------------------------------------------------------------

def build_report(
    repo: QueryRepository,
    schema: SchemaManager
) -> dict:

    return {
        "rooms_with_student_count": repo.rooms_with_student_count(),
        "five_rooms_youngest_avg_age": repo.five_rooms_youngest_avg_age(),
        "five_rooms_largest_age_diff": repo.five_rooms_largest_age_diff(),
        "mixed_sex_rooms": repo.mixed_sex_rooms(),
        "index_ddl_applied": schema.index_ddl(),
    }


# ---------------------------------------------------------------------------

def main() -> int:
    args = build_arg_parser().parse_args()

    cfg = DatabaseConfig(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
    )

    conn = DatabaseConnection(cfg)
    conn.connect()

    try:
        # Create schema and indexes
        conn.create_schema_if_needed(args.database)

        schema = SchemaManager(conn)
        schema.apply()

        logger.info(
            "Tables and indexes ready in database '%s'.",
            args.database
        )

        # Load data
        loader = DataLoader(conn)

        n_rooms = loader.load_rooms(args.rooms)
        n_students = loader.load_students(args.students)

        logger.info(
            "Inserted/skipped: %s rooms, %s students.",
            n_rooms,
            n_students
        )

        # Run queries
        repo = QueryRepository(conn)
        report = build_report(repo, schema)

        # Serialize report
        serializer = SerializerFactory.create(args.format)

        output_path = Path(
            args.output or f"output/report.{serializer.extension()}"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        serializer.write(report, output_path)

        logger.info(
            "Report written to: %s",
            output_path
        )

        # Log report summary
        _log_summary(report)

    except Exception:
        logger.exception("Pipeline failed.")
        raise

    finally:
        conn.close()
        logger.info("Database connection closed.")

    return 0


# ---------------------------------------------------------------------------

def _log_summary(report: dict) -> None:
    sep = "-" * 60

    logger.info("")
    logger.info(sep)
    logger.info("ROOMS & STUDENT COUNTS")
    logger.info(sep)
    input("\nPress Enter to review results...")

    for r in report["rooms_with_student_count"]:
        logger.info(
            "%-15s %s students",
            r["room_name"],
            r["student_count"]
        )
    

    logger.info("")
    logger.info(sep)
    logger.info("5 ROOMS – LOWEST AVERAGE AGE")
    logger.info(sep)
    input("\nPress Enter to review results...")

    for r in report["five_rooms_youngest_avg_age"]:
        logger.info(
            "%-15s avg age %.2f yrs",
            r["room_name"],
            r["avg_age_years"]
        )

    logger.info("")
    logger.info(sep)
    logger.info("5 ROOMS – LARGEST AGE DIFFERENCE")
    logger.info(sep)
    input("\nPress Enter to review results...")

    for r in report["five_rooms_largest_age_diff"]:
        logger.info(
            "%-15s diff %.2f yrs",
            r["room_name"],
            r["age_diff_years"]
        )

    logger.info("")
    logger.info(sep)
    logger.info("MIXED-SEX ROOMS")
    logger.info(sep)
    input("\nPress Enter to review results...")

    mixed = report["mixed_sex_rooms"]

    if mixed:
        for r in mixed:
            logger.info("%s", r["room_name"])
    else:
        logger.info("(none)")

    logger.info("")
    logger.info(sep)
    logger.info("INDEXES APPLIED")
    logger.info(sep)
    input("\nPress Enter to review results...")

    for stmt in report["index_ddl_applied"]:
        logger.info("%s", stmt)
    

# ---------------------------------------------------------------------------
# Run App

if __name__ == "__main__":
    sys.exit(main())
