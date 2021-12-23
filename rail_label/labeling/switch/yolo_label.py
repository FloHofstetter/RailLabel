import itertools
from functools import lru_cache

import cv2
import pathlib
import argparse
import yaml
import concurrent.futures
from typing import Iterable, Union

import numpy as np

from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
from rail_label.labeling.track.track import RailPoint


class Yolo:
    """
    Generation of YOLO labels for switches.
    """

    def __init__(self, desired_label, data, settings):
        """
        :param desired_label: List of labels
        :param data: Dict representing a scene
        :param settings: Dict representing settings
        """
        all_labels = ["direction", "kind", "both"]
        if not desired_label:
            msg = "Expected at least one label, got none."
            raise ValueError(msg)
        if desired_label not in all_labels:
            msg = f"Expected labels to be one of {all_labels}"
            msg += f", got {desired_label}"
            raise ValueError(msg)
        self.desired_label = desired_label

        self.image = data["image"]
        self.x_resolution = self.image.shape[1]
        self.y_resolution = self.image.shape[0]
        self.scene = Scene("", data["image"], data["camera_yml"], settings)
        self.scene.from_dict(data["annotations"])

    @property
    def text(self):
        """
        :return: List of label-names sorted by id
        """
        if self.desired_label == "both":
            text = ["fork_right", "merge_right", "fork_left", "merge_left"]
            return text
        elif self.desired_label == "kind":
            text = ["fork", "merge"]
            return text
        elif self.desired_label == "direction":
            text = ["right", "left"]
            return text

    @property
    def labels(self) -> list[str]:
        """
        Calculate YOLO-style relative annotations for switches.
        :return: YOLO-style list of switches and attributes
        """
        yolo_labels = []
        for switch in self.scene.switches.values():
            center = switch.marks[0].midpoint(switch.marks[1])
            center_x = center.x / self.x_resolution
            center_y = center.y / self.y_resolution
            width = abs(switch.marks[0].x - switch.marks[1].x) / self.x_resolution
            height = abs(switch.marks[0].y - switch.marks[1].y) / self.x_resolution
            if self.desired_label == "direction":
                label_id = 0 if switch.direction else 1
                label = f"{label_id} {center_x} {center_y} {width} {height}"
                yolo_labels.append(label)
            elif self.desired_label == "kind":
                label_id = 0 if switch.fork else 1
                label = f"{label_id} {center_x} {center_y} {width} {height}"
                yolo_labels.append(label)
            elif self.desired_label == "both":
                if switch.fork and switch.direction:
                    label_id = 0
                elif not switch.fork and switch.direction:
                    label_id = 1
                elif switch.fork and not switch.direction:
                    label_id = 2
                elif not switch.fork and not switch.direction:
                    label_id = 3
                label = f"{label_id} {center_x} {center_y} {width} {height}"
                yolo_labels.append(label)
        return yolo_labels


def create_label(
    desired_labels: list[str],
    output_path: pathlib.Path,
    data: dict,
    settings: dict,
    verbose: bool,
) -> list[str]:
    """
    Generate YOLO labels for switches from RailLabel
    dataset.
    :param desired_labels: Option of ["kind", "direction", "both"]
    :param output_path: Path to store labels
    :param data: Dict representing scene
    :param settings: Dict of RailLabel settings
    :param verbose: Verbose output of RailLabel
    :return: List of text labels in id order
    """
    yolo = Yolo(desired_labels, data, settings)
    if data["annotations"]:
        label_data = yolo.labels
        output_path.mkdir(exist_ok=True, parents=True)
        output_path = output_path / (data["name"] + ".txt")
        with open(output_path, "w") as file_pointer:
            file_pointer.write("\n".join(label_data))
        msg: str = f'Created "{data["name"]}" YOLO label.'
        print(msg) if verbose else None
    else:
        msg: str = f'No annotations found for "{data["name"]}".'
        print(msg) if verbose else None
    return yolo.text


def create_labels(
    desired_labels: str,
    output_path: pathlib.Path,
    data: DataSet,
    settings: dict,
    verbose: bool,
) -> None:
    """
    Concurrently generate YOLO labels for switches from RailLabel
    dataset.
    :param desired_labels: Option of ["kind", "direction", "both"]
    :param output_path: Path to store labels
    :param data: Dict representing scene
    :param settings: Dict of RailLabel settings
    :param verbose: Verbose output of RailLabel
    """
    arguments: list[Union[Iterable, dict]] = [
        itertools.repeat(desired_labels),
        itertools.repeat(output_path),
        data,
        itertools.repeat(settings),
        itertools.repeat(verbose),
    ]

    # Create labels for scenes concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        yolo_names = executor.map(create_label, *arguments)
    yolo_names = next(yolo_names)

    output_path.mkdir(exist_ok=True, parents=True)
    output_path = output_path / "labels.txt"
    with open(output_path, "w") as file_pointer:
        file_pointer.write("\n".join(yolo_names))


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
    dataset = DataSet(data_set_path)

    create_labels("both", output_path, dataset, settings, verbose)


if __name__ == "__main__":
    main()
