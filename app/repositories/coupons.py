import sqlite3
from typing import Optional

def create(conn: sqlite3.Connection, code: str, type: str, value: int, max_discount_paise: Optional[int], expires_at: Optional[str]):
    try:
        conn.execute(
            "INSERT INTO coupons (code, type, value, max_discount_paise, expires_at) VALUES (?, ?, ?, ?, ?)",
            (code, type, value, max_discount_paise, expires_at)
        )
    except sqlite3.IntegrityError:
        raise ValueError("COUPON_ALREADY_EXISTS")

def get_by_code(conn: sqlite3.Connection, code: str) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM coupons WHERE code = ?", (code,))
    return cur.fetchone()

def delete(conn: sqlite3.Connection, code: str) -> bool:
    cur = conn.execute("DELETE FROM coupons WHERE code = ?", (code,))
    return cur.rowcount > 0
