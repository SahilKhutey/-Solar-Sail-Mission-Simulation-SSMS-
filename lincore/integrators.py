import math
import numpy as np

def rk4(f, t, y, dt, *args):
    """
    Classical 4th order Runge-Kutta integrator.
    """
    k1 = f(t, y, *args)
    # Handle list vs numpy array for y
    if isinstance(y, list):
        # Fallback for list-based state (though we are moving to numpy)
        # But f returns numpy array usually in 6-DOF
        # Let's try to support both if possible, or convert y to numpy
        y_np = np.array(y)
        dtype_conv = True
    else:
        y_np = y
        dtype_conv = False

    k1 = np.array(k1)
    
    k2 = np.array(f(t + dt/2, y_np + dt*k1/2, *args))
    k3 = np.array(f(t + dt/2, y_np + dt*k2/2, *args))
    k4 = np.array(f(t + dt,   y_np + dt*k3,   *args))

    y_next = y_np + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    
    return y_next.tolist() if dtype_conv else y_next

def rk45_step(f, t, y, dt, tol, *args, dt_max=None):
    """
    Perform a single adaptive Runge-Kutta-Fehlberg (RKF45) step.
    Returns: (success (bool), t_new, y_new, dt_next)
    """
    # RKF45 Coefficients
    c2, c3, c4, c5, c6 = 1/4, 3/8, 12/13, 1, 1/2
    a21 = 1/4
    a31, a32 = 3/32, 9/32
    a41, a42, a43 = 1932/2197, -7200/2197, 7296/2197
    a51, a52, a53, a54 = 439/216, -8, 3680/513, -845/4104
    a61, a62, a63, a64, a65 = -8/27, 2, -3544/2565, 1859/4104, -11/40
    
    # 4th order solution weights (b4)
    b4_1, b4_3, b4_4, b4_5 = 25/216, 1408/2565, 2197/4104, -1/5
    # 5th order solution weights (b5)
    b5_1, b5_3, b5_4, b5_5, b5_6 = 16/135, 6656/12825, 28561/56430, -9/50, 2/55
    
    y_np = np.array(y)
    
    k1 = np.array(f(t, y_np, *args))
    k2 = np.array(f(t + c2*dt, y_np + dt*(a21*k1), *args))
    k3 = np.array(f(t + c3*dt, y_np + dt*(a31*k1 + a32*k2), *args))
    k4 = np.array(f(t + c4*dt, y_np + dt*(a41*k1 + a42*k2 + a43*k3), *args))
    k5 = np.array(f(t + c5*dt, y_np + dt*(a51*k1 + a52*k2 + a53*k3 + a54*k4), *args))
    k6 = np.array(f(t + c6*dt, y_np + dt*(a61*k1 + a62*k2 + a63*k3 + a64*k4 + a65*k5), *args))
    
    # Calculate 4th and 5th order solutions
    y4 = y_np + dt * (b4_1*k1 + b4_3*k3 + b4_4*k4 + b4_5*k5)
    y5 = y_np + dt * (b5_1*k1 + b5_3*k3 + b5_4*k4 + b5_5*k5 + b5_6*k6)
    
    # Error estimate
    delta = np.abs(y5 - y4)
    
    # Scientific Mixed Tolerance Metric
    # tol_i = atol + rtol * max(|y4_i|, |y5_i|)
    # This prevents division by zero and scales correctly for position vs velocity.
    if isinstance(tol, tuple) and len(tol) == 2:
        atol, rtol = tol
    else:
        # Fallback if only one tol is provided
        atol = tol
        rtol = tol
        
    scale_y = np.maximum(np.abs(y4), np.abs(y5))
    tol_metric = np.maximum(atol + rtol * scale_y, 1e-15)
    
    ratio = delta / tol_metric
    error_metric = np.max(ratio)
    
    if error_metric < 1e-15:
        error_metric = 1e-15
        
    # Valid step check
    if error_metric <= 1.0:
        success = True
        scale = 0.9 * (1.0 / error_metric)**0.2
        scale = min(max(scale, 0.2), 5.0)
        dt_next = dt * scale
        t_new = t + dt
        y_new = y5
    else:
        success = False
        t_new = t
        y_new = y_np
        scale = 0.9 * (1.0 / error_metric)**0.25
        scale = min(max(scale, 0.1), 1.0)
        dt_next = dt * scale
        
    if dt_max is not None:
        dt_next = min(dt_next, dt_max)
        
    return success, t_new, y_new, dt_next
