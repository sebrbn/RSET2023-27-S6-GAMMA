import sqlite3

conn = sqlite3.connect("mental_health.db")
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

conn.commit()
conn.close()

print("Users table created successfully")