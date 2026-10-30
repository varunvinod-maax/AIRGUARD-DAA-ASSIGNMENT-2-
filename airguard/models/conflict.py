from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Dict, Any
from models.aircraft import Aircraft


class ThreatLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SAFE = "SAFE"

    @property
    def color(self) -> str:
        """Hex color associated with threat level for GUI visualization."""
        if self == ThreatLevel.HIGH:
            return "#FF2A55"  # Neon Red/Coral
        elif self == ThreatLevel.MEDIUM:
            return "#FFB703"  # Amber/Yellow
        elif self == ThreatLevel.LOW:
            return "#00E5FF"  # Cyan/Warning Info
        return "#00E676"      # Emerald Green (Safe)

    @property
    def badge_color(self) -> str:
        if self == ThreatLevel.HIGH:
            return "#D90429"
        elif self == ThreatLevel.MEDIUM:
            return "#F48C06"
        elif self == ThreatLevel.LOW:
            return "#0096C7"
        return "#2D6A4F"

    @property
    def rank(self) -> int:
        """Lower rank means higher priority (for sorting conflicts)."""
        if self == ThreatLevel.HIGH:
            return 1
        elif self == ThreatLevel.MEDIUM:
            return 2
        elif self == ThreatLevel.LOW:
            return 3
        return 4


@dataclass
class ThresholdConfig:
    """Educational separation threshold configuration.
    
    Disclaimer: These thresholds are for illustrative DAA simulation purposes only
    and do NOT reflect real-world certified FAA / ICAO separation minimums.
    """
    high_horiz: float = 0.50    # km (< 500 meters)
    high_vert: float = 0.15     # km (< 150 meters)
    med_horiz: float = 1.50     # km (< 1500 meters)
    med_vert: float = 0.30      # km (< 300 meters)
    low_horiz: float = 3.00     # km (< 3000 meters)
    low_vert: float = 0.50      # km (< 500 meters)
    prediction_horizon: float = 60.0  # seconds (default 60s prediction lookahead)

    @property
    def max_conflict_distance(self) -> float:
        """Maximum horizontal distance for any conflict threat level."""
        return max(self.high_horiz, self.med_horiz, self.low_horiz)


@dataclass
class ConflictPair:
    """Represents a potential collision threat detected between two aircraft."""
    aircraft_a: Aircraft
    aircraft_b: Aircraft
    threat_level: ThreatLevel
    time_to_closest_approach: float  # seconds
    horizontal_separation: float     # km
    vertical_separation: float       # km
    relative_speed: float            # km/s
    pos_a_at_t: Tuple[float, float]  # (x, y) at time of closest approach
    pos_b_at_t: Tuple[float, float]  # (x, y) at time of closest approach

    @property
    def pair_key(self) -> Tuple[str, str]:
        """Canonical ordered pair ID tuple for deduplication."""
        id_1, id_2 = self.aircraft_a.id, self.aircraft_b.id
        return (id_1, id_2) if id_1 < id_2 else (id_2, id_1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_a": self.aircraft_a.id,
            "aircraft_b": self.aircraft_b.id,
            "threat_level": self.threat_level.value,
            "time_to_closest_approach": round(self.time_to_closest_approach, 2),
            "horizontal_separation_km": round(self.horizontal_separation, 3),
            "horizontal_separation_m": round(self.horizontal_separation * 1000.0, 1),
            "vertical_separation_km": round(self.vertical_separation, 3),
            "vertical_separation_m": round(self.vertical_separation * 1000.0, 1),
            "relative_speed_kms": round(self.relative_speed, 4),
            "pos_a_at_t": (round(self.pos_a_at_t[0], 2), round(self.pos_a_at_t[1], 2)),
            "pos_b_at_t": (round(self.pos_b_at_t[0], 2), round(self.pos_b_at_t[1], 2))
        }
