import pytest
from PIL import Image
from modules.canvas import render


def _white_img(w, h):
    return Image.new("RGBA", (w, h), (255, 255, 255, 255))


def test_render_returns_correct_size():
    img = render()
    assert img.size == (1029, 258)


def test_render_is_rgb():
    img = render()
    assert img.mode == "RGB"


def test_render_with_product_images():
    products = [{"image": _white_img(200, 200), "x": 10, "y": 10, "scale": 50}]
    img = render(product_images=products)
    assert img.size == (1029, 258)


def test_render_with_main_copy():
    img = render(main_copy="테스트 카피")
    assert img.size == (1029, 258)


def test_render_with_custom_font_sizes():
    img = render(main_copy="메인", main_copy_size=60, sub_copy="서브", sub_copy_size=40)
    assert img.size == (1029, 258)


def test_render_with_all_layers():
    products = [
        {"image": _white_img(200, 200), "x": 600, "y": 10, "scale": 80},
        {"image": _white_img(150, 150), "x": 750, "y": 30, "scale": 60},
    ]
    logo = _white_img(100, 30)
    img = render(
        product_images=products,
        logo_image=logo, logo_x=20, logo_y=12, logo_scale=15,
        main_copy="메인 카피", main_x=50, main_y=70, main_copy_size=48,
        sub_copy="서브 카피", sub_x=50, sub_y=155, sub_copy_size=39,
    )
    assert img.size == (1029, 258)


def test_render_with_guidelines():
    img = render(show_guidelines=True)
    assert img.size == (1029, 258)
    assert img.mode == "RGB"
