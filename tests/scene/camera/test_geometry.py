import unittest
import pytest
import numpy as np
from scene.camera.geometry import Line, Plane, intersection


class TestLine(unittest.TestCase):
    def test_p_p(self) -> None:
        """
        Assert the Line.p property.
        """
        with self.subTest(msg="Return correct property"):
            p: np.ndarray = np.array([5, 10, 15])
            a: np.ndarray = np.array([10, 20, 30])

            line: Line = Line(p, a)

            assert np.array_equal(line.p, p)

    def test_p_a(self) -> None:
        """
        Assert the Line.a property.
        """
        with self.subTest(msg="Return correct property"):
            p: np.ndarray = np.array([5, 10, 15])
            a: np.ndarray = np.array([10, 20, 30])

            line: Line = Line(p, a)

            assert np.array_equal(line.a, a)


class TestPlane(unittest.TestCase):
    def test_p_c(self) -> None:
        """
        Assert the Plane.c property.
        """
        with self.subTest(msg="Return correct property"):
            c: np.ndarray = np.array([23, 17, 11])
            r: float = 15.0

            plane: Plane = Plane(c, r)

            assert np.array_equal(plane.c, c)

    def test_p_r(self) -> None:
        """
        Assert the Plane.r property.
        """
        with self.subTest(msg="Return correct property"):
            c: np.ndarray = np.array([5, 10])
            r: float = 15.0

            plane: Plane = Plane(c, r)

            assert plane.r == r


@pytest.mark.skip
def test_m_intersection() -> None:
    """
    Assert the Plane.intersection methode.
    """
    p: np.ndarray = np.array([5, 10])
    a: np.ndarray = np.array([10, 20])
    line: Line = Line(p, a)

    c: np.ndarray = np.array([5, 10], dtype=int)
    r: float = 15.0
    plane: Plane = Plane(c, r)

    # intersect = intersection(plane, line)
    # TODO: Write testcase
    assert False
