from lincore.utils.jit import num_jit
import numpy as np

MU_EARTH = 398600.4418  # km^3/s^2


@num_jit
def two_body_gravity(r, mu):
    """
    Basic 2-body acceleration: -mu/r^3 * r
    """
    r_mag = np.linalg.norm(r)
    if r_mag == 0:
        return np.zeros(3)
    return -mu * r / r_mag**3


def multi_body_gravity(r, t):
    """
    Multi-body gravity acceleration (Sun + Earth + Mars).
    Assumes r is Heliocentric position.
    """
    acc = np.zeros(3)

    # 1. Sun (Central)
    acc += two_body_gravity(r, MU_SUN)

    # 2. Earth Perturbation
    r_earth = get_body_state("earth", t)[:3]
    r_rel_earth = r - r_earth
    d_earth = np.linalg.norm(r_rel_earth)

    # Direct gravitational pull from Earth
    acc += -MU_EARTH * r_rel_earth / d_earth**3

    # 3. Mars Perturbation
    r_mars = get_body_state("mars", t)[:3]
    r_rel_mars = r - r_mars
    d_mars = np.linalg.norm(r_rel_mars)

    acc += -42828.37 * r_rel_mars / d_mars**3

    return acc
