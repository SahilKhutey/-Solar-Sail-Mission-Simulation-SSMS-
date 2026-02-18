import numpy as np
from lincore.environment.ephemeris import AU, get_body_state
from lincore.attitude.quaternion import quat_rotate

P_SOLAR = 1361.0       # W/m^2
C_LIGHT = 299792.458   # km/s
R_SUN = 696340.0       # km
R_EARTH = 6378.0       # km
R_MARS = 3390.0        # km

def conical_shadow(r_sc, r_planet, R_planet, R_sun=R_SUN):
    """
    Calculate shadow factor (nu).
    0.0 = Full Shadow (Umbra)
    1.0 = Full Sun
    0.0 < nu < 1.0 = Penumbra
    
    r_sc: Spacecraft pos relative to Sun (km)
    r_planet: Planet pos relative to Sun (km)
    """
    # Vector from Planet to Sun
    r_ps = -r_planet
    d_ps = np.linalg.norm(r_ps)
    
    # Vector from Planet to SC
    r_psc = r_sc - r_planet
    d_psc = np.linalg.norm(r_psc)
    
    # Check if SC is "behind" planet relative to Sun
    # Projection of r_psc onto r_ps direction
    proj = np.dot(r_psc, r_ps) / d_ps
    if proj > 0:
        # SC is on the sun-side of the planet
        return 1.0
        
    # Apparent radii
    a_sun = np.arcsin(R_sun / d_ps) # Approx, usually R_sun / |r_planet|
    a_planet = np.arcsin(R_planet / d_psc)
    
    # Angle between Sun center and Planet center as seen from SC
    # Wait, simple conical model usually does:
    # Check geometrical intersection of line from Sun to SC with sphere.
    
    # Let's use the simple cylindrical model for robustness first, or simple conical.
    # Analytical Conical Shadow:
    # See: "Fundamentals of Astrodynamics and Applications", Vallado.
    
    # Simplified logic:
    # 1. Coordinate check (behind planet?)
    # 2. Distance from axis check.
    
    # Vector from Sun to SC
    r_sun_sc = r_sc
    d_sun_sc = np.linalg.norm(r_sun_sc)
    
    # Angle Separating Sun and Planet seen from SC? No.
    
    # Let's use simple logic:
    # Vector from Planet to SC: r_psc
    # Vector from Sun to Planet: r_planet
    # We treat Sun as point source for Umbra check approx.
    # Parallel light (Cylindrical):
    # Cross product magnitude gives distance from line.
    
    # UMBRA CONE:
    # Vertex is behind planet.
    
    # Simple Cylindrical (good enough for initial Mission-Grade, upgradable):
    # 1. Project SC onto Sun-Planet line.
    # s = r_planet (Sun to Planet)
    # p = r_sc (Sun to SC)
    # t = dot(p, s) / dot(s, s)
    # cls = t * s (Closest point on line extended)
    # But this is for line passing through origin. 
    # Shadow axis is line from Sun through Planet.
    
    # Define unit vector u = r_planet / |r_planet|
    u = r_planet / np.linalg.norm(r_planet)
    
    # Projection of SC along axis
    dist_along_axis = np.dot(r_sc, u)
    
    # If dist_along_axis < |r_planet|, SC is between Sun and Planet -> No shadow
    if dist_along_axis < np.linalg.norm(r_planet):
        return 1.0
        
    # Perpendicular distance from axis
    r_perp = r_sc - dist_along_axis * u
    dist_from_axis = np.linalg.norm(r_perp)
    
    if dist_from_axis < R_planet:
        return 0.0 # Shadow
    else:
        return 1.0 # Sun

def solar_pressure(r_helio, q, mass, area, reflectivity, t=0.0):
    """
    SRP Acceleration with Eclipse Check.
    """
    r_dist = np.linalg.norm(r_helio)
    if r_dist == 0: return np.zeros(3)
    
    # Eclipse Check
    nu = 1.0
    
    # Check Earth
    if t >= 0:
        r_earth = get_body_state('earth', t)[:3]
        nu *= conical_shadow(r_helio, r_earth, R_EARTH)
        
    # Check Mars
    if t >= 0 and nu > 0:
        r_mars = get_body_state('mars', t)[:3]
        nu *= conical_shadow(r_helio, r_mars, R_MARS)
        
    if nu == 0.0:
        return np.zeros(3)
        
    # Flux scaling
    flux = P_SOLAR * (AU / r_dist)**2 # W/m^2
    
    # Sail Normal in Body Frame (assumed +Z)
    n_body = np.array([0, 0, 1])
    n_eci = quat_rotate(n_body, q)
    n_eci = np.array(n_eci)
    
    # Sun Vector (from Sun to Sat)
    s_hat = r_helio / r_dist
    
    # Cos(theta) = n . (-s_hat) (since s_hat is from Sun)
    s_to_sun = -s_hat
    cos_theta = np.dot(n_eci, s_to_sun)
    
    if cos_theta <= 0:
        return np.zeros(3) # Backside or edge-on
        
    # Acc = P * A / (c * m) * (1+rho) * cos^2(theta) * n
    # P in W/m^2. A in m^2. m in kg. c in m/s.
    # Include nu (shadow factor)
    
    acc_mag_m_s2 = nu * (flux * area / (mass * (C_LIGHT * 1000))) * (1 + reflectivity) * (cos_theta**2)
    acc_mag_km_s2 = acc_mag_m_s2 / 1000.0
    
    return acc_mag_km_s2 * n_eci
