from typing import Union
import numpy as np


class ImagePoint:
    """
    Represents a point in image coordinates aka. pixel coordinates.
    """

    def __init__(self, x: Union[int, float], y: Union[int, float]):
        """
        :param x: X coordinate
        :param y: Y coordinate
        :return: None
        """
        self._point: np.ndarray
        self._point = np.rint(np.array([x, y])).astype(int)

    def __str__(self):
        msg = f"X:{self.x} Y:{self.y}"
        return str(msg)

    @property
    def point(self):
        return self._point

    @property
    def x(self):
        return self._point[0].item()

    @property
    def y(self):
        return self._point[1].item()

    def midpoint(self, other: "ImagePoint"):
        """
        Calculate midpoint between this point and other point.
        :param other: Other point
        :return: Midpoint
        """
        mean: np.ndarray = np.mean((self._point, other._point), axis=0)
        # Pixels are discrete values
        mean = np.rint(mean).astype(int)
        midpoint: ImagePoint = self.__class__(mean[0], mean[1])
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
    pass


if __name__ == "__main__":
    main()
