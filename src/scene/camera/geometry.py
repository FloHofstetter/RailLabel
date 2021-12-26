from typing import Union
import numpy as np


class Line:
    """
    Represent
    """

    def __init__(self, p: np.ndarray, a: np.ndarray) -> None:
        """ """
        self.p: np.ndarray = p
        self.a: np.ndarray = a


class Plane:
    """ """

    def __init__(self, c: np.ndarray, r: Union[float, int]) -> None:
        """ """
        self.c: np.ndarray = c
        self.r: Union[int, float] = r


def intersection(plane: Plane, line: Line) -> np.ndarray:
    p: float = plane.r - np.dot(plane.c, line.p)
    q: np.ndarray = np.dot(plane.c, line.a.T)
    intersect = line.p + p / q * line.a
    return intersect
