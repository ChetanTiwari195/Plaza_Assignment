from dataclasses import dataclass

@dataclass
class Settings:
    db_path: str = "ride_hailing.db"
    search_radius_km: float = 5.0
