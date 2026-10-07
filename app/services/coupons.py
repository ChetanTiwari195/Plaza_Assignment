from typing import Optional
from datetime import datetime
from app.db import transaction
from app.repositories import coupons as coupons_repo
from app.errors import DomainError, NotFoundError

class CouponAlreadyExists(DomainError):
    code = "COUPON_ALREADY_EXISTS"
    status_code = 409
    def __init__(self):
        super().__init__("Coupon already exists")

class InvalidCoupon(DomainError):
    code = "INVALID_COUPON"
    status_code = 422
    def __init__(self, msg: str = "Invalid coupon"):
        super().__init__(msg)

def create_coupon(conn, code: str, type_str: str, value: int, max_discount_paise: Optional[int], expires_at: Optional[str]) -> dict:
    code = code.upper()
    with transaction(conn):
        try:
            coupons_repo.create(conn, code, type_str, value, max_discount_paise, expires_at)
        except ValueError:
            raise CouponAlreadyExists()
    return dict(coupons_repo.get_by_code(conn, code))

def get_coupon(conn, code: str) -> dict:
    code = code.upper()
    row = coupons_repo.get_by_code(conn, code)
    if not row:
        raise NotFoundError("COUPON_NOT_FOUND", "Coupon not found")
    return dict(row)

def delete_coupon(conn, code: str):
    code = code.upper()
    with transaction(conn):
        if not coupons_repo.delete(conn, code):
            raise NotFoundError("COUPON_NOT_FOUND", "Coupon not found")

def validate(conn, code: str, now: datetime) -> dict:
    code = code.upper()
    row = coupons_repo.get_by_code(conn, code)
    if not row:
        raise InvalidCoupon()
    if row["expires_at"]:
        expires = datetime.fromisoformat(row["expires_at"])
        if expires <= now:
            raise InvalidCoupon("Coupon expired")
    return dict(row)
