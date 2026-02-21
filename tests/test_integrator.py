import numpy as np
import sys
import os
import pytest

sys.path.append(os.path.abspath("."))

from lincore.core.integrator import rk45_step, velocity_verlet_step
from lincore.forces.gravity import two_body_gravity, MU_EARTH


def dynamics_rk(t, y):
    r = y[:3]
    v = y[3:]
    acc = two_body_gravity(r, MU_EARTH)
    return np.concatenate((v, acc))


def dynamics_verlet(t, r, v):
    return two_body_gravity(r, MU_EARTH)


def test_integrator_comparison():
    """
    Test Case 8: Integrator Validation
    Compare RK45 and Symplectic (Verlet).
    """
    print("\nTesting Integrator Comparison...")
    r0 = np.array([7000.0, 0, 0])
    v_mag = np.sqrt(MU_EARTH / 7000.0)
    v0 = np.array([0, v_mag, 0])

    y = np.concatenate((r0, v0))
    t = 0
    dt = 10.0
    duration = 6000.0  # ~1 Orbit

    # RK45
    y_rk = y.copy()
    t_rk = 0.0
    while t_rk < duration:
        step = min(dt, duration - t_rk)
        success, t_next, y_next, dt_next = rk45_step(dynamics_rk, t_rk, y_rk, step, 1e-9)
        if success:
            t_rk = t_next
            y_rk = y_next
        dt = dt_next  # Adaptive
        if dt < 1e-3:
            dt = 1e-3

    # Symplectic
    r_ver = r0.copy()
    v_ver = v0.copy()
    t_ver = 0.0
    dt_ver = 1.0  # Fixed step for Symplectic
    steps = int(duration / dt_ver)

    for _ in range(steps):
        r_ver, v_ver = velocity_verlet_step(dynamics_verlet, t_ver, r_ver, v_ver, dt_ver)
        t_ver += dt_ver

    # Compare Final State
    diff_r = np.linalg.norm(y_rk[:3] - r_ver)
    print(f"Difference (RK45 vs Verlet): {diff_r:.4f} km")

    # They won't be identical, but should be close.
    # RK45 is high precision. Verlet is lower order but stable.
    # 6000 steps of Verlet. error ~ dt^2 * N = 1^2 * 6000? No.
    # Expect match within 1 km or so for LEO.
    assert diff_r < 10.0, f"Integrators diverge too much: {diff_r} km"


def test_numerical_convergence():
    """
    Test Case 9: Numerical Convergence (dt, dt/2, dt/4)
    Using basic RK4 (embedded in RK45 mechanism or similar manual loop) or Verlet.
    Let's use Verlet which is 2nd order. Error should scale by 4.
    """
    print("\nTesting Numerical Convergence (Verlet 2nd Order)...")
    r0 = np.array([7000.0, 0, 0])
    v_mag = np.sqrt(MU_EARTH / 7000.0)
    v0 = np.array([0, v_mag, 0])
    duration = 100.0

    def run_verlet(dt):
        r = r0.copy()
        v = v0.copy()
        t = 0
        steps = int(duration / dt)
        for _ in range(steps):
            r, v = velocity_verlet_step(dynamics_verlet, t, r, v, dt)
        return r, v

    # Reference (very small step)
    r_ref, _ = run_verlet(0.01)

    dt1 = 1.0
    dt2 = 0.5
    dt4 = 0.25

    r1, _ = run_verlet(dt1)
    r2, _ = run_verlet(dt2)
    r4, _ = run_verlet(dt4)

    eff1 = np.linalg.norm(r1 - r_ref)
    eff2 = np.linalg.norm(r2 - r_ref)
    eff4 = np.linalg.norm(r4 - r_ref)

    print(f"Error dt={dt1}: {eff1:.6e}")
    print(f"Error dt={dt2}: {eff2:.6e}")
    print(f"Error dt={dt4}: {eff4:.6e}")

    # 2nd Order: Error ~ dt^2.
    # Halving dt -> Error / 4.
    ratio1 = eff1 / eff2
    ratio2 = eff2 / eff4

    print(f"Ratio 1 (Expect ~4): {ratio1:.2f}")
    print(f"Ratio 2 (Expect ~4): {ratio2:.2f}")

    assert ratio1 > 3.0 and ratio1 < 5.0
    assert ratio2 > 3.0 and ratio2 < 5.0


if __name__ == "__main__":
    test_integrator_comparison()
    test_numerical_convergence()
