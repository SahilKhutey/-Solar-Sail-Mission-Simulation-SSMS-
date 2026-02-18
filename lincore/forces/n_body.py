import numpy as np
from lincore.utils.jit import num_jit
from lincore.environment.ephemeris import get_body_state, MU_SUN

@num_jit
def n_body_accel(r_sc, r_bodies, mus):
    """
    Calculate N-Body perturbation acceleration.
    r_sc: Satellite position (x, y, z)
    r_bodies: Array of body positions (N, 3) relative to central body (Sun)
    mus: Array of gravitational parameters (N,)
    """
    acc = np.zeros(3)
    # Iterate over bodies
    for i in range(len(mus)):
        r_b = r_bodies[i]
        mu = mus[i]
        
        # d_vec = r_sc - r_b (Vector from Body to SC)
        d_vec = r_sc - r_b
        dist_sq = np.sum(d_vec**2)
        dist = np.sqrt(dist_sq)
        
        # r_b magnitude
        rb_dist_sq = np.sum(r_b**2)
        rb_dist = np.sqrt(rb_dist_sq)
        
        if dist < 1e-6 or rb_dist < 1e-6:
            continue
            
        # Perturbation = -mu * ( (r-rb)/|r-rb|^3 + rb/|rb|^3 )
        term1 = d_vec / dist**3
        term2 = r_b / rb_dist**3
        
        acc -= mu * (term1 + term2)
        
    return acc

class NBodyGravity:
    def __init__(self, bodies=None):
        """
        bodies: List of body names to include (e.g. ['EARTH', 'JUPITER'])
        """
        self.bodies = bodies if bodies else ['EARTH', 'JUPITER', 'MARS', 'VENUS']
        # MUs (km^3/s^2) - Should load from SPICE or constants
        self.mus = {
            'EARTH': 398600.4418,
            'JUPITER': 1.26686534e8,
            'MARS': 42828.37,
            'VENUS': 324859.0,
            'MOON': 4902.8,
            'SATURN': 3.7931187e7
        }
        
    def __call__(self, t, r):
        """
        Calculate perturbation acceleration.
        t: Time (seconds past J2000)
        r: Position vector (km) relative to Sun
        """
        r_bodies_list = []
        mus_list = []
        
        for body in self.bodies:
            # Get state [r, v], we need r
            # get_body_state returns state relative to Sun
            state = get_body_state(body, t) 
            r_b = state[:3]
            
            r_bodies_list.append(r_b)
            mus_list.append(self.mus.get(body.upper(), 0.0))
            
        r_bodies = np.array(r_bodies_list)
        mus = np.array(mus_list)
        
        return n_body_accel(r, r_bodies, mus)
