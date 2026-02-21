import numpy as np
import sys
import os

sys.path.append(os.path.abspath("."))

from lincore.attitude.rigid_body import attitude_derivative
from lincore.core.integrator import rk45_step


def test_attitude_stability():
    """
    Test Case 5: Attitude Stability (Tennis Racket Theorem)
    Inertia I1 < I2 < I3.
    Rotate about axes.
    1 (Min) -> Stable
    2 (Int) -> Unstable
    3 (Max) -> Stable
    """
    print("\nTesting Attitude Stability...")

    # Inertia: Diagonal [10, 20, 30]
    I = np.diag([10.0, 20.0, 30.0])
    I_inv = np.linalg.inv(I)

    dt = 0.1
    duration = 100.0

    def dynamics(t, y):
        # y = [q, w]
        q = y[:4]
        w = y[4:]
        torque = [0, 0, 0]
        dq, dw = attitude_derivative(q.tolist(), w.tolist(), I.tolist(), torque)
        return np.concatenate((dq, dw))

    def run_case(axis_idx, name):
        # Perturbed initial velocity
        w0 = np.zeros(3)
        w0[axis_idx] = 1.0
        # Small perturbation on other axes
        w0[(axis_idx + 1) % 3] = 0.01

        y = np.array([1, 0, 0, 0, w0[0], w0[1], w0[2]])
        t = 0
        dt = 0.1  # Local init

        w_max_pert = 0.0

        while t < duration:
            success, t_next, y_next, dt_next = rk45_step(dynamics, t, y, dt, 1e-6)
            if success:
                t = t_next
                y = y_next
            dt = dt_next

            # Check perturbation growth
            w_curr = y[4:]

            # Magnitude of orthogonal components
            w_main = w_curr[axis_idx]
            w_orth = np.linalg.norm(w_curr) - abs(w_main)
            # Better: sqrt(w_y^2 + w_z^2)
            orth_mag = np.sqrt(np.sum(w_curr**2) - w_main**2)

            w_max_pert = max(w_max_pert, orth_mag)

        print(f"Axis {name}: Max Perturbation = {w_max_pert:.4f}")
        return w_max_pert

    # 1. Min Axis (X) -> Stable
    p1 = run_case(0, "Min (X)")
    assert p1 < 0.2, "Min axis should be stable (small perturbation growth)"

    # 2. Max Axis (Z) -> Stable
    p3 = run_case(2, "Max (Z)")
    assert p3 < 0.2, "Max axis should be stable"

    # 3. Intermediate Axis (Y) -> Unstable
    p2 = run_case(1, "Int (Y)")
    print(f"Intermediate perturbation: {p2}")
    assert p2 > 0.5, "Intermediate axis should be unstable (large perturbation growth)"


def test_quaternion_norm():
    """
    Test Case 5: Quaternion Norm
    """
    print("\nTesting Quaternion Norm...")
    I = np.diag([10.0, 10.0, 10.0])
    # Fast rotation
    y = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

    def dynamics(t, y):
        q = y[:4]
        w = y[4:]
        dq, dw = attitude_derivative(q.tolist(), w.tolist(), I.tolist(), [0, 0, 0])
        return np.concatenate((dq, dw))

    t = 0
    dt = 0.01
    duration = 10.0

    norms = []
    while t < duration:
        success, t_next, y_next, dt_next = rk45_step(dynamics, t, y, dt, 1e-9)
        if success:
            t = t_next
            y = y_next
            q = y[:4]
            norms.append(np.linalg.norm(q))
        dt = dt_next

    max_drift = max([abs(n - 1.0) for n in norms])
    print(f"Max Quaternion Drift: {max_drift:.2e}")
    assert max_drift < 1e-8, "Quaternion norm drifted too much"


if __name__ == "__main__":
    test_attitude_stability()
    test_quaternion_norm()
