from fastapi import APIRouter
from app.domain.pricing import PricingEngine, CarType

router = APIRouter(prefix="/pricing", tags=["Pricing"])

@router.get("/estimate")
def estimate_pricing(car_type: CarType, distance_km: float):
    if distance_km < 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Distance cannot be negative")
    
    breakdown = PricingEngine.compute(car_type, distance_km)
    return breakdown
