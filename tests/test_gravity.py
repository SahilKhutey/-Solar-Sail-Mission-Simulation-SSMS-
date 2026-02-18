import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.abspath('.'))

from lincore.forces.gravity import two_body_gravity, MU_EARTH
from lincore.core.integrator import rk45_step

def test_gravity_energy_conservation():
    """
    Test Case 1.A: Energy Conservation for Two-Body Motion
    Acceptable drift: < 1e-6 relative over one orbit.
    """
    # Initial State (LEO Circular-ish)
    r_mag = 7000.0 # km
    v_mag = np.sqrt(MU_EARTH / r_mag)
    r0 = np.array([r_mag, 0.0, 0.0])
    v0 = np.array([0.0, v_mag, 0.0])
    y = np.concatenate((r0, v0))
    t = 0.0
    dt = 10.0
    
    # Dynamics (Gravity Only)
    def dynamics(t, y):
        r = y[:3]
        v = y[3:]
        acc = two_body_gravity(r, MU_EARTH)
        return np.concatenate((v, acc))
    
    # Simulate one period
    period = 2 * np.pi * np.sqrt(r_mag**3 / MU_EARTH)
    steps = int(period / dt)
    
    energies = []
    
    for _ in range(steps):
        # Calculate Energy
        r = y[:3]
        v = y[3:]
        E = 0.5 * np.linalg.norm(v)**2 - MU_EARTH / np.linalg.norm(r)
        energies.append(E)
        
        # Integrate
        _, t, y, _ = rk45_step(dynamics, t, y, dt, 1e-9)
        
    # Check Drift
    E_start = energies[0]
    E_end = energies[-1]
    rel_error = abs((E_end - E_start) / E_start)
    
    print(f"Energy Drift: {rel_error:.2e}")
    assert rel_error < 1e-6, f"Energy drift {rel_error} exceeds 1e-6"

def test_angular_momentum_conservation():
    """
    Test Case 1.B: Angular Momentum Conservation
    h = r x v magnitude must stay constant.
    """
    r_mag = 42164.0 # GEO
    v_mag = np.sqrt(MU_EARTH / r_mag)
    r0 = np.array([r_mag, 0.0, 0.0])
    v0 = np.array([0.0, v_mag * 0.8, 0.0]) # Elliptical
    y = np.concatenate((r0, v0))
    
    def dynamics(t, y):
        r = y[:3]
        v = y[3:]
        acc = two_body_gravity(r, MU_EARTH)
        return np.concatenate((v, acc))
        
    h_start = np.linalg.norm(np.cross(r0, v0))
    
    # Simulate
    for _ in range(100):
        _, _, y, _ = rk45_step(dynamics, 0, y, 60.0, 1e-9)
        
    r_final = y[:3]
    v_final = y[3:]
    h_final = np.linalg.norm(np.cross(r_final, v_final))
    
    rel_error = abs((h_final - h_start) / h_start)
    print(f"H Drift: {rel_error:.2e}")
    assert rel_error < 1e-9

def test_closed_orbit():
    """
    Test Case 1.C: Closed Orbit Test
    After one period, |r_final - r_initial| < tolerance.
    """
    r_mag = 7000.0
    v_mag = np.sqrt(MU_EARTH / r_mag)
    y0 = np.array([r_mag, 0, 0, 0, v_mag, 0])
    
    period = 2 * np.pi * np.sqrt(r_mag**3 / MU_EARTH)
    
    # Precise integration needed
    y = y0.copy()
    t = 0
    dt = 1.0 # Small step
    
    # We step exactly 'period' seconds? RK45 is adaptive, so we step until t >= period
    # Let's enforce fixed steps or use solve_ivp style logic.
    # For this test, let's just run huge number of small steps or use exact updated adaptive logic
    
    def dynamics(t, y):
        r = y[:3]
        v = y[3:]
        acc = two_body_gravity(r, MU_EARTH)
        return np.concatenate((v, acc))
        
    current_t = 0
    while current_t < period:
        step = min(10.0, period - current_t)
        _, current_t, y, _ = rk45_step(dynamics, current_t, y, step, 1e-10)
        
    dist = np.linalg.norm(y[:3] - y0[:3])
    print(f"Closure Error: {dist:.4f} km")
    # Tolerance: 1 meter = 0.001 km
    assert dist < 0.001, f"Orbit did not close within 1m: {dist} km"

if __name__ == "__main__":
    # Manual run
    try:
        test_gravity_energy_conservation()
        test_angular_momentum_conservation()
        test_closed_orbit()
        print("Gravity Tests Passed.")
    except AssertionError as e:
        print(f"Gravity Tests FAILED: {e}")
