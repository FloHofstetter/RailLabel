from __future__ import annotations
import numpy as np


class ImagePoint:
    """
    Represents a point in image coordinates aka. pixel coordinates.
    """

    def __init__(self, x: int, y: int):
        """

        :param x: X coordinate
        :param y: Y coordinate
        :return: None
        """
        self._point: np.ndarray = np.array([x, y])

    def __str__(self):
        msg = f"X:{self.x} Y:{self.y}"
        return str(msg)

    @property
    def point(self):
        return self._point

    @property
    def x(self):
        return self._point[0]

    @property
    def y(self):
        return self._point[1]

    def midpoint(self, other: ImagePoint):
        """
        Calculate midpoint between this point and other point.
        :param other: Other point
        :return: Midpoint
        """
        mean: np.ndarray = np.mean((self._point, other._point), axis=0)
        # Pixels are discrete values
        mean = np.rint(mean).astype(int)
        midpoint: ImagePoint = ImagePoint(mean[0], mean[1])
        return midpoint


class WorldPoint(ImagePoint):
    """
    Represents a point in word coordinates.
    """

    def __init__(self, x: int, y: int, z: int):
        """

        :param x: X coordinate
        :param y: Y coordinate
        :param z: Z coordinate
        :return: None
        """
        super().__init__(x, y)
        self._point = np.append(self._point, z)

    def __str__(self):
        msg = f"X:{self.x} Y:{self.y} Z:{self.z}"
        return str(msg)

    @property
    def z(self):
        return self._point[2]


def main():
    a = ImagePoint(4, 8)
    b = WorldPoint(5, 2, 18)

    print(a)
    print(b)


if __name__ == "__main__":
    main()
