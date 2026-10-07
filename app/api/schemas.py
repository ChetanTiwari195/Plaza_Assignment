from pydantic import BaseModel, Field, constr
from enum import Enum
from typing import Optional

class CarType(str, Enum):
    HATCHBACK = "HATCHBACK"
    SEDAN = "SEDAN"

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
