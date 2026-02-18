# tests/test_eigen.py

import math
from lincore.matrix import Matrix
from lincore.eigen import power_iteration



def test_power_iteration_simple():
    A = Matrix([[2, 0], [0, 1]])
    eigenvalue, eigenvector = power_iteration(A)

    assert math.isclose(eigenvalue, 2.0, rel_tol=1e-5)


def test_power_iteration_symmetric():
    A = Matrix([[4, 1],
                [1, 3]])
    eigenvalue, eigenvector = power_iteration(A)

    # Dominant eigenvalue approx 4.618
    assert math.isclose(eigenvalue, 4.618, rel_tol=1e-2)


def test_eigenvector_direction():
    A = Matrix([[3, 0],
                [0, 2]])

    eigenvalue, v = power_iteration(A)

    # Should align with x-axis
    assert abs(v.data[1]) < 1e-3
