import numpy as np

def state_to_keplerian(r, v, mu):
    """
    Convert state vector (r, v) to Keplerian elements.
    
    Args:
        r (np.ndarray): Position vector [km]
        v (np.ndarray): Velocity vector [km/s]
        mu (float): Gravitational parameter [km^3/s^2]
        
    Returns:
        dict: {
            'a': semi-major axis [km],
            'e': eccentricity magnitude,
            'i': inclination [deg],
            'raan': right ascension of ascending node [deg],
            'arg_p': argument of periapsis [deg],
            'nu': true anomaly [deg],
            'mean_anomaly': mean anomaly [deg],
            'period': orbital period [s],
            'specific_energy': specific mechanical energy [km^2/s^2]
        }
    """
    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)
    
    # Specific Angular Momentum
    h_vec = np.cross(r, v)
    h_mag = np.linalg.norm(h_vec)
    
    # Node Vector (along line of nodes)
    # n = k x h
    k_unit = np.array([0, 0, 1])
    n_vec = np.cross(k_unit, h_vec)
    n_mag = np.linalg.norm(n_vec)
    
    # Eccentricity Vector
    # e = ( (v^2 - mu/r)*r - (r.v)*v ) / mu
    e_vec = ((v_mag**2 - mu/r_mag)*r - np.dot(r, v)*v) / mu
    e = np.linalg.norm(e_vec)
    
    # Specific Energy
    energy = v_mag**2 / 2 - mu / r_mag
    
    # Semi-major Axis
    if abs(energy) < 1e-9:
        a = np.inf # Parabolic
    elif energy < 0:
        a = -mu / (2 * energy) # Elliptic
    else:
        a = -mu / (2 * energy) # Hyperbolic (negative a convention usually)
        
    # Inclination
    i_rad = np.arccos(h_vec[2] / h_mag)
    
    # RAAN (Omega)
    if n_mag != 0:
        raan_rad = np.arccos(n_vec[0] / n_mag)
        if n_vec[1] < 0:
            raan_rad = 2*np.pi - raan_rad
    else:
        raan_rad = 0 # Equatorial orbit
        
    # Argument of Periapsis (omega)
    if n_mag != 0 and e > 1e-9:
        arg_p_rad = np.arccos(np.dot(n_vec, e_vec) / (n_mag * e))
        if e_vec[2] < 0:
            arg_p_rad = 2*np.pi - arg_p_rad
    else:
        arg_p_rad = 0
        
    # True Anomaly (nu)
    if e > 1e-9:
        nu_rad = np.arccos(np.dot(e_vec, r) / (e * r_mag))
        if np.dot(r, v) < 0:
            nu_rad = 2*np.pi - nu_rad
    else:
        # Circular: angle from node? or just u
        nu_rad = 0
        
    # Period (Elliptic only)
    period = 0
    if energy < 0:
        period = 2 * np.pi * np.sqrt(a**3 / mu)
        
    return {
        'a': a,
        'e': e,
        'i': np.degrees(i_rad),
        'raan': np.degrees(raan_rad),
        'arg_p': np.degrees(arg_p_rad),
        'nu': np.degrees(nu_rad),
        'period': period,
        'specific_energy': energy,
        'b': a * np.sqrt(1 - e**2) if e < 1 and energy < 0 else 0
    }
