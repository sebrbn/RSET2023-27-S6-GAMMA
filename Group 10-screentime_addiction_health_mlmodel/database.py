import sqlite3

DB_NAME = "mental_health.db"

def connect():
    return sqlite3.connect(DB_NAME, timeout=10)  # Add timeout

def create_tables():
    with connect() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            addiction_score REAL,
            addiction_level TEXT,
            health_risk TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        conn.commit()