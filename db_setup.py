# db_setup.py

import os
import sqlite3

DB_PATH = 'secure_passwords.db'

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    return conn


def initialize_db():
    # Check if the database file already exists
    is_first_run = not os.path.exists(DB_PATH)

    conn = get_db_connection()
    cursor = conn.cursor()

    if is_first_run:
        print("Initializing new database...")

    # Create credentials table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY,
        service TEXT NOT NULL,
        username TEXT,
        password BLOB NOT NULL,  -- will store encrypted password
        url TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # You can add more one-time setup operations here if needed
    conn.commit()
    conn.close()

    if not is_first_run:
        print("Database already exists and is up-to-date.")
