import sqlite3
from typing import Optional

def create(conn: sqlite3.Connection, name: str, phone: str, car_type: str, lat: float, lng: float, rating: float) -> int:
    try:
        cur = conn.execute(
            "INSERT INTO drivers (name, phone, car_type, lat, lng, rating) VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone, car_type, lat, lng, rating)
        )
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("DUPLICATE_PHONE")

def get_by_id(conn: sqlite3.Connection, driver_id: int) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
    return cur.fetchone()

def update_location(conn: sqlite3.Connection, driver_id: int, lat: float, lng: float) -> bool:
    cur = conn.execute("UPDATE drivers SET lat = ?, lng = ? WHERE id = ?", (lat, lng, driver_id))
    return cur.rowcount > 0
