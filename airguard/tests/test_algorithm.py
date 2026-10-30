import unittest
from models.aircraft import Aircraft
from models.conflict import ThresholdConfig, ThreatLevel
from models.scenarios import (
    get_safe_airspace_scenario,
    get_head_on_scenario,
    get_crossing_scenario,
    get_multiple_conflicts_scenario,
    generate_random_traffic
)
from algorithms.divide_and_conquer import detect_conflicts_divide_and_conquer
from algorithms.brute_force import detect_conflicts_brute_force


class TestDivideAndConquerAlgorithm(unittest.TestCase):
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

    def test_empty_aircraft_list(self):
        conflicts, comparisons, tracer = detect_conflicts_divide_and_conquer([], self.config, record_steps=True)
        self.assertEqual(len(conflicts), 0)
        self.assertEqual(comparisons, 0)
        self.assertIsNotNone(tracer)

    def test_single_aircraft(self):
        ac = Aircraft("SOLO-1", x=0.0, y=0.0, altitude=10.0, vx=0.2, vy=0.0)
        conflicts, comparisons, tracer = detect_conflicts_divide_and_conquer([ac], self.config, record_steps=True)
        self.assertEqual(len(conflicts), 0)
        self.assertEqual(comparisons, 0)

    def test_cross_boundary_conflict_detected(self):
        """CRITICAL TEST: Ensures that aircraft on opposite sides of the median
        dividing line are correctly identified during the combine/strip phase!
        """
        # Aircraft arranged such that X-split will fall exactly between X = -5 and X = +5.
        # AC_L is at -5 km heading East (+X) at 0.20 km/s
        # AC_R is at +5 km heading West (-X) at 0.20 km/s
        # They will collide at X = 0 at t = 25 seconds!
        aircraft = [
            Aircraft("FAR_LEFT", x=-50.0, y=20.0, altitude=10.0, vx=0.1, vy=0.0),
            Aircraft("AC_L", x=-5.0, y=0.0, altitude=10.0, vx=0.20, vy=0.0),
            Aircraft("AC_R", x=5.0, y=0.0, altitude=10.0, vx=-0.20, vy=0.0),
            Aircraft("FAR_RIGHT", x=50.0, y=-20.0, altitude=10.0, vx=-0.1, vy=0.0),
        ]
        
        conflicts, comparisons, tracer = detect_conflicts_divide_and_conquer(aircraft, self.config, record_steps=True)
        
        # Verify that AC_L and AC_R are detected as a HIGH threat conflict
        conflict_keys = [c.pair_key for c in conflicts]
        self.assertIn(("AC_L", "AC_R"), conflict_keys)
        
        cross_conflict = next(c for c in conflicts if c.pair_key == ("AC_L", "AC_R"))
        self.assertEqual(cross_conflict.threat_level, ThreatLevel.HIGH)
        self.assertAlmostEqual(cross_conflict.time_to_closest_approach, 25.0, delta=0.1)

    def test_safe_airspace_scenario(self):
        aircraft = get_safe_airspace_scenario()
        conflicts, _, _ = detect_conflicts_divide_and_conquer(aircraft, self.config)
        self.assertEqual(len(conflicts), 0)

    def test_head_on_scenario(self):
        aircraft = get_head_on_scenario()
        conflicts, _, _ = detect_conflicts_divide_and_conquer(aircraft, self.config)
        self.assertGreaterEqual(len(conflicts), 1)
        self.assertTrue(any(c.pair_key == ("AI-101", "UA-202") for c in conflicts))

    def test_crossing_scenario(self):
        aircraft = get_crossing_scenario()
        conflicts, _, _ = detect_conflicts_divide_and_conquer(aircraft, self.config)
        self.assertGreaterEqual(len(conflicts), 1)
        self.assertTrue(any(c.pair_key == ("BA-505", "DL-404") for c in conflicts))

    def test_multiple_conflicts_scenario(self):
        aircraft = get_multiple_conflicts_scenario()
        conflicts, _, _ = detect_conflicts_divide_and_conquer(aircraft, self.config)
        self.assertGreaterEqual(len(conflicts), 3)
        keys = [c.pair_key for c in conflicts]
        self.assertIn(("AF-111", "LH-222"), keys)
        self.assertIn(("EK-444", "SQ-333"), keys)
        self.assertIn(("CX-666", "QR-555"), keys)  # Cross-boundary pair!

    def test_repeatability_of_fixed_seed(self):
        traffic_1 = generate_random_traffic(count=12, seed=12345)
        traffic_2 = generate_random_traffic(count=12, seed=12345)
        
        self.assertEqual(len(traffic_1), len(traffic_2))
        for a, b in zip(traffic_1, traffic_2):
            self.assertEqual(a.id, b.id)
            self.assertEqual(a.x, b.x)
            self.assertEqual(a.y, b.y)
            self.assertEqual(a.vx, b.vx)
            self.assertEqual(a.vy, b.vy)

    def test_cross_validation_against_brute_force_exhaustive(self):
        """Cross-validates Divide & Conquer against brute force across multiple seeds.
        Confirms 100% equivalence of detected conflict pairs!
        """
        for seed in [11, 42, 99, 101, 777]:
            traffic = generate_random_traffic(count=14, seed=seed)
            
            # Ground truth from brute force
            bf_conflicts, bf_comps = detect_conflicts_brute_force(traffic, self.config)
            
            # Divide & conquer execution
            dac_conflicts, dac_comps, _ = detect_conflicts_divide_and_conquer(traffic, self.config)
            
            bf_keys = sorted([c.pair_key for c in bf_conflicts])
            dac_keys = sorted([c.pair_key for c in dac_conflicts])
            
            self.assertEqual(
                dac_keys, bf_keys,
                f"Seed {seed}: Divide & Conquer conflict keys {dac_keys} do not match Brute Force {bf_keys}!"
            )
            
            for c_dac, c_bf in zip(dac_conflicts, bf_conflicts):
                self.assertEqual(c_dac.pair_key, c_bf.pair_key)
                self.assertEqual(c_dac.threat_level, c_bf.threat_level)
                self.assertAlmostEqual(c_dac.time_to_closest_approach, c_bf.time_to_closest_approach, delta=0.01)
                self.assertAlmostEqual(c_dac.horizontal_separation, c_bf.horizontal_separation, delta=0.01)


if __name__ == "__main__":
    unittest.main()
