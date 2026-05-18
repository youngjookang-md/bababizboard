import pytest
from modules.templates import get_template, TEMPLATE_NAMES


def test_template_names_has_three():
    assert len(TEMPLATE_NAMES) == 3


def test_left_image_template_keys():
    t = get_template("left_image")
    for layer in ("logo", "main_text", "sub_text", "default_product"):
        assert layer in t


def test_right_image_product_x_is_right_side():
    t = get_template("right_image")
    assert t["default_product"]["x"] >= 500


def test_text_focus_main_text_x_is_left():
    t = get_template("text_focus")
    assert t["main_text"]["x"] < 300


def test_invalid_template_raises():
    with pytest.raises(KeyError):
        get_template("nonexistent")
