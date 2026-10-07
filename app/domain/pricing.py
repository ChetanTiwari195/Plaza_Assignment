from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Tuple
from decimal import Decimal
from app.domain.money import to_paise

class CarType(str, Enum):
    HATCHBACK = "HATCHBACK"
    SEDAN = "SEDAN"

@dataclass
class RateCard:
    slabs: List[Tuple[Optional[float], int]]
    min_fare_paise: int

@dataclass
class FareBreakdown:
    slab_total_paise: int
    base_fare_paise: int
    surge_multiplier: float
    surged_fare_paise: int
    discount_paise: int
    total_paise: int

RATE_CARDS = {
    CarType.HATCHBACK: RateCard(
        slabs=[(2.0, 1000), (5.0, 800), (None, 500)],
        min_fare_paise=5000
    ),
    CarType.SEDAN: RateCard(
        slabs=[(2.0, 1200), (5.0, 1000), (None, 700)],
        min_fare_paise=6000
    )
}

UPGRADE_PATH = {
    CarType.HATCHBACK: [CarType.SEDAN],
    CarType.SEDAN: []
}

class PricingEngine:
    @staticmethod
    def compute(car_type: CarType, distance_km: float, surge_multiplier: float = 1.0, discount_paise: int = 0) -> FareBreakdown:
        if distance_km < 0:
            raise ValueError("Distance cannot be negative")
            
        rate_card = RATE_CARDS[car_type]
        slab_total = Decimal("0")
        remaining_km = Decimal(str(distance_km))
        
        prev_upper = Decimal("0")
        for upper, rate in rate_card.slabs:
            if remaining_km <= 0:
                break
            
            slab_width = Decimal(str(upper)) - prev_upper if upper is not None else remaining_km
            km_in_slab = min(remaining_km, slab_width)
            
            slab_total += km_in_slab * Decimal(rate)
            remaining_km -= km_in_slab
            if upper is not None:
                prev_upper = Decimal(str(upper))
            
        slab_total_paise = to_paise(slab_total)
        base_fare_paise = max(slab_total_paise, rate_card.min_fare_paise)
        surged_fare_paise = to_paise(Decimal(base_fare_paise) * Decimal(str(surge_multiplier)))
        total_paise = max(0, surged_fare_paise - discount_paise)
        
        return FareBreakdown(
            slab_total_paise=slab_total_paise,
            base_fare_paise=base_fare_paise,
            surge_multiplier=surge_multiplier,
            surged_fare_paise=surged_fare_paise,
            discount_paise=discount_paise,
            total_paise=total_paise
        )
