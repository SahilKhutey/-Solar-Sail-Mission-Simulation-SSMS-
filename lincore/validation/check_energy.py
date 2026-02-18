import numpy as np
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lincore.core.integrator import rk45_step
from lincore.forces.gravity import two_body_gravity
from lincore.environment.ephemeris import MU_SUN, AU

def dynamics_2body(t, y):
    r = y[:3]
    v = y[3:6]
    acc = two_body_gravity(r, MU_SUN)
    return np.concatenate((v, acc))

def check_energy_conservation():
    print("PHASE 2: Two-Body Gravity Validation")
    print("-------------------------------------")
    
    # Initial State (Circular Orbit at 1 AU)
    r_mag = AU
    v_mag = np.sqrt(MU_SUN / r_mag)
    
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])
    y = np.concatenate((r0, v0))
    
    t = 0.0
    dt = 100.0
    tol = 1e-10 # Strict
    
    period = 2 * np.pi * np.sqrt(r_mag**3 / MU_SUN)
    t_end = period * 2 # 2 orbits
    
    energies = []
    h_mags = []
    times = []
    
    print(f"Integrating for {t_end/86400:.1f} days...")
    
    while t < t_end:
        success, t_next, y_next, dt_next = rk45_step(dynamics_2body, t, y, dt, tol)
        if success:
            t = t_next
            y = y_next
            dt = dt_next
            
            # Energy
            r = y[:3]
            v = y[3:6]
            r_norm = np.linalg.norm(r)
            v_norm = np.linalg.norm(v)
            E = 0.5*v_norm**2 - MU_SUN/r_norm
            
            # Angular Momentum
            h = np.cross(r, v)
            h_norm = np.linalg.norm(h)
            
            energies.append(E)
            h_mags.append(h_norm)
            times.append(t)
            
    # Statistics
    E0 = energies[0]
    H0 = h_mags[0]
    
    dE = [abs(e - E0)/abs(E0) for e in energies]
    dH = [abs(h - H0)/abs(H0) for h in h_mags]
    
    max_dE = max(dE)
    max_dH = max(dH)
    
    print(f"Max Relative Energy Error: {max_dE:.3e}")
    print(f"Max Relative H Error:      {max_dH:.3e}")
    
    if max_dE < 1e-9 and max_dH < 1e-9:
        print("SUCCESS: Conservation laws satisfied.")
    else:
        print("FAILURE: Conservation drift detected.")

if __name__ == "__main__":
    check_energy_conservation()
