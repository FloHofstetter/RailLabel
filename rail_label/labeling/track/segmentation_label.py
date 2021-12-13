import itertools

import cv2
import pathlib
import argparse
import concurrent.futures

import numpy as np

from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene.scene import Scene
from rail_label.labeling.track.track import RailPoint


class SegmentationLabel:
    """
    Generation of segmentation labels.
    """
    def __init__(self, data):
        self.image = data["image"]
        self._label = np.zeros(data["image"].shape)
        self.scene = Scene("", data["image"], data["camera_yml"])
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
                points = [point.point for point in rail.contour_points(self.scene.camera, 15)]
                points_arr = np.array(points).astype(np.int32)
                if len(points) > 1:
                    if track.relative_position == "ego":
                        cv2.fillConvexPoly(self._label, points_arr, track_to_color["ego_rails"])
                    elif track.relative_position == "left":
                        cv2.fillConvexPoly(self._label, points_arr, track_to_color["left_rails"])
                    elif track.relative_position == "right":
                        cv2.fillConvexPoly(self._label, points_arr, track_to_color["right_rails"])
            if len(points) > 1:
                # Trackbed
                points = [point.point for point in track.track_bed_spline_points(self.scene.camera, 15)]
                points_arr = np.array(points).astype(np.int32)
                if track.relative_position == "ego":
                    cv2.fillConvexPoly(self._label, points_arr, track_to_color["ego_bed"])
                elif track.relative_position == "left":
                    cv2.fillConvexPoly(self._label, points_arr, track_to_color["left_bed"])
                elif track.relative_position == "right":
                    cv2.fillConvexPoly(self._label, points_arr, track_to_color["right_bed"])
        if color_type == "overlay":
            alpha = 0.5
            cv2.addWeighted(self.image, alpha, self._label, 1 - alpha, 0, self._label)
        return self._label


def create_label(data, output_path, color_type="segmentation"):
    """

    :param data:
    :param output_path:
    :param color_type:
    :return:
    """
    if data["annotations"]:
        segmentation_label = SegmentationLabel(data)
        image = segmentation_label.label(color_type)
        output_path.mkdir(parents=True, exist_ok=True)
        file_extension = ".png" if color_type == "segmentation" else ".jpg"
        output_path = output_path / (data["name"] + file_extension)
        cv2.imwrite(str(output_path), image)
    else:
        msg = f'No annotations found for "{data["name"]}"'
        print(msg)


def create_labels(data_set_path, output_path, color_type="segmentation"):
    """

    :param data_set_path:
    :param output_path:
    :param color_type:
    :return:
    """
    # Get data
    data_set_path = pathlib.Path(data_set_path)
    dataset = DataSet(data_set_path)
    if not dataset:
        print(f'Dataset in directory "{str(data_set_path.absolute())}" is empty.')

    arguments = [dataset, itertools.repeat(output_path), itertools.repeat(color_type)]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(create_label, *arguments)


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
        required=True
    )
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        help="Path to save the labels.",
        required=True
    )
    return parser.parse_args()


def main():
    # Parse arguments from cli
    parser = argparse.ArgumentParser()
    args = parse_args(parser)
    data_set_path = pathlib.Path(args.dataset_path)
    output_path = pathlib.Path(args.output_path)

    create_labels(data_set_path, output_path, "overlay")


if __name__ == "__main__":
    main()
