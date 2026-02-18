# tests/test_vector.py

import math
import pytest
from lincore.vector import Vector



def test_vector_addition():
    a = Vector([1, 2, 3])
    b = Vector([4, 5, 6])
    result = a + b
    assert result.data == [5, 7, 9]


def test_vector_subtraction():
    a = Vector([5, 7, 9])
    b = Vector([1, 2, 3])
    result = a - b
    assert result.data == [4, 5, 6]


def test_dot_product():
    a = Vector([1, 2, 3])
    b = Vector([4, -5, 6])
    assert a.dot(b) == 12  # 1*4 + 2*(-5) + 3*6


def test_cross_product():
    a = Vector([1, 0, 0])
    b = Vector([0, 1, 0])
    c = a.cross(b)
    assert c.data == [0, 0, 1]


def test_cross_orthogonality():
    a = Vector([1, 2, 3])
    b = Vector([4, 5, 6])
    c = a.cross(b)
    assert abs(c.dot(a)) < 1e-10
    assert abs(c.dot(b)) < 1e-10


def test_norm_l2():
    v = Vector([3, 4])
    assert math.isclose(v.norm(), 5.0)


def test_norm_l1():
    v = Vector([-1, 2, -3])
    assert v.norm(order=1) == 6


def test_unit_vector():
    v = Vector([3, 4])
    u = v.unit()
    assert math.isclose(u.norm(), 1.0, rel_tol=1e-9)
