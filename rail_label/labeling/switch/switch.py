from typing import List, Type

import numpy as np
import cv2
from rail_label.utils.mouse import Mouse
from rail_label.labeling.scene.crosshair import CrossHair
from rail_label.labeling.scene.point import ImagePoint


class BoundingBox:
    """
    Represents a bounding box marking an object.
    """

    def __init__(self, point1: ImagePoint, point2: ImagePoint):
        self._point1: ImagePoint = point1
        self._point2: ImagePoint = point2


class Switch:
    """
    Represent a witch.
    """

    def __init__(self, switch_id: int, fork: bool, right: bool, tracks=None) -> None:
        """
        :param fork: Fork(True) or merge(False)
        :param right: Right(True) or left(False)
        """
        self._id = switch_id
        self._fork: bool = fork
        self._direction: bool = right
        self._tracks: list[int] = [] if tracks is None else tracks
        self._marks: list[ImagePoint] = []

    def del_point(self, mark: ImagePoint):
        """
        Remove the nearest point to given point.
        :param mark: Rough point
        """
        # Can only delete point if there is at least one
        print("Delete: ", end="")
        print(mark)
        if len(self._marks) >= 1:
            mark_points_arr: np.ndarray
            mark_points_arr = np.vstack([mark.point for mark in self._marks])
            # Calculate euclidean distance for all points
            distances: np.ndarray
            distances = np.linalg.norm(mark_points_arr - mark.point, axis=1)
            lowest_dist_index: int = np.argmin(distances).item()
            self._marks.pop(lowest_dist_index)

    def add_mark(self, mark: ImagePoint):
        """
        Add point to switch.
        :param mark:
        :return:
        """
        if len(self.marks) < 2:
            self.marks.append(mark)
        else:
            msg = f"Expected two points per box, this is the "
            msg += f"{len(self.marks) + 1}rd"
            raise ValueError(msg)

    def __str__(self):
        kind = "forg" if self.fork else "merge"
        direction = "right" if self.direction else "left"
        msg = f"{self._id:02d}, {kind}, {direction}"
        return msg

    def to_dict(self) -> dict:
        """
        Dict representation of a switch
        :return: Switch information
        """
        switch: dict
        switch = {
            "marks": [mark.point.tolist() for mark in self.marks],
            "kind": self.fork,
            "direction": self.direction,
            "tracks": [],
        }
        return switch

    @property
    def id(self) -> int:
        return self._id

    @property
    def marks(self) -> list[ImagePoint]:
        return self._marks

    @marks.setter
    def marks(self, marks):
        self._marks = marks

    @property
    def fork(self) -> bool:
        return self._fork

    @property
    def direction(self) -> bool:
        return self._direction


def main():
    window_name = "window"
    mouse = Mouse()
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse.mouse_callback)
    points = []
    while True:
        input_key = cv2.waitKey(1)

        if input_key == ord("q"):
            cv2.destroyAllWindows()
            break
        elif input_key == ord("f"):
            if len(points) < 2:
                points.append(mouse.position)
        elif input_key == ord("r"):
            if len(points) > 0:
                points.pop()

        image = np.zeros((1080, 1920, 3))

        image_height = image.shape[0]
        image_width = image.shape[1]

        # Crosshair
        crosshair = CrossHair(image_height, image_width)
        crosshair.calculate(mouse)
        crosshair.draw(image)

        # Horizontal line
        cv2.line(image, *crosshair.left, (255, 255, 255), 5)
        cv2.line(image, *crosshair.right, (255, 255, 255), 5)
        cv2.line(image, *crosshair.top, (255, 255, 255), 5)
        cv2.line(image, *crosshair.bottom, (255, 255, 255), 5)
        cv2.circle(image, crosshair.center, 5, color=(255, 255, 255), thickness=-1)
        # Vertical line
        # cv2.line(image, (mouse.position[0], 0), (mouse.position[0], image_width), (255, 255, 255), 5)

        for point in points:
            cv2.circle(image, point, 5, color=(0, 0, 255), thickness=-1)
        if len(points) == 2:
            cv2.rectangle(image, points[0], points[1], (0, 255, 0), 5)

        cv2.imshow(window_name, image)


if __name__ == "__main__":
    main()
