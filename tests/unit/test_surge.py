from app.domain.surge import SURGE_MODES

def test_no_surge():
    p = SURGE_MODES["OFF"]()
    assert p.multiplier(100, 1) == 1.0

def test_demand_supply_surge():
    p = SURGE_MODES["DEMAND_SUPPLY"]()
    # ratio <= 1
    assert p.multiplier(1, 1) == 1.0
    assert p.multiplier(1, 2) == 1.0
    # 1 < ratio <= 2
    assert p.multiplier(2, 1) == 1.25
    assert p.multiplier(4, 2) == 1.25
    # ratio > 2
    assert p.multiplier(3, 1) == 1.5
    
    # 0 supply handled
    assert p.multiplier(1, 0) == 1.0 # ratio = 1/1 = 1.0 -> 1.0
    assert p.multiplier(2, 0) == 1.25 # ratio = 2/1 = 2.0 -> 1.25
    assert p.multiplier(3, 0) == 1.5 # ratio = 3/1 = 3.0 -> 1.5
