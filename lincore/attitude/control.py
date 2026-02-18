import numpy as np

def attitude_control_torque(current_normal, desired_normal, omega, Kp=0.1, Kd=1.0, max_torque=0.2):
    """
    Computes control torque to align current_normal with desired_normal.
    PD Controller.
    """
    n_curr = np.array(current_normal)
    n_des = np.array(desired_normal)
    w = np.array(omega)

    # Cross product gives axis of rotation to align normals
    error = np.cross(n_curr, n_des)
    
    # PD Control Law
    torque_command = Kp * error - Kd * w
    
    # Saturation
    t_mag = np.linalg.norm(torque_command)
    if t_mag > max_torque:
        torque_command = torque_command / t_mag * max_torque

    return torque_command.tolist()
