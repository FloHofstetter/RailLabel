import json
from typing import Union
import pathlib
import cv2


class DataSet:
    """
    Loads images and annotations.

    """

    def __init__(self, dataset_path: Union[pathlib.Path, str]):
        """
        Initialize the data loader.

        :param dataset_path: Path containing images and annotations.
        :return: None.
        """
        self._dataset_path = pathlib.Path(dataset_path)

        # Collect all images and annotations
        # Directory with images
        images_path = self._dataset_path / "images"

        # Find paths to images with all given extensions
        extensions = {"*.jpg", "*.jpeg", "*.png"}
        self._images_paths = []
        for extension in extensions:
            for image_path in images_path.glob(extension):
                self._images_paths.append(image_path)
        # Sort to get video image order.
        self._images_paths = sorted(self._images_paths)
        # Path to directory with annotations
        self._json_path = self._dataset_path / "annotations"
        self._json_path.mkdir(parents=True, exist_ok=True)
        self._camera_yml = self._dataset_path / "camera" / "camera.yaml"

    def __len__(self):
        """
        Implement the len() call on the data loader.
        :return: Length of dataset.
        """
        return len(self._images_paths)

    def __getitem__(self, item):
        """
        :param item: Subscription of data loader.
        :return: Dictionary with image and annotation.
        """
        image_path = self._images_paths[item]
        image = cv2.imread(str(image_path))
        # Try to get annotations file.
        self.annotation_path = self._json_path / (image_path.stem + ".json")
        try:
            with open(self.annotation_path) as file_pointer:
                annotation = json.load(file_pointer)
        except FileNotFoundError:
            annotation = None
        data = {
            "image": image,
            "name": image_path.stem,
            "annotations": annotation,
            "camera_yml": self._camera_yml,
        }
        return data

    def write_annotations(self, annotations):
        """
        Write serialized scenes to dedicated JSON file.

        :param annotations:
        :return: None.
        """
        with open(self.annotation_path, "w") as file_pointer:
            json.dump(annotations, file_pointer, indent=4, sort_keys=True)
