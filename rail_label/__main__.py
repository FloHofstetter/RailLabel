import cv2
import pathlib
import argparse

from rail_label.utils.mouse import Mouse
from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
import PySimpleGUI as sg


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


def configure_settings_window():
    tracks_marks = sg.Checkbox('Show marks', key='tracks_marks', enable_events=True, default=True)
    tracks_fill = sg.Checkbox('Fill tracks', key='tracks_fill', enable_events=True, default=True)
    tracks_grid = sg.Checkbox('Show grid', key='tracks_grid', enable_events=True, default=False)
    tracks_splines = sg.Checkbox('Show splines', key='tracks_splines', enable_events=True, default=False)
    layout = [[sg.Text("Output will go here", key="-OUT-")],
              [sg.Button('Previous'), sg.Button("Next")],
              [tracks_marks, tracks_fill, tracks_grid, tracks_splines],
              [sg.Slider(range=(0, 1), resolution=0.1, default_value=0.5, orientation='h', size=(34, 20),
                         key="transparency", enable_events=True, )],
              [sg.Button("Exit")]]
    window = sg.Window("Label-tool settings", layout)
    return window


def main():
    window = configure_settings_window()
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
            scene.stencil.toggle_mode()
        elif input_key == ord("d"):
            scene.stencil.set_width_correction(1)
        elif input_key == ord("a"):
            scene.stencil.set_width_correction(-1)
        elif input_key == ord("-"):
            scene.stencil.angle_correction -= 1
        elif input_key == ord("+"):
            scene.stencil.angle_correction += 1
        elif input_key == ord("f"):
            scene.add_double_point()
        elif input_key == ord("r"):
            scene.remove_double_point()
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
            track_id: int = scene.add_track("ego")
            scene.activate_track(track_id)
        elif input_key == ord("y"):
            track_id: int = scene.add_track("left")
            scene.activate_track(track_id)
        elif input_key == ord("c"):
            track_id: int = scene.add_track("right")
            scene.activate_track(track_id)
        elif input_key == ord("l"):
            scene.fill_tracks = not scene.fill_tracks
        # Keys 0-9 represent track-ids
        elif input_key in [ord(str(zero_to_nine)) for zero_to_nine in range(10)]:
            scene.activate_track(int(chr(input_key)))
        else:
            scene.draw(mouse)
            scene.show()


if __name__ == "__main__":
    main()
