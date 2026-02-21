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
        self.bodies = bodies if bodies else ["EARTH", "JUPITER", "MARS", "VENUS"]
        # MUs (km^3/s^2) - Should load from SPICE or constants
        self.mus = {
            "EARTH": 398600.4418,
            "JUPITER": 1.26686534e8,
            "MARS": 42828.37,
            "VENUS": 324859.0,
            "MOON": 4902.8,
            "SATURN": 3.7931187e7,
        }

    def __call__(self, t, r, origin="SUN"):
        """
        Calculate perturbation acceleration.
        t: Time (seconds past J2000)
        r: Position vector (km) relative to Origin
        origin: Central body name (default 'SUN')
        """
        r_bodies_list = []
        mus_list = []

        # Get Origin State (if not Sun)
        if origin != "SUN":
            r_origin = get_body_state(origin, t)[:3]
        else:
            r_origin = np.zeros(3)

        for body in self.bodies:
            # Skip if body is the origin
            if body.upper() == origin.upper():
                continue

            # Get state [r, v], relative to Sun
            state = get_body_state(body, t)
            r_b_sun = state[:3]

            # Shift to Origin Frame
            r_b = r_b_sun - r_origin

            r_bodies_list.append(r_b)
            mus_list.append(self.mus.get(body.upper(), 0.0))

        # Special case: If origin is Earth, we likely want Sun as a Third Body
        # But Sun is not in get_body_state list explicitly (returns 0).
        # We need to handle 'SUN' in self.bodies explicitly if origin != 'SUN'.
        if origin != "SUN" and "SUN" in self.bodies:
            # Sun position relative to Origin (e.g. Earth)
            # r_sun_rel = r_sun - r_origin = 0 - r_origin = -r_origin
            r_bodies_list.append(-r_origin)
            mus_list.append(MU_SUN)

        r_bodies = np.array(r_bodies_list)
        mus = np.array(mus_list)

        return n_body_accel(r, r_bodies, mus)
