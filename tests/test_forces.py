import numpy as np
import pytest

from lincore.forces.gravity import two_body_gravity
from lincore.forces.drag import atmospheric_drag
from lincore.forces.srp import solar_pressure

def test_exponential_drag():
    """Directly test the drag equation to hit its branches."""
    # Low altitude (e.g. 300km)
    r = np.array([6378.0 + 300.0, 0, 0])
    v = np.array([0, 7.5, 0])
    
    # Test with standard ballistic coeff
    acc1 = atmospheric_drag(r, v, mass=100.0, area=10.0, Cd=2.2)
    assert np.linalg.norm(acc1) > 0.0

    # Test with zero velocity (should be zero drag)
    acc2 = atmospheric_drag(r, np.array([0, 0, 0]), 100, 10, 2.2)
    assert np.linalg.norm(acc2) == 0.0

    # High altitude (>1000km) where atmospheric density is 0
    r_high = np.array([6378.0 + 1500.0, 0, 0])
    acc3 = atmospheric_drag(r_high, v, 100, 10, 2.2)
    assert np.linalg.norm(acc3) == 0.0


def test_two_body_gravity_branches():
    """Test gravity with optional central body mass."""
    r = np.array([7000.0, 0, 0])
    
    # Earth (Default if mu omitted or not, usually passed)
    acc_earth = two_body_gravity(r, mu=398600.4418)
    
    # Sun
    acc_sun = two_body_gravity(r, mu=1.327e11)
    
    assert np.linalg.norm(acc_sun) > np.linalg.norm(acc_earth)


def test_srp_conical_shadow():
    """Test SRP branches and shadow calculations."""
    # Put satellite on the Y-axis so it does not intersect Earth (which is on X-axis at t=0)
    r_sat = np.array([0, 1.5e8, 0]) # 1 AU on Y
    
    # Needs a quaternion pointing the sail at the Sun (-Y direction)
    # Using an arbitrary q here that ensures dot(n, s) > 0
    # Or simply let the test assert norm(acc) since 'q' rotation might yield negative dot if unlucky
    # The default +Z normal rotated by identity [1,0,0,0] is +Z. Sun is -Y. Dot = 0.
    # We must provide a quaternion that aligns +Z axis with the sun vector (-Y).
    # Since r_sat=[0, 1.5e8, 0], s_hat = [0, 1, 0]. Sun vector from sat is [0, -1, 0].
    # We want +Z body -> [0, -1, 0] eci. 
    # A 90 deg rotation around X axis: q = [cos(45), sin(45), 0, 0]
    q_sun_facing = [0.70710678, 0.70710678, 0.0, 0.0]
    
    # Standard Reflection - use t=0 so Ephemeris body positions are loaded
    acc = solar_pressure(r_sat, q=q_sun_facing, mass=10.0, area=100.0, reflectivity=0.9, t=0.0)
    assert np.linalg.norm(acc) > 0.0
