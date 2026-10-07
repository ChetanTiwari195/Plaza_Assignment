import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.main import create_app
from app.config import Settings

class FakeClock:
    def __init__(self):
        self._now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    def now(self) -> datetime:
        return self._now
    def advance(self, seconds: int):
        self._now += timedelta(seconds=seconds)

@pytest.fixture
def fake_clock():
    return FakeClock()

@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    settings = Settings(db_path=db_path)
    app = create_app(settings)
    return TestClient(app)

def make_user(client: TestClient, name: str, phone: str) -> dict:
    resp = client.post("/users", json={"name": name, "phone": phone})
    assert resp.status_code == 201
    return resp.json()

def make_driver(client: TestClient, name: str, phone: str, car_type: str, lat: float, lng: float, rating: float = 5.0) -> dict:
    resp = client.post("/drivers", json={"name": name, "phone": phone, "car_type": car_type, "lat": lat, "lng": lng, "rating": rating})
    assert resp.status_code == 201
    return resp.json()

def book(client: TestClient, user_id: int, lat: float, lng: float, car_type: str, coupon_code: str = None) -> dict:
    payload = {"user_id": user_id, "pickup": {"lat": lat, "lng": lng}, "car_type": car_type}
    if coupon_code:
        payload["coupon_code"] = coupon_code
    resp = client.post("/rides", json=payload)
    assert resp.status_code == 201
    return resp.json()
