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

def test_render_with_product_image():
    product = _white_img(200, 200)
    img = render(product_image=product, product_x=10, product_y=10, product_scale=50)
    assert img.size == (1029, 258)

def test_render_with_main_copy():
    img = render(main_copy="테스트 카피")
    assert img.size == (1029, 258)

def test_render_with_all_layers():
    product = _white_img(200, 200)
    logo = _white_img(100, 50)
    img = render(
        product_image=product, product_x=20, product_y=20, product_scale=70,
        logo_image=logo, logo_x=800, logo_y=10, logo_scale=20,
        main_copy="메인 카피", main_x=440, main_y=70,
        sub_copy="서브 카피", sub_x=440, sub_y=145,
    )
    assert img.size == (1029, 258)
