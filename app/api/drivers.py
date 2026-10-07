from fastapi import APIRouter, Depends, Request
from app.api.schemas import DriverCreate, LocationUpdate
from app.services import drivers as drivers_service
from app.db import connect

router = APIRouter(prefix="/drivers", tags=["Drivers"])

def get_db(request: Request):
    settings = request.app.state.settings
    with connect(settings.db_path) as conn:
        yield conn

@router.post("", status_code=201)
def create_driver(driver: DriverCreate, db = Depends(get_db)):
    return drivers_service.create_driver(db, driver.name, driver.phone, driver.car_type.value, driver.lat, driver.lng, driver.rating)

@router.get("/{driver_id}")
def get_driver(driver_id: int, db = Depends(get_db)):
    return drivers_service.get_driver(db, driver_id)

@router.put("/{driver_id}/location")
def update_location(driver_id: int, loc: LocationUpdate, db = Depends(get_db)):
    return drivers_service.update_location(db, driver_id, loc.lat, loc.lng)
