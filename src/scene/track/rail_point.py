from __future__ import annotations
from typing import Union
from scene.point import ImagePoint


class RailPoint(ImagePoint):
    """
    Represent point on rail.
    """

    def __init__(self, x: Union[int, float], y: Union[int, float]):
        super().__init__(x, y)

    def __lt__(self, other: RailPoint) -> bool:
        """
        One rail point is less than the other if it has a larger
        y-axis value, i.e. it is closer to the observer.
        :param other: Other rail point.
        """
        return self.y < other.y
