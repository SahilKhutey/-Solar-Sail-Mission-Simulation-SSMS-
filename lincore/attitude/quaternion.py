import math
import numpy as np
from lincore.utils.jit import num_jit


@num_jit
def norm(v):
    return np.linalg.norm(v)


@num_jit
def cross(a, b):
    return np.cross(a, b)


@num_jit
def quat_mult(q1, q2):
    w0, x0, y0, z0 = q1
    w1, x1, y1, z1 = q2
    return np.array(
        [
            w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1,
            w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1,
            w0 * y1 - x0 * z1 + y0 * w1 + z0 * x1,
            w0 * z1 + x0 * y1 - y0 * x1 + z0 * w1,
        ]
    )


@num_jit
def quat_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


@num_jit
def quat_rotate(v, q):
    """
    Rotate vector v by quaternion q.
    """
    # q_v = [0, v...]
    q_v = np.array([0.0, v[0], v[1], v[2]])
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

    # q * v * q_conj
    # q_temp = q * q_v

    q_temp = quat_mult(q, q_v)
    q_res = quat_mult(q_temp, q_conj)

    return q_res[1:]


@num_jit
def quat_derivative(q, omega):
    """
    Kinematic derivative of quaternion.
    q_dot = 0.5 * Omega * q
    """
    wx, wy, wz = omega
    q0, q1, q2, q3 = q
    # 0.5 * Omega * q
    return np.array(
        [
            0.5 * (-q1 * wx - q2 * wy - q3 * wz),
            0.5 * (q0 * wx + q2 * wz - q3 * wy),
            0.5 * (q0 * wy - q1 * wz + q3 * wx),
            0.5 * (q0 * wz + q1 * wy - q2 * wx),
        ]
    )
