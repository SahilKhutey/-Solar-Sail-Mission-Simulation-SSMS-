import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath('.'))
from lincore.core.dynamics import DynamicsModel
from lincore.environment.ephemeris import MU_SUN

def test_n_body_integration():
    print("Testing N-Body Gravity Integration...")
    
    config = {
        'mission': {'duration_days': 1.0, 'step_size': 60.0},
        'spacecraft': {'mass': 100, 'sail_area': 100, 'reflectivity': 0.9},
        'orbit': {'type': 'Heliocentric', 'altitude_km': 1.5e8},
        'physics': {
            'gravity_model': 'two_body',
            'perturbations': {
                'n_body': ['EARTH', 'JUPITER'] # Explicit list
            }
        }
    }
    
    dynamics = DynamicsModel(config)
    assert dynamics.n_body is not None
    
    # State: 1 AU on X axis, circular velocity
    r = np.array([1.55e8, 0, 0])
    v = np.array([0, 29.78, 0])
    state = np.concatenate([r, v, [1,0,0,0], [0,0,0]])
    
    # Calc dynamics at t=0
    dy = dynamics(0.0, state)
    acc = dy[3:6]
    
    # Base sun gravity
    acc_sun = -MU_SUN * r / np.linalg.norm(r)**3
    
    # Total acc should differ from acc_sun due to N-Body
    diff = acc - acc_sun
    diff_mag = np.linalg.norm(diff)
    
    print(f"Sun Accel: {acc_sun}")
    print(f"Total Accel: {acc}")
    print(f"N-Body Perturbation: {diff_mag} km/s^2")
    
    assert diff_mag > 0.0
    assert diff_mag < np.linalg.norm(acc_sun) * 0.1 # Should be small perturbation

if __name__ == "__main__":
    test_n_body_integration()
