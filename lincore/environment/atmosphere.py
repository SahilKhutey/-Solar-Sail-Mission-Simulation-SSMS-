import math

# Earth Atmosphere Constants (Exponential Model)
RHO_0 = 1.225  # kg/m^3 (sea level)
H_SCALE = 8.5  # km scale height
R_EARTH = 6378.137  # km


def get_density(r_mag):
    """
    Returns atmospheric density in kg/m^3 given geocentric distance r_mag (km).
    """
    altitude = r_mag - R_EARTH

    if altitude > 1000:  # Negligible above 1000km
        return 0.0
    if altitude < 0:
        return RHO_0  # Cap at sea level

    rho = RHO_0 * math.exp(-altitude / H_SCALE)
    return rho
