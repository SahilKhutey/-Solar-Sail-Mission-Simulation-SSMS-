import math
import numpy as np
import os

# Constants (km, s)
MU_SUN = 1.32712440018e11
AU = 1.495978707e8

# Planetary Parameters (Simplified Circular) for Fallback
A_EARTH = AU
A_MARS = 1.524 * AU
A_JUPITER = 5.20 * AU
N_EARTH = math.sqrt(MU_SUN / A_EARTH**3)
N_MARS = math.sqrt(MU_SUN / A_MARS**3)
N_JUPITER = math.sqrt(MU_SUN / A_JUPITER**3)
PHASE_EARTH = 0.0
PHASE_MARS = 0.5
PHASE_JUPITER = 1.0  # Arbitrary

# SPICE Integration
HAS_SPICE = False
try:
    import spiceypy as sp

    HAS_SPICE = True
except ImportError:
    pass

# Kernel Loading Flag
KERNELS_LOADED = False


def load_kernels(kernel_path="kernels/de440.bsp"):
    """
    Load SPICE kernels.
    """
    global KERNELS_LOADED
    if not HAS_SPICE:
        print("Warning: spiceypy not installed. Using analytical ephemeris.")
        return False

    if os.path.exists(kernel_path):
        try:
            sp.furnsh(kernel_path)
            # Load leapseconds if available (often needed for precise time)
            lsk_path = os.path.join(os.path.dirname(kernel_path), "naif0012.tls")
            if os.path.exists(lsk_path):
                sp.furnsh(lsk_path)

            KERNELS_LOADED = True
            print(f"SPICE Kernels loaded: {kernel_path}")
            return True
        except Exception as e:
            print(f"Failed to load kernels: {e}")
            return False
    else:
        # Silently fail to fallback, or print info
        # print(f"Info: Kernel not found at {kernel_path}. Using fallback.")
        return False


from lincore.utils.jit import num_jit


@num_jit
def calc_planet_state(t, a, n, phase, mu):
    angle = n * t + phase
    r = a
    v = math.sqrt(mu / r)
    # nopython mode supports math.cos/sin
    pos = np.array([r * math.cos(angle), r * math.sin(angle), 0.0])
    vel = np.array([-v * math.sin(angle), v * math.cos(angle), 0.0])
    return np.concatenate((pos, vel))


def _get_analytical_state(body_name, t):
    """
    Analytical Circular Orbit Fallback.
    t: seconds past J2000 (approx)
    """
    body = body_name.lower()
    if body == "earth":
        return calc_planet_state(t, A_EARTH, N_EARTH, PHASE_EARTH, MU_SUN)
    elif body == "mars":
        return calc_planet_state(t, A_MARS, N_MARS, PHASE_MARS, MU_SUN)
    elif body == "jupiter":
        return calc_planet_state(t, A_JUPITER, N_JUPITER, PHASE_JUPITER, MU_SUN)
    elif body == "sun":
        return np.zeros(6)
    else:
        raise ValueError(f"Unknown body for analytical model: {body}")


def get_body_state(body_name, t):
    """
    Get state [r, v] of body relative to Sun (Heliocentric).
    """
    if KERNELS_LOADED and HAS_SPICE:
        try:
            # SPICE expects Ephemeris Time (ET). Assumes t is ET seconds past J2000.
            # Target is body name (e.g. 'EARTH', 'MARS', 'EARTH BARYCENTER'?)
            # Using 'EARTH' usually refers to the planet center.
            # Frame 'ECLIPJ2000' is Ecliptic. 'J2000' is Equatorial.
            # User probably wants J2000 if not specified, but for solar system Ecliptic is nicer.
            # Let's stick to J2000 as standard inertial frame.
            target = body_name.upper()
            if target == "EARTH":
                target = "EARTH"  # or 399

            state, _ = sp.spkgeo(target=target, et=t, frame="J2000", obsr="SUN")
            return np.array(state)
        except Exception:
            return _get_analytical_state(body_name, t)
    else:
        return _get_analytical_state(body_name, t)
