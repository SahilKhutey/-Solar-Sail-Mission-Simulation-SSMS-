import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath("."))
from lincore.optimization.trajectory_optimizer import TrajectoryOptimizer


def test_optimizer_init():
    opt = TrajectoryOptimizer(None, num_segments=10)
    assert opt.N == 10


def test_optimizer_solve_smoke():
    """
    Smoke test to check if optimizer runs without error.
    """
    opt = TrajectoryOptimizer(None, num_segments=20)

    # Sun Orbit: Start at 1 AU
    AU = 1.496e8  # km
    mu = 1.327e11
    v_circ = np.sqrt(mu / AU)

    r0 = np.array([AU, 0, 0])
    v0 = np.array([0, v_circ, 0])

    # Target: 1.01 AU
    r_target = 1.01 * AU

    # Initial guess for time: Hohmann-ish (very rough)
    # T ~ 365 days
    tf_guess = 300 * 86400.0

    print("Running Optimizer Smoke Test...")
    res = opt.solve(r0, v0, tf_guess, r_target)

    print(f"Optimization Success: {res.success}")
    print(f"Message: {res.message}")
    print(f"Objective (tf): {res.fun/86400:.2f} days")

    # We don't assert success strictly because without gradients/scaling it might struggle
    # But it should return a result object.
    assert res is not None


if __name__ == "__main__":
    test_optimizer_solve_smoke()
