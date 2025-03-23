import sqlite3
import os
from pathlib import Path


def init_database(db_path='vibemeter.db'):
    """Initialize the database with the schema.sql file"""
    # Get the absolute path to the current directory (where this script is located)
    base_dir = Path(__file__).resolve().parent

    # Connect to the database (will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Execute the schema file
    with open(os.path.join(base_dir, 'schema.sql')) as f:
        conn.executescript(f.read())

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    init_database()
