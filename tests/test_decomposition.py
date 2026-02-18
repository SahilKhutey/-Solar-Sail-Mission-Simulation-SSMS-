import math
import pytest

from lincore.matrix import Matrix
from lincore.vector import Vector
from lincore.decomposition import (
    lu_decomposition,
    solve_lu,
    determinant_lu,
    qr_decomposition,
    conjugate_gradient
)


# -------------------------
# LU Decomposition Tests
# -------------------------

def test_lu_reconstruction():
    A = Matrix([[4, 3],
                [6, 3]])

    L, U, P = lu_decomposition(A)

    # Reconstruct PA
    PA = [A.data[P[i]] for i in range(A.rows)]
    PA_matrix = Matrix(PA)

    LU = L.matmul(U)

    for i in range(A.rows):
        for j in range(A.cols):
            assert math.isclose(PA_matrix.data[i][j],
                                LU.data[i][j],
                                rel_tol=1e-9)


def test_lu_solve():
    A = Matrix([[3, 1],
                [1, 2]])
    b = [9, 8]

    L, U, P = lu_decomposition(A)
    x = solve_lu(L, U, P, b)

    # Expected solution: x = [2, 3]
    assert math.isclose(x[0], 2.0, rel_tol=1e-9)
    assert math.isclose(x[1], 3.0, rel_tol=1e-9)


def test_determinant_lu():
    A = Matrix([[4, 3],
                [6, 3]])

    det = determinant_lu(A)

    # Manual determinant = 4*3 - 6*3 = -6
    assert math.isclose(det, -6.0, rel_tol=1e-9)


# -------------------------
# QR Decomposition Tests
# -------------------------

def test_qr_reconstruction():
    A = Matrix([[12, -51],
                [6, 167]])

    Q, R = qr_decomposition(A)

    QR = Q.matmul(R)

    for i in range(A.rows):
        for j in range(A.cols):
            assert math.isclose(QR.data[i][j],
                                A.data[i][j],
                                rel_tol=1e-5)


def test_q_orthogonality():
    A = Matrix([[12, -51],
                [6, 167]])

    Q, R = qr_decomposition(A)
    QT = Q.transpose()
    I = QT.matmul(Q)

    for i in range(I.rows):
        for j in range(I.cols):
            if i == j:
                assert math.isclose(I.data[i][j], 1.0, rel_tol=1e-5)
            else:
                assert abs(I.data[i][j]) < 1e-5


# -------------------------
# Conjugate Gradient Tests
# -------------------------

def test_conjugate_gradient():
    A = Matrix([[4, 1],
                [1, 3]])
    b = [1, 2]

    x = conjugate_gradient(A, b)

    # Expected solution: [0.0909..., 0.6363...]
    assert math.isclose(x[0], 0.090909, rel_tol=1e-4)
    assert math.isclose(x[1], 0.636364, rel_tol=1e-4)
