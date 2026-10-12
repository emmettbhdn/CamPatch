import pytest

from campatch.camera import parse_points


def test_parse_four_calibration_points() -> None:
    assert parse_points("0,1;2,3;4,5;6,7") == [(0, 1), (2, 3), (4, 5), (6, 7)]


def test_parse_points_requires_four() -> None:
    with pytest.raises(ValueError):
        parse_points("0,1;2,3")
