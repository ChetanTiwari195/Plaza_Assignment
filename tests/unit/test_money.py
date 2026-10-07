from decimal import Decimal
from app.domain.money import to_paise

def test_to_paise_rounding():
    assert to_paise(Decimal("0.5")) == 1
    assert to_paise(Decimal("2.5")) == 3
    assert to_paise(Decimal("2.4")) == 2
