import cv2
import numpy as np
import splines

from utils.camera import Camera


class Track:
    """
    Represents all information of a track in the label tool.
    """
    def __init__(self, t_id, rel_pos):
        """

        :param rel_pos: Relative position to ego-track
                        ("left", "ego", "right").
        """
        self._id = t_id
        # Track currently worked on
        self.is_active = False
        # Flags for expensive calculations only need on change
        self._new_splines_needed = True
        self._new_wire_grid_points_needed = True
        self._new_image_draw_needed = True
        # Amount of rail points
        self._rail_points_count = 0
        # Rail points marked by hand
        self._rail_points = {
            "leftrail": [],
            "centerpoint": [],
            "rightrail": [],
        }
        # Interpolated rail points
        self._spline_points = {
            "leftrail": [],
            "centerpoint": [],
            "rightrail": [],
        }
        # Wire grid point around rails
        self._rail_wire_grid_points = {
            "leftrail": [],
            "centerpoint": [],
            "rightrail": [],
        }
        self.rail_to_color: dict = {
            "leftrail": (0, 255, 0),
            "centerpoint": (255, 0, 0),
            "rightrail": (0, 0, 255),
        }
        rel_positions = ["left", "ego", "right"]
        if rel_pos not in rel_positions:
            msg = f"Expected rel_pos to be in {rel_positions}, got {rel_pos}"
            raise ValueError(msg)
        self.rel_pos = rel_pos

    def get_railpoints(self):
        return self._rail_points

    def get_flat_railpoints(self):
        flat_rail_points = {}
        for rail, points in self._rail_points.items():
            points = np.array(points)
            points = points.reshape(-1).tolist()
            flat_rail_points[rail] = points
        return flat_rail_points

    def unflatten_flat_rails(self):
        """
        Reconstruct 2D-coordinates from flat rails.

        :return:
        """
        rail_points = {}
        for rail, points in self._rail_points.items():
            points = np.array(points)
            points = points.reshape(-1, 2).tolist()
            rail_points[rail] = points
            print(points)
        self._rail_points = rail_points

    def recalculation_needed(self):
        """
        Set flags for ned of expensive calculations True.

        :return:
        """
        self._new_splines_needed = True
        self._new_splines_needed = True
        self._new_wire_grid_points_needed = True
        self._new_image_draw_needed = True

    def get_id(self):
        return self._id

    def get_rel_pos(self):
        return self.rel_pos

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def add_point(self, point):
        # Need recalculation of derived information
        self.recalculation_needed()
        self._rail_points["leftrail"].append(point[0])
        self._rail_points["rightrail"].append(point[1])
        # Sort all points for all rails by y-value (second)
        for name in self._rail_points:
            self._rail_points[name] = sorted(self._rail_points[name], key=lambda x: x[1], reverse=False)

    def add_points(self, points):
        """
        Add a batch of points as dict.

        :param points:
        :return:
        """
        self.recalculation_needed()
        self._rail_points = {**self._rail_points, **points}
        self._rail_points_count = len(self._rail_points)

    def remove_point(self, remove_point):
        """
        Remove nearest point to given point.

        :param remove_point: Point to remove.
        :return:
        """
        # Need recalculation of derived information
        self.recalculation_needed()
        distances = []
        # Calculate euclidean distance for all points
        for pnt in self._rail_points["leftrail"]:
            pnt = np.array(pnt)
            # Only left rail point is considered
            rem_pnt = np.array(remove_point[0])
            distance = np.linalg.norm(pnt - rem_pnt).item()
            distances.append(distance)
        # Remove point if there is at leas one
        if len(distances) > 0:
            distances = np.array(distances)
            min_index = np.argmin(distances)
            for name in self._rail_points.keys():
                # If list not empty
                if self._rail_points[name]:
                    self._rail_points[name].pop(min_index)

    def _calculate_spline(self, spline_steps):
        """
        Calculate splines over all rails.

        :param spline_steps: Interpolation steps between points.
        :return: None
        """
        # Fresh calculation only needed when rail points change
        if self._new_splines_needed:
            self._new_splines_needed = False
            for rail, points in self._rail_points.items():
                # Calculate splines if at leas two points are available.
                if len(points) >= 2:
                    # Every other item is respectively x and y coordinate
                    points = np.array(points)
                    # Create interpolation splines
                    sp = splines.CatmullRom(points, endconditions='natural')
                    td = sp.grid[-1] - sp.grid[0]
                    t = np.linspace(0, td, len(points) * spline_steps)
                    spline_arr = sp.evaluate(t)
                    # Round spline to integer because it represents a pixels
                    spline_arr = np.rint(spline_arr).astype(int)
                    self._spline_points[rail] = spline_arr.tolist()
                # Delete remaining splines if one annotation point left
                else:
                    self._spline_points[rail] = []

    def calculate_wire_grid_points(self, camera: Camera, steps=15):
        """
        Calculate points for wire grid around rails.

        :param steps: Annotation point interpolation steps.
        :return:
        """
        self._calculate_spline(steps)
        if self._new_wire_grid_points_needed:
            self._new_wire_grid_points_needed = False
            # Calculate wire points if at leas one spline-point is available.
            if len(self._spline_points["leftrail"]) >= 1:
                for rail, points in self._spline_points.items():
                    # Center point rail has no wire grid.
                    if rail == "centerpoint":
                        continue
                    wire_points = []
                    for point in points:
                        point_world = camera.pixel_to_world(point)
                        left_world = point_world - np.array([33.5, 0, 0])
                        right_world = point_world + np.array([33.5, 0, 0])
                        left_pixel = camera.world_to_pixel(left_world)
                        left_pixel = list(np.rint(left_pixel).astype(int))
                        right_pixel = camera.world_to_pixel(right_world)
                        right_pixel = list(np.rint(right_pixel).astype(int))
                        wire_points.append((left_pixel, right_pixel))
                    wire_points = np.array(wire_points)
                    # Shape: rail-side, points, coordinates
                    wire_points = wire_points.transpose(1, 0, 2)
                    # Change point order on right side top-bottom
                    wire_points[1] = np.flip(wire_points, axis=1)[1]
                    self._rail_wire_grid_points[rail] = wire_points
            # Delete remaining grid points if less then one spline point left
            else:
                for rail in self._rail_wire_grid_points.keys():
                    self._rail_wire_grid_points[rail] = []
            if len(self._spline_points["leftrail"]) >= 1:
                track_bed_wire_grid = np.vstack((self._rail_wire_grid_points["leftrail"][1], self._rail_wire_grid_points["rightrail"][0]))
                self._rail_wire_grid_points["centerpoint"] = track_bed_wire_grid

    def draw_track_wire_polygon(self, img, fill=False):
        """
        Calculate the polygon around rails.

        :return:
        """
        # Draw rail wire grid
        for rail, points in self. _rail_wire_grid_points.items():
            points = np.array(points)
            # Flatten out rail sides polygons
            points = points.reshape(-1, 2)
            points = np.expand_dims(points, axis=0)
            points = points.astype(np.int32)
            if fill:
                cv2.fillConvexPoly(img, points, self.rail_to_color[rail])
            else:
                cv2.polylines(img, points, True, self.rail_to_color[rail], thickness=3)
        return img

    def _draw(self, img, track_points, c_size=5, c_thickness=-1):
        """
        Draw points from a dict representing rails of a track.

        :param track_points: Track points dict to draw.
        :param img: Image to draw on.
        :param c_size: Size of circle point.
        :param c_thickness: Thickness of circle.
        :return: Image with track points
        """
        for rail, points in track_points.items():
            for point in points:
                img = cv2.circle(img, point, c_size, color=self.rail_to_color[rail], thickness=c_thickness)
        return img

    def draw_points(self, img):
        """
        Draw annotation points of track.

        :param img: Image to draw points on.
        :return: Image with rail points.
        """
        img = self._draw(img, self._rail_points, c_size=20, c_thickness=5)
        return img

    def draw_splines(self, img, steps: int = 5):
        """
        Draw interpolated splines of track.

        :param img: Image to draw splines on.
        :param steps: Interpolation steps between points.
        :return: Images with splines.
        """
        if steps < 1:
            msg = f"Expected steps to be positive integer, got {steps}"
            raise ValueError(msg)
        self._calculate_spline(steps)
        self._draw(img, self._spline_points)
        return img

    def draw_wire_grid_points(self, img):
        """

        :param img: Image to draw grid points.
        :return:
        """
        # Draw rail wire grid
        for rail, points in self._rail_wire_grid_points.items():
            points = np.array(points)
            # Flatten out rail sides polygons
            points = points.reshape(-1, 2)
            points = list(points)
            for point in points:
                cv2.circle(img, point, 5, color=self.rail_to_color[rail], thickness=-1)
        return img