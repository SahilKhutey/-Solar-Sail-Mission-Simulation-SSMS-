import numpy as np

class ExtendedKalmanFilter:
    def __init__(self, x0, P0, Q, R_std):
        """
        x0: Initial state (n_states,)
        P0: Initial covariance (n_states, n_states)
        Q:  Process noise covariance (n_states, n_states)
        R_std: Measurement noise standard deviation (scalar or array)
        """
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)
        self.Q = np.array(Q, dtype=float)
        # R is usually passed in update, but we store default
        if np.isscalar(R_std):
            self.R = np.eye(len(x0)) * R_std**2
        else:
            self.R = np.diag(np.array(R_std)**2)
            
        self.n = len(self.x)

    def predict(self, f_dynamics, dt, *args):
        """
        Time Update.
        f_dynamics: function(t, x, *args) -> dx/dt
        """
        # 1. Propagate State
        # Simple Euler for Jacobian linearization, but use RK4 for state?
        # Ideally state matches the high-fidelity integrator.
        # Here we assume a simple integrator for the Filter itself is sufficient (e.g. RK4).
        
        k1 = f_dynamics(0, self.x, *args) # t not used for Jacobian usually, or passed
        # Simple Euler prediction for Covariance linearization
        # x_pred = x + k1 * dt
        
        # Better: RK4 prediction for State
        # But we need Jacobian of the *propagation function* Phi.
        # Phi ~ I + J_f * dt.
        # Let's compute J_f (Jacobian of dynamics f) at current x.
        
        F = self.numerical_jacobian(f_dynamics, self.x, *args)
        
        # State Transition Matrix Phi
        Phi = np.eye(self.n) + F * dt
        
        # Propagate State (using RK4 locally)
        # We need a mini-integrator here since we don't depend on external one
        self.x = self._rk4_step(f_dynamics, self.x, dt, *args)
        
        # Propagate Covariance
        # P = Phi * P * Phi' + Q
        self.P = Phi @ self.P @ Phi.T + self.Q * dt # Q is usually power spectral density, so * dt?
        # If Q is discrete noise covariance per step, then + Q.
        # Usually Q is continuous, so Q_discrete ~ Q_cont * dt.
        
    def update(self, z, h_meas, R_meas=None, *args):
        """
        Measurement Update.
        z: Measurement vector
        h_meas: function(x, *args) -> z_hat (Expected measurement)
        """
        if R_meas is None:
            R = self.R
        else:
            R = R_meas
            
        # 1. Measurement Residual
        z_hat = h_meas(self.x, *args)
        y = z - z_hat
        
        # 2. Measurement Jacobian H
        H = self.numerical_jacobian(h_meas, self.x, *args)
        
        # 3. Kalman Gain
        # S = H P H' + R
        S = H @ self.P @ H.T + R
        try:
            K = self.P @ H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            print("EKF Warning: Singular S matrix.")
            return
            
        # 4. Update State
        self.x = self.x + K @ y
        
        # 5. Update Covariance
        # P = (I - K H) P
        I = np.eye(self.n)
        self.P = (I - K @ H) @ self.P
        
    def numerical_jacobian(self, func, x, *args, epsilon=1e-6):
        n = len(x)
        
        # Try call with t=0 first
        try:
             f0 = np.array(func(0, x, *args))
             uses_t = True
        except TypeError:
             f0 = np.array(func(x, *args))
             uses_t = False
             
        m = len(f0)
        J = np.zeros((m, n))
        
        for i in range(n):
            x_perturbed = x.copy()
            x_perturbed[i] += epsilon
            
            if uses_t:
                val = func(0, x_perturbed, *args)
            else:
                val = func(x_perturbed, *args)
                
            f_perturbed = np.array(val)
            J[:, i] = (f_perturbed - f0) / epsilon
            
        return J
        
    def _rk4_step(self, f, x, dt, *args):
        # Determine signature same way or just try
        try:
            # Assume f(t, x)
            k1 = np.array(f(0, x, *args))
            k2 = np.array(f(0, x + 0.5*dt*k1, *args))
            k3 = np.array(f(0, x + 0.5*dt*k2, *args))
            k4 = np.array(f(0, x + dt*k3, *args))
            return x + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        except TypeError:
             # Assume f(x)
            k1 = np.array(f(x, *args))
            k2 = np.array(f(x + 0.5*dt*k1, *args))
            k3 = np.array(f(x + 0.5*dt*k2, *args))
            k4 = np.array(f(x + dt*k3, *args))
            return x + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
