from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1029
CANVAS_H = 258
BG_COLOR = (0, 0, 0, 0)

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"

# Spoqa Han Sans
_SPOQA_BOLD    = _FONT_DIR / "SpoqaHanSansBold.ttf"
_SPOQA_REGULAR = _FONT_DIR / "SpoqaHanSansRegular.ttf"

# Pretendard
_PRETENDARD_BOLD    = _FONT_DIR / "PretendardBold.otf"
_PRETENDARD_REGULAR = _FONT_DIR / "PretendardRegular.otf"

FONT_FAMILIES = {
    "Spoqa Han Sans": (_SPOQA_BOLD,    _SPOQA_REGULAR),
    "Pretendard":     (_PRETENDARD_BOLD, _PRETENDARD_REGULAR),
}

DEFAULT_MAIN_SIZE = 48
DEFAULT_SUB_SIZE  = 39
MAIN_COPY_COLOR   = (76,  76,  76)
SUB_COPY_COLOR    = (119, 119, 119)

# 카카오 비즈보드 권장 텍스트 색상
KAKAO_TEXT_COLORS = {
    "기본 (#4C4C4C)":  (76,  76,  76),
    "중간 (#555555)":  (85,  85,  85),
    "연한 (#777777)":  (119, 119, 119),
    "커스텀":          None,
}

SAFE_MARGIN    = 20
GUIDELINE_COLOR = (190, 190, 190)


def _font_paths(family: str) -> tuple:
    return FONT_FAMILIES.get(family, FONT_FAMILIES["Spoqa Han Sans"])


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def _paste_image(canvas: Image.Image, layer: Optional[Image.Image], x: int, y: int, scale: int) -> None:
    if layer is None:
        return
    new_w = max(1, int(layer.width  * scale / 100))
    new_h = max(1, int(layer.height * scale / 100))
    resized = layer.resize((new_w, new_h), Image.LANCZOS)
    if resized.mode != "RGBA":
        resized = resized.convert("RGBA")
    canvas.paste(resized, (x, y), resized)


def _draw_guidelines(canvas: Image.Image) -> Image.Image:
    preview = canvas.copy()
    draw = ImageDraw.Draw(preview)
    m = SAFE_MARGIN
    x0, y0 = m, m
    x1, y1 = CANVAS_W - m - 1, CANVAS_H - m - 1
    dash_len, gap_len = 8, 5

    def draw_dashed_line(p1, p2):
        px, py = p1
        ex, ey = p2
        dx, dy = ex - px, ey - py
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        pos, drawing = 0, True
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


def _draw_badge(draw, text, x, y, font, bg_color, text_color):
    pad_x, pad_y = 10, 5
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle([x, y, x + tw + pad_x*2, y + th + pad_y*2], radius=5, fill=bg_color)
    draw.text((x + pad_x, y + pad_y - bbox[1]), text, font=font, fill=text_color)


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
    main_font_family: str = "Spoqa Han Sans",
    main_color: tuple = MAIN_COPY_COLOR,
    sub_copy: str = "",
    sub_x: int = 50,
    sub_y: int = 155,
    sub_copy_size: int = DEFAULT_SUB_SIZE,
    sub_font_family: str = "Spoqa Han Sans",
    sub_color: tuple = SUB_COPY_COLOR,
    badges: Optional[list] = None,
    extra_copies: Optional[list] = None,
    show_guidelines: bool = False,
) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG_COLOR)

    if product_images:
        for item in product_images:
            _paste_image(canvas, item.get("image"), item.get("x", 0), item.get("y", 0), item.get("scale", 75))

    _paste_image(canvas, logo_image, logo_x, logo_y, logo_scale)

    draw = ImageDraw.Draw(canvas)

    if main_copy:
        bold_path, regular_path = _font_paths(main_font_family)
        font = _load_font(bold_path, main_copy_size)
        draw.text((main_x, main_y), main_copy, font=font, fill=main_color)

    if sub_copy:
        bold_path, regular_path = _font_paths(sub_font_family)
        font = _load_font(regular_path, sub_copy_size)
        draw.text((sub_x, sub_y), sub_copy, font=font, fill=sub_color)

    for ec in (extra_copies or []):
        if ec.get("enabled") and ec.get("text"):
            bold_path, regular_path = _font_paths(ec.get("font_family", "Spoqa Han Sans"))
            ec_path = bold_path if ec.get("bold") else regular_path
            ecfont = _load_font(ec_path, ec.get("size", 36))
            ec_color = tuple(ec.get("color", list(MAIN_COPY_COLOR)))
            draw.text((ec.get("x", 50), ec.get("y", 100)), ec["text"], font=ecfont, fill=ec_color)

    for badge in (badges or []):
        bfont = _load_font(_SPOQA_BOLD, badge.get("font_size", 28))
        _draw_badge(
            draw, badge["text"],
            badge.get("x", 50), badge.get("y", 100),
            bfont,
            tuple(badge.get("bg_color",   (29, 158, 117))),
            tuple(badge.get("text_color", (255, 255, 255))),
        )

    if show_guidelines:
        canvas = _draw_guidelines(canvas)

    return canvas
