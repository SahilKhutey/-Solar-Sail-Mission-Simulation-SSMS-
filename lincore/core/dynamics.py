import numpy as np
from lincore.forces.gravity import two_body_gravity, MU_EARTH
from lincore.forces.j2 import j2_perturbation
from lincore.forces.srp import solar_pressure
from lincore.forces.drag import atmospheric_drag
from lincore.environment.ephemeris import get_body_state, MU_SUN

from lincore.forces.n_body import NBodyGravity


class DynamicsModel:
    """
    Centralized dynamics engine.
    Aggregates all force models based on configuration.
    """

    def __init__(self, config):
        self.config = config
        self.gravity_type = config["physics"].get("gravity_model", "two_body")
        self.perturbations = config["physics"].get("perturbations", {})
        self.sc_config = config["spacecraft"]

        # Cache constants
        self.mass = self.sc_config["mass"]
        self.area = self.sc_config["sail_area"]
        self.refl = self.sc_config.get("reflectivity", 1.0)
        self.drag_coeff = self.sc_config.get("drag_coeff", 2.2)
        self.degradation_half_life = self.sc_config.get("degradation_half_life", 0.0)
        self.billowing_factor = self.sc_config.get("billowing_factor", 0.0)

        # Determine center body
        self.orbit_type = config["orbit"]["type"]
        if self.orbit_type == "Heliocentric":
            self.mu = MU_SUN
        else:
            self.mu = MU_EARTH

        self.external_torque = np.zeros(3)
        self.external_force = np.zeros(3)  # For thrusters if any check

        # N-Body
        self.n_body = None
        n_body_conf = self.perturbations.get("n_body")
        if n_body_conf:
            bodies = n_body_conf if isinstance(n_body_conf, list) else None
            self.n_body = NBodyGravity(bodies)

        # Inertia
        self.inertia = np.array(self.sc_config.get("inertia", np.eye(3)))
        self.inertia_inv = np.linalg.inv(self.inertia)

    def set_control(self, torque):
        """Update external control torque."""
        self.external_torque = torque

    def __call__(self, t, y):
        """
        Computes the derivative dy/dt = [v, a, q_dot, w_dot].
        y: Flat state vector.
        """
        r = y[0:3]
        v = y[3:6]
        q = y[6:10]
        w = y[10:13]

        # 1. Gravity
        if self.gravity_type == "two_body":
            acc = two_body_gravity(r, self.mu)
        else:
            acc = two_body_gravity(r, self.mu)

        # 2. Perturbations
        if self.perturbations.get("j2") and self.orbit_type == "LEO":
            acc += j2_perturbation(r)

        if self.perturbations.get("srp"):
            # Convert to Heliocentric if necessary
            if self.orbit_type == "LEO":  # or any geocentric
                r_sun_earth = get_body_state("earth", t)[:3]  # Vector Sun->Earth?
                # get_body_state returns r referenced to Sun. So r_earth (Sun->Earth).
                # r is Earth->SC.
                # r_helio (Sun->SC) = r_earth (Sun->Earth) + r (Earth->SC)
                r_earth = get_body_state("earth", t)[:3]
                r_helio = r_earth + r
            else:
                # Assumed heliocentric
                r_helio = r

            # Use actual attitude 'q'
            acc += solar_pressure(
                r_helio, q, self.mass, self.area, self.refl, t=t,
                degradation_half_life=self.degradation_half_life,
                billowing_factor=self.billowing_factor
            )

        if self.perturbations.get("drag") and self.orbit_type == "LEO":
            acc += atmospheric_drag(r, v, self.mass, self.area, self.drag_coeff)

        if self.n_body:
            # Determine origin
            origin = "SUN" if self.orbit_type == "Heliocentric" else "EARTH"
            acc += self.n_body(t, r, origin=origin)

        # 3. Rotational Dynamics
        # Kinematics: q_dot = 0.5 * Omega * q
        # Construct Omega matrix
        wx, wy, wz = w
        Omega = np.array([[0, -wx, -wy, -wz], [wx, 0, wz, -wy], [wy, -wz, 0, wx], [wz, wy, -wx, 0]])
        q_dot = 0.5 * Omega @ q

        # Dynamics: w_dot = I^-1 * (Torque - w x (I*w))
        h_rot = self.inertia @ w
        torque_total = self.external_torque  # + Disturbances if any
        w_dot = self.inertia_inv @ (torque_total - np.cross(w, h_rot))

        d_y = np.zeros_like(y)
        d_y[0:3] = v
        d_y[3:6] = acc
        d_y[6:10] = q_dot
        d_y[10:13] = w_dot

        return d_y
