from app.db import transaction
from app.repositories import drivers as drivers_repo
from app.errors import DuplicatePhone, NotFoundError

def create_driver(conn, name: str, phone: str, car_type: str, lat: float, lng: float, rating: float) -> dict:
    with transaction(conn):
        try:
            driver_id = drivers_repo.create(conn, name, phone, car_type, lat, lng, rating)
        except ValueError:
            raise DuplicatePhone()
    return dict(drivers_repo.get_by_id(conn, driver_id))

def get_driver(conn, driver_id: int) -> dict:
    row = drivers_repo.get_by_id(conn, driver_id)
    if not row:
        raise NotFoundError("DRIVER_NOT_FOUND", "Driver not found")
    return dict(row)

def update_location(conn, driver_id: int, lat: float, lng: float) -> dict:
    with transaction(conn):
        if not drivers_repo.update_location(conn, driver_id, lat, lng):
            raise NotFoundError("DRIVER_NOT_FOUND", "Driver not found")
    return get_driver(conn, driver_id)
