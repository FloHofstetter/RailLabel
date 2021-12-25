import unittest
import numpy as np
from scene.camera.geometry import Line


class TestLine(unittest.TestCase):
    def test_p_p(self) -> None:
        """
        Assert the Line.p property.
        """
        with self.subTest(msg="Return correct property"):
            p: np.ndarray = np.array([5, 10], dtype=int)
            a: np.ndarray = np.array([10, 20], dtype=int)

            line: Line = Line(p, a)

            self.assertTrue(np.array_equal(line.p, p))

        with self.subTest(msg="Return correct type"):
            p: np.ndarray = np.array([5.0, 10.0], dtype=float)
            a: np.ndarray = np.array([10.0, 20.0], dtype=float)

            line: Line = Line(p, a)

            p = p.astype(int)

            self.assertTrue(line.p.dtype == p.dtype)

    def test_p_a(self) -> None:
        """
        Assert the Line.a property.
        """
        with self.subTest(msg="Return correct property"):
            p: np.ndarray = np.array([5, 10], dtype=int)
            a: np.ndarray = np.array([10, 20], dtype=int)

            line: Line = Line(p, a)

            self.assertTrue(np.array_equal(line.a, a))

        with self.subTest(msg="Return correct type"):
            p: np.ndarray = np.array([5.0, 10.0], dtype=float)
            a: np.ndarray = np.array([10.0, 20.0], dtype=float)

            line: Line = Line(p, a)

            a = a.astype(int)

            self.assertTrue(line.a.dtype == a.dtype)
