CANVAS_W = 1029
CANVAS_H = 258

TEMPLATE_NAMES = ["left_image", "right_image", "text_focus"]

_TEMPLATES = {
    "left_image": {
        "label": "좌측 이미지형",
        "product": {"x": 20,  "y": 20, "scale": 75},
        "logo":    {"x": 830, "y": 10, "scale": 20},
        "main_text": {"x": 440, "y": 70},
        "sub_text":  {"x": 440, "y": 145},
    },
    "right_image": {
        "label": "우측 이미지형",
        "product": {"x": 700, "y": 20, "scale": 75},
        "logo":    {"x": 20,  "y": 10, "scale": 20},
        "main_text": {"x": 50, "y": 70},
        "sub_text":  {"x": 50, "y": 145},
    },
    "text_focus": {
        "label": "텍스트 강조형",
        "product": {"x": 800, "y": 10, "scale": 60},
        "logo":    {"x": 20,  "y": 10, "scale": 18},
        "main_text": {"x": 50, "y": 55},
        "sub_text":  {"x": 50, "y": 135},
    },
}

def get_template(name: str) -> dict:
    return _TEMPLATES[name]

def template_label_map() -> dict:
    return {k: v["label"] for k, v in _TEMPLATES.items()}
