from datetime import datetime
from app.db import transaction
from app.repositories import rides as rides_repo
from app.repositories import users as users_repo
from app.repositories import drivers as drivers_repo
from app.services import coupons as coupons_service
from app.domain.pricing import CarType, UPGRADE_PATH, PricingEngine
from app.domain.geo import haversine_km
from app.domain.coupons import build_coupon
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

def book_ride(conn, user_id: int, p_lat: float, p_lng: float, req_car_type: str, coupon_code: str, now: datetime, radius: float) -> dict:
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
                    candidates.append((dist, d["id"], d))
            
            candidates.sort(key=lambda x: (x[0], x[1]))
            
            for _, did, d in candidates:
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
        
        ride_id = rides_repo.insert_ride(
            conn, user_id, assigned_driver["id"], req_car_type, assigned_driver["car_type"],
            p_lat, p_lng, 1.0, c_code, c_type, c_val, c_max, now.isoformat()
        )
        return get_ride(conn, ride_id)

def get_ride(conn, ride_id: int) -> dict:
    row = rides_repo.get_ride(conn, ride_id)
    if not row:
        raise NotFoundError("RIDE_NOT_FOUND", "Ride not found")
    ride = dict(row)
    ride["driver"] = dict(drivers_repo.get_by_id(conn, ride["driver_id"]))
    ride["pickup"] = {"lat": ride["pickup_lat"], "lng": ride["pickup_lng"]}
    if ride["end_lat"] is not None:
        ride["end_location"] = {"lat": ride["end_lat"], "lng": ride["end_lng"]}
        ride["fare"] = {
            "slab_total_paise": ride["base_fare_paise"],
            "base_fare_paise": ride["base_fare_paise"],
            "surge_multiplier": ride["surge_multiplier"],
            "discount_paise": ride["discount_paise"],
            "total_paise": ride["total_fare_paise"]
        }
    return ride

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
