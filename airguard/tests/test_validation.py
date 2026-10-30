import unittest
from models.aircraft import Aircraft, AircraftValidationError
from algorithms.divide_and_conquer import validate_aircraft_dataset


class TestValidationAndEdgeCases(unittest.TestCase):
    def test_valid_aircraft_creation(self):
        ac = Aircraft("AG-101", x=12.5, y=-34.2, altitude=10.5, vx=0.22, vy=-0.15, callsign="COMMERCIAL")
        self.assertEqual(ac.id, "AG-101")
        self.assertAlmostEqual(ac.x, 12.5)
        self.assertAlmostEqual(ac.y, -34.2)

    def test_negative_coordinates_accepted(self):
        """Negative spatial coordinates are valid in Cartesian airspace."""
        ac = Aircraft("NEG-1", x=-45.0, y=-60.0, altitude=9.0, vx=-0.2, vy=-0.1)
        self.assertEqual(ac.x, -45.0)
        self.assertEqual(ac.y, -60.0)

    def test_empty_or_whitespace_id_rejected(self):
        with self.assertRaises(AircraftValidationError):
            Aircraft("", x=0.0, y=0.0, altitude=10.0, vx=0.1, vy=0.1)
        with self.assertRaises(AircraftValidationError):
            Aircraft("   ", x=0.0, y=0.0, altitude=10.0, vx=0.1, vy=0.1)

    def test_negative_altitude_rejected(self):
        with self.assertRaises(AircraftValidationError):
            Aircraft("CRASH-1", x=0.0, y=0.0, altitude=-1.5, vx=0.1, vy=0.1)

    def test_non_numeric_coordinates_rejected(self):
        with self.assertRaises(AircraftValidationError):
            Aircraft("BAD-X", x="invalid", y=0.0, altitude=10.0, vx=0.1, vy=0.1)

    def test_nan_coordinates_rejected(self):
        with self.assertRaises(AircraftValidationError):
            Aircraft("NAN-1", x=float('nan'), y=0.0, altitude=10.0, vx=0.1, vy=0.1)

    def test_duplicate_aircraft_ids_rejected(self):
        dataset = [
            Aircraft("DUP-1", x=0.0, y=0.0, altitude=10.0, vx=0.1, vy=0.1),
            Aircraft("DUP-2", x=10.0, y=10.0, altitude=10.0, vx=-0.1, vy=-0.1),
            Aircraft("DUP-1", x=20.0, y=20.0, altitude=11.0, vx=0.2, vy=0.0),
        ]
        with self.assertRaises(AircraftValidationError) as ctx:
            validate_aircraft_dataset(dataset)
        self.assertIn("Duplicate aircraft ID", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
