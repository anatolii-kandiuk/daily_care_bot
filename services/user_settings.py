import sqlite3
import os

DB_PATH = "data/user.db"

os.makedirs("data", exist_ok=True)

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            city TEXT NOT NULL
        )
    """)
    conn.commit()


def get_user_city(user_id: int) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT city FROM user_settings WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else "Siegen" 


def set_user_city(user_id: int, city: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_settings (user_id, city)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET city = excluded.city
        """, (user_id, city))
        conn.commit()
