CANVAS_W = 1029
CANVAS_H = 258

TEMPLATE_NAMES = ["right_image", "left_image", "center_image", "text_focus"]

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
    "center_image": {
        "label": "가운데 이미지형",
        "default_product": {"x": 390, "y": 0, "scale": 80},
        "logo": {"x": 860, "y": 15, "scale": 12},
        "main_text": {"x": 30, "y": 65, "size": 46},
        "sub_text":  {"x": 590, "y": 65, "size": 40},
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
