from __future__ import annotations
from typing import Union
import numpy as np


class ImagePoint:
    """
    Represents a point in image coordinates aka. pixel coordinates.
    """

    def __init__(self, x: Union[int, float], y: Union[int, float]) -> None:
        """
        :param x: X coordinate
        :param y: Y coordinate
        """
        self._point: np.ndarray
        self._point = np.rint(np.array([x, y])).astype(int)

    def __eq__(self, other: ImagePoint) -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __str__(self) -> str:
        msg: str = f"x={self.x} y={self.y}"
        return msg

    @property
    def point(self) -> np.ndarray:
        return self._point

    @property
    def x(self) -> int:
        return self._point[0].item()

    @property
    def y(self) -> int:
        return self._point[1].item()

    def midpoint(self, other: ImagePoint) -> ImagePoint:
        """
        Calculate midpoint between this point and other point.
        :param other: Other point
        :return: Midpoint
        """
        mean: np.ndarray = np.mean((self._point, other._point), axis=0)
        # Pixels are discrete values
        mean: np.ndarray = np.rint(mean).astype(int)
        midpoint: ImagePoint = self.__class__(*mean)
        return midpoint


class WorldPoint(ImagePoint):
    """
    Represents a point in word coordinates.
    """

    def __init__(
        self,
        x: Union[int, float],
        y: Union[int, float],
        z: Union[int, float],
    ) -> None:
        """
        :param x: X coordinate
        :param y: Y coordinate
        :param z: Z coordinate
        """
        super().__init__(x, y)
        z: int = np.rint(z).astype(int).item()
        self._point = np.append(self._point, z)

    def __eq__(self, other: WorldPoint) -> bool:
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        else:
            return False

    def __str__(self) -> str:
        msg: str = f"x={self.x} y={self.y} z={self.z}"
        return msg

    @property
    def z(self) -> int:
        return self._point[2].item()
