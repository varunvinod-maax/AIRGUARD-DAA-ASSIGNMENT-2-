import math
from typing import Optional
from models.aircraft import Aircraft
from models.conflict import ThreatLevel, ThresholdConfig, ConflictPair


def calculate_closest_approach(
    aircraft_a: Aircraft,
    aircraft_b: Aircraft,
    config: ThresholdConfig
) -> Optional[ConflictPair]:
    """Calculates horizontal relative motion, time of closest approach,
    and predicted separation between aircraft A and B.
    
    Formula:
        Relative position: r = position(B) - position(A)
        Relative velocity: v = velocity(B) - velocity(A)
        Time of closest approach: t = clamp(-(r · v) / (v · v), 0, horizon)
        Predicted horizontal separation: ||r(t)|| = ||r + v * t||
        Predicted vertical separation: |altitude(B) - altitude(A)|
    
    Returns:
        ConflictPair if threat level is HIGH, MEDIUM, or LOW; otherwise None.
    """
    rx = aircraft_b.x - aircraft_a.x
    ry = aircraft_b.y - aircraft_a.y
    
    vx = aircraft_b.vx - aircraft_a.vx
    vy = aircraft_b.vy - aircraft_a.vy
    
    v_dot_v = vx * vx + vy * vy
    horizon = max(0.0, config.prediction_horizon)
    
    # Handle zero or near-zero relative velocity without division by zero
    if v_dot_v < 1e-12:
        t_closest = 0.0
    else:
        r_dot_v = rx * vx + ry * vy
        t_raw = - (r_dot_v) / v_dot_v
        # Clamp to [0, prediction_horizon]
        if horizon <= 0.0:
            t_closest = 0.0
        else:
            t_closest = max(0.0, min(t_raw, horizon))
            
    # Position at time t_closest
    pos_a_t = aircraft_a.position_at(t_closest)
    pos_b_t = aircraft_b.position_at(t_closest)
    
    # Predicted horizontal separation
    dx = pos_b_t[0] - pos_a_t[0]
    dy = pos_b_t[1] - pos_a_t[1]
    horiz_sep = math.hypot(dx, dy)
    
    # Predicted vertical separation (constant altitude model)
    vert_sep = abs(aircraft_b.altitude - aircraft_a.altitude)
    
    # Classify threat level
    threat: Optional[ThreatLevel] = None
    if horiz_sep <= config.high_horiz and vert_sep <= config.high_vert:
        threat = ThreatLevel.HIGH
    elif horiz_sep <= config.med_horiz and vert_sep <= config.med_vert:
        threat = ThreatLevel.MEDIUM
    elif horiz_sep <= config.low_horiz and vert_sep <= config.low_vert:
        threat = ThreatLevel.LOW
        
    if threat is None:
        return None
        
    rel_speed = math.sqrt(v_dot_v)
    
    return ConflictPair(
        aircraft_a=aircraft_a,
        aircraft_b=aircraft_b,
        threat_level=threat,
        time_to_closest_approach=t_closest,
        horizontal_separation=horiz_sep,
        vertical_separation=vert_sep,
        relative_speed=rel_speed,
        pos_a_at_t=pos_a_t,
        pos_b_at_t=pos_b_t
    )
