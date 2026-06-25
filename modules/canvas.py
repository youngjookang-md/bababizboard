from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1029
CANVAS_H = 258
BG_COLOR = (255, 255, 255)

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_FONT_BOLD = _FONT_DIR / "SpoqaHanSansBold.ttf"
_FONT_REGULAR = _FONT_DIR / "SpoqaHanSansRegular.ttf"

DEFAULT_MAIN_SIZE = 48
DEFAULT_SUB_SIZE = 39
MAIN_COPY_COLOR = (76, 76, 76)
SUB_COPY_COLOR = (119, 119, 119)

SAFE_MARGIN = 20
GUIDELINE_COLOR = (190, 190, 190)


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
    """Draw a subtle dashed safe-area rectangle on a copy of the canvas."""
    preview = canvas.copy()
    draw = ImageDraw.Draw(preview)
    m = SAFE_MARGIN
    x0, y0 = m, m
    x1, y1 = CANVAS_W - m - 1, CANVAS_H - m - 1
    dash_len, gap_len = 8, 5

    def draw_dashed_line(p1, p2):
        px, py = p1
        ex, ey = p2
        dx = ex - px
        dy = ey - py
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        pos = 0
        drawing = True
        while pos < length:
            seg = dash_len if drawing else gap_len
            end_pos = min(pos + seg, length)
            if drawing:
                draw.line(
                    [(px + ux * pos, py + uy * pos), (px + ux * end_pos, py + uy * end_pos)],
                    fill=GUIDELINE_COLOR, width=1,
                )
            pos = end_pos
            drawing = not drawing

    draw_dashed_line((x0, y0), (x1, y0))
    draw_dashed_line((x1, y0), (x1, y1))
    draw_dashed_line((x1, y1), (x0, y1))
    draw_dashed_line((x0, y1), (x0, y0))
    return preview


def _draw_badge(draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
                font: ImageFont.FreeTypeFont, bg_color: tuple, text_color: tuple) -> None:
    """Draw a pill-shaped badge with background color."""
    pad_x, pad_y = 10, 5
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    rx0, ry0 = x, y
    rx1, ry1 = x + tw + pad_x * 2, y + th + pad_y * 2
    draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=5, fill=bg_color)
    draw.text((rx0 + pad_x, ry0 + pad_y - bbox[1]), text, font=font, fill=text_color)


def render(
    product_images: Optional[list] = None,
    logo_image: Optional[Image.Image] = None,
    logo_x: int = 20,
    logo_y: int = 12,
    logo_scale: int = 15,
    main_copy: str = "",
    main_x: int = 50,
    main_y: int = 70,
    main_copy_size: int = DEFAULT_MAIN_SIZE,
    sub_copy: str = "",
    sub_x: int = 50,
    sub_y: int = 155,
    sub_copy_size: int = DEFAULT_SUB_SIZE,
    badges: Optional[list] = None,
    show_guidelines: bool = False,
) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

    if product_images:
        for item in product_images:
            _paste_image(canvas, item.get("image"), item.get("x", 0), item.get("y", 0), item.get("scale", 75))

    _paste_image(canvas, logo_image, logo_x, logo_y, logo_scale)

    draw = ImageDraw.Draw(canvas)

    if main_copy:
        font = _load_font(_FONT_BOLD, main_copy_size)
        draw.text((main_x, main_y), main_copy, font=font, fill=MAIN_COPY_COLOR)

    if sub_copy:
        font = _load_font(_FONT_REGULAR, sub_copy_size)
        draw.text((sub_x, sub_y), sub_copy, font=font, fill=SUB_COPY_COLOR)

    for badge in (badges or []):
        bfont = _load_font(_FONT_BOLD, badge.get("font_size", 28))
        _draw_badge(
            draw,
            badge["text"],
            badge.get("x", 50),
            badge.get("y", 100),
            bfont,
            tuple(badge.get("bg_color", (29, 158, 117))),
            tuple(badge.get("text_color", (255, 255, 255))),
        )

    if show_guidelines:
        canvas = _draw_guidelines(canvas)

    return canvas
