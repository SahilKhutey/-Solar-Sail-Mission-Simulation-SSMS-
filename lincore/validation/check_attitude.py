import numpy as np
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lincore.core.integrator import rk45_step
from lincore.attitude.rigid_body import attitude_derivative
from lincore.attitude.quaternion import norm

def dynamics_attitude(t, y, inertia):
    q = y[:4]
    w = y[4:7]
    torque = [0, 0, 0] # Torque free
    dq, dw = attitude_derivative(q.tolist(), w.tolist(), inertia, torque)
    return np.concatenate((dq, dw))

def check_torque_free_motion():
    print("PHASE 3: Attitude Dynamics Validation")
    print("-------------------------------------")
    
    # Inertia tensor (Diagonal)
    # I1 < I2 < I3
    I = np.array([[10.0, 0.0, 0.0],
                  [0.0, 20.0, 0.0],
                  [0.0, 0.0, 30.0]])
                  
    print(f"Inertia:\n{I}")
         
    # Case 1: Stable Major Axis Spin (Z-axis)
    print("Testing Major Axis Spin (Stable)...")
    q0 = np.array([1.0, 0, 0, 0])
    w0 = np.array([0.01, 0.01, 2.0]) # Slight perturbation
    y = np.concatenate((q0, w0))
    
    t = 0.0
    dt = 0.1
    t_end = 100.0
    tol = 1e-9
    
    w_history = []
    
    while t < t_end:
        # Pass I as *args. dt_max as kwarg.
        success, t_next, y_next, dt_next = rk45_step(dynamics_attitude, t, y, dt, tol, I, dt_max=1.0)
        if success:
            t = t_next
            y = y_next
            dt = dt_next
            w_history.append(y[4:7])
            
    w_final = w_history[-1]
    print(f"Final Omega: {w_final}")
    if abs(w_final[2]) > 1.0 and abs(w_final[0]) < 0.5:
        print("PASS: Major axis spin remained stable.")
    else:
        print("FAIL: Major axis spin unstable.")

    # Case 2: Unstable Intermediate Axis Spin (Y-axis)
    print("\nTesting Intermediate Axis Spin (Unstable)...")
    w0 = np.array([0.01, 2.0, 0.01]) # Perturbed Y-spin
    y = np.concatenate((q0, w0))
    
    t = 0.0
    w_y_hist = []
    
    while t < t_end:
        success, t_next, y_next, dt_next = rk45_step(dynamics_attitude, t, y, dt, tol, I, dt_max=1.0)
        if success:
            t = t_next
            y = y_next
            dt = dt_next
            w_y_hist.append(y[5])

    # Check for Polhode flip (sign change of wy is possible, or large excursions)
    # Actually, intermediate axis theorem says it will drift away.
    # Energy and Momentum sphere interaction.
    # We check if wx and wz grew significantly.
    
    w_final = y[4:7]
    print(f"Final Omega: {w_final}")
    
    # If it stayed perfectly near [0, 2, 0], it failed (simulation too perfect or physics wrong)
    # But we added perturbation.
    # It should tumble.
    dist_from_axis = np.sqrt(w_final[0]**2 + w_final[2]**2)
    print(f"Off-axis magnitude: {dist_from_axis:.4f}")
    
    if dist_from_axis > 0.5:
        print("PASS: Intermediate axis instability detected (Polhode motion).")
    else:
        print("FAIL: Intermediate axis spin remained too stable (Check physics/integrator).")

if __name__ == "__main__":
    check_torque_free_motion()
