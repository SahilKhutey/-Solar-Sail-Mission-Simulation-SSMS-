import sys
import os
import numpy as np

# Add parent path
sys.path.append(os.path.abspath("."))

from lincore.forces.srp import conical_shadow, R_EARTH
from lincore.environment.ephemeris import get_body_state, AU
from lincore.core.integrator import velocity_verlet_step


def test_shadow():
    print("\nTesting Shadow Model...")
    r_earth = np.array([AU, 0, 0])

    # 1. Full Sun (In front of Earth)
    r_sc_sun = np.array([0.9 * AU, 0, 0])
    nu = conical_shadow(r_sc_sun, r_earth, R_EARTH)
    print(f"In Front (Expect 1.0): {nu}")

    # 2. Deep Shadow (Behind Earth)
    r_sc_shadow = np.array([1.01 * AU, 0, 0])  # 1% AU behind Earth?
    # Earth is at 1.0 AU. SC at 1.01 AU.
    # Distance from Sun-Earth line is 0.
    # Should be in shadow.
    nu = conical_shadow(r_sc_shadow, r_earth, R_EARTH)
    print(f"Behind Earth (Expect 0.0): {nu}")

    # 3. Penumbra/Side (Just outside radius)
    # Earth Radius ~6400 km.
    offset = R_EARTH * 2.0
    r_sc_side = np.array([1.01 * AU, offset, 0])
    nu = conical_shadow(r_sc_side, r_earth, R_EARTH)
    print(f"Side (Expect 1.0): {nu}")


def test_ephemeris():
    print("\nTesting Ephemeris Fallback...")
    t = 0.0
    state = get_body_state("earth", t)
    r_mag = np.linalg.norm(state[:3])
    print(f"Earth Radius at t=0: {r_mag/AU:.4f} AU (Expect ~1.0)")

    state_mars = get_body_state("mars", t)
    r_mag_mars = np.linalg.norm(state_mars[:3])
    print(f"Mars Radius at t=0: {r_mag_mars/AU:.4f} AU (Expect ~1.524)")


def harmonic_oscillator_acc(t, r, v):
    # a = -k*x. Let k=1.
    return -r


def test_verlet():
    print("\nTesting Velocity Verlet...")
    r = np.array([1.0])
    v = np.array([0.0])
    dt = 0.1
    steps = 100

    # Integrate for 10 seconds (approx 1.5 periods)
    history_r = []

    for i in range(steps):
        r, v = velocity_verlet_step(harmonic_oscillator_acc, 0, r, v, dt)
        history_r.append(r[0])

    print(f"Final r: {r[0]:.4f}")
    # Energy check? 0.5*v^2 + 0.5*r^2 should be constant 0.5
    energy = 0.5 * v[0] ** 2 + 0.5 * r[0] ** 2
    print(f"Final Energy: {energy:.6f} (Expect 0.5)")


if __name__ == "__main__":
    test_shadow()
    test_ephemeris()
    test_verlet()
