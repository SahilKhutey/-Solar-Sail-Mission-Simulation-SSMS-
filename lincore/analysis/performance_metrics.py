import numpy as np


def calculate_delta_v(force_history, dt, mass):
    """
    Integrate thrust acceleration to get Delta-V.
    Args:
        force_history (list): List of force vectors or magnitudes [N]
        dt (float): Time step in seconds.
        mass (float): Spacecraft mass [kg].
    Returns:
        float: Total Delta-V in m/s.
    """
    # Simply sum(F/m * dt)
    # If force_history contains vectors:
    # dV = integral(|F|/m) dt

    total_dv = 0.0
    for f in force_history:
        f_mag = np.linalg.norm(f)
        acc = f_mag / mass  # m/s^2
        total_dv += acc * dt

    return total_dv


def evaluate_eclipse_fraction(history):
    """
    Calculate percentage of time in eclipse.
    Args:
        history (list of dict): Mission history with 'in_shadow' flag if available.
        Else compute from geometry.
    """
    # Placeholder
    return 0.0
