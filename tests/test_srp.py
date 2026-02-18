import numpy as np
import sys
import os

sys.path.append(os.path.abspath('.'))

from lincore.forces.srp import solar_pressure, P_SOLAR, AU, C_LIGHT, R_EARTH
from lincore.attitude.quaternion import quat_rotate

def test_srp_magnitude():
    """
    Test Case 3: SRP Magnitude
    At 1 AU, idealized flat plate facing sun.
    acc = P * A / m / c * (1+rho)
    """
    print("\nTesting SRP Magnitude...")
    r = np.array([AU, 0, 0])
    q = np.array([1, 0, 0, 0]) # Identity (Z aligned with Z?)
    # In srp.py: n_body = [0,0,1]. Identity q -> n_eci=[0,0,1].
    # Sun vector s_hat = [1,0,0].
    # n . (-s) = [0,0,1] . [-1,0,0] = 0.
    # So identity attitude is edge-on to sun at [AU, 0, 0].
    
    # We need n to point to Sun (-X).
    # Rotate +Z to -X. Rotation -90 deg (-pi/2) about Y axis.
    # q = [cos(-45), 0, sin(-45), 0] = [0.707, 0, -0.707, 0]
    angle = -np.pi/2
    q_face = np.array([np.cos(angle/2), 0, np.sin(angle/2), 0])
    
    mass = 1000.0 # kg
    area = 100.0 # m^2
    refl = 1.0
    
    # Disable shadow check by t=-1
    acc = solar_pressure(r, q_face, mass, area, refl, t=-1.0)
    acc_mag = np.linalg.norm(acc) * 1000.0 # Convert km/s^2 back to m/s^2
    
    # Analytical
    # Acc = P * A / m * (1+rho) / c 
    # Wait, srp.py logic: (flux * area / (mass * c)) * (1+rho) * cos^2(theta)
    # flux = P * (1/1)^2 = P
    # cos(theta) = 1
    
    expected = (P_SOLAR * area / (mass * (C_LIGHT * 1000))) * (1 + refl)
    
    error = abs((acc_mag - expected) / expected)
    print(f"SRP Magnitude Error: {error*100:.4f}%")
    assert error < 0.01

def test_srp_angle():
    """
    Test Case 3 (Angle): 90 deg incidence -> 0 acceleration.
    """
    print("Testing SRP Angle Cutoff...")
    r = np.array([AU, 0, 0])
    # Face +Z (Identity q)
    # Sun is at +X (relative). Light comes from -X.
    # Normal (+Z) is perp to Light (-X).
    # cos(theta) = 0.
    q = np.array([1, 0, 0, 0])
    
    acc = solar_pressure(r, q, 1000, 100, 1.0, t=-1.0)
    acc_mag = np.linalg.norm(acc)
    
    print(f"SRP at 90 deg: {acc_mag} (Expect 0.0)")
    assert acc_mag < 1e-15

def test_eclipse_model():
    """
    Test Case 4: Eclipse Model
    1. Behind Earth -> 0
    2. Side -> Full
    """
    print("Testing Eclipse Model...")
    # Earth at [AU, 0, 0] approx for test logic
    # But srp.py usually calls get_body_state for Earth.
    # To test srp.py in isolation with dynamic Earth, we need to know where Earth IS at t=0.
    # 'ephemeris.py' analytical model: Earth at [AU, 0, 0] at t=0.
    # So we place SC at [1.01 AU, 0, 0].
    
    r_shadow = np.array([1.01 * AU, 0, 0])
    q = np.array([0.707, 0, -0.707, 0]) # Face sun
    
    # We need to mock get_body_state or ensure t=0 puts Earth at [AU,0,0]
    # In analytical model: angle = 0 at t=0. Correct.
    
    # Debug Earth Position
    from lincore.environment.ephemeris import get_body_state
    r_earth_internal = get_body_state('earth', 0.0)[:3]
    print(f"DEBUG: Internal Earth Pos: {r_earth_internal}")
    print(f"DEBUG: SC Pos: {r_shadow}")
    
    acc_shadow = solar_pressure(r_shadow, q, 1000, 100, 1.0, t=0.0)
    mag_shadow = np.linalg.norm(acc_shadow)
    
    print(f"SRP in Shadow: {mag_shadow} (Expect 0.0)")
    assert mag_shadow == 0.0
    
    # Move sideways 2*R_EARTH
    r_light = np.array([1.01 * AU, 2*R_EARTH, 0])
    acc_light = solar_pressure(r_light, q, 1000, 100, 1.0, t=0.0)
    mag_light = np.linalg.norm(acc_light)
    
    print(f"SRP in Light: {mag_light} (Expect > 0)")
    assert mag_light > 0.0

if __name__ == "__main__":
    test_srp_magnitude()
    test_srp_angle()
    test_eclipse_model()
