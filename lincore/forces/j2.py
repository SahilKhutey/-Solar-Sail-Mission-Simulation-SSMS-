import numpy as np

MU_EARTH = 398600.4418  # km^3/s^2
R_EARTH = 6378.137  # km
J2_EARTH = 1.08263e-3


def j2_perturbation(r_geo):
    """
    J2 Perturbation acceleration (Earth specific).
    Must pass r relative to Earth (r_geo).
    """
    r = np.linalg.norm(r_geo)
    if r < R_EARTH + 100:  # Below surface/atmosphere check
        return np.zeros(3)

    x, y, z = r_geo

    factor = (3 / 2) * J2_EARTH * MU_EARTH * (R_EARTH**2) / (r**5)

    z2 = z**2
    r2 = r**2

    ax = factor * x * (5 * z2 / r2 - 1)
    ay = factor * y * (5 * z2 / r2 - 1)
    az = factor * z * (5 * z2 / r2 - 3)

    return np.array([ax, ay, az])
