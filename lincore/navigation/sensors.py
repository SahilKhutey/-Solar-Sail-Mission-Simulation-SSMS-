import numpy as np


class SensorModel:
    """
    Simulates sensor measurements with noise and bias.
    """

    def __init__(self, config):
        self.config = config
        self.rng = np.random.default_rng()

        nav_cfg = config.get("navigation", {})
        # Noise parameters (Standard Deviation)
        # Position noise [km]
        self.sigma_r = nav_cfg.get("position_noise_km", 0.010)
        # Velocity noise [km/s]
        self.sigma_v = nav_cfg.get("velocity_noise_kms", 0.001)
        # Attitude noise [rad] (Star Tracker)
        self.sigma_q = np.radians(nav_cfg.get("attitude_noise_deg", 0.01))
        # Rate noise [rad/s] (Gyro)
        self.sigma_w = np.radians(nav_cfg.get("rate_noise_deg_s", 0.001))

        # Bias (Constant for a mission duration usually)
        self.bias_r = self.rng.normal(0, self.sigma_r * 0.1, 3)
        self.bias_v = self.rng.normal(0, self.sigma_v * 0.1, 3)

    def measure(self, true_state):
        """
        Add noise to true state.
        Args:
            true_state (State): True spacecraft state.
        Returns:
            np.ndarray: Measured state vector (flat).
        """
        # True values
        r_true = true_state.r
        v_true = true_state.v
        q_true = true_state.q
        w_true = true_state.w

        # Add Noise
        r_meas = r_true + self.rng.normal(0, self.sigma_r, 3) + self.bias_r
        v_meas = v_true + self.rng.normal(0, self.sigma_v, 3) + self.bias_v

        # Attitude Noise (Simplified Additive for small angles)
        # Ideally multiplicative quaternion noise
        # q_meas = q_true * q_noise
        # For now, just add noise to vector and re-normalize
        q_noise = self.rng.normal(0, self.sigma_q, 4)
        q_meas = q_true + q_noise
        q_meas /= np.linalg.norm(q_meas)

        w_meas = w_true + self.rng.normal(0, self.sigma_w, 3)

        # Return full vector
        # [r, v, q, w]
        # Mass is not measured directly usually, assumed known or estimated separately
        # We append mass from true state for the filter to use as 'measurement' or just propagate

        return np.concatenate((r_meas, v_meas, q_meas, w_meas))
