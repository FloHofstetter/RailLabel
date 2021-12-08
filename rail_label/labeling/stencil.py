import cv2
import numpy as np

from rail_label.utils import Camera, Mouse


class Stencil:
    """
    Represents the stencil to aim for both rails.

    """
    def __init__(self, camera: Camera, mouse: Mouse):
        """

        :param camera: Camera class calculating pixel/world coordinates.
        :param mouse: Mouse class to handle input.
        """
        self._camera = camera
        self._mouse = mouse
        self._left_rail_point = 0
        self._center_rail_point = 1
        self._right_rail_point = 1
        # Width between crosshair circles on rails.
        self._width = 1
        # Manually correct stencil width
        self._width_correction = 0
        # Stencil aiming mode
        self._mode = "aim_left_rail"

    def set_width_correction(self, correction: int):
        """
        Correct the with of the stencil by amount of pixel.
        :param correction: Number of pixel to correct.
        :return: None
        """
        if not isinstance(correction, int):
            msg = f"Expectet correction to be type int, got {type(correction)}"
            raise TypeError(msg)
        # Don't drive width correction to negative value
        if self._width <= 1 and correction < 0:
            self._width_correction += 0
        else:
            self._width_correction += correction

    def _set_width(self, width):
        """
        Set width of the stencil. Width can not be negative.
        :param width: Width of the stencil.
        :return: None
        """
        self._width = width if width > 0 else 1

    def _calculate_rail_points(self):
        """
        Calculate the points on witch the stencil aims.

        :return: None
        """
        l_rail_px = self._mouse.position
        l_rail_wd = self._camera.pixel_to_world(l_rail_px)
        r_rail_wd = l_rail_wd + np.array([1502, 0, 0])
        r_rail_px = self._camera.world_to_pixel(r_rail_wd)
        width = r_rail_px[0] - l_rail_px[0]
        width = width if width > 0 else 1
        width += self._width_correction
        self._set_width(width)

        # Free circle is on the right
        if self._mode == "aim_left_rail":
            self._left_rail_point = self._mouse.position
            self._right_rail_point = (self._left_rail_point[0] + self._width, self._left_rail_point[1])
        # Free circle is on the left
        elif self._mode == "aim_right_rail":
            self._right_rail_point = self._mouse.position
            self._left_rail_point = (self._right_rail_point[0] - self._width, self._right_rail_point[1])
        else:
            msg = "Expected mode to be 'aim_left_rail' "
            msg += f"or 'aim_right_rail', got {self._mode}"
            raise ValueError(msg)
        # Center is in the middle ether way
        center_rail_point = np.mean((self._left_rail_point, self._right_rail_point), axis=0)
        # Round to full pixel
        self._center_rail_point = np.rint(center_rail_point).astype(int)

    def get_rail_points(self):
        return self._left_rail_point, self._center_rail_point, self._right_rail_point

    def draw(self, img):
        """
        Update position of the stencil elements to mouse position.

        :param img: Image to draw stencil on.
        :return: None.
        """
        self._calculate_rail_points()
        # Draw left circle
        center = self._left_rail_point
        radius = 20
        color = (255, 0, 0)
        thickness = 1

        # Draw left circle
        cv2.circle(img, center, radius, color, thickness)
        # Draw crosshair
        pt1 = [self._left_rail_point[0] - radius, self._left_rail_point[1]]
        pt2 = [self._left_rail_point[0] + radius, self._left_rail_point[1]]
        cv2.line(img, pt1, pt2, color, thickness)
        pt1 = [self._left_rail_point[0], self._left_rail_point[1] - radius]
        pt2 = [self._left_rail_point[0], self._left_rail_point[1] + radius]
        cv2.line(img, pt1, pt2, color, thickness)

        # Draw right circle
        center = self._right_rail_point
        cv2.circle(img, center, radius, color, thickness)
        # Draw crosshair
        pt1 = [self._right_rail_point[0] - radius, self._right_rail_point[1]]
        pt2 = [self._right_rail_point[0] + radius, self._right_rail_point[1]]
        cv2.line(img, pt1, pt2, color, thickness)
        pt1 = [self._right_rail_point[0], self._right_rail_point[1] - radius]
        pt2 = [self._right_rail_point[0], self._right_rail_point[1] + radius]
        cv2.line(img, pt1, pt2, color, thickness)

        # Draw line between circles
        pt1 = [self._right_rail_point[0] - radius, self._right_rail_point[1]]
        pt2 = [self._left_rail_point[0] + radius, self._left_rail_point[1]]
        cv2.line(img, pt1, pt2, color, thickness)
        return img

    def toggle_mode(self):
        """
        Toggle the mode of the stencil.
        :return:
        """
        if self._mode == "aim_left_rail":
            self._mode = "aim_right_rail"
        else:
            self._mode = "aim_left_rail"