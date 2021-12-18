import numpy as np
import cv2
from rail_label.utils.mouse import Mouse


class CrossHair:
    """
    Implements bounding box crosshair.
    """

    def __init__(
        self,
        image_height: int,
        image_width: int,
        buffer: float = 0.025,
    ) -> None:
        """
        :param image_height: Height of the target image
        :param image_width: Width of the target image
        :param buffer: Relative buffer to mouse
        """
        # Relative buffer to absolute buffer
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.buffer: int
        self.buffer = np.rint(image_width * buffer).astype(int).item()
        self._left: tuple[tuple[int, int], tuple[int, int]]
        self._left = ((0, 0), (0, 0))
        self._right: tuple[tuple[int, int], tuple[int, int]]
        self._right = ((0, 0), (0, 0))
        self._top: tuple[tuple[int, int], tuple[int, int]]
        self._top = ((0, 0), (0, 0))
        self._bottom: tuple[tuple[int, int], tuple[int, int]]
        self._bottom = ((0, 0), (0, 0))
        self._center = (0, 0)

    def calculate(self, mouse: Mouse):
        mouse_x: int = mouse.position[0]
        mouse_y: int = mouse.position[1]
        self._left = ((0, mouse_y), (mouse_x - self.buffer, mouse_y))
        self._right = ((mouse_x + self.buffer, mouse_y), (self.image_width, mouse_y))
        self._top = ((mouse_x, 0), (mouse_x, mouse_y - self.buffer))
        self._bottom = ((mouse_x, mouse_y + self.buffer), (mouse_x, self.image_height))
        self._center = mouse.position

    def draw(self, image):
        cv2.line(image, *self.left, (255, 255, 255), 5)
        cv2.line(image, *self.right, (255, 255, 255), 5)
        cv2.line(image, *self.top, (255, 255, 255), 5)
        cv2.line(image, *self.bottom, (255, 255, 255), 5)
        cv2.circle(image, self.center, 5, color=(255, 255, 255), thickness=-1)
        return image

    @property
    def center(self) -> tuple[int, int]:
        return self._center

    @center.setter
    def center(self, center: tuple[int, int]):
        self._center = center

    @property
    def left(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self._left

    @left.setter
    def left(self, left: tuple[tuple[int, int], tuple[int, int]]):
        self._left = left

    @property
    def right(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self._right

    @right.setter
    def right(self, right: tuple[tuple[int, int], tuple[int, int]]):
        self._right = right

    @property
    def top(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self._top

    @top.setter
    def top(self, top: tuple[tuple[int, int], tuple[int, int]]):
        self._top = top

    @property
    def bottom(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self._bottom

    @bottom.setter
    def bottom(self, bottom: tuple[tuple[int, int], tuple[int, int]]):
        self._bottom = bottom
