from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from enum import Enum

router = APIRouter(prefix="/admin", tags=["Admin"])

class SurgeMode(str, Enum):
    OFF = "OFF"
    DEMAND_SUPPLY = "DEMAND_SUPPLY"

class MatchingStrategy(str, Enum):
    NEAREST = "NEAREST"
    HIGHEST_RATED = "HIGHEST_RATED"

class ConfigUpdate(BaseModel):
    surge_mode: Optional[SurgeMode] = None
    matching_strategy: Optional[MatchingStrategy] = None

@router.get("/config")
def get_config(request: Request):
    return {
        "surge_mode": getattr(request.app.state, "surge_mode", "OFF"),
        "matching_strategy": getattr(request.app.state, "matching_strategy", "NEAREST")
    }

@router.put("/config")
def update_config(config: ConfigUpdate, request: Request):
    if config.surge_mode is not None:
        request.app.state.surge_mode = config.surge_mode.value
    if config.matching_strategy is not None:
        request.app.state.matching_strategy = config.matching_strategy.value
    return get_config(request)
