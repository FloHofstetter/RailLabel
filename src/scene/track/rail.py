import splines
import numpy as np
from scene.camera.camera import Camera
from scene.track.rail_point import RailPoint


class Rail:
    """
    Represent one rail of a track.
    """

    def __init__(self, width) -> None:
        """
        :param width: Rail width in mm
        """
        self._width: float = width
        self._marks: list[RailPoint] = []

    @property
    def width(self) -> float:
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
            t: np.ndarray
            t = np.linspace(0, total_duration, len(mark_points_arr) * steps)
            splines_arr: np.ndarray
            splines_arr = sp.evaluate(t)
            # Round splines because it represents discrete pixels
            splines_arr = np.rint(splines_arr).astype(int)
            spline_arr: np.array
            spline_points = []
            for spline_arr in splines_arr:
                spline_point: RailPoint
                spline_point = RailPoint(spline_arr[0].item(), spline_arr[1].item())
                spline_points.append(spline_point)
            return spline_points
        else:
            return []

    def _contour_point(
        self, camera: Camera, spline_point: RailPoint, side: int
    ) -> RailPoint:
        """
        Calculate points on contour for given side on given spline_point.
        :param camera: Camera translating world- and image
                       coordinates
        :param spline_point: Point on center of rail
        :param side: Contour side relative to mid of the rail
        :return: Contur point
        """
        # Grid points to the left
        spline_point_world_arr: np.ndarray
        spline_point_world_arr = camera.pixel_to_world(spline_point.point)
        contour_point_world_arr: np.ndarray
        contour_point_world_arr = spline_point_world_arr
        # Left side add half of rail width, right side subtracts half of rail width.
        contour_point_world_arr[0] = spline_point_world_arr[0] + self.width * side / 2
        contour_point_image_arr: np.ndarray
        contour_point_image_arr = camera.world_to_pixel(contour_point_world_arr)
        # Round coordinate because it represents discrete pixels
        contour_point_image_arr = np.rint(contour_point_image_arr).astype(int)
        contour_point: RailPoint
        contour_point = RailPoint(
            contour_point_image_arr[0].item(),
            contour_point_image_arr[1].item(),
        )
        return contour_point

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
        :param contour_side: Part of contour points ['left', 'right' 'both']
        :return: Points describing rail contour
        """
        contour_points_left: list[RailPoint] = []
        contour_points_right: list[RailPoint] = []
        spline_point: RailPoint
        for spline_point in self.splines(steps):
            for side in [-1, 1]:
                contour_point = self._contour_point(camera, spline_point, side)
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
            msg = f"Expected parameter side to be in ['left', 'right', 'both'],"
            msg += f" got '{contour_side}'"
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
