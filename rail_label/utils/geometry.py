import numpy as np


class Line:
    """
    Represent
    """

    def __init__(self, p: np.ndarray, a: np.ndarray):
        """ """
        self.p: np.ndarray = p
        self.a: np.ndarray = a


class Plane:
    """ """

    def __init__(self, c: np.ndarray, r: float):
        """ """
        self.c: np.ndarray = c
        self.r: float = r


def intersection(plane: Plane, line: Line):
    p: float = plane.r - np.dot(plane.c, line.p)
    q: np.ndarray = np.dot(plane.c, line.a.T)
    intersect = line.p + p / q * line.a
    return intersect


def main():
    pass


if __name__ == "__main__":
    main()
