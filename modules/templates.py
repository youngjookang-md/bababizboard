CANVAS_W = 1200
CANVAS_H = 600

TEMPLATE_NAMES = ["left_image", "right_image", "text_focus"]

_TEMPLATES = {
    "left_image": {
        "label": "좌측 이미지형",
        "default_product": {"x": 30, "y": 50, "scale": 75},
        "logo": {"x": 20, "y": 15, "scale": 20},
        "main_text": {"x": 520, "y": 200},
        "sub_text":  {"x": 520, "y": 330},
    },
    "right_image": {
        "label": "우측 이미지형",
        "default_product": {"x": 680, "y": 50, "scale": 75},
        "logo": {"x": 20, "y": 15, "scale": 20},
        "main_text": {"x": 50, "y": 200},
        "sub_text":  {"x": 50, "y": 330},
    },
    "text_focus": {
        "label": "텍스트 강조형",
        "default_product": {"x": 850, "y": 30, "scale": 60},
        "logo": {"x": 20, "y": 15, "scale": 18},
        "main_text": {"x": 50, "y": 150},
        "sub_text":  {"x": 50, "y": 300},
    },
}


def get_template(name: str) -> dict:
    t = _TEMPLATES[name]
    return {
        "logo": dict(t["logo"]),
        "main_text": dict(t["main_text"]),
        "sub_text": dict(t["sub_text"]),
        "default_product": dict(t["default_product"]),
    }


def template_label_map() -> dict:
    return {k: v["label"] for k, v in _TEMPLATES.items()}
