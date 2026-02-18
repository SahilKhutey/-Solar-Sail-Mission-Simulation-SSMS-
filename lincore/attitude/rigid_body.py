import numpy as np
from .quaternion import cross, quat_derivative

def attitude_derivative(q, omega, inertia, torque):
    """
    Computes derivative of state [q, omega].
    dq: Quaternion derivative
    domega: Angular acceleration (Euler equations)
    """
    # Helper to handle list/numpy
    if isinstance(omega, list):
        omega = np.array(omega)
    if isinstance(torque, list):
        torque = np.array(torque)
        
    I = np.array(inertia)

    # Calculate I * omega
    # If I is 3x3 diagonal passed as list of lists
    Iw = I @ omega
    
    omega_cross_Iw = np.cross(omega, Iw)
    
    # rigid body equations: I * dw/dt + w x (I*w) = T
    # dw/dt = I^-1 * (T - w x (I*w))
    
    # Solve Euler's Equation: I * dw/dt = rhs
    rhs = torque - omega_cross_Iw
    
    # Robust Diagonal Check
    off_diag_sum = np.sum(np.abs(I)) - np.sum(np.abs(np.diagonal(I)))
    is_diagonal = off_diag_sum < 1e-10
    
    if is_diagonal:
        # Diagonal inversion (element-wise)
        # Avoid division by zero
        diag = np.diagonal(I)
        if np.any(np.abs(diag) < 1e-12):
             # Singular diagonal
             domega = np.zeros(3)
        else:
             domega = rhs / diag
    else:
        # Full matrix solve
        try:
            domega = np.linalg.solve(I, rhs)
        except np.linalg.LinAlgError:
            print(f"Error: Singular Inertia Matrix:\n{I}")
            domega = np.zeros(3)

    dq = quat_derivative(q, omega.tolist())
    
    return dq, domega.tolist()
