import unittest
import sys
import os

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.app import AirGuardApp
from models.scenarios import PRESET_SCENARIOS
from reports.report_generator import generate_assignment_html_report


class TestGUISmokeAndLifecycle(unittest.TestCase):
    def setUp(self):
        # Initialize app
        self.app = AirGuardApp()
        self.app.withdraw()  # Hide window during automated test

    def tearDown(self):
        self.app.destroy()

    def test_app_initialization_and_default_state(self):
        """Ensures app initializes with scenario loaded and radar rendered."""
        self.app.update_idletasks()
        self.assertGreater(len(self.app.aircraft_list), 0)
        self.assertIsNotNone(self.app.tracer)
        self.assertGreater(self.app.tracer.total_steps, 0)

    def test_switch_all_scenarios(self):
        """Switches through all 4 demonstration scenarios and verifies pipeline executes."""
        for scenario_name in PRESET_SCENARIOS.keys():
            self.app.load_scenario(scenario_name)
            self.app.update_idletasks()
            self.assertGreater(len(self.app.aircraft_list), 0)
            self.assertIsNotNone(self.app.tracer)

    def test_step_replay_mechanics(self):
        """Verifies step navigation forwards and backwards through ExecutionTracer."""
        self.app.load_scenario("4. MULTIPLE CONFLICTS (CROSS-BOUNDARY)")
        tot = self.app.tracer.total_steps
        self.assertGreater(tot, 3)

        # Advance 3 steps from 0 -> index should be 3
        for _ in range(3):
            self.app._step_next()
        self.assertEqual(self.app.tracer.current_step_index, 3)

        # Step backwards -> index should be 2
        self.app._step_prev()
        self.assertEqual(self.app.tracer.current_step_index, 2)

        # Run to completion
        self.app._run_to_completion()
        self.assertEqual(self.app.tracer.current_step_index, tot - 1)

        # Reset to start
        self.app._reset_steps()
        self.assertEqual(self.app.tracer.current_step_index, 0)

    def test_report_generation(self):
        """Verifies report generator creates valid HTML with embedded radar base64."""
        self.app.load_scenario("4. MULTIPLE CONFLICTS (CROSS-BOUNDARY)")
        html = generate_assignment_html_report(
            student_info={"name": "Test Student", "roll": "12345"},
            scenario_name=self.app.current_scenario_name,
            aircraft_list=self.app.aircraft_list,
            conflicts=self.app.conflicts,
            config=self.app.config,
            radar_figure=self.app.radar.fig
        )
        self.assertIn("AirGuard — Air Traffic Collision Threat Detector", html)
        self.assertIn("Divide & Conquer", html)
        self.assertIn("data:image/png;base64,", html)


if __name__ == "__main__":
    unittest.main()
