import sqlite3
from typing import Optional

def check_user_ongoing(conn: sqlite3.Connection, user_id: int) -> bool:
    cur = conn.execute("SELECT 1 FROM rides WHERE user_id = ? AND status = 'ONGOING'", (user_id,))
    return cur.fetchone() is not None

def claim_driver(conn: sqlite3.Connection, driver_id: int) -> bool:
    cur = conn.execute("UPDATE drivers SET status = 'ON_RIDE' WHERE id = ? AND status = 'AVAILABLE'", (driver_id,))
    return cur.rowcount > 0

def insert_ride(conn: sqlite3.Connection, user_id: int, driver_id: int, req_car: str, assign_car: str, p_lat: float, p_lng: float, surge: float,
                coupon_code: Optional[str], coupon_type: Optional[str], coupon_val: Optional[int], coupon_max: Optional[int], created_at: str) -> int:
    cur = conn.execute(
        """INSERT INTO rides (user_id, driver_id, requested_car_type, assigned_car_type, status, pickup_lat, pickup_lng, 
           surge_multiplier, coupon_code, coupon_type, coupon_value, coupon_max_discount_paise, created_at) 
           VALUES (?, ?, ?, ?, 'ONGOING', ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, driver_id, req_car, assign_car, p_lat, p_lng, surge, coupon_code, coupon_type, coupon_val, coupon_max, created_at)
    )
    return cur.lastrowid

def get_ride(conn: sqlite3.Connection, ride_id: int) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM rides WHERE id = ?", (ride_id,))
    return cur.fetchone()

def end_ride(conn: sqlite3.Connection, ride_id: int, e_lat: float, e_lng: float, dist: float, base_fare: int, discount: int, total: int, ended_at: str):
    conn.execute(
        """UPDATE rides SET status = 'COMPLETED', end_lat = ?, end_lng = ?, distance_km = ?, base_fare_paise = ?, 
           discount_paise = ?, total_fare_paise = ?, ended_at = ? WHERE id = ?""",
        (e_lat, e_lng, dist, base_fare, discount, total, ended_at, ride_id)
    )

def release_driver(conn: sqlite3.Connection, driver_id: int, lat: float, lng: float):
    conn.execute("UPDATE drivers SET status = 'AVAILABLE', lat = ?, lng = ? WHERE id = ?", (lat, lng, driver_id))

def get_available_drivers_by_type(conn: sqlite3.Connection, car_type: str) -> list[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM drivers WHERE status = 'AVAILABLE' AND car_type = ?", (car_type,))
    return cur.fetchall()

def get_rides_by_user(conn: sqlite3.Connection, user_id: int, status: Optional[str]) -> list[sqlite3.Row]:
    query = "SELECT * FROM rides WHERE user_id = ?"
    params = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC"
    cur = conn.execute(query, params)
    return cur.fetchall()

def get_rides_by_driver(conn: sqlite3.Connection, driver_id: int, status: Optional[str]) -> list[sqlite3.Row]:
    query = "SELECT * FROM rides WHERE driver_id = ?"
    params = [driver_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC"
    cur = conn.execute(query, params)
    return cur.fetchall()
