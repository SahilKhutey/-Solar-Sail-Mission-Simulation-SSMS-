import numpy as np
import sys
import os
sys.path.append(os.path.abspath('.'))

from lincore.forces.gravity import two_body_gravity, MU_EARTH
from lincore.core.integrator import rk45_step

def debug_gauss():
    print("Debugging Gauss Eq...")
    r_mag = 7000.0
    v_mag = np.sqrt(MU_EARTH / r_mag) # ~7.546 km/s
    
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])
    y = np.concatenate((r0, v0))
    
    T_acc = 1e-6
    
    a_start = -MU_EARTH / (v_mag**2 - 2*MU_EARTH/r_mag)
    # Check a_start
    print(f"a_start: {a_start:.4f} (Expect 7000)")
    
    # Analytical Rate
    da_dt_anal = 2 * a_start**2 * v_mag * T_acc / MU_EARTH
    print(f"da/dt Anal: {da_dt_anal:.6e}")
    
    def dynamics(t, y):
        r = y[:3]
        v = y[3:]
        acc = two_body_gravity(r, MU_EARTH)
        # Tangential Thrust
        v_norm = np.linalg.norm(v)
        acc += T_acc * (v / v_norm)
        return np.concatenate((v, acc))

    # Run for very short time to approach instantaneous rate
    dt_test = 1.0 
    _, t, y_next, _ = rk45_step(dynamics, 0, y, dt_test, 1e-12)
    
    r_next = y_next[:3]
    v_next = y_next[3:]
    v_mag_next = np.linalg.norm(v_next)
    r_mag_next = np.linalg.norm(r_next)
    
    a_next = -MU_EARTH / (v_mag_next**2 - 2*MU_EARTH/r_mag_next)
    
    da = a_next - a_start
    da_dt_num = da / dt_test
    
    print(f"da/dt Num (dt={dt_test}): {da_dt_num:.6e}")
    
    ratio = da_dt_num / da_dt_anal
    print(f"Ratio: {ratio:.2f}")

if __name__ == "__main__":
    debug_gauss()
