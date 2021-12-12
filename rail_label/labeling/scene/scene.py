import pathlib

import cv2
import numpy as np
import tabulate
from typing import Union
import itertools

from rail_label.labeling.scene.stencil import Stencil
from rail_label.labeling.track.track import RailPoint
from rail_label.labeling.track.track import Track
from rail_label.labeling.track.rail import Rail
from rail_label.utils.camera import Camera
from rail_label.utils.mouse import Mouse


class Scene:
    """
    Represent everything on one image.
    """
    def __init__(self, window_name: str, image: np.ndarray, camera_parameters: pathlib.Path) -> None:
        self._camera = Camera(camera_parameters)
        self.stencil = Stencil()
        self._tracks: dict[int, Track] = {}
        self._active_track: Union[Track, None] = None
        self._redraw_tracks = True
        self._track_image_cache = None
        self._image: np.ndarray = image
        self._image_show: np.ndarray = image
        self._window_name: str = window_name
        self._fill_tracks: bool = True

    @property
    def fill_tracks(self) -> bool:
        return self._fill_tracks

    @fill_tracks.setter
    def fill_tracks(self, fill_tracks: bool) -> None:
        self._fill_tracks = fill_tracks

    def add_track(self, relative_position) -> int:
        """
        Create a new track.
        :param relative_position: Position relative to ego track
        :return: ID of new track
        """
        new_track_id: int = max(self._tracks.keys()) + 1 if self._tracks else 0
        new_track: Track = Track(relative_position)
        self._tracks[new_track_id] = new_track
        return new_track_id

    def activate_track(self, track_id: int) -> None:
        """
        Set one track active an all other passive.
        :param track_id: Track to set active.
        """
        if track_id in self._tracks.keys():
            self._active_track = self._tracks[track_id]
        else:
            msg = f"Could not activate Track {track_id}, it does not"
            msg += f" exist. Choose between {list(self._tracks.keys())}."
            print(msg)

    def add_double_point(self) -> None:
        """
        Ad marking point on both rails.
        """
        # TODO: Stencil should provide RailPoint point
        left_mark: RailPoint = RailPoint(self.stencil.left_rail_point[0], self.stencil.left_rail_point[1])
        right_mark: RailPoint = RailPoint(self.stencil.right_rail_point[0], self.stencil.right_rail_point[1])
        self._active_track.add_left_mark(left_mark)
        self._active_track.add_right_mark(right_mark)
        self._redraw_tracks = True

    def remove_double_point(self) -> None:
        """
        Delete marking point near to given marking point on the rails.
        """
        # TODO: Stencil should provide RailPoint point
        left_mark: RailPoint = RailPoint(self.stencil.left_rail_point[0], self.stencil.left_rail_point[1])
        right_mark: RailPoint = RailPoint(self.stencil.right_rail_point[0], self.stencil.right_rail_point[1])
        self._active_track.del_left_mark(left_mark)
        self._active_track.del_right_mark(right_mark)
        self._redraw_tracks = True

    def draw(self, mouse: Mouse) -> None:
        self.stencil.calculate_rail_points(self._camera, mouse)

        # Draw tracks
        if self._redraw_tracks:
            self._redraw_tracks = False
            self._track_image_cache = self._image.copy()
            self._draw_tracks(self._track_image_cache, splines=True, grid_points=True)

        stencil_image = self._track_image_cache.copy()
        self.stencil.draw(stencil_image)
        self._image_show = stencil_image

    def _draw_tracks(self, image: np.ndarray, splines: bool = False, marks: bool = True, grid_points: bool = False, grid_polygon: bool = True):
        """
        Draw track related items.
        :param image: Image to draw on
        :param splines: Draw splines
        :param marks: Draw marks
        :param grid_points: Draw grid
        """
        track: Track
        # Draw marked points
        if marks:
            marks_image: np.ndarray = image.copy()
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.marks:
                    cv2.circle(marks_image, mark.point, 20, color=(255, 0, 0), thickness=-1)
                for mark in track.right_rail.marks:
                    cv2.circle(marks_image, mark.point, 20, color=(0, 255, 0), thickness=-1)
                for mark in track.center_points:
                    cv2.circle(marks_image, mark.point, 20, color=(0, 0, 255), thickness=-1)
        if splines:
            splines_image: np.ndarray = image.copy()
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.splines(15):
                    cv2.circle(splines_image, mark.point, 5, color=(255, 0, 0), thickness=-1)
                for mark in track.right_rail.splines(15):
                    cv2.circle(splines_image, mark.point, 5, color=(0, 255, 0), thickness=-1)
        if grid_points:
            grid_points_image: np.ndarray = image.copy()
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.contour_points(self._camera, 15):
                    cv2.circle(grid_points_image, mark.point, 5, color=(255, 0, 0), thickness=-1)
                for mark in track.right_rail.contour_points(self._camera, 15):
                    cv2.circle(grid_points_image, mark.point, 5, color=(0, 255, 0), thickness=-1)
        if grid_polygon:
            grid_polygon_image: np.ndarray = image.copy()
            for track in self._tracks.values():
                point: RailPoint
                points: list[np.ndarray]
                points_arr: np.ndarray
                # Rails
                for rail in [track.left_rail, track.right_rail]:
                    points = [point.point for point in rail.contour_points(self._camera, 15)]
                    # Polylines expects 32-bit integer https://stackoverflow.com/a/18817152/4835208
                    points_arr = np.array(points).astype(np.int32)
                    if self.fill_tracks and len(points) > 1:
                        cv2.fillConvexPoly(grid_polygon_image, points_arr, (0, 0, 255))
                    elif not self.fill_tracks and len(points) > 1:
                        # Polylines needs list of points https://stackoverflow.com/a/56426368/4835208
                        cv2.polylines(grid_polygon_image, [points_arr], True, (0, 0, 255), thickness=3)
                # Trackbed
                points = [point.point for point in track.track_bed_spline_points(self._camera, 15)]
                # Polylines expects 32-bit integer https://stackoverflow.com/a/18817152/4835208
                points_arr = np.array(points).astype(np.int32)
                if self.fill_tracks and len(points) > 1:
                    cv2.fillConvexPoly(grid_polygon_image, points_arr, (0, 255, 0))
                elif not self.fill_tracks and len(points) > 1:
                    # Polylines needs list of points https://stackoverflow.com/a/56426368/4835208
                    cv2.polylines(grid_polygon_image, [points_arr], True, (0, 255, 0), thickness=3)
        # Blend track images
        # cv2.addWeighted(splines_image, marks_alpha, image, 1 - marks_alpha, 0, image)
        # cv2.addWeighted(grid_points_image, marks_alpha, image, 1 - marks_alpha, 0, image)
        polygons_alpha = 0.5
        cv2.addWeighted(grid_polygon_image, polygons_alpha, image, 1 - polygons_alpha, 0, image)
        marks_alpha = 0.5
        cv2.addWeighted(marks_image, marks_alpha, image, 1 - marks_alpha, 0, image)

    def show(self) -> None:
        cv2.imshow(self._window_name, self._image_show)

    def to_dict(self) -> dict:
        """
        Conclude scene annotations to dict.
        :return: Annotations as dict
        """
        scene = {
            "tracks": {track_id: track.to_dict() for (track_id, track) in self._tracks.items()},
            "switches": {},
            "tags": {}
        }
        return scene

    def from_dict(self, annotations: dict) -> None:
        """
        Recreate scene from dict.
        :param annotations: Annotations as dict
        """
        # Track objects
        for track_id, track in annotations["tracks"].items():
            track_obj = Track(track["relative position"])
            track_obj.left_rail = Rail(67)
            track_obj.right_rail = Rail(67)
            for point in track["left rail"]["points"]:
                rail_points = RailPoint(point[0], point[1])
                track_obj.left_rail.marks.append(rail_points)
            for point in track["right rail"]["points"]:
                rail_points = RailPoint(point[0], point[1])
                track_obj.right_rail.marks.append(rail_points)
            self._tracks[int(track_id)] = track_obj
        if 0 in self._tracks.keys():
            self.activate_track(0)


def main():
    pass


if __name__ == "__main__":
    main()
