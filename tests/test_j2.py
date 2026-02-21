import numpy as np
import sys
import os

sys.path.append(os.path.abspath("."))

from lincore.forces.gravity import two_body_gravity, MU_EARTH
from lincore.forces.j2 import j2_perturbation, J2_EARTH, R_EARTH
from lincore.core.integrator import rk45_step


def test_j2_nodal_precession():
    """
    Test Case 2: J2 Nodal Precession
    Compare numerical precession rate with analytical formula.
    """
    print("\nTesting J2 Nodal Precession...")

    # 1. Setup Orbit (LEO, high inclination to see precession)
    # Altitude 800 km, inc 98 deg (Sun-Sync approx)
    alt = 800.0
    r_mag = R_EARTH + alt
    v_mag = np.sqrt(MU_EARTH / r_mag)
    inc_deg = 45.0  # Use 45 deg for clear precession
    inc = np.radians(inc_deg)

    # Initial State (Ascending Node at X axis)
    # Position (at crossing node): [r, 0, 0]
    # Velocity: [0, v*cos(i), v*sin(i)]
    r0 = np.array([r_mag, 0.0, 0.0])
    v0 = np.array([0.0, v_mag * np.cos(inc), v_mag * np.sin(inc)])
    y = np.concatenate((r0, v0))

    # Analytical Rate
    # dOmega/dt = -1.5 * n * J2 * (Re/p)^2 * cos(i)
    # Circular: p = a = r
    # n = sqrt(mu / a^3)
    n = np.sqrt(MU_EARTH / r_mag**3)
    p = r_mag

    dOmega_dt_analytic = -1.5 * n * J2_EARTH * (R_EARTH / p) ** 2 * np.cos(inc)
    print(f"Analytical Rate: {dOmega_dt_analytic:.4e} rad/s")
    print(f"                 {np.degrees(dOmega_dt_analytic)*86400:.4f} deg/day")

    # Simulation
    t = 0.0
    dt = 10.0
    orbits = 1.0  # Reduced for speed
    period = 2 * np.pi / n
    duration = orbits * period

    def dynamics(t, y):
        r = y[:3]
        v = y[3:]
        acc = two_body_gravity(r, MU_EARTH) + j2_perturbation(r)
        return np.concatenate((v, acc))

    # Track RAAN (Omega)
    # We can estimate Omega from state vector at each step or just final.
    # Omega = atan2(h_x, -h_y)

    # Integration
    while t < duration:
        step = min(dt, duration - t)
        success, t_next, y_next, dt_next = rk45_step(dynamics, t, y, step, 1e-9)
        if success:
            t = t_next
            y = y_next
        dt = dt_next  # Step update

    # Final State RAAN
    r_final = y[:3]
    v_final = y[3:]
    h = np.cross(r_final, v_final)
    n_vec = np.cross([0, 0, 1], h)  # Node vector
    n_mag = np.linalg.norm(n_vec)

    # RAAN is angle of n_vec in XY plane
    Omega_final = np.arctan2(n_vec[1], n_vec[0])

    # Initial RAAN was 0 (Logic: r=[r,0,0], v=[0,vc,vs] -> h=[0, -r*vs, r*vc].
    # n = k x h = [-1, 0, 0] x [0, -r*vs, r*vc] = [0, r*vs, 0]?
    # Wait, h = [0, -rvs, rvc]. k=[0,0,1].
    # n = [-(-rvs), -(0), 0] = [rvs, 0, 0].
    # So n matches X-axis. Omega = 0. Correct.

    Omega_change = Omega_final  # Modulo check? Small change expected.

    # Numerical Rate
    dOmega_dt_num = Omega_change / t

    error = abs((dOmega_dt_num - dOmega_dt_analytic) / dOmega_dt_analytic)
    print(f"Numerical Rate:  {dOmega_dt_num:.4e} rad/s")
    print(f"Error: {error*100:.4f}%")

    assert error < 0.02, f"J2 Precession error {error*100}% exceeds 2%"


if __name__ == "__main__":
    test_j2_nodal_precession()
