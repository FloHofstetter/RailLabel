import unittest
from src.scene.track import RailPoint


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
