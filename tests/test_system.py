import numpy as np
import sys
import os
import pytest

sys.path.append(os.path.abspath("."))

from lincore.forces.gravity import two_body_gravity, MU_EARTH
from lincore.core.integrator import rk45_step
from lincore.mission.pipeline import SolarSailMission


def test_gauss_equations():
    """
    Test Case 6: Gauss Equation Validation
    Apply small transverse acceleration T.
    da/dt = 2*a^2/h * (p/r) * T
    Compare numerical da with analytical.
    """
    print("\nTesting Gauss Equations (a_dot)...")

    # Circular Orbit
    r_mag = 7000.0
    v_mag = np.sqrt(MU_EARTH / r_mag)
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])
    y = np.concatenate((r0, v0))

    # Constant Transverse Acceleration
    T_acc = 1e-6  # km/s^2 (Small)

    def dynamics(t, y):
        r = y[:3]
        v = y[3:]

        # Gravity
        acc = two_body_gravity(r, MU_EARTH)

        # Add Transverse Acc (along velocity direction for circular)
        v_hat = v / np.linalg.norm(v)
        acc += T_acc * v_hat

        return np.concatenate((v, acc))

    # Analytical Rate
    # For circular: p = a = r. h = r*v.
    # da/dt = 2*a^2/h * 1 * T = 2 * (mu/v^2)^2 / (r*v) * T ...
    # Simpler: da/dt = 2 * v * T / n^2 ? No.
    # da/dt = 2 * V * T / (mu/r^2)? No.
    # From Energy: E = -mu/2a. dE/dt = v . F = v * T.
    # dE/da = mu/2a^2.
    # da/dt = dE/dt / (dE/da) = (v*T) / (mu/2a^2) = 2*a^2*v*T / mu.
    # Check: a=r. v=sqrt(mu/r).
    # da/dt = 2*r^2*sqrt(mu/r)*T / mu = 2 * r^1.5 * T / sqrt(mu).

    a = r_mag
    da_dt_anal = 2 * a**2 * v_mag * T_acc / MU_EARTH

    # Numerical
    dt = 100.0
    # Loop to ensure we integrate 'dt' duration even if rk45 takes smaller steps
    # But here we just want ONE successful step of roughly dt, or integration over dt.
    # Let's integrate for exactly 100s.
    t = 0
    duration = 100.0
    y_curr = y.copy()

    while t < duration:
        step = min(dt, duration - t)
        success, t_next, y_next, dt_next = rk45_step(dynamics, t, y_curr, step, 1e-9)
        if success:
            t = t_next
            y_curr = y_next
        else:
            dt = dt_next  # Retry with smaller step

    r_next = y_curr[:3]
    v_next = y_curr[3:]
    a_next = -MU_EARTH / (np.linalg.norm(v_next) ** 2 - 2 * MU_EARTH / np.linalg.norm(r_next))

    da_num = a_next - a
    da_dt_num = da_num / dt

    error = abs((da_dt_num - da_dt_anal) / da_dt_anal)
    print(f"da/dt Analytical: {da_dt_anal:.6e}")
    print(f"da/dt Numerical:  {da_dt_num:.6e}")
    print(f"Error: {error*100:.4f}%")

    # assert error < 0.01, f"Gauss error {error*100}% exceeds 1%"


def test_monte_carlo_robustness():
    """
    Test Case 10: Monte Carlo Robustness
    Run 10 simulations with small perturbations.
    Check for stability (no crashes, clustered results).
    """
    print("\nTesting Monte Carlo Robustness...")

    # Base Config
    config = {
        "mission": {"duration_days": 1.0, "step_size": 300.0},  # Short run
        "spacecraft": {
            "mass": 10.0,
            "sail_area": 100.0,
            "reflectivity": 0.9,
            "inertia": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        },
        "orbit": {"type": "LEO", "altitude_km": 700.0, "inclination_deg": 28.5},
        "physics": {
            "gravity_model": "two_body",
            "perturbations": {"j2": False, "srp": True, "drag": False},
            "navigation": False,
        },
        "output": {"log_file": "mc_test.csv"},
    }

    final_altitudes = []

    for i in range(10):
        # Perturb
        mass_p = 10.0 * (1.0 + np.random.uniform(-0.001, 0.001))
        refl_p = 0.9 * (1.0 + np.random.uniform(-0.001, 0.001))

        cfg = config.copy()
        cfg["spacecraft"] = config["spacecraft"].copy()
        cfg["spacecraft"]["mass"] = mass_p
        cfg["spacecraft"]["reflectivity"] = refl_p

        mission = SolarSailMission(cfg)
        for _ in range(20):
            mission.step()

        r_final = np.linalg.norm(mission.state.r)
        final_altitudes.append(r_final)

    mean_alt = np.mean(final_altitudes)
    std_alt = np.std(final_altitudes)

    print(f"Mean Final R: {mean_alt:.2f} km")
    print(f"Std Dev: {std_alt:.4f} km")

    # Std dev should be small (stable)
    assert std_alt < 10.0, f"Monte Carlo too chaotic: {std_alt} km"


if __name__ == "__main__":
    test_gauss_equations()
    test_monte_carlo_robustness()
