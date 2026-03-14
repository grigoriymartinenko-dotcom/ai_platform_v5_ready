import sqlite3
from pathlib import Path

DB_PATH = "memory.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS messages
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                user_id
                TEXT,
                role
                TEXT,
                content
                TEXT
            )
            """)

conn.commit()


def save_context(user_id, message):
    cur.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, message["role"], message["content"])
    )

    conn.commit()


def get_context(user_id, limit=20):
    cur.execute(
        "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )

    rows = cur.fetchall()

    rows.reverse()

    return [
        {"role": r[0], "content": r[1]}
        for r in rows
    ]
