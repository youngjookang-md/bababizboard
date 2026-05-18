CANVAS_W = 1029
CANVAS_H = 258

TEMPLATE_NAMES = ["right_image", "left_image", "text_focus"]

_TEMPLATES = {
    "right_image": {
        "label": "우측 이미지형",
        "default_product": {"x": 600, "y": 10, "scale": 80},
        "logo": {"x": 20, "y": 12, "scale": 15},
        "main_text": {"x": 50, "y": 70, "size": 48},
        "sub_text":  {"x": 50, "y": 155, "size": 39},
    },
    "left_image": {
        "label": "좌측 이미지형",
        "default_product": {"x": 20, "y": 10, "scale": 80},
        "logo": {"x": 20, "y": 12, "scale": 15},
        "main_text": {"x": 430, "y": 70, "size": 48},
        "sub_text":  {"x": 430, "y": 155, "size": 39},
    },
    "text_focus": {
        "label": "텍스트 강조형",
        "default_product": {"x": 800, "y": 10, "scale": 60},
        "logo": {"x": 20, "y": 12, "scale": 15},
        "main_text": {"x": 50, "y": 60, "size": 48},
        "sub_text":  {"x": 50, "y": 155, "size": 39},
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
