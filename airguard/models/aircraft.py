from dataclasses import dataclass
from typing import Tuple, Dict, Any
import math


class AircraftValidationError(ValueError):
    """Raised when aircraft parameters fail validation."""
    pass


@dataclass
class Aircraft:
    """Represents an aircraft in 3D simulated airspace.
    
    Coordinates:
        x: Horizontal X coordinate in simulated kilometers (km)
        y: Horizontal Y coordinate in simulated kilometers (km)
        altitude: Vertical altitude in kilometers (km)
        vx: Velocity component along X in km/s (e.g., 0.25 km/s = 900 km/h)
        vy: Velocity component along Y in km/s
        callsign: Category or call sign (e.g., 'COMMERCIAL', 'CARGO', 'MILITARY', 'PRIVATE')
    """
    id: str
    x: float
    y: float
    altitude: float
    vx: float
    vy: float
    callsign: str = "COMMERCIAL"

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validates aircraft properties."""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise AircraftValidationError("Aircraft ID must be a non-empty string.")
        
        self.id = self.id.strip().upper()

        for field_name, value in [('x', self.x), ('y', self.y), ('altitude', self.altitude),
                                  ('vx', self.vx), ('vy', self.vy)]:
            if not isinstance(value, (int, float)) or math.isnan(value) or math.isinf(value):
                raise AircraftValidationError(f"Aircraft field '{field_name}' must be a valid finite number, got {value}.")
        
        self.x = float(self.x)
        self.y = float(self.y)
        self.altitude = float(self.altitude)
        self.vx = float(self.vx)
        self.vy = float(self.vy)

        if self.altitude < 0.0:
            raise AircraftValidationError(f"Aircraft altitude cannot be negative (got {self.altitude} km).")

    @property
    def speed(self) -> float:
        """Horizontal speed in km/s."""
        return math.hypot(self.vx, self.vy)

    @property
    def heading_deg(self) -> float:
        """Aviation heading in degrees (0 deg = North / +Y, 90 deg = East / +X)."""
        angle = math.degrees(math.atan2(self.vx, self.vy))
        return (angle + 360.0) % 360.0

    def position_at(self, t: float) -> Tuple[float, float]:
        """Calculates simulated (x, y) coordinates at time t seconds from t=0."""
        return (self.x + self.vx * t, self.y + self.vy * t)

    def x_extent(self, horizon: float, buffer: float = 0.0) -> Tuple[float, float]:
        """Calculates the [x_min, x_max] extent covered over time [0, horizon] with buffer."""
        x0 = self.x
        x1 = self.x + self.vx * horizon
        x_min = min(x0, x1) - buffer
        x_max = max(x0, x1) + buffer
        return (x_min, x_max)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "altitude": round(self.altitude, 3),
            "vx": round(self.vx, 4),
            "vy": round(self.vy, 4),
            "speed": round(self.speed, 4),
            "heading": round(self.heading_deg, 1),
            "callsign": self.callsign
        }
