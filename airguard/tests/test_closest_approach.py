import unittest
from models.aircraft import Aircraft
from models.conflict import ThresholdConfig, ThreatLevel
from algorithms.closest_approach import calculate_closest_approach


class TestClosestApproachMath(unittest.TestCase):
    def setUp(self):
        self.config = ThresholdConfig(
            high_horiz=0.5,
            high_vert=0.15,
            med_horiz=1.5,
            med_vert=0.30,
            low_horiz=3.0,
            low_vert=0.50,
            prediction_horizon=60.0
        )

    def test_head_on_collision_high_threat(self):
        """Two aircraft moving head-on at same altitude should trigger HIGH threat."""
        ac1 = Aircraft("AI-1", x=-10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("AI-2", x=10.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.0)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.threat_level, ThreatLevel.HIGH)
        # Expected collision at t = 20 / 0.40 = 50.0 seconds
        self.assertAlmostEqual(conflict.time_to_closest_approach, 50.0, delta=0.1)
        self.assertAlmostEqual(conflict.horizontal_separation, 0.0, delta=0.01)
        self.assertAlmostEqual(conflict.vertical_separation, 0.0, delta=0.01)

    def test_diverging_aircraft_no_threat(self):
        """Aircraft moving apart should produce SAFE (None) or non-conflict."""
        ac1 = Aircraft("AC-A", x=-10.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.0)
        ac2 = Aircraft("AC-B", x=10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNone(conflict)

    def test_crossing_trajectories_threat(self):
        """Orthogonal paths intersecting at origin at t=50s."""
        ac1 = Aircraft("AC-X", x=-10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("AC-Y", x=0.0, y=-10.0, altitude=10.0, vx=0.0, vy=0.20)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.threat_level, ThreatLevel.HIGH)
        self.assertAlmostEqual(conflict.time_to_closest_approach, 50.0, delta=0.1)
        self.assertAlmostEqual(conflict.horizontal_separation, 0.0, delta=0.01)

    def test_zero_relative_velocity_parallel_far(self):
        """Aircraft with identical velocities (zero relative velocity) well separated."""
        ac1 = Aircraft("P1", x=0.0, y=0.0, altitude=10.0, vx=0.20, vy=0.10)
        ac2 = Aircraft("P2", x=20.0, y=20.0, altitude=10.0, vx=0.20, vy=0.10)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNone(conflict)

    def test_zero_relative_velocity_parallel_close(self):
        """Aircraft flying in close formation (parallel) below threshold."""
        ac1 = Aircraft("F1", x=0.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("F2", x=0.2, y=0.1, altitude=10.0, vx=0.20, vy=0.0)  # ~223m separation
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.threat_level, ThreatLevel.HIGH)
        self.assertEqual(conflict.time_to_closest_approach, 0.0)

    def test_different_altitudes_safely_separated(self):
        """Aircraft horizontally on collision course but separated by 1000m vertically."""
        ac1 = Aircraft("HI", x=-10.0, y=0.0, altitude=11.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("LO", x=10.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.0)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        # Vertical difference is 1.0 km > 0.50 km max vertical threshold -> No conflict
        self.assertIsNone(conflict)

    def test_medium_threat_classification(self):
        """Passes at 1.0 km horiz separation, 0.20 km vert separation -> MEDIUM threat."""
        # Closest approach at t=50s has distance dx=1.0, dy=0
        ac1 = Aircraft("M1", x=-10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("M2", x=10.0, y=1.0, altitude=10.2, vx=-0.20, vy=0.0)
        
        conflict = calculate_closest_approach(ac1, ac2, self.config)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.threat_level, ThreatLevel.MEDIUM)
        self.assertAlmostEqual(conflict.horizontal_separation, 1.0, delta=0.05)
        self.assertAlmostEqual(conflict.vertical_separation, 0.2, delta=0.01)

    def test_zero_prediction_horizon(self):
        """Prediction horizon = 0 evaluates only current position (t=0)."""
        cfg_zero = ThresholdConfig(
            high_horiz=0.5, high_vert=0.15,
            prediction_horizon=0.0
        )
        # Starting 20 km apart
        ac1 = Aircraft("Z1", x=-10.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0)
        ac2 = Aircraft("Z2", x=10.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.0)
        
        conflict = calculate_closest_approach(ac1, ac2, cfg_zero)
        # At t=0 distance is 20km -> No conflict
        self.assertIsNone(conflict)


if __name__ == "__main__":
    unittest.main()
