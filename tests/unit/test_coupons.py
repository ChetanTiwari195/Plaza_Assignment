import pytest
from app.domain.coupons import build_coupon

def test_percent_coupon():
    c = build_coupon("PERCENT", 20, max_discount_paise=None)
    assert c.discount_paise(6900) == 1380

def test_percent_coupon_with_cap():
    c = build_coupon("PERCENT", 50, max_discount_paise=1000)
    assert c.discount_paise(6900) == 1000

def test_flat_coupon():
    c = build_coupon("FLAT", 10000)
    assert c.discount_paise(6900) == 6900

def test_percent_100():
    c = build_coupon("PERCENT", 100)
    assert c.discount_paise(5000) == 5000
