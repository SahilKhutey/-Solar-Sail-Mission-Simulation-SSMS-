import sys
import os
import math
import numpy as np
import pytest

sys.path.append(os.path.abspath('.'))
from lincore.mission.design_tools import HohmannTransfer, LambertSolver, EscapeTimeEstimator
from lincore.forces.gravity import MU_EARTH

def test_hohmann():
    print("Testing Hohmann Transfer...")
    hohmann = HohmannTransfer(MU_EARTH)
    
    # LEO to GEO
    r1 = 6378 + 200
    r2 = 42164.0
    
    dv1, dv2, tof = hohmann.calculate(r1, r2)
    
    # Analytical verification
    # v1 = sqrt(mu/r1) = 7.78
    # vt1 = sqrt(mu(2/r1 - 1/a)) = 10.2
    # dv1 ~ 2.4 km/s
    
    print(f"Delta-V 1: {dv1:.3f} km/s")
    print(f"Delta-V 2: {dv2:.3f} km/s")
    print(f"TOF: {tof/3600:.2f} hrs")
    
    assert 2.0 < dv1 < 3.0
    assert tof > 0

def test_lambert():
    print("Testing Lambert Solver...")
    solver = LambertSolver(MU_EARTH)
    
    r1 = np.array([7000.0, 0, 0])
    # Target: 90 deg away in circular orbit of same radius
    # Transfer time = 1/4 period? No, that's for circular velocity
    # If we want to reach there in T_circ/4, v should be v_circ
    
    period = 2 * math.pi * math.sqrt(7000**3 / MU_EARTH)
    dt = period / 4.0
    r2 = np.array([0, 7000.0, 0])
    
    v1, v2 = solver.solve(r1, r2, dt)
    print(f"V1: {v1}")
    
    # Check if v1 matches circular velocity
    v_circ = math.sqrt(MU_EARTH/7000.0)
    # Velocity at r1 (X axis) should be Y direction
    err = np.linalg.norm(v1 - np.array([0, v_circ, 0]))
    print(f"Error vs Circular: {err:.4f}")
    assert err < 0.1

def test_escape():
    print("Testing Escape Time...")
    est = EscapeTimeEstimator(MU_EARTH, beta=0.05) # light sail
    
    t_days = est.estimate_time(7000.0, 42164.0)
    print(f"Time to GEO: {t_days:.2f} days")
    
    assert t_days > 0

if __name__ == "__main__":
    test_hohmann()
    test_lambert()
    test_escape()
