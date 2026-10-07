from fastapi import APIRouter, Depends, Request
from app.api.schemas import RideBook, RideEnd
from app.services import rides as rides_service
from app.db import connect
from app.clock import SystemClock

router = APIRouter(prefix="/rides", tags=["Rides"])

def get_db(request: Request):
    settings = request.app.state.settings
    with connect(settings.db_path) as conn:
        yield conn

def get_clock(request: Request):
    return getattr(request.app.state, "clock", SystemClock())

@router.post("", status_code=201)
def book_ride(ride: RideBook, request: Request, db = Depends(get_db), clock = Depends(get_clock)):
    radius = request.app.state.settings.search_radius_km
    return rides_service.book_ride(db, ride.user_id, ride.pickup.lat, ride.pickup.lng, ride.car_type.value, ride.coupon_code, clock.now(), radius)

@router.post("/{ride_id}/end")
def end_ride(ride_id: int, req: RideEnd, db = Depends(get_db), clock = Depends(get_clock)):
    return rides_service.end_ride(db, ride_id, req.end_location.lat, req.end_location.lng, clock.now())

@router.get("/{ride_id}")
def get_ride(ride_id: int, db = Depends(get_db)):
    return rides_service.get_ride(db, ride_id)
