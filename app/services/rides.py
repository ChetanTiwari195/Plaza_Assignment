from typing import Optional
from datetime import datetime
from app.db import transaction
from app.repositories import rides as rides_repo
from app.repositories import users as users_repo
from app.repositories import drivers as drivers_repo
from app.services import coupons as coupons_service
from app.domain.pricing import CarType, UPGRADE_PATH, PricingEngine
from app.domain.geo import haversine_km
from app.domain.coupons import build_coupon
from app.domain.surge import SURGE_MODES
from app.errors import DomainError, NotFoundError

class UserHasActiveRide(DomainError):
    code = "USER_HAS_ACTIVE_RIDE"
    status_code = 409
    def __init__(self):
        super().__init__("User already has an active ride")

class NoDriverAvailable(DomainError):
    code = "NO_DRIVER_AVAILABLE"
    status_code = 409
    def __init__(self):
        super().__init__("No driver available")

class RideNotOngoing(DomainError):
    code = "RIDE_NOT_ONGOING"
    status_code = 409
    def __init__(self):
        super().__init__("Ride is not ongoing")

def book_ride(conn, user_id: int, p_lat: float, p_lng: float, req_car_type: str, coupon_code: str, now: datetime, radius: float, surge_mode: str = "OFF", matching_strategy: str = "NEAREST") -> dict:
    with transaction(conn):
        if not users_repo.get_by_id(conn, user_id):
            raise NotFoundError("USER_NOT_FOUND", "User not found")
            
        if rides_repo.check_user_ongoing(conn, user_id):
            raise UserHasActiveRide()
            
        coupon_data = None
        if coupon_code:
            coupon_data = coupons_service.validate(conn, coupon_code, now)
            
        types_to_search = [CarType(req_car_type)] + UPGRADE_PATH[CarType(req_car_type)]
        
        assigned_driver = None
        for ctype in types_to_search:
            drivers = rides_repo.get_available_drivers_by_type(conn, ctype.value)
            candidates = []
            for d in drivers:
                dist = haversine_km(p_lat, p_lng, d["lat"], d["lng"])
                if dist <= radius:
                    candidates.append((dist, d["rating"], d["id"], d))
            
            if matching_strategy == "HIGHEST_RATED":
                candidates.sort(key=lambda x: (-x[1], x[0], x[2]))
            else:
                candidates.sort(key=lambda x: (x[0], x[2]))
            
            for dist, rating, did, d in candidates:
                if rides_repo.claim_driver(conn, did):
                    assigned_driver = d
                    break
            
            if assigned_driver:
                break
                
        if not assigned_driver:
            raise NoDriverAvailable()
            
        c_code = coupon_data["code"] if coupon_data else None
        c_type = coupon_data["type"] if coupon_data else None
        c_val = coupon_data["value"] if coupon_data else None
        c_max = coupon_data["max_discount_paise"] if coupon_data else None
        
        provider = SURGE_MODES[surge_mode]()
        all_avail = rides_repo.get_available_drivers(conn)
        supply = sum(1 for d in all_avail if haversine_km(p_lat, p_lng, d["lat"], d["lng"]) <= radius)
        
        ongoing = rides_repo.get_ongoing_rides(conn)
        demand = 1 + sum(1 for r in ongoing if haversine_km(p_lat, p_lng, r["pickup_lat"], r["pickup_lng"]) <= radius)
        
        surge_mult = provider.multiplier(demand, supply)
        
        ride_id = rides_repo.insert_ride(
            conn, user_id, assigned_driver["id"], req_car_type, assigned_driver["car_type"],
            p_lat, p_lng, surge_mult, c_code, c_type, c_val, c_max, now.isoformat()
        )
        return get_ride(conn, ride_id)

def _format_ride(conn, row) -> dict:
    ride = dict(row)
    ride["driver"] = dict(drivers_repo.get_by_id(conn, ride["driver_id"]))
    ride["pickup"] = {"lat": ride["pickup_lat"], "lng": ride["pickup_lng"]}
    if ride["end_lat"] is not None:
        ride["end_location"] = {"lat": ride["end_lat"], "lng": ride["end_lng"]}
        if ride["total_fare_paise"] is not None:
            ride["fare"] = {
                "slab_total_paise": ride["base_fare_paise"],
                "base_fare_paise": ride["base_fare_paise"],
                "surge_multiplier": ride["surge_multiplier"],
                "discount_paise": ride["discount_paise"],
                "total_paise": ride["total_fare_paise"]
            }
    return ride

def get_ride(conn, ride_id: int) -> dict:
    row = rides_repo.get_ride(conn, ride_id)
    if not row:
        raise NotFoundError("RIDE_NOT_FOUND", "Ride not found")
    return _format_ride(conn, row)

def get_user_rides(conn, user_id: int, status: Optional[str]) -> dict:
    if not users_repo.get_by_id(conn, user_id):
        raise NotFoundError("USER_NOT_FOUND", "User not found")
    rows = rides_repo.get_rides_by_user(conn, user_id, status)
    return {"rides": [_format_ride(conn, r) for r in rows]}

def get_driver_rides(conn, driver_id: int, status: Optional[str]) -> dict:
    if not drivers_repo.get_by_id(conn, driver_id):
        raise NotFoundError("DRIVER_NOT_FOUND", "Driver not found")
    rows = rides_repo.get_rides_by_driver(conn, driver_id, status)
    return {"rides": [_format_ride(conn, r) for r in rows]}

def end_ride(conn, ride_id: int, e_lat: float, e_lng: float, now: datetime) -> dict:
    with transaction(conn):
        ride = rides_repo.get_ride(conn, ride_id)
        if not ride:
            raise NotFoundError("RIDE_NOT_FOUND", "Ride not found")
        if ride["status"] != "ONGOING":
            raise RideNotOngoing()
            
        dist = round(haversine_km(ride["pickup_lat"], ride["pickup_lng"], e_lat, e_lng), 2)
        
        discount = 0
        if ride["coupon_code"]:
            coupon = build_coupon(ride["coupon_type"], ride["coupon_value"], ride["coupon_max_discount_paise"])
            temp_fare = PricingEngine.compute(CarType(ride["requested_car_type"]), dist, ride["surge_multiplier"])
            discount = coupon.discount_paise(temp_fare.surged_fare_paise)
            
        breakdown = PricingEngine.compute(CarType(ride["requested_car_type"]), dist, ride["surge_multiplier"], discount)
        
        rides_repo.end_ride(conn, ride_id, e_lat, e_lng, dist, breakdown.base_fare_paise, breakdown.discount_paise, breakdown.total_paise, now.isoformat())
        rides_repo.release_driver(conn, ride["driver_id"], e_lat, e_lng)
        
    return get_ride(conn, ride_id)
