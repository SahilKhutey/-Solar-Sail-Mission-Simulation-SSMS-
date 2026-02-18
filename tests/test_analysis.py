import numpy as np
import os
import sys

sys.path.append(os.path.abspath('.'))

from lincore.analysis.orbital_elements import state_to_keplerian
from lincore.utils.logger import MissionLogger

def test_orbital_elements():
    print("Testing Orbital Elements Conversion...")
    mu = 398600.4418
    
    # 1. Circular Orbit at 7000 km
    r = np.array([7000.0, 0, 0])
    v_mag = np.sqrt(mu / 7000.0)
    v = np.array([0, v_mag, 0])
    
    els = state_to_keplerian(r, v, mu)
    
    print(f"SMA: {els['a']:.2f} (Expected 7000)")
    print(f"Ecc: {els['e']:.6f} (Expected 0.0)")
    print(f"Inc: {els['i']:.2f} (Expected 0.0)")
    
    assert abs(els['a'] - 7000.0) < 1.0
    assert els['e'] < 1e-6
    
    # 2. Elliptical Orbit
    # Perigee 7000, Apogee 10000
    # a = 8500. e = (10000-7000)/(10000+7000) = 3000/17000 = 0.176
    rp = 7000.0
    ra = 10000.0
    a_ref = (rp + ra) / 2
    e_ref = (ra - rp) / (ra + rp)
    
    # VP (Max Velocity at Perigee)
    # Vis-viva: v^2 = mu(2/r - 1/a)
    vp = np.sqrt(mu * (2/rp - 1/a_ref))
    
    r2 = np.array([rp, 0, 0])
    v2 = np.array([0, vp, 0]) # Perigee passing
    
    els2 = state_to_keplerian(r2, v2, mu)
    
    print(f"SMA 2: {els2['a']:.2f} (Expect {a_ref})")
    print(f"Ecc 2: {els2['e']:.4f} (Expect {e_ref:.4f})")
    
    assert abs(els2['a'] - a_ref) < 1.0
    assert abs(els2['e'] - e_ref) < 1e-4

def test_logger():
    print("Testing MissionLogger...")
    fname = "test_log.csv"
    if os.path.exists(fname): os.remove(fname)
    
    logger = MissionLogger(fname, format='csv', buffer_size=2)
    
    # Log 3 lines
    logger.log_state(0.0, 1.0, np.zeros(14))
    logger.log_state(1.0, 1.0, np.zeros(14))
    logger.log_state(2.0, 1.0, np.zeros(14))
    
    # Flush (buffer size 2 means first 2 flushed, 1 remains)
    logger.close() # Flush output
    
    # Check file
    with open(fname, 'r') as f:
        lines = f.readlines()
        print(f"Log lines: {len(lines)}")
        # Header + 3 data lines = 4 lines
        assert len(lines) == 4
        
    print("Logger Passed.")
    
    # Clean up
    if os.path.exists(fname): os.remove(fname)

if __name__ == "__main__":
    test_orbital_elements()
    test_logger()
