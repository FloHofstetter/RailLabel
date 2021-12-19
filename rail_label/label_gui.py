import pathlib

import cv2
import PySimpleGUI as sg
from typing import Union, Optional
from rail_label.utils.mouse import Mouse
from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
from rail_label.labeling.gui.simple_gui import settings_window_layout


class LabelGui:
    def __init__(
        self,
        settings: dict,
    ) -> None:
        """ """
        # Settings
        self.settings: dict = settings
        dataset_path: pathlib.Path = settings["dataset_path"]

        # PySimpleGUI window
        layout = settings_window_layout()
        self.window: sg.Window = sg.Window("Label-tool settings", layout)
        self.event = None
        self.values = None

        # OpenCV window
        self.cv2_window_name = "Image"
        self.cv_window = cv2.namedWindow(self.cv2_window_name, cv2.WINDOW_NORMAL)

        self.dataset: DataSet = DataSet(dataset_path)
        if not self.dataset:
            print(f'Dataset in directory "{str(dataset_path.absolute())}" is empty.')
            return
        self.mouse = Mouse()
        cv2.setMouseCallback(self.cv2_window_name, self.mouse.mouse_callback)
        self.scene: Optional[Scene] = None
        # Initial scene
        self.dataset_counter: int = -1
        self.refresh_simple_gui()
        self.next_scene()

        self._exit = False

    @property
    def exit(self):
        return self._exit

    def refresh_simple_gui(self) -> None:
        """
        Refresh PySimpleGUI window elements.
        """
        # Get window content
        self.event, self.values = self.window.read(0)

        # Disable 'New track' button if attributes not set.
        if (
            self.values["track.relpos.left"]
            or self.values["track.relpos.ego"]
            or self.values["track.relpos.right"]
        ):
            self.window["track.new"].update(disabled=False)
        else:
            self.window["track.new"].update(disabled=True)

        # Disable 'Delete track' button
        if len(self.values["track.active.track"]):
            self.window["track.del"].update(disabled=False)
        else:
            self.window["track.del"].update(disabled=True)

        # Disable 'New Switch' button it attributes not set.
        if (self.values["switch.kind.fork"] or self.values["switch.kind.merge"]) and (
            self.values["switch.direction.right"]
            or self.values["switch.direction.left"]
        ):
            self.window["switch.new"].update(disabled=False)
        else:
            self.window["switch.new"].update(disabled=True)

        # Disable 'Delete switch' button
        if len(self.values["switch.active.switch"]):
            self.window["switch.del"].update(disabled=False)
        else:
            self.window["switch.del"].update(disabled=True)

    def refresh_cv_gui(self) -> None:
        """
        Refresh OpenCV GUI.
        """
        self.scene.draw(self.mouse)
        self.scene.show()

    def remove_item(self) -> None:
        """
        Remove active mark from scene on active labeling mode.
        """
        if self.scene.tracks_mode:
            self.scene.remove_double_point()
        elif self.scene.switches_mode:
            self.scene.del_switch_mark()

    def next_scene(self):
        self._prepare_scene_switch("next")

    def previous_scene(self):
        self._prepare_scene_switch("previous")

    def _prepare_scene_switch(self, direction: str):
        self._write_scene_tags() if self.scene else None
        self.dataset.write_annotations(self.scene.to_dict()) if self.scene else None
        if direction == "next":
            if self.dataset_counter < len(self.dataset) - 1:
                self.dataset_counter += 1
            else:
                self.dataset_counter = 0
        elif direction == "previous":
            if self.dataset_counter > 0:
                self.dataset_counter -= 1
            else:
                self.dataset_counter = len(self.dataset) - 1
        else:
            msg = f"Expected value to be in ['previous', 'next'], got '{direction}'"
            raise ValueError(msg)
        image = self.dataset[self.dataset_counter]["image"]
        annotations = self.dataset[self.dataset_counter]["annotations"]
        camera_yml = self.dataset[self.dataset_counter]["camera_yml"]
        self.scene = Scene(self.cv2_window_name, image, camera_yml, self.settings)
        self.scene.from_dict(annotations) if annotations else None
        self.scene.tracks_mode = (
            True if self.values["mode.tab"] == "track.tab" else False
        )
        self.scene.switches_mode = (
            True if self.values["mode.tab"] == "switch.tab" else False
        )
        self._refresh_switch_list_box()
        self._refresh_track_list_box()
        self._refresh_track_drawing_attributes()
        self._read_scene_tags()
        self._refresh_scene_counter()
        self._refresh_scene_name()

    def _refresh_track_drawing_attributes(self):
        self.splines_tracks()
        self.fill_tracks()
        self.grid_tracks()
        self.show_marks()

    def _refresh_track_list_box(self) -> None:
        """
        Refresh the box listing tracks.
        """
        track_list = [track for track in self.scene.tracks.values()]
        self.window["track.active.track"].update(track_list)

    def _clear_track_radio_buttons(self):
        """
        Reset values of the track radio buttons.
        """
        self.window["track.relpos.left"].update(False)
        self.window["track.relpos.ego"].update(False)
        self.window["track.relpos.right"].update(False)

    def _write_scene_tags(self):
        self.scene.tags = self.values["scene.tags"]

    def _read_scene_tags(self):
        available_tags = list({*self.scene.settings["tags"], *self.scene.tags})
        available_tags = sorted(available_tags)
        indexes = [available_tags.index(tag) for tag in self.scene.tags]
        self.window["scene.tags"].update(available_tags)
        self.window["scene.tags"].update(set_to_index=indexes)

    def new_track(self) -> None:
        """
        Process event 'New Track' button is pressed.
        """
        if self.values["track.relpos.left"]:
            self.scene.add_track("left")
        elif self.values["track.relpos.ego"]:
            self.scene.add_track("ego")
        elif self.values["track.relpos.right"]:
            self.scene.add_track("right")
        track_list = [track for track in self.scene.tracks.values()]
        self.window["track.active.track"].update(track_list)
        self._clear_track_radio_buttons()

    def del_track(self) -> None:
        """
        Proces event 'Del Track' button is pressed.
        """
        if self.values["track.active.track"]:
            track_id = self.values["track.active.track"][0].id
            self.scene.activate_track(track_id)
            self.scene.del_track(track_id)
            self._refresh_track_list_box()

    def select_track(self) -> None:
        """
        Process event to select active track.
        """
        if self.values["track.active.track"]:
            track_id = self.values["track.active.track"][0].id
            self.scene.activate_track(track_id)

    def show_marks(self) -> None:
        """
        Process event 'marks track' checkbox checked.
        """
        self.scene.show_tracks_marks = self.values["track.marks"]

    def fill_tracks(self) -> None:
        """
        Process event 'fill track' checkbox checked.
        """
        self.scene.show_tracks_fill = self.values["track.fill"]

    def grid_tracks(self) -> None:
        """
        Process event 'grid track' checkbox checked.
        """
        self.scene.show_tracks_grid = self.values["track.grid"]

    def splines_tracks(self) -> None:
        """
        Process event 'splines track' checkbox checked.
        """
        self.scene.show_tracks_splines = self.values["track.splines"]

    def transparency_tracks(self) -> None:
        """
        Process event track transparency slider is changed.
        """
        self.scene.tracks_transparency = self.values["track.transparency"]

    def _refresh_scene_name(self) -> None:
        """
        Refresh the name of the scene.
        """
        counter = self.dataset_counter
        scene_name: str = f"{self.dataset[counter]['name']}"
        self.window["scene.name"].update(scene_name)

    def _refresh_scene_counter(self) -> None:
        """
        Refresh the numbers of scene counter.
        """
        total = len(self.dataset)
        actual = self.dataset_counter + 1
        self.window["scene.counter"].update(f"{actual: 04d} of {total: 04d}")

    def _refresh_switch_list_box(self) -> None:
        """
        Refresh the box listing scenes.
        """
        switch_list = [switch for switch in self.scene.switches.values()]
        self.window["switch.active.switch"].update(switch_list)

    def _clear_switch_radio_buttons(self):
        """
        Reset values of the switch radio buttons.
        """
        self.window["switch.kind.fork"].update(False)
        self.window["switch.kind.merge"].update(False)
        self.window["switch.direction.right"].update(False)
        self.window["switch.direction.left"].update(False)

    def new_switch(self) -> None:
        """
        Process event 'New Switch' button is pressed.
        """
        kind = True if self.values["switch.kind.fork"] else False
        direction = True if self.values["switch.direction.right"] else False
        self.scene.add_switch(kind, direction)
        self._refresh_switch_list_box()
        self._clear_switch_radio_buttons()

    def del_switch(self) -> None:
        """
        Process event 'Del Switch' button is pressed.
        """
        if self.values["switch.active.switch"]:
            switch_id = self.values["switch.active.switch"][0].id
            self.scene.activate_switch(switch_id)
            self.scene.del_switch(switch_id)
            self._refresh_switch_list_box()

    def select_switch(self) -> None:
        """
        Process event to select active switch.
        """
        if self.values["switch.active.switch"]:
            switch_id = self.values["switch.active.switch"][0].id
            self.scene.activate_switch(switch_id)

    def select_label_mode(self) -> None:
        """
        Process event to select label mode.
        """
        if self.values["mode.tab"] == "track.tab":
            self.scene.tracks_mode = True
            self.scene.switches_mode = False
            self._refresh_track_list_box()
        elif self.values["mode.tab"] == "switch.tab":
            self.scene.tracks_mode = False
            self.scene.switches_mode = True
            self._refresh_switch_list_box()

    def add_mark(self):
        """
        Take actual position of aiming device and add mark.
        """
        if self.scene.tracks_mode:
            self.scene.add_double_point()
        elif self.scene.switches_mode:
            self.scene.add_switch_mark()

    def del_mark(self):
        """
        Take actual position of aiming device delete nearest.
        """
        if self.scene.tracks_mode:
            self.scene.remove_double_point()
        elif self.scene.switches_mode:
            self.scene.del_switch_mark()

    def event_loop(self):
        """ """
        while True:
            input_key = cv2.waitKey(1)
            cv_window = cv2.getWindowProperty(
                self.cv2_window_name, cv2.WND_PROP_VISIBLE
            )
            if (
                cv_window < 1.0
                or input_key == ord("q")
                or self.event == "Exit"
                or self.event is None
            ):
                cv2.destroyAllWindows()
                self.dataset.write_annotations(self.scene.to_dict())
                break
            elif self.event == "track.new":
                self.new_track()
            elif self.event == "track.del":
                self.del_track()
            elif self.event == "switch.del":
                self.del_switch()
            elif self.event == "switch.new":
                self.new_switch()
            elif self.event == "switch.active.switch":
                self.select_switch()
            elif self.event == "track.active.track":
                self.select_track()
            elif self.event == "mode.tab":
                self.select_label_mode()
            elif self.event == "track.marks":
                self.show_marks()
            elif self.event == "track.fill":
                self.fill_tracks()
            elif self.event == "track.grid":
                self.grid_tracks()
            elif self.event == "track.splines":
                self.splines_tracks()
            elif self.event == "track.transparency":
                self.transparency_tracks()
            elif input_key == ord("s"):
                self.scene.stencil.toggle_mode() if self.scene.tracks_mode else None
            elif input_key == ord("d"):
                self.scene.stencil.set_width_correction(
                    1
                ) if self.scene.tracks_mode else None
            elif input_key == ord("a"):
                self.scene.stencil.set_width_correction(
                    -1
                ) if self.scene.tracks_mode else None
            elif input_key == ord("-"):
                self.scene.stencil.angle_correction -= (
                    1 if self.scene.tracks_mode else None
                )
            elif input_key == ord("+"):
                self.scene.stencil.angle_correction += (
                    1 if self.scene.tracks_mode else None
                )
            elif input_key == ord("f"):
                self.add_mark()
            elif input_key == ord("r"):
                self.del_mark()
            elif input_key == ord("n") or self.event == "Next":
                self.next_scene()
            elif input_key == ord("b") or self.event == "Previous":
                self.previous_scene()
            elif input_key == ord("x"):
                pass
                # create_ego_track(scene)
            elif input_key == ord("y"):
                pass
                # create_left_track(scene)
            elif input_key == ord("c"):
                pass
                # create_right_track(scene)
            elif input_key == ord("l"):
                pass
                # toggle_fill_elements(scene)
            # Keys 0-9 represent track-ids
            elif input_key in [ord(str(zero_to_nine)) for zero_to_nine in range(10)]:
                pass
                # activate_label(scene, input_key)

            self.refresh_simple_gui()
            self.refresh_cv_gui()
