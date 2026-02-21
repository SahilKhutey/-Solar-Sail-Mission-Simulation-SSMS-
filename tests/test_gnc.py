import sys
import os
import numpy as np

# Add project root
sys.path.append(os.path.abspath("."))

from lincore.mission.pipeline import SolarSailMission
from lincore.core.state import State


def test_closed_loop_gnc():
    print("Testing Closed-Loop GNC...")

    config = {
        "mission": {"duration_days": 0.05, "step_size": 10.0},  # Short run ~1 hour
        "spacecraft": {
            "mass": 10,
            "sail_area": 100,
            "reflectivity": 0.9,
            "inertia": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        },
        "orbit": {"type": "LEO", "altitude_km": 700.0, "inclination_deg": 0.0},
        "physics": {
            "gravity_model": "two_body",
            "perturbations": {},
            "navigation": True,  # ENABLE GNC
        },
        "navigation": {
            "position_noise_km": 0.001,  # 1m
            "velocity_noise_kms": 0.0001,
            "attitude_noise_deg": 0.01,
            "rate_noise_deg_s": 0.001,
        },
        "output": {"log_file": "test_gnc.csv"},
    }

    mission = SolarSailMission(config)

    # Run loop manually to check internals
    steps = 100
    errors_r = []

    print(f"Initial State: {mission.state.r}")

    for i in range(steps):
        t, state = mission.step()

        # Access internals
        true_r = mission.state.r
        est_r = mission.ekf.x[0:3]

        err = np.linalg.norm(true_r - est_r)
        errors_r.append(err)

    avg_err = np.mean(errors_r)
    max_err = np.max(errors_r)

    print(f"Avg Position Error: {avg_err*1000:.3f} m")
    print(f"Max Position Error: {max_err*1000:.3f} m")

    # Expect convergence or low error (initially perfect match)
    # With 1m noise, error should be around 1m or less (filtering)
    assert avg_err < 0.010  # 10m tolerance (generous)

    print("GNC Test Passed.")


if __name__ == "__main__":
    test_closed_loop_gnc()
