import sqlite3
from typing import Optional

def create(conn: sqlite3.Connection, name: str, phone: str) -> int:
    try:
        cur = conn.execute("INSERT INTO users (name, phone) VALUES (?, ?)", (name, phone))
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("DUPLICATE_PHONE")

def get_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()
