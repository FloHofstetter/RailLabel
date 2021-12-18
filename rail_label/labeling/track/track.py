import cv2
import numpy as np
import splines
import functools

from rail_label.utils.camera import Camera
from rail_label.labeling.track.rail import Rail, RailPoint


class Track:
    """
    Represents all information of a track.
    """

    def __init__(self, track_id, relative_position: str) -> None:
        """
        :param track_id: Id of track
        :param relative_position: Position relative to ego track
        """
        self._id = track_id
        self._relative_position: str = relative_position
        self._left_rail: Rail = Rail(67)
        self._right_rail = Rail(67)
        self._center_points: list[RailPoint] = []
        self._track_bed_spline_points: list[RailPoint] = []

    @property
    def id(self) -> int:
        return self._id

    def __str__(self) -> None:
        msg = f"ID: {self.id}, {self.relative_position}"
        return msg

    @property
    def relative_position(self) -> str:
        return self._relative_position

    @property
    def right_rail(self) -> Rail:
        return self._right_rail

    @right_rail.setter
    def right_rail(self, right_rail: Rail):
        self._right_rail = right_rail

    @property
    def left_rail(self) -> Rail:
        return self._left_rail

    @left_rail.setter
    def left_rail(self, left_rail: Rail):
        self._left_rail = left_rail

    @property
    def center_points(self) -> list[RailPoint]:
        """
        Center points between two rail points if there are
        same amount on left and right side.
        :return: Center points between rails
        """
        left_point: RailPoint
        right_point: RailPoint
        center_points: list[RailPoint] = []
        len_left: int = len(self.left_rail.marks)
        len_right: int = len(self.right_rail.marks)
        # Midpoints exist only between respectively two points
        if len_left == len_right and len_right > 0:
            for left_point, right_point in zip(
                self.left_rail.marks, self.right_rail.marks
            ):
                center_point: RailPoint = left_point.midpoint(right_point)
                center_points.append(center_point)
                self._center_points = center_points
        else:
            self._center_points = []
        return self._center_points

    def track_bed_spline_points(self, camera: Camera, steps: int) -> list[RailPoint]:
        """
        Polygon points between two rails aka. track bed.
        :param camera: Camera translating world- and image
                       coordinates.
        :param steps: Interpolation steps
        :return: Trackbed polygon points
        """
        left_rail_splines: list[RailPoint]
        left_rail_splines = self.left_rail.contour_points(
            camera, steps, contour_side="right"
        )
        right_rail_splines: list[RailPoint]
        right_rail_splines = self.right_rail.contour_points(
            camera, steps, contour_side="left"
        )
        self._track_bed_spline_points = [*left_rail_splines, *right_rail_splines]
        return self._track_bed_spline_points

    def add_left_mark(self, mark: RailPoint) -> None:
        """
        Add mark point to left rail.
        :param mark: Mark point.
        """
        self.left_rail.add_mark(mark)

    def del_left_mark(self, mark: RailPoint) -> None:
        """
        Delete marking point near to given marking point on the left
        rail.
        :param mark: Rough marking point to delete
        :return:
        """
        self.left_rail.del_mark(mark)

    def add_right_mark(self, mark: RailPoint) -> None:
        """
        Add mark point to left rail.
        :param mark: Mark point.
        """
        self.right_rail.add_mark(mark)

    def del_right_mark(self, mark: RailPoint) -> None:
        """
        Delete marking point near to given marking point on the right
        rail.
        :param mark: Rough marking point to delete
        :return:
        """
        self.right_rail.del_mark(mark)

    def to_dict(self) -> dict:
        """
        Dict representation of a track.
        """
        track: dict = {
            "relative position": self.relative_position,
            "left rail": self._left_rail.to_dict(),
            "right rail": self._right_rail.to_dict(),
        }
        return track


def main():
    pass


if __name__ == "__main__":
    main()
