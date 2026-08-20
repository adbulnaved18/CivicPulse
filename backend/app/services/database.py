import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = BASE_DIR / "database" / "civicpulse.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite connection.

    Foreign-key enforcement is enabled for every connection.
    """
    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database() -> None:
    """
    Create the database tables and indexes if they do not exist.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    try:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()