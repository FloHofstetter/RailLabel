import cv2
import pathlib
import argparse

from rail_label.utils.mouse import Mouse
from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
from rail_label.labeling.gui.simple_gui import settings_window


def parse_args(parser: argparse.ArgumentParser):
    """
    Parse CLI arguments.

    :param parser: Argument parser Object.
    :return: CLI Arguments object.
    """
    parser.add_argument(
        "-d",
        "--dataset_path",
        type=str,
        help="Path to the directory containing a dataset.",
        default="."
    )
    return parser.parse_args()


def main():
    # Show settings window
    window = settings_window()
    # Parse arguments from cli
    parser = argparse.ArgumentParser()
    args = parse_args(parser)

    # Path parameters
    data_set_path = pathlib.Path(args.dataset_path)

    # Object representing a labeling junk dataset
    data_set_counter: int = 0
    dataset = DataSet(data_set_path)
    if not dataset:
        print(f'Dataset in directory "{str(data_set_path.absolute())}" is empty.')
        return

    # Main window
    window_name = "image"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Mouse object handling callbacks on main window
    mouse = Mouse()
    cv2.setMouseCallback(window_name, mouse.mouse_callback)

    # Initial scene
    image = dataset[data_set_counter]["image"]
    annotations = dataset[0]["annotations"]
    camera_yml = dataset[0]["camera_yml"]
    scene = Scene(window_name, image, camera_yml)
    if annotations:
        scene.from_dict(annotations)
    else:
        scene.add_track("ego")
        scene.activate_track(0)

    # main loop
    while True:
        # GUI events
        event, values = window.read(timeout=0)
        input_key = cv2.waitKey(1)

        if input_key == ord("q") or event == "Exit" or event is None:
            # Save scene and exit program
            cv2.destroyAllWindows()
            dataset.write_annotations(scene.to_dict())
            break
        elif event == "track.new":
            if values["track.relpos.left"]:
                scene.add_track("left")
            elif values["track.relpos.ego"]:
                scene.add_track("ego")
            elif values["track.relpos.right"]:
                scene.add_track("right")
            track_list = [track for track in scene.tracks.values()]
            window["track.active.track"].update(track_list)
        elif event == "track.del":
            if values["track.active.track"]:
                track_id = values["track.active.track"][0].id
                scene.activate_track(track_id)
                scene.del_track(track_id)
                track_list = [track for track in scene.tracks.values()]
                window["track.active.track"].update(track_list)
        elif event == "switch.del":
            if values["switch.active.switch"]:
                switch_id = values["switch.active.switch"][0].id
                scene.activate_switch(switch_id)
                scene.del_switch(switch_id)
                switch_list = [switch for switch in scene.switches.values()]
                window["switch.active.switch"].update(switch_list)
        elif event == "switch.new":
            kind = True if values['switch.kind.fork'] else False
            direction = True if values["switch.direction.right"] else False
            state = True if values["switch.state.on"] else False
            scene.add_switch(kind, direction, state)
            track_list = [switch for switch in scene.switches.values()]
            window["switch.active.switch"].update(track_list)
        elif event == "switch.active.switch":
            if values["switch.active.switch"]:
                switch_id = values["switch.active.switch"][0].id
                scene.activate_switch(switch_id)
        elif event == "mode.tab":
            scene.tracks_mode = True if values["mode.tab"] == "track.tab" else False
            scene.switches_mode = True if values["mode.tab"] == "switch.tab" else False
            switch_list = [switch for switch in scene.switches.values()]
            window["switch.active.switch"].update(switch_list)
            track_list = [track for track in scene.tracks.values()]
            window["track.active.track"].update(track_list)
        elif event == "tracks_marks":
            scene.show_tracks_marks = values["tracks_marks"]
        elif event == "tracks_fill":
            scene.show_tracks_fill = values["tracks_fill"]
        elif event == "tracks_grid":
            scene.show_tracks_grid = values["tracks_grid"]
        elif event == "tracks_splines":
            scene.show_tracks_splines = values["tracks_splines"]
        elif event == "transparency":
            scene.tracks_alpha = values["transparency"]
        elif input_key == ord("s"):
            scene.stencil.toggle_mode() if scene.tracks_mode else None
        elif input_key == ord("d"):
            scene.stencil.set_width_correction(1) if scene.tracks_mode else None
        elif input_key == ord("a"):
            scene.stencil.set_width_correction(-1) if scene.tracks_mode else None
        elif input_key == ord("-"):
            scene.stencil.angle_correction -= 1 if scene.tracks_mode else None
        elif input_key == ord("+"):
            scene.stencil.angle_correction += 1 if scene.tracks_mode else None
        elif input_key == ord("f"):
            if scene.tracks_mode:
                scene.add_double_point()
            elif scene.switches_mode:
                scene.add_switch_mark()
        elif input_key == ord("r"):
            if scene.tracks_mode:
                scene.remove_double_point()
            elif scene.switches_mode:
                scene.del_switch_mark()
        elif input_key == ord("n") or event == "Next":
            dataset.write_annotations(scene.to_dict())
            del scene
            data_set_counter += 1
            image = dataset[data_set_counter]["image"]
            annotations = dataset[data_set_counter]["annotations"]
            camera_yml = dataset[data_set_counter]["camera_yml"]
            scene = Scene(window_name, image, camera_yml)
            if annotations:
                scene.from_dict(annotations)
            else:
                scene.add_track("ego")
                scene.activate_track(0)
        elif input_key == ord("b") or event == "Previous":
            dataset.write_annotations(scene.to_dict())
            del scene
            data_set_counter -= 1
            image = dataset[data_set_counter]["image"]
            annotations = dataset[data_set_counter]["annotations"]
            camera_yml = dataset[data_set_counter]["camera_yml"]
            scene = Scene(window_name, image, camera_yml)
            if annotations:
                scene.from_dict(annotations)
            else:
                scene.add_track("ego")
                scene.activate_track(0)
        elif input_key == ord("x"):
            if scene.tracks_mode:
                track_id: int = scene.add_track("ego")
                scene.activate_track(track_id)
        elif input_key == ord("y"):
            if scene.tracks_mode:
                track_id: int = scene.add_track("left")
                scene.activate_track(track_id)
        elif input_key == ord("c"):
            if scene.tracks_mode:
                track_id: int = scene.add_track("right")
                scene.activate_track(track_id)
        elif input_key == ord("l"):
            if scene.tracks_mode:
                scene.fill_tracks = not scene.fill_tracks
        # Keys 0-9 represent track-ids
        elif input_key in [ord(str(zero_to_nine)) for zero_to_nine in range(10)]:
            if scene.tracks_mode:
                scene.activate_track(int(chr(input_key)))
        else:
            # Draw OpenCV scene
            scene.draw(mouse)
            scene.show()


if __name__ == "__main__":
    main()
