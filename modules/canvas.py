from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1200
CANVAS_H = 600
BG_COLOR = (255, 255, 255)

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_FONT_BOLD = _FONT_DIR / "SpoqaHanSansBold.ttf"
_FONT_REGULAR = _FONT_DIR / "SpoqaHanSansRegular.ttf"

MAIN_COPY_SIZE = 80
SUB_COPY_SIZE = 52
MAIN_COPY_COLOR = (76, 76, 76)
SUB_COPY_COLOR = (119, 119, 119)

GUIDELINE_COLOR = (220, 60, 60)
GUIDELINE_WIDTH = 2
SAFE_MARGIN = 30


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def _paste_image(canvas: Image.Image, layer: Optional[Image.Image], x: int, y: int, scale: int) -> None:
    if layer is None:
        return
    new_w = max(1, int(layer.width * scale / 100))
    new_h = max(1, int(layer.height * scale / 100))
    resized = layer.resize((new_w, new_h), Image.LANCZOS)
    if resized.mode == "RGBA":
        canvas.paste(resized, (x, y), resized)
    else:
        canvas.paste(resized, (x, y))


def _draw_guidelines(canvas: Image.Image) -> Image.Image:
    """Draw safe-area guideline border on a copy of the canvas (preview only)."""
    preview = canvas.copy()
    draw = ImageDraw.Draw(preview)
    m = SAFE_MARGIN
    w, h = CANVAS_W, CANVAS_H
    # outer border
    draw.rectangle([(0, 0), (w - 1, h - 1)], outline=GUIDELINE_COLOR, width=GUIDELINE_WIDTH)
    # safe area inner border
    draw.rectangle([(m, m), (w - m - 1, h - m - 1)], outline=GUIDELINE_COLOR, width=1)
    return preview


def render(
    product_images: Optional[list] = None,
    logo_image: Optional[Image.Image] = None,
    logo_x: int = 20,
    logo_y: int = 15,
    logo_scale: int = 20,
    main_copy: str = "",
    main_x: int = 500,
    main_y: int = 200,
    sub_copy: str = "",
    sub_x: int = 500,
    sub_y: int = 320,
    show_guidelines: bool = False,
) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

    # render product images (list of dicts: {image, x, y, scale})
    if product_images:
        for item in product_images:
            _paste_image(canvas, item.get("image"), item.get("x", 0), item.get("y", 0), item.get("scale", 75))

    _paste_image(canvas, logo_image, logo_x, logo_y, logo_scale)

    draw = ImageDraw.Draw(canvas)

    if main_copy:
        font = _load_font(_FONT_BOLD, MAIN_COPY_SIZE)
        draw.text((main_x, main_y), main_copy, font=font, fill=MAIN_COPY_COLOR)

    if sub_copy:
        font = _load_font(_FONT_REGULAR, SUB_COPY_SIZE)
        draw.text((sub_x, sub_y), sub_copy, font=font, fill=SUB_COPY_COLOR)

    if show_guidelines:
        canvas = _draw_guidelines(canvas)

    return canvas
