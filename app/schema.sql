CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    car_type TEXT NOT NULL,
    rating REAL NOT NULL DEFAULT 5.0,
    status TEXT NOT NULL DEFAULT 'AVAILABLE',
    lat REAL NOT NULL,
    lng REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS coupons (
    code TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    value INTEGER NOT NULL,
    max_discount_paise INTEGER,
    expires_at TEXT
);

CREATE TABLE IF NOT EXISTS rides (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    driver_id INTEGER NOT NULL REFERENCES drivers(id),
    requested_car_type TEXT NOT NULL,
    assigned_car_type TEXT NOT NULL,
    status TEXT NOT NULL,
    pickup_lat REAL NOT NULL,
    pickup_lng REAL NOT NULL,
    end_lat REAL,
    end_lng REAL,
    distance_km REAL,
    surge_multiplier REAL NOT NULL DEFAULT 1.0,
    coupon_code TEXT,
    coupon_type TEXT,
    coupon_value INTEGER,
    coupon_max_discount_paise INTEGER,
    base_fare_paise INTEGER,
    discount_paise INTEGER,
    total_fare_paise INTEGER,
    cancellation_fee_paise INTEGER,
    created_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rides_driver_ongoing ON rides(driver_id) WHERE status='ONGOING';
CREATE UNIQUE INDEX IF NOT EXISTS idx_rides_user_ongoing ON rides(user_id) WHERE status='ONGOING';
