import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath("."))
from lincore.analysis.sensitivity import sobol_sensitivity


def ishigami_function(X):
    # Test function: f(x) = sin(x1) + a*sin(x2)^2 + b*x3^4*sin(x1)
    # Common benchmark for Sobol
    a = 7
    b = 0.1
    x1 = X[:, 0]
    x2 = X[:, 1]
    x3 = X[:, 2]
    return np.sin(x1) + a * np.sin(x2) ** 2 + b * x3**4 * np.sin(x1)


def test_sobol_indices():
    problem = {
        "num_vars": 3,
        "names": ["x1", "x2", "x3"],
        "bounds": [[-np.pi, np.pi], [-np.pi, np.pi], [-np.pi, np.pi]],
    }

    indices = sobol_sensitivity(ishigami_function, problem, n_samples=5000)

    print("Sobol Indices:", indices)

    # Expected analytical S1:
    # x1: ~0.31
    # x2: ~0.44
    # x3: ~0.0 (interaction only)

    assert indices["x2"] > indices["x1"]
    assert indices["x3"] < 0.1  # Should be small S1


if __name__ == "__main__":
    test_sobol_indices()
