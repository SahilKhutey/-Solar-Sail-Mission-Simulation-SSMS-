import cProfile
import pstats
import io
import sys
import os

sys.path.append(os.path.abspath("."))
from lincore.mission.pipeline import SolarSailMission


def benchmark():
    config = {
        "mission": {"duration_days": 100.0, "step_size": 60.0},  # Long run
        "spacecraft": {
            "mass": 10,
            "sail_area": 100,
            "reflectivity": 0.9,
            "inertia": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        },
        "orbit": {"type": "LEO", "altitude_km": 700.0, "inclination_deg": 28.5},
        "physics": {
            "gravity_model": "two_body",
            "perturbations": {"j2": True, "srp": True, "drag": True},
            "navigation": False,
        },
        "navigation": {
            "position_noise_km": 0.01,
            "velocity_noise_kms": 0.001,
            "attitude_noise_deg": 0.01,
            "rate_noise_deg_s": 0.001,
        },
        "output": {"log_file": "profile.csv"},
    }

    print("Initializing Mission for Benchmarking...")
    mission = SolarSailMission(config)

    steps = int(config["mission"]["duration_days"] * 86400 / config["mission"]["step_size"])
    print(f"Running {steps} steps...")

    # Profile the loop
    pr = cProfile.Profile()
    pr.enable()

    for _ in range(steps):
        mission.step()

    pr.disable()

    # Print Stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(20)  # Top 20 time consumers
    print(s.getvalue())


if __name__ == "__main__":
    benchmark()
