import numpy as np
from lincore.core.dynamics import DynamicsModel
from lincore.core.state import State
from lincore.core.integrator import rk45_step
# guidance, navigation imports...

from lincore.navigation.sensors import SensorModel
from lincore.navigation.ekf import ExtendedKalmanFilter

class SolarSailMission:
    def __init__(self, config):
        self.config = config
        self.dynamics = DynamicsModel(config)
        self.state = self._init_state()
        self.time = 0.0
        self.dt = float(config['mission'].get('step_size', 60.0)) # Adaptive step state
        self.rtol = float(config['physics'].get('relative_tolerance', 1e-9))
        self.atol = float(config['physics'].get('absolute_tolerance', 1e-12))
        
        # Navigation
        self.sensors = SensorModel(config)
        
        # EKF Init
        if self.config['physics'].get('navigation', False):
            # Q: Process Noise, R: Measurement Noise
            # Simplified P0
            x0 = self.state.vector
            dim = len(x0)
            P0 = np.eye(dim) * 1.0
            
            # Helper to get config noise or default
            sig_r = config['navigation'].get('position_noise_km', 0.010)
            sig_v = config['navigation'].get('velocity_noise_kms', 0.001)
            sig_q = np.radians(config['navigation'].get('attitude_noise_deg', 0.01))
            sig_w = np.radians(config['navigation'].get('rate_noise_deg_s', 0.001))
            
            # R matrix (Measurement Noise Covariance)
            # Assuming uncorrelated
            # size 13
            R = np.diag([sig_r]*3 + [sig_v]*3 + [sig_q]*4 + [sig_w]*3)**2
            
            # Q matrix (Process Noise Covariance)
            # Tunable
            Q = np.eye(dim) * 1e-6
            
            self.ekf = ExtendedKalmanFilter(x0, P0, Q, R)
        else:
            self.ekf = None
        
    def _init_state(self):
        # ... (Same as before)
        # Initialize from config
        orb = self.config['orbit']
        # Simple placeholder logic for LEO/Helio
        if orb['type'] == 'LEO':
             r_mag = 6378.0 + orb['altitude_km']
             v_mag = np.sqrt(398600.4418 / r_mag)
             r = np.array([r_mag, 0, 0])
             v = np.array([0, v_mag, 0])
             # Inclination logic could be added here
        elif orb['type'] == 'Heliocentric':
             # 1 AU
             r = np.array([1.496e8 * orb.get('distance_au', 1.0), 0, 0])
             v = np.array([0, 29.78, 0])
        else:
             # Default
             r = np.array([7000.0, 0, 0])
             v = np.array([0, 7.5, 0])
        
        q = np.array([1, 0, 0, 0])
        w = np.array([0, 0, 0])
        
        # Handle scalar float for mass in State
        return State(0.0, r, v, q, w, float(self.config['spacecraft']['mass']))

    def step(self):
        # 1. Propagation (Dynamics) - Adaptive loop
        success = False
        actual_dt = self.dt
        while not success:
            y = self.state.vector
            success, t_next, y_next, dt_next = rk45_step(self.dynamics, self.time, y, self.dt, (self.atol, self.rtol))
            actual_dt = self.dt
            self.dt = dt_next
            
        self.time = t_next
        self.state = State.from_vector(self.time, y_next, self.state.mass)
        
        # 2. Sensors (Measurement)
        z_meas = self.sensors.measure(self.state)
        
        # 3. Navigation (Estimation)
        if self.ekf:
             # Predict Step forward to new time using the exact advanced dt
             self.ekf.predict(self.dynamics, actual_dt)
             
             # Update Step (Measurement)
             def h_meas(x):
                 return x
             self.ekf.update(z_meas, h_meas)
             
             # Get Estimate
             est_vec = self.ekf.x
             estimated_state = State.from_vector(self.time, est_vec, self.state.mass)
        else:
             if self.config['physics'].get('navigation', False):
                 estimated_state = State.from_vector(self.time, z_meas, self.state.mass)
             else:
                 estimated_state = self.state
                 
        # 4. Guidance & Control
        control_torque = self._get_control_torque(estimated_state)
        self.dynamics.set_control(control_torque)
            
        return self.time, [self.state.r[0], self.state.r[1], self.state.r[2], 
                           self.state.v[0], self.state.v[1], self.state.v[2]]

    def _get_control_torque(self, state):
        # Default: zero torque (passive stability test)
        return np.zeros(3)
