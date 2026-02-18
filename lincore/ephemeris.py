import math
import numpy as np

# Constants (km, s)
MU_SUN = 1.32712440018e11
AU = 1.495978707e8

# Planetary Parameters (Simplified Circular)
# Semimajor axes (km)
A_EARTH = AU
A_MARS = 1.524 * AU

# Mean Motion (rad/s)
N_EARTH = math.sqrt(MU_SUN / A_EARTH**3)
N_MARS = math.sqrt(MU_SUN / A_MARS**3)

# Phase offsets (arbitrary for now, or 0)
PHASE_EARTH = 0.0
PHASE_MARS = 0.5  # radians, just to separate them

def get_earth_state(t):
    """
    Returns Earth's position and velocity [x, y, z, vx, vy, vz] in Heliocentric frame at time t.
    Simplified circular orbit.
    """
    angle = N_EARTH * t + PHASE_EARTH
    r = A_EARTH
    v = math.sqrt(MU_SUN / r)
    
    pos = [r * math.cos(angle), r * math.sin(angle), 0.0]
    vel = [-v * math.sin(angle), v * math.cos(angle), 0.0]
    
    return np.array(pos + vel)

def get_mars_state(t):
    """
    Returns Mars' position and velocity [x, y, z, vx, vy, vz] in Heliocentric frame at time t.
    Simplified circular orbit.
    """
    angle = N_MARS * t + PHASE_MARS
    r = A_MARS
    v = math.sqrt(MU_SUN / r)
    
    pos = [r * math.cos(angle), r * math.sin(angle), 0.0]
    vel = [-v * math.sin(angle), v * math.cos(angle), 0.0]
    
    return np.array(pos + vel)

def get_body_state(body_name, t):
    if body_name.lower() == 'earth':
        return get_earth_state(t)
    elif body_name.lower() == 'mars':
        return get_mars_state(t)
    else:
        raise ValueError(f"Unknown body: {body_name}")
