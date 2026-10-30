import random
from typing import List, Dict, Callable
from models.aircraft import Aircraft


def get_safe_airspace_scenario() -> List[Aircraft]:
    """Scenario 1: Safe Airspace - Well-separated aircraft with diverging/parallel paths."""
    return [
        Aircraft(id="AF-101", x=-30.0, y=25.0, altitude=10.0, vx=0.20, vy=0.00, callsign="COMMERCIAL"),
        Aircraft(id="BA-202", x=-25.0, y=-20.0, altitude=11.0, vx=0.18, vy=0.05, callsign="COMMERCIAL"),
        Aircraft(id="DL-303", x=15.0, y=35.0, altitude=9.5, vx=-0.15, vy=-0.05, callsign="CARGO"),
        Aircraft(id="LH-404", x=20.0, y=-25.0, altitude=10.5, vx=-0.22, vy=0.02, callsign="COMMERCIAL"),
        Aircraft(id="EK-505", x=-5.0, y=-40.0, altitude=12.0, vx=0.05, vy=0.20, callsign="PRIVATE"),
    ]


def get_head_on_scenario() -> List[Aircraft]:
    """Scenario 2: Head-On Approach - Two aircraft on collision course at same altitude."""
    return [
        Aircraft(id="AI-101", x=-10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.00, callsign="COMMERCIAL"),
        Aircraft(id="UA-202", x=10.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.00, callsign="COMMERCIAL"),
        Aircraft(id="SW-303", x=-25.0, y=20.0, altitude=11.5, vx=0.15, vy=0.05, callsign="CARGO"),
        Aircraft(id="QF-404", x=20.0, y=-20.0, altitude=9.0, vx=-0.18, vy=0.02, callsign="COMMERCIAL"),
    ]


def get_crossing_scenario() -> List[Aircraft]:
    """Scenario 3: Crossing Traffic - Orthogonal trajectories intersecting at origin."""
    return [
        Aircraft(id="DL-404", x=0.0, y=-10.0, altitude=10.2, vx=0.00, vy=0.20, callsign="COMMERCIAL"),
        Aircraft(id="BA-505", x=-10.0, y=0.0, altitude=10.2, vx=0.20, vy=0.00, callsign="COMMERCIAL"),
        Aircraft(id="NH-606", x=-20.0, y=25.0, altitude=11.0, vx=0.10, vy=-0.10, callsign="CARGO"),
        Aircraft(id="JL-707", x=30.0, y=15.0, altitude=9.8, vx=-0.15, vy=0.00, callsign="PRIVATE"),
    ]


def get_multiple_conflicts_scenario() -> List[Aircraft]:
    """Scenario 4: Multiple Conflicts - Includes simultaneous internal conflicts and
    a critical cross-boundary conflict spanning across the spatial dividing line.
    """
    return [
        # Left cluster internal conflict (AF-111 & LH-222)
        Aircraft(id="AF-111", x=-30.0, y=10.0, altitude=10.0, vx=0.15, vy=0.05, callsign="COMMERCIAL"),
        Aircraft(id="LH-222", x=-20.0, y=13.0, altitude=10.0, vx=-0.10, vy=-0.02, callsign="COMMERCIAL"),
        
        # Right cluster internal conflict (SQ-333 & EK-444)
        Aircraft(id="SQ-333", x=20.0, y=-15.0, altitude=10.5, vx=0.05, vy=0.15, callsign="COMMERCIAL"),
        Aircraft(id="EK-444", x=23.0, y=-5.0, altitude=10.5, vx=-0.02, vy=-0.10, callsign="COMMERCIAL"),
        
        # Cross-boundary pair spanning dividing line X ~ 0 (QR-555 on left, CX-666 on right)
        Aircraft(id="QR-555", x=-6.0, y=0.0, altitude=11.0, vx=0.15, vy=0.00, callsign="COMMERCIAL"),
        Aircraft(id="CX-666", x=6.0, y=0.0, altitude=11.0, vx=-0.15, vy=0.00, callsign="COMMERCIAL"),
        
        # Safe background traffic
        Aircraft(id="SA-777", x=-35.0, y=-30.0, altitude=8.5, vx=0.22, vy=0.10, callsign="CARGO"),
        Aircraft(id="GA-888", x=35.0, y=30.0, altitude=12.2, vx=-0.18, vy=-0.12, callsign="PRIVATE"),
    ]


def generate_random_traffic(
    count: int = 10,
    seed: int = 42,
    x_range: tuple = (-40.0, 40.0),
    y_range: tuple = (-40.0, 40.0),
    altitude_range: tuple = (9.0, 11.5),
    speed_range: tuple = (0.15, 0.25)
) -> List[Aircraft]:
    """Generates reproducible randomized aircraft traffic using a fixed random seed."""
    rng = random.Random(seed)
    categories = ["COMMERCIAL", "CARGO", "MILITARY", "PRIVATE"]
    prefixes = ["AG", "NX", "FL", "SKY", "VTR", "AER", "ORB", "STR"]
    
    traffic: List[Aircraft] = []
    used_ids = set()

    for i in range(count):
        # Generate unique callsign ID
        while True:
            prefix = rng.choice(prefixes)
            num = rng.randint(100, 999)
            ac_id = f"{prefix}-{num}"
            if ac_id not in used_ids:
                used_ids.add(ac_id)
                break
                
        x = round(rng.uniform(*x_range), 1)
        y = round(rng.uniform(*y_range), 1)
        alt = round(rng.uniform(*altitude_range), 2)
        
        # Random heading
        speed = rng.uniform(*speed_range)
        angle_rad = rng.uniform(0.0, 2.0 * 3.1415926535)
        vx = round(speed * rng.choice([-1, 1]) * abs(rng.uniform(0.3, 1.0)), 4)
        vy = round(speed * rng.choice([-1, 1]) * abs(rng.uniform(0.3, 1.0)), 4)
        
        cat = rng.choice(categories)
        traffic.append(Aircraft(id=ac_id, x=x, y=y, altitude=alt, vx=vx, vy=vy, callsign=cat))

    return traffic


PRESET_SCENARIOS: Dict[str, Callable[[], List[Aircraft]]] = {
    "1. SAFE AIRSPACE": get_safe_airspace_scenario,
    "2. HEAD-ON APPROACH": get_head_on_scenario,
    "3. CROSSING TRAFFIC": get_crossing_scenario,
    "4. MULTIPLE CONFLICTS (CROSS-BOUNDARY)": get_multiple_conflicts_scenario,
}
