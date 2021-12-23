import pathlib
import json
import itertools
import concurrent.futures
from typing import Union, Iterable, Generator
import iteration_utilities


class LegacyConverter:
    """
    Create new annotation files from old annotation files.
    """

    def __init__(
        self,
        output_path: Union[str, pathlib.Path],
    ) -> None:
        """
        :param output_path: Directory to store new annotation
        """
        self._old_label_path: pathlib.Path = pathlib.Path()
        self._output_path: pathlib.Path = pathlib.Path(output_path)
        self._old_tracks_labels: dict = {}
        self._new_track_labels: dict = {}

    def __call__(self, old_label_path: Union[pathlib.Path, str]):
        """
        Read old annotation file and store in new annotations
        directory.
        :param old_label_path: Path to old annotation
        """
        self._old_label_path = pathlib.Path(old_label_path)
        self._read_old_labels()
        self._write_new_labels()

    def _read_old_labels(self) -> None:
        """
        Read json file of old labels.
        """
        track_position_converter: dict = {
            "ego track": "ego",
            "left neighbors": "left",
            "right neighbors": "right",
        }
        with open(self._old_label_path) as file_pointer:
            self._old_labels = json.load(file_pointer)
        track_counter: int = 0
        new_tracks: dict = {}
        for track_position, tracks in self._old_labels.items():
            for track in tracks:
                left_rail: dict = {"points": []}
                right_rail: dict = {"points": []}
                rail_position: str
                points: list[int]
                for rail_position, points in track.items():
                    point: tuple[int, int]
                    for point in iteration_utilities.grouper(points, 2):
                        if rail_position == "leftrail":
                            left_rail["points"].append(point)
                        elif rail_position == "rightrail":
                            right_rail["points"].append(point)
                new_tracks[track_counter] = {
                    "relative position": track_position_converter[track_position],
                    "left rail": {**left_rail},
                    "right rail": {**right_rail},
                }
                track_counter += 1
        self._new_track_labels["tracks"] = new_tracks

    def _write_new_labels(self):
        filename: pathlib.Path = self._old_label_path
        while filename.suffix:
            filename = filename.with_suffix("")
        save_path: pathlib.Path = self._output_path / (filename.stem + ".json")
        with open(save_path, "w") as file_pointer:
            json.dump(self._new_track_labels, file_pointer, indent=4, sort_keys=True)


def convert_annotation(
    old_annotation_path: Union[pathlib.Path, str],
    new_annotations_path: Union[pathlib.Path, str],
) -> None:
    old_annotation_path: pathlib.Path
    old_annotation_path = pathlib.Path(old_annotation_path)
    new_annotations_path: pathlib.Path
    new_annotations_path = pathlib.Path(new_annotations_path)
    legacy_convert = LegacyConverter(new_annotations_path)
    legacy_convert(old_annotation_path)


def convert_annotations(
    old_annotations_path: Union[pathlib.Path, str],
    new_annotations_path: Union[pathlib.Path, str],
):
    old_annotations_path: pathlib.Path
    old_annotations_path = pathlib.Path(old_annotations_path)
    new_annotations_path: pathlib.Path
    new_annotations_path = pathlib.Path(new_annotations_path)

    old_annotation_paths: Generator[pathlib.Path]
    old_annotation_paths = old_annotations_path.glob("*.yaml")
    arguments: list[Iterable]
    arguments = [old_annotation_paths, itertools.repeat(new_annotations_path)]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(convert_annotation, *arguments)


def main():
    old_label_path: str = ""
    new_label_path: str = ""
    convert_annotations(old_label_path, new_label_path)


if __name__ == "__main__":
    main()
