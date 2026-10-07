from pydantic import BaseModel, Field, constr, field_validator
from typing import Optional
from enum import Enum
from app.domain.pricing import CarType

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)

class DriverCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    car_type: CarType
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    rating: float = Field(5.0, ge=0, le=5)

class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class CouponType(str, Enum):
    PERCENT = "PERCENT"
    FLAT = "FLAT"

class CouponCreate(BaseModel):
    code: str = Field(..., min_length=1)
    type: CouponType
    value: int = Field(..., gt=0)
    max_discount_paise: Optional[int] = None
    expires_at: Optional[str] = None
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v, info):
        if info.data.get('type') == CouponType.PERCENT and v > 100:
            raise ValueError("Percent coupon value must be <= 100")
        return v
    
    @field_validator('max_discount_paise')
    @classmethod
    def validate_max_discount(cls, v, info):
        if info.data.get('type') == CouponType.FLAT and v is not None:
            raise ValueError("Flat coupon cannot have max_discount_paise")
        return v

class LocationPoint(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class RideBook(BaseModel):
    user_id: int
    pickup: LocationPoint
    car_type: CarType
    coupon_code: Optional[str] = None

class RideEnd(BaseModel):
    end_location: LocationPoint
