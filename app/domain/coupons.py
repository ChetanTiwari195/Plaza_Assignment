from typing import Protocol, Optional
from decimal import Decimal
from app.domain.money import to_paise

class Coupon(Protocol):
    def discount_paise(self, fare_paise: int) -> int: ...

class PercentCoupon:
    def __init__(self, value: int, max_discount_paise: Optional[int]):
        self.value = value
        self.max_discount_paise = max_discount_paise
        
    def discount_paise(self, fare_paise: int) -> int:
        discount = to_paise(Decimal(fare_paise) * Decimal(self.value) / Decimal(100))
        if self.max_discount_paise is not None:
            discount = min(discount, self.max_discount_paise)
        return min(discount, fare_paise)

class FlatCoupon:
    def __init__(self, value: int, max_discount_paise: Optional[int] = None):
        self.value = value
        
    def discount_paise(self, fare_paise: int) -> int:
        return min(self.value, fare_paise)

COUPON_TYPES = {
    "PERCENT": PercentCoupon,
    "FLAT": FlatCoupon
}

def build_coupon(type_str: str, value: int, max_discount_paise: Optional[int] = None) -> Coupon:
    return COUPON_TYPES[type_str](value, max_discount_paise)
