import math
import numpy as np

MU_EARTH = 398600.4418


def get_rsw_frame(state):
    """
    Returns the Radial-Transverse-Normal (RSW) frame unit vectors.
    R: Radial (along position vector)
    W: Normal (along angular momentum)
    S: Transverse (WxR, completes triad)
    """
    r_vec = np.array(state[:3])
    v_vec = np.array(state[3:6])

    r_mag = np.linalg.norm(r_vec)
    h_vec = np.cross(r_vec, v_vec)
    h_mag = np.linalg.norm(h_vec)

    if r_mag == 0 or h_mag == 0:
        return np.eye(3)  # Identity as fallback

    r_hat = r_vec / r_mag
    w_hat = h_vec / h_mag
    s_hat = np.cross(w_hat, r_hat)

    return r_hat, s_hat, w_hat


def state_to_elements(state, mu=MU_EARTH):
    """
    Convert state vector [r, v] to Keplerian elements.
    """
    r = np.array(state[:3])
    v = np.array(state[3:6])

    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)

    h = np.cross(r, v)
    h_mag = np.linalg.norm(h)

    # Node vector
    k = np.array([0, 0, 1])
    n = np.cross(k, h)
    n_mag = np.linalg.norm(n)

    # Eccentricity vector
    e_vec = (np.cross(v, h) / mu) - (r / r_mag)
    e = np.linalg.norm(e_vec)

    # Energy
    energy = v_mag**2 / 2 - mu / r_mag

    if abs(energy) < 1e-9:
        a = float("inf")
    else:
        a = -mu / (2 * energy)

    # Inclination
    i = math.acos(max(-1.0, min(1.0, h[2] / h_mag)))

    # RAAN
    if n_mag != 0:
        RAAN = math.acos(max(-1.0, min(1.0, n[0] / n_mag)))
        if n[1] < 0:
            RAAN = 2 * math.pi - RAAN
    else:
        RAAN = 0

    # Argument of Perigee
    if n_mag != 0 and e > 1e-8:
        val = np.dot(n, e_vec) / (n_mag * e)
        val = max(-1.0, min(1.0, val))
        omega = math.acos(val)
        if e_vec[2] < 0:
            omega = 2 * math.pi - omega
    else:
        omega = 0

    # True Anomaly
    if e > 1e-8:
        val = np.dot(e_vec, r) / (e * r_mag)
        val = max(-1.0, min(1.0, val))
        nu = math.acos(val)
        if np.dot(r, v) < 0:
            nu = 2 * math.pi - nu
    else:
        nu = 0

    # Mean motion
    mean_motion = math.sqrt(mu / a**3) if a > 0 else 0

    # Argument of Latitude u = omega + nu
    u = omega + nu
    if u >= 2 * math.pi:
        u -= 2 * math.pi

    # Semi-latus rectum
    p = a * (1 - e**2) if e < 1.0 else 0  # or h^2/mu

    return {
        "a": a,
        "e": e,
        "i": i,
        "RAAN": RAAN,
        "omega": omega,
        "nu": nu,
        "f": nu,
        "u": u,
        "n": mean_motion,
        "p": p,
    }
