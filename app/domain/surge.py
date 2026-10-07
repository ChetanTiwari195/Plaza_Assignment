from typing import Protocol

class SurgeProvider(Protocol):
    def multiplier(self, demand: int, supply: int) -> float: ...

class NoSurge:
    def multiplier(self, demand: int, supply: int) -> float:
        return 1.0

class DemandSupplySurge:
    def multiplier(self, demand: int, supply: int) -> float:
        s = max(supply, 1)
        ratio = demand / s
        if ratio <= 1:
            return 1.0
        elif ratio <= 2:
            return 1.25
        else:
            return 1.5

SURGE_MODES = {
    "OFF": NoSurge,
    "DEMAND_SUPPLY": DemandSupplySurge
}
