import numpy as np
import math
from .propulsion import solar_radiation_force

MU_SUN = 1.32712440018e11  # km^3/s^2 (Corrected from e20 for m^3 to match km usage elsewhere if needed, but wait, 1.327e20 m^3/s^2 is correct. 1.327e11 km^3/s^2. The code had e20, likely m^3. I will standardize to km for consistency with eci_two_body)
# Actually, eci_two_body uses km (MU_EARTH = 398600).
# MU_SUN in km^3/s^2 is ~1.327e11.
# The original code had 1.327e20 which is likely m^3/s^2.
# I will stick to km^3/s^2 for consistency across the project as observed in eci_two_body.
MU_SUN = 1.32712440018e11

MU_EARTH = 398600.4418  # km^3 / s^2


def gravity_acceleration(r):
    r_norm = np.linalg.norm(r)
    return -MU_SUN * r / r_norm**3


def two_body(t, state):
    """
    Earth-centered two-body dynamics (Keplerian).
    state: [x, y, z, vx, vy, vz]
    """
    x, y, z, vx, vy, vz = state
    r = math.sqrt(x * x + y * y + z * z)

    ax = -MU_EARTH * x / r**3
    ay = -MU_EARTH * y / r**3
    az = -MU_EARTH * z / r**3

    return [vx, vy, vz, ax, ay, az]


def total_acceleration(state, sail_normal, mass):
    r = state[:3]

    a_grav = gravity_acceleration(r)
    # sail_normal must be numpy array
    a_sail = solar_radiation_force(r, sail_normal) / mass

    return a_grav + a_sail


def translational_derivative(state, sail_normal, mass):
    r_dot = state[3:]
    v_dot = total_acceleration(state, sail_normal, mass)

    return np.concatenate((r_dot, v_dot))
