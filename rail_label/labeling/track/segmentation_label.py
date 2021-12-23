import itertools

import cv2
import yaml
import pathlib
import argparse
import concurrent.futures
from typing import Iterable, Union

import numpy as np

from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
from rail_label.labeling.track.track import RailPoint


class SegmentationLabel:
    """
    Generation of segmentation labels.
    """

    def __init__(self, data, settings):
        self.image = data["image"]
        self._label = np.zeros(data["image"].shape)
        self.scene = Scene("", data["image"], data["camera_yml"], settings)
        self.scene.from_dict(data["annotations"])

    def label(self, color_type="segmentation"):
        """

        :param color_type:
        :return:
        """
        choice = ["segmentation", "human", "overlay"]
        if color_type not in choice:
            msg = f"Expected type property to be in {choice}, got"
            msg += f" {color_type}"

        if color_type in ["human", "overlay"]:
            self._label = np.zeros(self._label[:, :, :].shape, dtype=np.uint8)
            track_to_color = {
                "left_bed": (58, 58, 197),
                "left_rails": (0, 0, 255),
                "ego_bed": (58, 197, 197),
                "ego_rails": (0, 255, 255),
                "right_bed": (58, 197, 58),
                "right_rails": (0, 255, 0),
            }
        elif color_type == "segmentation":
            self._label = np.zeros(self._label[:, :, 0].shape, dtype=np.uint8)
            track_to_color = {
                "left_bed": (48,),
                "left_rails": (49,),
                "ego_bed": (50,),
                "ego_rails": (51,),
                "right_bed": (52,),
                "right_rails": (53,),
            }

        for track in self.scene.tracks.values():
            point: RailPoint
            points: list[np.ndarray]
            points_arr: np.ndarray
            # Rails
            for rail in [track.left_rail, track.right_rail]:
                points = []
                for point in rail.contour_points(self.scene.camera, 15):
                    points.append(point.point)
                points_arr = np.array(points).astype(np.int32)
                if len(points) > 1:
                    if track.relative_position == "ego":
                        cv2.fillConvexPoly(
                            self._label,
                            points_arr,
                            track_to_color["ego_rails"],
                        )
                    elif track.relative_position == "left":
                        cv2.fillConvexPoly(
                            self._label,
                            points_arr,
                            track_to_color["left_rails"],
                        )
                    elif track.relative_position == "right":
                        cv2.fillConvexPoly(
                            self._label,
                            points_arr,
                            track_to_color["right_rails"],
                        )
            if len(points) > 1:
                # Trackbed
                points = []
                for point in track.track_bed_spline_points(self.scene.camera, 15):
                    points.append(point.point)
                points_arr = np.array(points).astype(np.int32)
                if track.relative_position == "ego":
                    cv2.fillConvexPoly(
                        self._label,
                        points_arr,
                        track_to_color["ego_bed"],
                    )
                elif track.relative_position == "left":
                    cv2.fillConvexPoly(
                        self._label,
                        points_arr,
                        track_to_color["left_bed"],
                    )
                elif track.relative_position == "right":
                    cv2.fillConvexPoly(
                        self._label,
                        points_arr,
                        track_to_color["right_bed"],
                    )
        if color_type == "overlay":
            alpha = 0.5
            cv2.addWeighted(self.image, alpha, self._label, 1 - alpha, 0, self._label)
        return self._label


def create_label(
    data: dict,
    output_path: pathlib.Path,
    settings: dict,
    color_type: str = "segmentation",
    verbose=False,
) -> None:
    """
    :param data:
    :param output_path:
    :param settings: Dict of RailLabel settings
    :param color_type:
    :param verbose: Verbose std out
    :return:
    """
    if data["annotations"]:
        segmentation_label: SegmentationLabel = SegmentationLabel(data, settings)
        image: np.ndarray = segmentation_label.label(color_type)
        output_path.mkdir(parents=True, exist_ok=True)
        file_extension: str
        file_extension = ".png" if color_type == "segmentation" else ".jpg"
        output_path = output_path / (data["name"] + file_extension)
        cv2.imwrite(str(output_path), image)
        msg: str = f'Created "{data["name"]}" segmentation label/mask.'
        print(msg) if verbose else None
    else:
        msg: str = f'No annotations found for "{data["name"]}" segmentation label/mask.'
        print(msg) if verbose else None


def create_labels(
    data_set_path: Union[str, pathlib.Path],
    output_path: Union[str, pathlib.Path],
    settings: dict,
    color_type: str = "segmentation",
    verbose: bool = False,
) -> None:
    """
    Create segmentation labels / masks for tracks.
    The 'color_type' parameter selects if the output are colored
    images masks 'human', overlaid images 'overlay' or
    segmentation maks 'segmentation'.
    :param data_set_path: Path to dataset root directory
    :param output_path: Path to store generated masks / labels
    :param settings: Dict of RailLabel settings
    :param color_type: Type of masks / labels to generate
                       ['human', 'overlay', 'segmentation']
    :param verbose: Verbose std out
    """
    # Get data
    data_set_path: pathlib.Path = pathlib.Path(data_set_path)
    output_path: pathlib.Path = pathlib.Path(output_path)
    dataset: DataSet = DataSet(data_set_path)
    if not dataset:
        print(f'Dataset in directory "{str(data_set_path.absolute())}" is empty.')

    arguments: list[Iterable]
    arguments = [
        dataset,
        itertools.repeat(output_path),
        itertools.repeat(settings),
        itertools.repeat(color_type),
        itertools.repeat(verbose),
    ]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(create_label, *arguments)


def parse_yaml(yaml_path: pathlib.Path) -> dict:
    """
    Parse configuration from YAML.
    :param yaml_path: Path to settings file
    :return:
    """
    with open(yaml_path) as file_pointer:
        yaml_args = yaml.load(file_pointer, yaml.Loader)
    return yaml_args


def parse_cli() -> dict:
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dataset_path",
        type=str,
        help="Path to the directory containing a dataset",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        help="Path to save the labels",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose std out",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--settings_path",
        type=str,
        help="Path to settings YAML-file for RailLabel.",
    )
    return vars(parser.parse_args())


def parse_settings() -> dict[str, pathlib.Path]:
    """
    Get configuration for label tool. Standard configuration is in YAML file.
    These are overwritten by CLI arguments.
    :return: Dictionary containing paths
    """
    # Parse CLI arguments
    cli_args = parse_cli()
    if cli_args["settings_path"]:
        yaml_path = cli_args["settings_path"]
    else:
        yaml_path = pathlib.Path("settings.yml")
    yaml_args = parse_yaml(yaml_path)
    settings = {**yaml_args, **cli_args}
    return settings


def main():
    settings = parse_settings()

    # Get input and output paths
    data_set_path: pathlib.Path = pathlib.Path(settings["dataset_path"])
    output_path: pathlib.Path = pathlib.Path(settings["output_path"])
    verbose: bool = settings["verbose"]

    # Create labels
    create_labels(data_set_path, output_path, settings, "overlay", verbose)


if __name__ == "__main__":
    main()
