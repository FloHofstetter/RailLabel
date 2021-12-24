import unittest
import numpy as np
from labeling.scene.point import ImagePoint, WorldPoint


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
            self.assertAlmostEqual(image_point.y, 10)

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
            self.assertTrue(image_point.point.dtype == point.dtype)

    def test_m_midpoint(self) -> None:
        """
        Assert correct calculation of midpoint between two
        ImagePoints.
        """
        x, y = 5, 10
        image_point_a: ImagePoint = ImagePoint(x, y)
        x, y = 15, 20
        image_point_b: ImagePoint = ImagePoint(x, y)

        image_point_c: ImagePoint = image_point_a.midpoint(image_point_b)

        self.assertAlmostEqual(image_point_c.x, 10)
        self.assertAlmostEqual(image_point_c.y, 15)


class TestWorldPoint(unittest.TestCase):
    def test_p_x(self) -> None:
        """
        Assert the self.x property.
        """
        with self.subTest(msg="Return correct property"):
            x: int = 5
            y: int = 10
            z: int = 15
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertAlmostEqual(world_point.x, 5)

        with self.subTest(msg="Return correct type"):
            x: float = 5.0
            y: float = 10.0
            z: float = 15.0
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertIsInstance(world_point.x, int)

    def test_p_y(self) -> None:
        """
        Assert the self.y property.
        """
        with self.subTest(msg="Return correct property"):
            x: int = 5
            y: int = 10
            z: int = 15
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertAlmostEqual(world_point.y, 10)

        with self.subTest(msg="Return correct type"):
            x: float = 5.0
            y: float = 10.0
            z: float = 15.0
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertIsInstance(world_point.y, int)

    def test_p_z(self) -> None:
        """
        Assert the self.z property.
        """
        with self.subTest(msg="Return correct property"):
            x: int = 5
            y: int = 10
            z: int = 15
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertAlmostEqual(world_point.z, 15)

        with self.subTest(msg="Return correct type"):
            x: float = 5.0
            y: float = 10.0
            z: float = 15.0
            world_point: WorldPoint = WorldPoint(x, y, z)
            self.assertIsInstance(world_point.z, int)

    def test_p_point(self) -> None:
        """
        Assert the self.point property.
        """
        with self.subTest(msg="Return correct point"):
            x: int = 5
            y: int = 10
            z: int = 15
            world_point: WorldPoint = WorldPoint(x, y, z)
            point = np.array([5, 10, 15], dtype=int)
            self.assertTrue(world_point.point.dtype == point.dtype)

    def test_m_midpoint(self) -> None:
        """
        Assert correct calculation of midpoint between two
        ImagePoints.
        """
        x: int = 5
        y: int = 10
        z: int = 15
        world_point_a: WorldPoint = WorldPoint(x, y, z)
        x: int = 20
        y: int = 25
        z: int = 30
        world_point_b: WorldPoint = WorldPoint(x, y, z)

        world_point_c: WorldPoint = world_point_a.midpoint(world_point_b)
        # For behaviour on rounding x.5 values look at:
        # https://numpy.org/doc/stable/reference/generated/numpy.rint.html
        self.assertAlmostEqual(world_point_c.x, 12)  # Odd x.5 round down
        self.assertAlmostEqual(world_point_c.y, 18)  # Even x.5 round up
        self.assertAlmostEqual(world_point_c.z, 22)  # Odd x.5 round down


if __name__ == "__main__":
    unittest.main()
