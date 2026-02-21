import math
import numpy as np
from .orbital_elements import state_to_elements, get_rsw_frame


def gauss_guidance_acceleration(state, desired_rates, mu):
    """
    Computes required RSW acceleration to achieve desired orbital element rates.
    """
    # 1. Get Elements
    els = state_to_elements(state, mu)
    a = els["a"]
    e = els["e"]
    i = els["i"]
    n = els["n"]
    p = els["p"]
    f = els["f"]  # True Anomaly
    u = els["u"]  # Argument of Latitude
    r = state[:3]
    r_mag = np.linalg.norm(r)
    h = math.sqrt(mu * p)

    target_da = desired_rates.get("a", 0.0)
    target_di = desired_rates.get("i", 0.0)

    # da/dt = ... at
    term_sqrt = math.sqrt(1 - e**2) if e < 1.0 else 1.0

    if n > 1e-9 and term_sqrt > 1e-9 and r_mag > 0:
        coeff_at = (2.0 * p) / (n * term_sqrt * r_mag)
        at = target_da / coeff_at
    else:
        at = 0.0

    ar = 0.0

    # di/dt = ... an
    if h > 1e-9:
        coeff_an = (r_mag * math.cos(u)) / h
        if abs(coeff_an) > 1e-6:
            an = target_di / coeff_an
        else:
            an = 0.0
    else:
        an = 0.0

    return ar, at, an


def get_desired_normal(state, desired_rates, mu):
    """
    computes n_des (inertial) for Gauss Control.
    """
    ar, at, an = gauss_guidance_acceleration(state, desired_rates, mu)

    r_hat, s_hat, w_hat = get_rsw_frame(state)

    acc_des = ar * r_hat + at * s_hat + an * w_hat
    norm_acc = np.linalg.norm(acc_des)

    if norm_acc < 1e-12:
        return r_hat  # Default

    return acc_des / norm_acc
