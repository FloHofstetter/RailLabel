import unittest
import numpy as np
from rail_label.labeling.scene.point import ImagePoint


class TestImagePoint(unittest.TestCase):
    def test_p_x(self) -> None:
        """
        Assert the self.x property.
        """
        with self.subTest(msg="Return correct property"):
            x: int = 5
            y: int = 10
            image_point: ImagePoint = ImagePoint(x, y)
            self.assertAlmostEqual(image_point.x, 5)

        with self.subTest(msg="Return correct type"):
            x: float = 5.0
            y: float = 10.0
            image_point: ImagePoint = ImagePoint(x, y)
            self.assertIsInstance(image_point.x, int)

    def test_p_y(self) -> None:
        """
        Assert the self.y property.
        """
        with self.subTest(msg="Return correct property"):
            x: int = 5
            y: int = 10
            image_point: ImagePoint = ImagePoint(x, y)
            self.assertAlmostEqual(image_point.y, 5)

        with self.subTest(msg="Return correct type"):
            x: float = 5.0
            y: float = 10.0
            image_point: ImagePoint = ImagePoint(x, y)
            self.assertIsInstance(image_point.y, int)

    def test_p_point(self) -> None:
        """
        Assert the self.point property.
        """
        with self.subTest(msg="Return correct point"):
            x: int = 5
            y: int = 10
            image_point: ImagePoint = ImagePoint(x, y)
            point = np.array([5, 10], dtype=int)
            self.assertTrue(np.allclose(image_point.point, point))

        with self.subTest(msg="Return correct type"):
            x: int = 5
            y: int = 10
            image_point: ImagePoint = ImagePoint(x, y)
            self.assertIsInstance(image_point.point, np.int)

    def test_m_midpoint(self) -> None:
        """
        Assert correct calculation of midpoint between two
        ImagePoints.
        """
        x, y = 5, 10
        image_point_a = ImagePoint(x, y)
        x, y = 15, 20
        image_point_b = ImagePoint(x, y)

        image_point_c = image_point_a.midpoint(image_point_b)

        self.assertAlmostEqual(image_point_c.x, 10)
        self.assertAlmostEqual(image_point_c.y, 15)


if __name__ == "__main__":
    unittest.main()
