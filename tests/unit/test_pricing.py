import pytest
from app.domain.pricing import PricingEngine, CarType

@pytest.mark.parametrize("car,km,expected", [
    (CarType.HATCHBACK, 1, 5000),
    (CarType.HATCHBACK, 2, 5000),
    (CarType.HATCHBACK, 5, 5000),
    (CarType.HATCHBACK, 6, 5000),
    (CarType.HATCHBACK, 10, 6900),
    (CarType.HATCHBACK, 7.5, 5650),
    (CarType.SEDAN, 10, 8900),
    (CarType.SEDAN, 3, 6000),
])
def test_pricing_cases(car, km, expected):
    breakdown = PricingEngine.compute(car, km)
    assert breakdown.total_paise == expected

def test_pricing_zero_km():
    assert PricingEngine.compute(CarType.HATCHBACK, 0).total_paise == 5000

def test_pricing_boundaries():
    assert PricingEngine.compute(CarType.HATCHBACK, 2.0).slab_total_paise == 2000
    assert PricingEngine.compute(CarType.HATCHBACK, 5.0).slab_total_paise == 4400
    assert PricingEngine.compute(CarType.HATCHBACK, 2.01).slab_total_paise == 2008

def test_pricing_negative():
    with pytest.raises(ValueError):
        PricingEngine.compute(CarType.HATCHBACK, -1.0)

def test_surge():
    b = PricingEngine.compute(CarType.HATCHBACK, 10, surge_multiplier=1.5)
    assert b.total_paise == 10350

def test_discount():
    b = PricingEngine.compute(CarType.HATCHBACK, 10, discount_paise=1380)
    assert b.total_paise == 5520

def test_discount_floors_at_zero():
    b = PricingEngine.compute(CarType.HATCHBACK, 10, discount_paise=10000)
    assert b.total_paise == 0
