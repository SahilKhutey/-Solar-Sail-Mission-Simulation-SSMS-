import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import numpy as np
import matplotlib.pyplot as plt
from lincore.mission.pipeline import SolarSailMission
from multiprocessing import Pool, cpu_count


def run_single_case(seed, base_config):
    """
    Run a single Monte Carlo case.
    """
    # Perturb config based on seed
    rng = np.random.default_rng(seed)

    config = base_config.copy()
    # Deep copy needed? distinct dicts for top level is usually enough if we replace sub-dicts
    # But safer to copy deeper for physics params
    import copy

    config = copy.deepcopy(base_config)

    # Perturb Mass (+/- 5%)
    mass_nom = config["spacecraft"]["mass"]
    config["spacecraft"]["mass"] = mass_nom * rng.uniform(0.95, 1.05)

    # Perturb Area (+/- 1%)
    area_nom = config["spacecraft"]["sail_area"]
    config["spacecraft"]["sail_area"] = area_nom * rng.uniform(0.99, 1.01)

    # Perturb Reflectivity (+/- 2%)
    refl_nom = config["spacecraft"]["reflectivity"]
    config["spacecraft"]["reflectivity"] = np.clip(refl_nom * rng.uniform(0.98, 1.02), 0, 1)

    # Run
    mission = SolarSailMission(config)

    # Run for duration
    duration = config["mission"]["duration_days"]
    dt = config["mission"]["step_size"]
    steps = int(duration * 86400 / dt)

    for _ in range(steps):
        mission.step()

    # Return Final State (r, v)
    return mission.state.r, mission.state.v


def run_monte_carlo(n_cases=50):
    print(f"Running {n_cases} Monte Carlo cases...")

    base_config = {
        "mission": {"duration_days": 1.0, "step_size": 60.0},  # 1 day run
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
        "output": {"log_file": "mc_void.csv"},  # Don't log or /dev/null
    }

    seeds = [i for i in range(n_cases)]

    # Serial for now to be safe with file/imports, or Pool
    results = []
    for seed in seeds:
        res = run_single_case(seed, base_config)
        results.append(res)
        if seed % 10 == 0:
            print(f"Case {seed} done.")

    # Analyse
    r_finals = np.array([res[0] for res in results])

    # Plot Dispersion (Projected on Orbit Plane? or just 3D Scatter)
    # LEO: Plot Altitude vs Latitude? Or In-Track vs Cross-Track?
    # Simple: X vs Y

    plt.figure(figsize=(10, 6))
    plt.scatter(r_finals[:, 0], r_finals[:, 1], alpha=0.6, edgecolors="w")
    plt.title(f"Monte Carlo Dispersion (N={n_cases}) - Final Position")
    plt.xlabel("X [km]")
    plt.ylabel("Y [km]")
    plt.grid(True)

    out_file = "monte_carlo_results.png"
    plt.savefig(out_file)
    print(f"Saved plot to {out_file}")

    # Stats
    mean_r = np.mean(r_finals, axis=0)
    std_r = np.std(r_finals, axis=0)
    print(f"Mean Final Position: {mean_r}")
    print(f"Std Dev Position: {std_r}")


if __name__ == "__main__":
    run_monte_carlo(10)  # Test with 10
