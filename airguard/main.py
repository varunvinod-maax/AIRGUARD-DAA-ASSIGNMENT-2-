"""AirGuard — Divide & Conquer Air Traffic Collision Threat Detector

Design and Analysis of Algorithms (DAA) Assignment 2
Academic Simulation of Airspace Spatial Partitioning and Threat Detection.
"""

import sys
import os

# Ensure project root is in python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.app import AirGuardApp


def main():
    try:
        app = AirGuardApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAirGuard simulation terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running AirGuard: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
