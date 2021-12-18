import pathlib
from typing import Union

from rail_label.utils.geometry import Line, Plane, intersection

import cv2
import numpy as np


class Camera:
    def __init__(self, calib_file: Union[str, pathlib.Path]):
        """

        :param calib_file: Path to the camera calibration file.
        """
        self.origin = np.array([0.0, 0.0, 0.0], dtype=float)
        self._read_yaml(calib_file)
        self.roll = np.radians(self.roll)
        self.pitch = np.radians(self.pitch)
        self.yaw = np.radians(self.yaw)
        self.center = np.squeeze(self.tvec.T)

    def _get_rotation_matrix(self):
        # Rotation on y-axis
        r_yaw = np.array(
            [
                [np.cos(self.yaw), 0, -np.sin(self.yaw)],
                [0, 1, 0],
                [np.sin(self.yaw), 0, np.cos(self.yaw)],
            ]
        )
        # Rotation on x-axis
        r_pitch = np.array(
            [
                [1, 0, 0],
                [0, np.cos(self.pitch), np.sin(self.pitch)],
                [0, -np.sin(self.pitch), np.cos(self.pitch)],
            ]
        )
        # Rotation on z-axis
        r_roll = np.array(
            [
                [np.cos(self.roll), np.sin(self.roll), 0],
                [-np.sin(self.roll), np.cos(self.roll), 0],
                [0, 0, 1],
            ]
        )
        # Combined rotation matrix
        r = np.dot(np.dot(r_roll, r_pitch), r_yaw)

        return r

    def _get_projection_matrix(self):
        """

        :return:
        """
        rotation_matrix = self._get_rotation_matrix()
        origin = self._world_to_camera(np.array([0, 0, 0]))
        origin = np.expand_dims(origin, axis=0)
        stacked = np.hstack((rotation_matrix, origin.T))
        extrinsic_matrix = np.dot(self.camera_matrix, stacked)

        return extrinsic_matrix

    def _get_origin(self):
        """

        :return:
        """
        return self._world_to_camera(np.array([[0, 0, 0]]))

    def _world_to_camera(self, w):
        """

        :param w:
        :return:
        """
        return np.dot(self._get_rotation_matrix(), (w - self.center))

    def world_to_pixel(self, world_point):
        """
        Compute point from 3D-world coordinates to 2D-pixel coordinates
        in image.

        :param world_point:
        :return:
        """
        projection = self._get_projection_matrix()
        world_point1 = np.hstack((world_point, 1))
        world_point1 = np.expand_dims(world_point1, axis=0)
        uv1 = np.dot(projection, world_point1.T)
        uv = np.zeros(2)
        uv[0] = uv1[0] / uv1[2] if uv1[2] > 0 else float("NaN")
        uv[1] = uv1[1] / uv1[2] if uv1[2] > 0 else float("NaN")
        uv = np.rint(uv).astype(int).tolist()
        return uv

    def pixel_to_world(self, uv, plane=Plane(np.array([0, 1, 0]), 0)):
        """
        Compute point from 2D-pixel coordinates in image to
        3D-world coordinates.

        :param uv:
        :param plane:
        :return:
        """
        rotation_invert = np.linalg.inv(self._get_rotation_matrix())

        # Pixel coordinates
        uv1 = np.array([uv[0], uv[1], 1], dtype=float)
        # Camera coordinates
        line_of_sight_cam = np.dot(np.linalg.inv(self.camera_matrix), uv1)
        # World coordinates
        line_of_sight = np.dot(rotation_invert, line_of_sight_cam)
        camera_center = self.center
        line: Line = Line(camera_center, line_of_sight)
        world_point = intersection(plane, line)

        return world_point

    def _read_yaml(self, camera_file_pth: Union[str, pathlib.Path]):
        """ """
        calibration_file = cv2.FileStorage(str(camera_file_pth), cv2.FileStorage_READ)
        numbers = calibration_file.getNode("distortion_coefficients")
        dest_coef = []
        for i in range(0, numbers.size()):
            dest_coef.append(numbers.at(i).real())
        dest_coef = np.array(dest_coef)

        self.roll = calibration_file.getNode("roll").real()
        self.pitch = calibration_file.getNode("pitch").real()
        self.yaw = calibration_file.getNode("yaw").real()
        self.width = calibration_file.getNode("width").real()
        self.height = calibration_file.getNode("height").real()
        self.f = calibration_file.getNode("f").real()
        self.tvec = calibration_file.getNode("tvec").mat()
        self.camera_matrix = calibration_file.getNode("camera_matrix").mat()
        self.distortion_coefficients = dest_coef

        calibration_file.release()


def main():
    pass


if __name__ == "__main__":
    main()
