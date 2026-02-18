import numpy as np
from scipy.optimize import minimize
from lincore.utils.jit import num_jit
import lincore.forces.gravity as gravity
import lincore.forces.srp as srp

class TrajectoryOptimizer:
    """
    Direct Transcription Trajectory Optimizer for Solar Sail Missions.
    Uses Trapezoidal Collocation.
    """
    def __init__(self, dynamics_model, num_segments=50):
        self.dynamics = dynamics_model
        self.N = num_segments
        
        # Problem Setup
        self.mu = 1.32712440018e11 # Sun
        self.bounds = []
        self.constraints = []
        
    def _pack_vector(self, state_history, control_history, tf):
        """Pack variables into 1D decision vector."""
        # X = [x0, y0, ..., u0, v0, ..., tf]
        # State: 6 vars * (N+1)
        # Control: 3 vars * (N+1) (or N? Collocation usually N+1)
        # Time: 1 var
        x_flat = state_history.flatten()
        u_flat = control_history.flatten()
        return np.concatenate([x_flat, u_flat, [tf]])
        
    def _unpack_vector(self, decision_vector):
        """Unpack 1D decision vector."""
        n_col = self.N + 1
        n_state = 6
        n_ctrl = 3
        
        len_x = n_col * n_state
        len_u = n_col * n_ctrl
        
        x_flat = decision_vector[:len_x]
        u_flat = decision_vector[len_x:len_x+len_u]
        tf = decision_vector[-1]
        
        states = x_flat.reshape((n_col, n_state))
        controls = u_flat.reshape((n_col, n_ctrl))
        
        return states, controls, tf
        
    def objective_min_time(self, decision_vector):
        """Objective: Minimize final time."""
        _, _, tf = self._unpack_vector(decision_vector)
        return tf

    def constraint_dynamics(self, decision_vector):
        """
        Defect constraints: x_{k+1} - x_k - 0.5*h*(f_k + f_{k+1}) = 0
        """
        states, controls, tf = self._unpack_vector(decision_vector)
        dt = tf / self.N
        
        defects = []
        
        # We need a vectorized dynamics function or loop
        # For scipy we return a flat array of defects
        
        for k in range(self.N):
            x_k = states[k]
            x_kp1 = states[k+1]
            u_k = controls[k]
            u_kp1 = controls[k+1]
            
            # evaluate dynamics f(x,u)
            # This needs to be efficient. calling self.dynamics might be slow if not optimized.
            # We assume self.dynamics can take (x, u)
            # Actually self.dynamics usually takes (t, y). We need an adapter.
            
            f_k = self._dynamics_func(x_k, u_k)
            f_kp1 = self._dynamics_func(x_kp1, u_kp1)
            
            defect = x_kp1 - x_k - 0.5 * dt * (f_k + f_kp1)
            defects.append(defect)
            
        return np.concatenate(defects)

    def _dynamics_func(self, state, control):
        """
        Simplified dynamics for the optimizer.
        state: [rx, ry, rz, vx, vy, vz]
        control: [nx, ny, nz] (Sail Normal)
        """
        r = state[:3]
        v = state[3:6]
        
        # Gravity
        acc_grav = gravity.two_body_gravity(r, self.mu)
        
        # SRP
        # Assume ideal sail for now or use simplified model
        # a_srp = beta * mu / r^2 * (n . s)^2 * n
        # This should call a JIT compiled simplified force model
        
        # For optimization we often use a simplified model 
        # to ensure smooth gradients if possible, or use the full model if robust.
        # Let's use a local helper.
        acc_srp = self._accel_srp(r, control)
        
        acc = acc_grav + acc_srp
        
        return np.concatenate([v, acc])
        
    def _accel_srp(self, r, n_vec):
        """
        Ideal SRP acceleration.
        beta = 0.05 (placeholder, should be class param)
        """
        beta = 0.05 # Lightness number
        r_mag = np.linalg.norm(r)
        if r_mag == 0: return np.zeros(3)
        
        # Unit vector from Sun to SC
        u_r = r / r_mag
        
        # Normal vector (control) should be unit length
        # The optimizer might violate this, so we normalize or penalize
        n_mag = np.linalg.norm(n_vec)
        if n_mag < 1e-6: return np.zeros(3)
        n = n_vec / n_mag
        
        # Cosine of angle between Sun-line and Normal
        # n should point away from Sun? 
        # Standard: Force F = 2 P A cos^2(alpha) n
        # alpha is angle between n and Sun-SC line.
        # If n aligns with u_r, alpha=0, full force.
        
        cos_alpha = np.dot(n, u_r)
        
        # Constraint: Sail cannot be lit from behind
        if cos_alpha < 0:
            return np.zeros(3) # No force if facing wrong way
            
        # Accel magnitude
        # a = beta * mu / r^2 * cos^2(alpha)
        ac_mag = beta * self.mu / r_mag**2 * cos_alpha**2
        
        return ac_mag * n

    def solve(self, r0, v0, tf_guess, r_target_mag):
        """
        Solve optimal trajectory from state (r0, v0) to a target radius.
        """
        # Initial Guess: Linear interpolation
        # ...
        
        # Build initial decision vector
        t = np.linspace(0, tf_guess, self.N+1)
        
        # Simple guess: circular orbit propagation or just static
        # Let's do a simple propagation guess
        states = []
        controls = []
        
        r_curr = np.array(r0)
        v_curr = np.array(v0)
        dt = tf_guess / self.N
        
        for _ in range(self.N+1):
            states.append(np.concatenate([r_curr, v_curr]))
            controls.append(np.array([1.0, 0.0, 0.0])) # Point radials
            
            # Simple Prop
            acc = -self.mu * r_curr / np.linalg.norm(r_curr)**3
            r_curr = r_curr + v_curr * dt
            v_curr = v_curr + acc * dt
            
        x0 = self._pack_vector(np.array(states), np.array(controls), tf_guess)
        
        # Constraints
        # 1. Defects (Equality)
        # 2. Boundary Condition Initial (Equality)
        # 3. Boundary Condition Final (Inequality/Equality)
        # 4. Control Unity Norm (Equality)
        
        cons = []
        
        # Dynamic Defects
        cons.append({'type': 'eq', 'fun': self.constraint_dynamics})
        
        # Initial State
        cons.append({'type': 'eq', 'fun': lambda x: self._unpack_vector(x)[0][0] - np.concatenate([r0, v0])})
        
        # Final Target (Radius)
        def final_radius_con(x):
            s, _, _ = self._unpack_vector(x)
            xf = s[-1]
            rf = np.linalg.norm(xf[:3])
            return rf - r_target_mag
            
        cons.append({'type': 'eq', 'fun': final_radius_con})
        
        # Control Norm Constraint (at each node)
        # n_x^2 + n_y^2 + n_z^2 = 1
        def control_norm_con(x):
            _, u, _ = self._unpack_vector(x)
            norms = np.sum(u**2, axis=1) - 1.0
            return norms
            
        cons.append({'type': 'eq', 'fun': control_norm_con})
        
        print("Starting Optimization...")
        res = minimize(
            self.objective_min_time, 
            x0, 
            method='SLSQP', 
            constraints=cons,
            options={'maxiter': 100, 'disp': True, 'ftol': 1e-4}
        )
        
        return res
