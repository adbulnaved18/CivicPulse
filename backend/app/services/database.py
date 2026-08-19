import sqlite3

DB_PATH = "database/civicpulse.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    db = get_db()

    with open("database/schema.sql", "r") as file:
        db.executescript(file.read())

    db.commit()
    db.close()


def add_status_column():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "ALTER TABLE complaints ADD COLUMN status TEXT DEFAULT 'Pending'"
        )
        db.commit()
    except sqlite3.OperationalError:
        pass

    db.close()


def init_votes_table():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS complaint_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            voter_id TEXT NOT NULL,
            UNIQUE(complaint_id, voter_id),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
        """
    )

    db.commit()
    db.close()