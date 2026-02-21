import numpy as np
from lincore.environment.atmosphere import get_density


def atmospheric_drag(r_geo, v_rel, mass, area, Cd):
    """
    Atmospheric Drag Acceleration (Earth).
    r_geo: Position relative to Earth (km)
    v_rel: Velocity relative to Atmosphere/Earth (km/s)
    mass: kg
    area: m^2
    Cd: Drag coefficient
    Returns acceleration in km/s^2
    """
    r_mag = np.linalg.norm(r_geo)
    rho = get_density(r_mag)  # kg/m^3

    if rho <= 0:
        return np.zeros(3)

    v_mag_km_s = np.linalg.norm(v_rel)
    v_mag_m_s = v_mag_km_s * 1000.0

    # Force = 0.5 * rho * v^2 * Cd * Area
    force_mag_N = 0.5 * rho * (v_mag_m_s**2) * Cd * area

    acc_mag_m_s2 = force_mag_N / mass
    acc_mag_km_s2 = acc_mag_m_s2 / 1000.0

    # Direction opposite to velocity
    if v_mag_km_s > 0:
        v_unit = v_rel / v_mag_km_s
    else:
        return np.zeros(3)

    return -acc_mag_km_s2 * v_unit
