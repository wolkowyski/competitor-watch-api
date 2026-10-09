import sqlite3
import os

DB_PATH = os.getenv("DATABASE_FILE", "competitor_data.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            product_url TEXT NOT NULL UNIQUE,
            price_text TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            availability_text TEXT NOT NULL,
            rating_text TEXT,
            description TEXT,
            source_page TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            items_ingested INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
