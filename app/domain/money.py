from decimal import Decimal, ROUND_HALF_UP

def to_paise(amount: Decimal) -> int:
    return int(amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
