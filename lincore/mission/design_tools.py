import numpy as np
import math
from scipy.optimize import newton

class HohmannTransfer:
    """
    Calculates Hohmann transfer parameters between two circular orbits.
    """
    def __init__(self, mu):
        self.mu = mu
        
    def calculate(self, r1, r2):
        """
        Calculate Delta-Vs and Time of Flight.
        r1: Radius of initial orbit (km)
        r2: Radius of final orbit (km)
        Returns: (dv1, dv2, tof_seconds)
        """
        # Semimajor axis of transfer orbit
        at = (r1 + r2) / 2
        
        # Velocities
        v1 = math.sqrt(self.mu / r1)
        v2 = math.sqrt(self.mu / r2)
        
        # Transfer velocities
        vt1 = math.sqrt(self.mu * (2/r1 - 1/at))
        vt2 = math.sqrt(self.mu * (2/r2 - 1/at))
        
        dv1 = abs(vt1 - v1)
        dv2 = abs(v2 - vt2)
        
        # Time of Flight (half period)
        tof = math.pi * math.sqrt(at**3 / self.mu)
        
        return dv1, dv2, tof

class LambertSolver:
    """
    Solves Lambert's Problem: Find v1, v2 given r1, r2, dt.
    """
    def __init__(self, mu):
        self.mu = mu
        
    def solve(self, r1, r2, dt, prograde=True):
        """
        Solve Lambert problem using Universal Variables.
        """
        from scipy.optimize import newton
        
        r1_mag = np.linalg.norm(r1)
        r2_mag = np.linalg.norm(r2)
        
        cross_r = np.cross(r1, r2)
        theta = math.acos(np.dot(r1, r2) / (r1_mag * r2_mag))
        
        # Check prograde
        if prograde:
            if cross_r[2] < 0: theta = 2*math.pi - theta
        else:
            if cross_r[2] >= 0: theta = 2*math.pi - theta
            
        A = math.sin(theta) * math.sqrt(r1_mag * r2_mag / (1 - math.cos(theta)))
        
        def stumpff_S(z):
            if z > 0: return (math.sqrt(z) - math.sin(math.sqrt(z))) / (math.sqrt(z)**3)
            elif z < 0: return (math.sinh(math.sqrt(-z)) - math.sqrt(-z)) / (math.sqrt(-z)**3)
            return 1/6
            
        def stumpff_C(z):
            if z > 0: return (1 - math.cos(math.sqrt(z))) / z
            elif z < 0: return (math.cosh(math.sqrt(-z)) - 1) / (-z)
            return 1/2
            
        def tof_eqn(z):
            # Universal variable y
            S = stumpff_S(z)
            C = stumpff_C(z)
            y = r1_mag + r2_mag + A * (z * S - 1) / math.sqrt(C)
            if y < 0: return float('inf') # Invalid
            x = math.sqrt(y / C)
            t = (x**3 * S + A * math.sqrt(y)) / math.sqrt(self.mu)
            return t - dt

        # Initial guess (z=0 is parabola)
        try:
             z_star = newton(tof_eqn, 0.0, maxiter=50)
        except RuntimeError:
             return None # Failed to converge
             
        # Compute V1, V2
        z = z_star
        S = stumpff_S(z)
        C = stumpff_C(z)
        y = r1_mag + r2_mag + A * (z * S - 1) / math.sqrt(C)
        
        f = 1 - y/r1_mag
        g = A * math.sqrt(y/self.mu)
        g_dot = 1 - y/r2_mag
        
        v1 = (r2 - f*r1) / g
        v2 = (g_dot*r2 - r1) / g
        
        return v1, v2

class EscapeTimeEstimator:
    """
    Estimates time to escape for a solar sail spiraling out.
    """
    def __init__(self, mu, beta):
        """
        mu: Gravitational parameter
        beta: Sail lightness number
        """
        self.mu = mu
        self.beta = beta
        
    def estimate_time(self, r0, r_target, efficiency=0.8):
        """
        Estimate time to spiral from r0 to r_target (or escape).
        Using McInnes approximation for energy rate.
        efficiency: Factor for non-optimal steering (0.0 - 1.0).
        """
        # t = (1 / (3 * eta * beta * sqrt(mu))) * (rf^1.5 - r0^1.5)
        # eta = efficiency * reflectivity term? 
        # beta is lightness number (ratio of accel to gravity).
        # Efficiency lumps in steering loss (e.g. 0.8 for tangential).
        
        # Check units: r in km. mu in km^3/s^2.
        
        term = r_target**1.5 - r0**1.5
        denom = 3 * efficiency * self.beta * math.sqrt(self.mu)
        
        if denom == 0: return float('inf')
        
        t_sec = term / denom
        return t_sec / 86400.0 # Days
