import base64
from io import BytesIO
from pathlib import Path

import streamlit.components.v1 as components
from PIL import Image

_COMPONENT_DIR = Path(__file__).parent
_drag_canvas = components.declare_component("canvas_drag", path=str(_COMPONENT_DIR))


def canvas_drag(
    canvas_img: Image.Image,
    elements: list,
    canvas_w: int = 1029,
    canvas_h: int = 258,
    preview_w: int = 700,
    key: str = None,
):
    buf = BytesIO()
    canvas_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    preview_h = int(canvas_h * preview_w / canvas_w) + 8
    return _drag_canvas(
        img_b64=img_b64,
        elements=elements,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        preview_w=preview_w,
        key=key,
        default=None,
        height=preview_h,
    )
