#!/usr/bin/env python
"""
Standalone script to initialize the database without running the Flask app.
"""
import os
import sqlite3
from pathlib import Path


def init_database(db_path='vibemeter.db'):
    """Initialize the SQLite database with the schema file"""
    # Get the absolute path to the schema file
    base_dir = Path(__file__).resolve().parent
    schema_path = os.path.join(base_dir, 'app', 'database', 'schema.sql')

    # Make sure the schema file exists
    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        return False

    try:
        # Connect to the database (will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)

        # Execute the schema file
        with open(schema_path) as f:
            conn.executescript(f.read())

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print(f"Database successfully initialized at {db_path}")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


if __name__ == "__main__":
    init_database()
