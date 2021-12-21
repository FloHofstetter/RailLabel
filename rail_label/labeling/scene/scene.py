import pathlib

import cv2
from PIL import Image
import numpy as np
from typing import Union

from labeling.scene.stencil import Stencil
from labeling.scene.crosshair import CrossHair
from labeling.track.track import RailPoint
from labeling.scene.point import ImagePoint
from labeling.track.track import Track
from labeling.switch.switch import Switch
from labeling.track.rail import Rail
from utils.camera import Camera
from utils.mouse import Mouse


class Scene:
    """
    Represent everything on one image.
    """

    def __init__(
        self,
        window_name: str,
        image: np.ndarray,
        camera_parameters: pathlib.Path,
        settings: dict,
    ) -> None:
        self._settings: dict = settings
        self._window_name: str = window_name
        self._camera = Camera(camera_parameters)

        # Labeling mode
        self._tracks_mode: bool = True
        self._switches_mode: bool = False

        # Aiming devices
        track_bed_width: int = self._settings["track_bed_width"]
        rail_width: int = self._settings["rail_width"]
        self.stencil: Stencil = Stencil(track_bed_width, rail_width)
        self.crosshair = CrossHair(image.shape[0], image.shape[1])
        self._aiming_device_image_cache: Union[np.ndarray, None] = None

        # Switches
        self._switches: dict[int, Switch] = {}
        self._active_switch: Union[Switch, None] = None
        self._redraw_switches: bool = True
        self._switch_image_cache: Union[np.ndarray, None] = None
        self._switches_alpha: float = 0.5
        self._show_switches_boxes: bool = True
        self._fill_switches: bool = True

        # Tracks
        self._tracks: dict[int, Track] = {}
        self._active_track: Union[Track, None] = None
        self._redraw_tracks = True
        self._tracks_transparency: float = 0.5
        self._track_image_cache = None
        self._show_tracks_splines = False
        self._show_tracks_marks = True
        self._show_tracks_fill = True
        self._show_tracks_grid = False

        # Scene
        self._image: np.ndarray = image
        self._image_show: np.ndarray = image
        self._tags: list[str] = []

    @property
    def tags(self) -> list[str]:
        return self._tags

    @tags.setter
    def tags(self, tags: list[str]):
        self._tags = tags

    @property
    def settings(self) -> dict:
        return self._settings

    @property
    def active_track(self) -> Union[Track, None]:
        return self._active_track

    @property
    def active_switch(self) -> Union[Switch, None]:
        return self._active_switch

    @property
    def switches(self) -> dict[int, Switch]:
        return self._switches

    @property
    def tracks_mode(self) -> bool:
        return self._tracks_mode

    @tracks_mode.setter
    def tracks_mode(self, tracks_mode: bool):
        self._tracks_mode = tracks_mode

    @property
    def switches_mode(self) -> bool:
        return self._switches_mode

    @switches_mode.setter
    def switches_mode(self, switches_mode: bool):
        self._switches_mode = switches_mode

    @property
    def show_tracks_marks(self) -> float:
        return self._show_tracks_marks

    @show_tracks_marks.setter
    def show_tracks_marks(self, show_tracks_marks) -> None:
        self._redraw_tracks = True
        self._show_tracks_marks = show_tracks_marks

    @property
    def show_tracks_fill(self) -> float:
        return self._show_tracks_fill

    @show_tracks_fill.setter
    def show_tracks_fill(self, show_tracks_fill) -> None:
        self._redraw_tracks = True
        self._show_tracks_fill = show_tracks_fill

    @property
    def show_tracks_grid(self) -> float:
        return self._show_tracks_grid

    @show_tracks_grid.setter
    def show_tracks_grid(self, show_tracks_grid) -> None:
        self._redraw_tracks = True
        self._show_tracks_grid = show_tracks_grid

    @property
    def show_tracks_splines(self) -> float:
        return self._show_tracks_splines

    @show_tracks_splines.setter
    def show_tracks_splines(self, show_tracks_splines) -> None:
        self._redraw_tracks = True
        self._show_tracks_splines = show_tracks_splines

    @property
    def tracks_transparency(self) -> float:
        return self._tracks_transparency

    @tracks_transparency.setter
    def tracks_transparency(self, tracks_transparency) -> None:
        self._redraw_tracks = True
        self._tracks_transparency = tracks_transparency

    @property
    def camera(self):
        return self._camera

    @property
    def tracks(self):
        return self._tracks

    def add_track(self, relative_position) -> int:
        """
        Create a new track.
        :param relative_position: Position relative to ego track
        :return: ID of new track
        """
        new_track_id: int = max(self._tracks.keys()) + 1 if self._tracks else 0
        new_track: Track = Track(new_track_id, relative_position)
        self._tracks[new_track_id] = new_track
        return new_track_id

    def del_track(self, track_id):
        """
        Delete track from scene.
        :param track_id: ID of track to delete
        """
        self._redraw_tracks = True
        if self._active_track:
            self._active_track = None
            self.tracks.pop(track_id)

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
        left_mark: RailPoint = RailPoint(
            self.stencil.left_rail_point[0], self.stencil.left_rail_point[1]
        )
        right_mark: RailPoint = RailPoint(
            self.stencil.right_rail_point[0], self.stencil.right_rail_point[1]
        )
        self._active_track.add_left_mark(left_mark)
        self._active_track.add_right_mark(right_mark)
        self._redraw_tracks = True

    def remove_double_point(self) -> None:
        """
        Delete marking point near to given marking point on the rails.
        """
        # TODO: Stencil should provide RailPoint point
        left_mark: RailPoint = RailPoint(
            self.stencil.left_rail_point[0], self.stencil.left_rail_point[1]
        )
        right_mark: RailPoint = RailPoint(
            self.stencil.right_rail_point[0], self.stencil.right_rail_point[1]
        )
        self._active_track.del_left_mark(left_mark)
        self._active_track.del_right_mark(right_mark)
        self._redraw_tracks = True

    def draw(self, mouse: Mouse) -> None:
        # Refresh image
        self._image_show = self._image.copy()

        # Draw tracks
        if self.tracks_mode:
            if self._redraw_tracks:
                self._redraw_tracks = False
                self._track_image_cache = self._image.copy()
                self._track_image_cache = self._draw_tracks(self._track_image_cache)
            self._image_show = self._track_image_cache.copy()

        # Draw switches
        if self.switches_mode:
            if self._redraw_switches:
                self._redraw_switches = False
                self._switch_image_cache = self._image.copy()
                self._draw_switches(self._switch_image_cache)
            self._image_show = self._switch_image_cache.copy()

        # Aiming device
        if self.tracks_mode:
            self.stencil.calculate_rail_points(self._camera, mouse)
            self.stencil.draw(self._image_show)
        elif self.switches_mode:
            self.crosshair.calculate(mouse)
            self.crosshair.draw(self._image_show)

    def _draw_tracks(self, image: np.ndarray, grid_points: bool = False):
        """
        Draw track related items.
        :param image: Image to draw on
        :param grid_points: Draw grid
        """
        track_to_color: dict = {
            "left_bed": (58, 58, 197),
            "left_rails": (0, 0, 255),
            "ego_bed": (58, 197, 197),
            "ego_rails": (0, 255, 255),
            "right_bed": (58, 197, 58),
            "right_rails": (0, 255, 0),
        }
        draw_image: np.ndarray
        draw_image = np.zeros(image.shape, dtype=np.uint8)

        # Draw marked points
        track: Track
        if self._show_tracks_marks:
            marks_image: np.ndarray
            marks_image = np.zeros(image.shape, dtype=np.uint8)
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.marks:
                    cv2.circle(
                        marks_image, mark.point, 5, color=(255, 0, 0), thickness=-1
                    )
                for mark in track.right_rail.marks:
                    cv2.circle(
                        marks_image, mark.point, 5, color=(0, 255, 0), thickness=-1
                    )
                for mark in track.center_points:
                    cv2.circle(
                        marks_image, mark.point, 5, color=(0, 0, 255), thickness=-1
                    )
        # Draw splines
        if self._show_tracks_splines:
            splines_image: np.ndarray
            splines_image = np.zeros(image.shape, dtype=np.uint8)
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.splines(
                    self._settings["marker_interpolation_steps"]
                ):
                    cv2.circle(
                        splines_image, mark.point, 2, color=(255, 0, 0), thickness=-1
                    )
                for mark in track.right_rail.splines(
                    self._settings["marker_interpolation_steps"]
                ):
                    cv2.circle(
                        splines_image, mark.point, 2, color=(0, 255, 0), thickness=-1
                    )
        # Draw grid
        if grid_points:
            polygon_image: np.ndarray
            polygon_image = np.zeros(image.shape, dtype=np.uint8)
            for track in self._tracks.values():
                mark: RailPoint
                for mark in track.left_rail.contour_points(
                    self._camera, self._settings["marker_interpolation_steps"]
                ):
                    cv2.circle(
                        polygon_image,
                        mark.point,
                        2,
                        color=(255, 0, 0),
                        thickness=-1,
                    )
                for mark in track.right_rail.contour_points(
                    self._camera, self._settings["marker_interpolation_steps"]
                ):
                    cv2.circle(
                        polygon_image,
                        mark.point,
                        2,
                        color=(0, 255, 0),
                        thickness=-1,
                    )
        if self.show_tracks_grid or self.show_tracks_fill:
            polygon_image: np.ndarray
            polygon_image = np.zeros(image.shape, dtype=np.uint8)
            for track in self._tracks.values():
                point: RailPoint
                points: list[np.ndarray]
                points_arr: np.ndarray
                # Rails
                for rail in [track.left_rail, track.right_rail]:
                    points = []
                    for point in rail.contour_points(
                        self._camera, self._settings["marker_interpolation_steps"]
                    ):
                        points.append(point.point)

                    # Polylines expects 32-bit integer https://stackoverflow.com/a/18817152/4835208
                    points_arr = np.array(points).astype(np.int32)
                    if self.show_tracks_fill and len(points) > 1:
                        if track.relative_position == "ego":
                            cv2.fillConvexPoly(
                                polygon_image,
                                points_arr,
                                track_to_color["ego_rails"],
                            )
                        elif track.relative_position == "left":
                            cv2.fillConvexPoly(
                                polygon_image,
                                points_arr,
                                track_to_color["left_rails"],
                            )
                        elif track.relative_position == "right":
                            cv2.fillConvexPoly(
                                polygon_image,
                                points_arr,
                                track_to_color["right_rails"],
                            )
                    if self.show_tracks_grid and len(points) > 1:
                        if track.relative_position == "ego":
                            cv2.polylines(
                                polygon_image,
                                [points_arr],
                                True,
                                track_to_color["ego_rails"],
                                thickness=3,
                            )
                        elif track.relative_position == "left":
                            cv2.polylines(
                                polygon_image,
                                [points_arr],
                                True,
                                track_to_color["left_rails"],
                                thickness=3,
                            )
                        elif track.relative_position == "right":
                            cv2.polylines(
                                polygon_image,
                                [points_arr],
                                True,
                                track_to_color["right_rails"],
                                thickness=3,
                            )
                # Trackbed
                points = []
                for point in track.track_bed_spline_points(
                    self._camera, self._settings["marker_interpolation_steps"]
                ):
                    points.append(point.point)

                # Polylines expects 32-bit integer https://stackoverflow.com/a/18817152/4835208
                points_arr = np.array(points).astype(np.int32)
                if self.show_tracks_fill and len(points) > 1:
                    if track.relative_position == "ego":
                        cv2.fillConvexPoly(
                            polygon_image, points_arr, track_to_color["ego_bed"]
                        )
                    elif track.relative_position == "left":
                        cv2.fillConvexPoly(
                            polygon_image, points_arr, track_to_color["left_bed"]
                        )
                    elif track.relative_position == "right":
                        cv2.fillConvexPoly(
                            polygon_image, points_arr, track_to_color["right_bed"]
                        )
                if self.show_tracks_grid and len(points) > 1:
                    if track.relative_position == "ego":
                        cv2.polylines(
                            polygon_image,
                            [points_arr],
                            True,
                            track_to_color["ego_bed"],
                            thickness=3,
                        )
                    elif track.relative_position == "left":
                        cv2.polylines(
                            polygon_image,
                            [points_arr],
                            True,
                            track_to_color["left_bed"],
                            thickness=3,
                        )
                    elif track.relative_position == "right":
                        cv2.polylines(
                            polygon_image,
                            [points_arr],
                            True,
                            track_to_color["right_bed"],
                            thickness=3,
                        )
                    # Polylines needs list of points https://stackoverflow.com/a/56426368/4835208
                    cv2.polylines(
                        polygon_image, [points_arr], True, (0, 255, 0), thickness=3
                    )

        alpha = self._tracks_transparency * 255

        if self._show_tracks_marks:
            marks_image = marks_image.transpose((2, 0, 1))
            alpha_mask = (marks_image[0]) | (marks_image[1]) | (marks_image[2])
            alpha_channel = np.where(alpha_mask, alpha, 0).astype(np.uint8)
            alpha_channel = np.expand_dims(alpha_channel, axis=0)
            marks_image = np.vstack((marks_image, alpha_channel))
            marks_image = marks_image.transpose((1, 2, 0))
            marks_image = Image.fromarray(marks_image)
            image = Image.fromarray(image).convert("RGBA")
            image.paste(marks_image, (0, 0), marks_image)
            image = image.convert("RGB")
            image = np.asarray(image)

        if self._show_tracks_splines:
            splines_image = splines_image.transpose((2, 0, 1))
            alpha_mask = (splines_image[0]) | (splines_image[1]) | (splines_image[2])
            alpha_channel = np.where(alpha_mask, alpha, 0).astype(np.uint8)
            alpha_channel = np.expand_dims(alpha_channel, axis=0)
            splines_image = np.vstack((splines_image, alpha_channel))
            splines_image = splines_image.transpose((1, 2, 0))
            splines_image = Image.fromarray(splines_image)
            image = Image.fromarray(image).convert("RGBA")
            image.paste(splines_image, (0, 0), splines_image)
            image = image.convert("RGB")
            image = np.asarray(image)

        if self.show_tracks_fill or self.show_tracks_grid:
            polygon_image = polygon_image.transpose((2, 0, 1))
            alpha_mask = (polygon_image[0]) | (polygon_image[1]) | (polygon_image[2])
            alpha_channel = np.where(alpha_mask, alpha, 0).astype(np.uint8)
            alpha_channel = np.expand_dims(alpha_channel, axis=0)
            polygon_image = np.vstack((polygon_image, alpha_channel))
            polygon_image = polygon_image.transpose((1, 2, 0))
            polygon_image = Image.fromarray(polygon_image)
            image = Image.fromarray(image).convert("RGBA")
            image.paste(polygon_image, (0, 0), polygon_image)
            image = image.convert("RGB")
            image = np.asarray(image)
        return image

    def add_switch_mark(self):
        """
        Add mark to active switch.
        """
        if self.active_switch:
            self._redraw_switches = True
            mark: ImagePoint
            mark = ImagePoint(self.crosshair.center[0], self.crosshair.center[1])
            if len(self.active_switch.marks) < 2:
                self.active_switch.add_mark(mark)

    def del_switch_mark(self):
        """
        Delete the nearest mark from active switch.
        """
        self._redraw_switches = True
        if self.active_switch:
            mark: ImagePoint
            mark = ImagePoint(self.crosshair.center[0], self.crosshair.center[1])
            self.active_switch.del_point(mark)

    def add_switch(
        self,
        kind: bool,
        direction: bool,
    ) -> int:
        """
        Create a new switch.
        :param kind:
        :param direction:
        :return: ID of new switch
        """
        new_switch_id: int = max(self._switches.keys()) + 1 if self._switches else 0
        new_switch: Switch = Switch(new_switch_id, kind, direction)
        self._switches[new_switch_id] = new_switch
        return new_switch_id

    def del_switch(self, switch_id):
        """
        Delete switch from scene.
        :param switch_id: ID of switch to delete
        """
        self._redraw_switches = True
        if self.active_switch:
            self._active_switch = None
            self.switches.pop(switch_id)

    def activate_switch(self, switch_id: int) -> None:
        """
        Set one switch active an all other passive.
        :param switch_id: Switch to set active.
        """
        if switch_id in self.switches.keys():
            self._active_switch = self.switches[switch_id]
        else:
            msg = f"Could not activate Switch {switch_id}, it does not"
            msg += f" exist. Choose between {list(self._tracks.keys())}."

    def _draw_switches(self, image: np.ndarray) -> None:
        """
        Draw switches on scene.
        :param image: Image to draw on
        """
        switch: Switch
        for switch in self.switches.values():
            if len(switch.marks) == 1:
                self._redraw_switches = True
                cv2.rectangle(
                    image,
                    switch.marks[0].point,
                    self.crosshair.center,
                    (0, 255, 0),
                    2,
                )
            elif len(switch.marks) == 2:
                cv2.rectangle(
                    image,
                    switch.marks[0].point,
                    switch.marks[1].point,
                    (0, 255, 0),
                    2,
                )
            if len(switch.marks) >= 1:
                cv2.putText(
                    img=image,
                    text=f"{switch.id:02d}",
                    org=switch.marks[0].point,
                    fontFace=0,
                    fontScale=1.0,
                    color=(0, 255, 0),
                    thickness=2,
                    lineType=cv2.LINE_AA,
                )

    def show(self) -> None:
        cv2.imshow(self._window_name, self._image_show)

    def to_dict(self) -> dict:
        """
        Conclude scene annotations to dict.
        :return: Annotations as dict
        """
        scene = {
            "tracks": {
                track_id: track.to_dict() for (track_id, track) in self._tracks.items()
            },
            "switches": {
                switch_id: switch.to_dict()
                for (switch_id, switch) in self.switches.items()
            },
            "tags": self.tags,
        }
        return scene

    def from_dict(self, annotations: dict) -> None:
        """
        Recreate scene from dict.
        :param annotations: Annotations as dict
        """
        # Track objects
        if "tracks" in annotations:
            for track_id, track in annotations["tracks"].items():
                track_obj = Track(int(track_id), track["relative position"])
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
        # Switch objects
        if "switches" in annotations:
            for switch_id, switch in annotations["switches"].items():
                kind = switch["kind"]
                direction = switch["direction"]
                tracks = switch["tracks"]
                switch_obj = Switch(int(switch_id), kind, direction, tracks)
                for mark_list in switch["marks"]:
                    mark = ImagePoint(mark_list[0], mark_list[1])
                    switch_obj.add_mark(mark)
                self.switches[int(switch_id)] = switch_obj
        if "tags" in annotations:
            self.tags = annotations["tags"]


def main():
    pass


if __name__ == "__main__":
    main()
