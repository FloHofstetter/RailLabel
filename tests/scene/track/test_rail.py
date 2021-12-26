import unittest
from src.scene.track import RailPoint, Rail


class TestRailPoint(unittest.TestCase):
    def test_p_x(self) -> None:
        """
        Assert RailPoint is sortable.
        """
        with self.subTest(msg="Sortable rail points"):
            rail_point_a = RailPoint(5, 10)
            rail_point_b = RailPoint(20, 15)
            rail_point_c = RailPoint(2.5, 5.2)

            un_sorted_a = [rail_point_a, rail_point_b, rail_point_c]
            un_sorted_b = [rail_point_c, rail_point_b, rail_point_a]
            un_sorted_c = [rail_point_b, rail_point_c, rail_point_a]
            _sorted = [rail_point_c, rail_point_a, rail_point_b]

            assert _sorted == sorted(un_sorted_a)
            assert _sorted == sorted(un_sorted_b)
            assert _sorted == sorted(un_sorted_c)


class TestRail(unittest.TestCase):
    def test_p_width(self) -> None:
        """
        Assert Rail.width property.
        """
        with self.subTest(msg="Return correct property"):
            width: float = 23.5
            rail = Rail(width)

            assert rail.width == width

    def test_p_marks(self) -> None:
        """
        Assert Rail.marks property.
        """
        with self.subTest(msg="Return correct and sorted property"):
            width: float = 23.5

            mark_a = RailPoint(5, 10)
            mark_b = RailPoint(20, 15)
            mark_c = RailPoint(2.5, 5.2)
            marks = [mark_a, mark_b, mark_c]

            rail = Rail(width)
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

            rail = Rail(width)

            assert rail.splines(steps) == []

        with self.subTest(msg="Amound of interpolated points"):
            width: float = 23.5

            mark_a = RailPoint(2.5, 5.2)
            mark_b = RailPoint(5, 10)
            mark_c = RailPoint(20, 15)
            marks = [mark_a, mark_b, mark_c]

            rail = Rail(width)
            rail.marks = marks
            splines = rail.splines(15)

            assert len(splines) == 15 * len(marks)

    def test_m_add_mark(self):
        """
        Assert Rail.add_mark methode.
        """
        with self.subTest(msg="Add property correctly"):
            width: float = 23.5

            mark_a = RailPoint(2.5, 5.2)
            mark_b = RailPoint(5, 10)
            mark_c = RailPoint(20, 15)
            marks = [mark_a, mark_b, mark_c]
            rail = Rail(width)
            [rail.add_mark(mark) for mark in marks]

            assert rail.marks[-1] == mark_c

    def test_m_del_mark(self):
        """
        Assert Rail.del_mark methode.
        """
        with self.subTest(msg="Delete nearest RailPoint"):
            width: float = 23.5

            mark_a = RailPoint(2.5, 5.2)
            mark_b = RailPoint(5, 10)
            mark_c = RailPoint(20, 15)
            marks = [mark_a, mark_b, mark_c]
            rail = Rail(width)
            [rail.add_mark(mark) for mark in marks]
            rail.del_mark(RailPoint(4, 9))

            assert rail.marks == sorted([mark_a, mark_c])

    def test_m_to_dict(self):
        """
        Assert Rail.to_dict methode.
        """
        with self.subTest(msg="Return correct dict"):
            width: float = 23.5

            mark_a = RailPoint(3, 5)
            mark_b = RailPoint(5, 10)
            mark_c = RailPoint(20, 15)
            marks = [mark_a, mark_b, mark_c]

            rail = Rail(width)
            rail.marks = marks

            rail_dict = {"points": [[3, 5], [5, 10], [20, 15]]}

            assert rail.to_dict() == rail_dict
