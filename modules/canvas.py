from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1029
CANVAS_H = 258
BG_COLOR = (255, 255, 255)

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_FONT_BOLD = _FONT_DIR / "SpoqaHanSansBold.ttf"
_FONT_REGULAR = _FONT_DIR / "SpoqaHanSansRegular.ttf"

MAIN_COPY_SIZE = 48
SUB_COPY_SIZE = 39
MAIN_COPY_COLOR = (76, 76, 76)      # #4C4C4C
SUB_COPY_COLOR = (119, 119, 119)    # #777777


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _paste_image(canvas: Image.Image, layer: Image.Image, x: int, y: int, scale: int) -> None:
    if layer is None:
        return
    new_w = max(1, int(layer.width * scale / 100))
    new_h = max(1, int(layer.height * scale / 100))
    resized = layer.resize((new_w, new_h), Image.LANCZOS)
    if resized.mode == "RGBA":
        canvas.paste(resized, (x, y), resized)
    else:
        canvas.paste(resized, (x, y))


def render(
    product_image: Image.Image | None = None,
    product_x: int = 20,
    product_y: int = 20,
    product_scale: int = 75,
    logo_image: Image.Image | None = None,
    logo_x: int = 830,
    logo_y: int = 10,
    logo_scale: int = 20,
    main_copy: str = "",
    main_x: int = 440,
    main_y: int = 70,
    sub_copy: str = "",
    sub_x: int = 440,
    sub_y: int = 145,
) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

    _paste_image(canvas, product_image, product_x, product_y, product_scale)
    _paste_image(canvas, logo_image, logo_x, logo_y, logo_scale)

    draw = ImageDraw.Draw(canvas)

    if main_copy:
        font = _load_font(_FONT_BOLD, MAIN_COPY_SIZE)
        draw.text((main_x, main_y), main_copy, font=font, fill=MAIN_COPY_COLOR)

    if sub_copy:
        font = _load_font(_FONT_REGULAR, SUB_COPY_SIZE)
        draw.text((sub_x, sub_y), sub_copy, font=font, fill=SUB_COPY_COLOR)

    return canvas
