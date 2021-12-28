import unittest
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
import numpy as np

from src.scene.track import RailPoint, Rail


class TestRailPoint(TestCase):
    def test_p_x(self) -> None:
        """
        Assert RailPoint is sortable.
        """
        with self.subTest(msg="Sortable rail points"):
            rail_point_a: RailPoint = RailPoint(5, 10)
            rail_point_b: RailPoint = RailPoint(20, 15)
            rail_point_c: RailPoint = RailPoint(2.5, 5.2)

            un_sorted_a: list[RailPoint]
            un_sorted_a = [rail_point_a, rail_point_b, rail_point_c]
            un_sorted_b: list[RailPoint]
            un_sorted_b = [rail_point_c, rail_point_b, rail_point_a]
            un_sorted_a: list[RailPoint]
            un_sorted_c = [rail_point_b, rail_point_c, rail_point_a]
            _sorted: list[RailPoint]
            _sorted = [rail_point_c, rail_point_a, rail_point_b]

            assert _sorted == sorted(un_sorted_a)
            assert _sorted == sorted(un_sorted_b)
            assert _sorted == sorted(un_sorted_c)


class TestRail(TestCase):
    def test_p_width(self) -> None:
        """
        Assert Rail.width property.
        """
        with self.subTest(msg="Return correct property"):
            width: float = 23.5
            rail: Rail = Rail(width)

            assert rail.width == width

    def test_p_marks(self) -> None:
        """
        Assert Rail.marks property.
        """
        with self.subTest(msg="Return correct and sorted property"):
            width: float = 23.5

            mark_a: RailPoint = RailPoint(5, 10)
            mark_b: RailPoint = RailPoint(20, 15)
            mark_c: RailPoint = RailPoint(2.5, 5.2)
            marks: list[RailPoint] = [mark_a, mark_b, mark_c]

            rail: Rail = Rail(width)
            rail.marks = marks

            assert rail.marks != marks  # Asserts this test is useful
            assert rail.marks == sorted(marks)

    def test_m_splines(self):
        """
        Assert Rail.splines methode.
        """
        with self.subTest(msg="No splines when no marks"):
            width: float = 23.5
            steps: int = 15

            rail: Rail = Rail(width)

            assert rail.splines(steps) == []

        with self.subTest(msg="Amound of interpolated points"):
            width: float = 23.5

            mark_a: RailPoint = RailPoint(2.5, 5.2)
            mark_b: RailPoint = RailPoint(5, 10)
            mark_c: RailPoint = RailPoint(20, 15)
            marks: list[RailPoint] = [mark_a, mark_b, mark_c]

            rail: Rail = Rail(width)
            rail.marks = marks
            splines: list[RailPoint] = rail.splines(15)

            assert len(splines) == 15 * len(marks)

    def test_m_add_mark(self):
        """
        Assert Rail.add_mark methode.
        """
        with self.subTest(msg="Add property correctly"):
            width: float = 23.5

            mark_a: RailPoint = RailPoint(2.5, 5.2)
            mark_b: RailPoint = RailPoint(5, 10)
            mark_c: RailPoint = RailPoint(20, 15)
            marks: list[:RailPoint] = [mark_a, mark_b, mark_c]
            rail: Rail = Rail(width)
            mark: RailPoint
            [rail.add_mark(mark) for mark in marks]

            assert rail.marks[-1] == mark_c

    def test_m_del_mark(self):
        """
        Assert Rail.del_mark methode.
        """
        with self.subTest(msg="Delete nearest RailPoint"):
            width: float = 23.5

            mark_a: RailPoint = RailPoint(2.5, 5.2)
            mark_b: RailPoint = RailPoint(5, 10)
            mark_c: RailPoint = RailPoint(20, 15)
            marks: list[RailPoint] = [mark_a, mark_b, mark_c]
            rail: Rail = Rail(width)
            mark: RailPoint
            [rail.add_mark(mark) for mark in marks]
            rail.del_mark(RailPoint(4, 9))

            assert rail.marks == sorted([mark_a, mark_c])

    def test_m_to_dict(self):
        """
        Assert Rail.to_dict methode.
        """
        with self.subTest(msg="Return correct dict"):
            width: float = 23.5

            mark_a: RailPoint = RailPoint(3, 5)
            mark_b: RailPoint = RailPoint(5, 10)
            mark_c: RailPoint = RailPoint(20, 15)
            marks: list[RailPoint] = [mark_a, mark_b, mark_c]

            rail = Rail(width)
            rail.marks = marks

            rail_dict = {"points": [[3, 5], [5, 10], [20, 15]]}

            assert rail.to_dict() == rail_dict

    def test_m__contour_point(self) -> None:
        """
        Assert Rail._contour_point methode.
        """
        world_point: np.ndarray = np.array([10, 15, 30])
        image_point: np.ndarray = np.array([13, 17])
        camera_mock = MagicMock()
        camera_mock.pixel_to_world = Mock(return_value=world_point)
        camera_mock.world_to_pixel = Mock(return_value=image_point)

        width: float = 2.7
        spline_a: RailPoint = RailPoint(3, 7)
        rail: Rail = Rail(width)

        with self.subTest(msg="Left contour point"):
            contour_point = rail._contour_point(camera_mock, spline_a, -1)
            np.testing.assert_array_equal(
                np.array([3, 7]),
                camera_mock.pixel_to_world.call_args[0][0],
            )
            calculated_world_point = world_point

            # Half rail width to the left (x-axis)
            calculated_world_point[0] = calculated_world_point[0] - width / 2
            np.testing.assert_array_equal(
                np.array(calculated_world_point),
                camera_mock.world_to_pixel.call_args[0][0],
            )

            # Assert contour point is nearest integer
            round_image_point = np.rint(image_point).astype(int)
            assert contour_point.x == round_image_point[0].item()
            assert contour_point.y == round_image_point[1].item()

        with self.subTest(msg="Right contour point"):
            contour_point = rail._contour_point(camera_mock, spline_a, 1)
            np.testing.assert_array_equal(
                np.array([3, 7]),
                camera_mock.pixel_to_world.call_args[0][0],
            )
            calculated_world_point = world_point

            # Half rail width to the left (x-axis)
            calculated_world_point[0] = calculated_world_point[0] + width / 2
            np.testing.assert_array_equal(
                np.array(calculated_world_point),
                camera_mock.world_to_pixel.call_args[0][0],
            )

            # Assert contour point is nearest integer
            round_image_point = np.rint(image_point).astype(int)
            assert contour_point.x == round_image_point[0].item()
            assert contour_point.y == round_image_point[1].item()

    @patch.object(Rail, "_contour_point")
    @patch.object(Rail, "splines")
    def test_m_contour_point(self, m_splines, m__contour_point) -> None:
        """
        Assert Rail.contour_points methode.
        """
        width: float = 2.7
        steps: int = 5
        rail: Rail = Rail(width)

        camera_mock: MagicMock = MagicMock()
        splines_side_effect: list[RailPoint] = [
            RailPoint(14, 18),
            RailPoint(15, 11),
            RailPoint(23, 26),
        ]

        m_splines.return_value = splines_side_effect
        m__contour_point.return_value = RailPoint(10, 12)

        with self.subTest(msg="Left contour only"):
            contour_points = rail.contour_points(camera_mock, steps, "left")
            assert contour_points == [
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
            ]

        with self.subTest(msg="Right contour only"):
            contour_points = rail.contour_points(camera_mock, steps, "right")
            assert contour_points == [
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
            ]

        with self.subTest(msg="Both contours"):
            contour_points = rail.contour_points(camera_mock, steps, "both")
            assert contour_points == [
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
                RailPoint(10, 12),
            ]

        with self.subTest(msg="False side Exception"):
            with self.assertRaises(ValueError):
                rail.contour_points(camera_mock, steps, "a")
