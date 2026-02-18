# tests/test_matrix.py

import math
from lincore.matrix import Matrix
from lincore.vector import Vector


def test_matrix_addition():
    A = Matrix([[1, 2], [3, 4]])
    B = Matrix([[5, 6], [7, 8]])
    C = A + B
    assert C.data == [[6, 8], [10, 12]]


def test_matrix_transpose():
    A = Matrix([[1, 2, 3], [4, 5, 6]])
    AT = A.transpose()
    assert AT.data == [[1, 4], [2, 5], [3, 6]]


def test_matrix_multiplication():
    A = Matrix([[1, 2], [3, 4]])
    B = Matrix([[2, 0], [1, 2]])
    C = A.matmul(B)
    assert C.data == [[4, 4], [10, 8]]


def test_matrix_vector_multiplication():
    A = Matrix([[1, 2], [3, 4]])
    v = Vector([1, 1])
    result = A.matvec(v)
    assert result == [3, 7]


def test_identity_behavior():
    I = Matrix([[1, 0], [0, 1]])
    A = Matrix([[5, 6], [7, 8]])
    result = I.matmul(A)
    assert result.data == A.data
