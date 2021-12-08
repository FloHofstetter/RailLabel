import cv2


class Mouse:
    """
    Stores coordinates from a left mouse click callback.
    """

    def __init__(self):
        """
        Create empty list of coordinates.
        """
        self.left_click_position = (0, 0)
        self.position = (0, 0)
        self.mouse_h_wheel = 0
        self.mouse_w_wheel = 0

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.left_click_position = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self.position = (x, y)
        # Can't disable zoom in QT built
        elif event == cv2.EVENT_MOUSEHWHEEL:
            pass
        # Can't disable zoom in QT built
        elif event == cv2.EVENT_MOUSEWHEEL:
            pass
