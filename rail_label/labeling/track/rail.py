from __future__ import annotations
import functools
import numpy
import splines
import numpy as np
from rail_label.labeling.scene.point import ImagePoint
from rail_label.utils.camera import Camera


class RailPoint(ImagePoint):
    """
    Represent point on rail.
    """

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def __lt__(self, other: RailPoint) -> bool:
        """
        One rail point is less than the other if it has a larger
        y-axis value, i.e. it is closer to the observer.
        :param other: Other rail point.
        """
        return self.y < other.y

    def midpoint(self, other: RailPoint):
        """
        Calculate midpoint between this point and other point.
        :param other: Other point
        :return: Midpoint
        """
        mean: np.ndarray = np.mean((self._point, other._point), axis=0)
        # Pixels are discrete values
        mean = np.rint(mean).astype(int)
        # TODO: How to create Class from derived Class type, not base class?
        midpoint: RailPoint = RailPoint(mean[0], mean[1])
        return midpoint


class Rail:
    """
    Represent one rail of a track.
    """

    def __init__(self, width) -> None:
        """
        :param width: Rail width in mm
        """
        self._width = width
        self._marks: list[RailPoint] = []

    @property
    def width(self) -> int:
        return self._width

    @property
    def marks(self) -> list[RailPoint]:
        return self._marks

    @marks.setter
    def marks(self, marks: RailPoint) -> None:
        self._marks = marks
        self._marks = sorted(self._marks)

    def splines(self, steps) -> list[RailPoint]:
        """
        Get interpolated points for marks.
        :param steps: Interpolation steps
        :return: Interpolated rail points
        """
        # Calculate splines if at leas two points are available.
        if len(self._marks) > 1:
            mark: RailPoint
            mark_points_arr: np.ndarray
            mark_points_arr = np.vstack([mark.point for mark in self._marks])
            sp: splines.CatmullRom
            sp = splines.CatmullRom(mark_points_arr, endconditions="natural")
            total_duration: int = sp.grid[-1] - sp.grid[0]
            t: numpy.ndarray
            t = np.linspace(0, total_duration, len(mark_points_arr) * steps)
            splines_arr: np.ndarray
            splines_arr = sp.evaluate(t)
            # Round splines because it represents discrete pixels
            splines_arr = np.rint(splines_arr).astype(int)
            spline_arr: np.array
            spline_points = [
                RailPoint(spline_arr[0], spline_arr[1]) for spline_arr in splines_arr
            ]
            return spline_points
        else:
            return []

    def contour_points(
        self, camera: Camera, steps: int, contour_side="both"
    ) -> list[RailPoint]:
        """
        Get points describing contour around the rail.
        The dots describe the contour of the rail clockwise starting
        from the bottom left.
        :param camera: Camera translating world- and image
                       coordinates.
        :param steps: Interpolation steps
        :param side: Part of contour points ['left', 'right' 'both']
        :return: Points describing rail contour
        """
        contour_points_left: list[RailPoint] = []
        contour_points_right: list[RailPoint] = []
        spline_point: RailPoint
        for spline_point in self.splines(steps):
            for side in [-1, 1]:
                # Grid points to the left
                spline_point_world_arr: np.ndarray = camera.pixel_to_world(
                    spline_point.point
                )
                contour_point_world_arr: np.ndarray = spline_point_world_arr
                # Left side add half of rail width, right side subtracts half of rail width.
                contour_point_world_arr[0] = (
                    spline_point_world_arr[0] + self.width * side / 2
                )
                contour_point_image_arr: np.ndarray = camera.world_to_pixel(
                    contour_point_world_arr
                )
                # Round coordinate because it represents discrete pixels
                contour_point_image_arr = np.rint(contour_point_image_arr).astype(int)
                contour_point: RailPoint
                contour_point = RailPoint(
                    contour_point_image_arr[0], contour_point_image_arr[1]
                )
                if side == -1:
                    contour_points_left.append(contour_point)
                else:
                    contour_points_right.append(contour_point)

        # Reverse to get clockwise point pattern
        contour_points_right = contour_points_right[::-1]
        contour_points: list[RailPoint] = [*contour_points_left, *contour_points_right]

        if contour_side == "both":
            return contour_points
        elif contour_side == "left":
            return contour_points_left
        elif contour_side == "right":
            return contour_points_right
        else:
            msg = f"Expected parameter side to be in ['left', 'rigt', 'both'], got '{contour_side}'"
            raise ValueError(msg)

    def add_mark(self, mark: RailPoint) -> None:
        """
        Add one mark to the rail.
        :param mark: Mark to add.
        :return:
        """
        self._marks.append(mark)
        self._marks = sorted(self._marks)

    def del_mark(self, mark: RailPoint) -> None:
        """
        Delete marking point near to given marking point.
        :param mark: Rough marking point to delete
        :return:
        """
        # Can only delete point if there is at least one
        if len(self._marks) >= 1:
            mark_points_arr: np.ndarray
            mark_points_arr = np.vstack([mark.point for mark in self._marks])
            # Calculate euclidean distance for all points
            distances: np.ndarray = np.linalg.norm(mark_points_arr - mark.point, axis=1)
            lowest_dist_index: int = np.argmin(distances).item()
            self._marks.pop(lowest_dist_index)

    def to_dict(self) -> dict:
        rail: dict = {"points": [mark.point.tolist() for mark in self._marks]}
        return rail


def main():
    pass


if __name__ == "__main__":
    main()
