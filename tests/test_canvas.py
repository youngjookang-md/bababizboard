import pytest
from PIL import Image
from modules.canvas import render


def _white_img(w, h):
    return Image.new("RGBA", (w, h), (255, 255, 255, 255))


def test_render_returns_correct_size():
    img = render()
    assert img.size == (1200, 600)


def test_render_is_rgb():
    img = render()
    assert img.mode == "RGB"


def test_render_with_product_images():
    products = [{"image": _white_img(200, 200), "x": 10, "y": 10, "scale": 50}]
    img = render(product_images=products)
    assert img.size == (1200, 600)


def test_render_with_main_copy():
    img = render(main_copy="테스트 카피")
    assert img.size == (1200, 600)


def test_render_with_all_layers():
    products = [
        {"image": _white_img(200, 200), "x": 20, "y": 20, "scale": 70},
        {"image": _white_img(150, 150), "x": 250, "y": 80, "scale": 60},
    ]
    logo = _white_img(100, 50)
    img = render(
        product_images=products,
        logo_image=logo, logo_x=20, logo_y=15, logo_scale=20,
        main_copy="메인 카피", main_x=520, main_y=200,
        sub_copy="서브 카피", sub_x=520, sub_y=330,
    )
    assert img.size == (1200, 600)


def test_render_with_guidelines():
    img = render(show_guidelines=True)
    assert img.size == (1200, 600)
    assert img.mode == "RGB"
