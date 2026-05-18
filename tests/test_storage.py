import json
import pytest
from pathlib import Path
from PIL import Image
from modules.storage import save_project, load_project, list_projects

@pytest.fixture
def tmp_projects(tmp_path, monkeypatch):
    monkeypatch.setattr("modules.storage.PROJECTS_DIR", tmp_path)
    return tmp_path

def test_save_creates_json(tmp_projects):
    state = {
        "name": "test_project",
        "template": "left_image",
        "main_copy": "안녕",
        "sub_copy": "반가워",
        "layers": {
            "product": {"x": 20, "y": 20, "scale": 75},
            "logo":    {"x": 830, "y": 10, "scale": 20},
            "main_text": {"x": 440, "y": 70},
            "sub_text":  {"x": 440, "y": 145},
        },
        "product_image": None,
        "logo_image": None,
    }
    save_project(state)
    json_path = tmp_projects / "test_project" / "project.json"
    assert json_path.exists()

def test_load_project_roundtrip(tmp_projects):
    state = {
        "name": "roundtrip",
        "template": "right_image",
        "main_copy": "카피",
        "sub_copy": "서브",
        "layers": {
            "product": {"x": 700, "y": 20, "scale": 75},
            "logo":    {"x": 20,  "y": 10, "scale": 20},
            "main_text": {"x": 50, "y": 70},
            "sub_text":  {"x": 50, "y": 145},
        },
        "product_image": None,
        "logo_image": None,
    }
    save_project(state)
    loaded = load_project("roundtrip")
    assert loaded["main_copy"] == "카피"
    assert loaded["layers"]["product"]["x"] == 700

def test_list_projects_returns_saved_names(tmp_projects):
    for name in ("proj_a", "proj_b"):
        (tmp_projects / name).mkdir()
        (tmp_projects / name / "project.json").write_text(
            json.dumps({"name": name})
        )
    names = list_projects()
    assert "proj_a" in names
    assert "proj_b" in names

def test_save_with_product_image(tmp_projects):
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    state = {
        "name": "with_image",
        "template": "left_image",
        "main_copy": "",
        "sub_copy": "",
        "layers": {
            "product": {"x": 20, "y": 20, "scale": 75},
            "logo":    {"x": 830, "y": 10, "scale": 20},
            "main_text": {"x": 440, "y": 70},
            "sub_text":  {"x": 440, "y": 145},
        },
        "product_image": img,
        "logo_image": None,
    }
    save_project(state)
    assert (tmp_projects / "with_image" / "product.png").exists()

def test_load_project_no_path_keys_in_result(tmp_projects):
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    state = {
        "name": "no_path_keys",
        "template": "left_image",
        "main_copy": "",
        "sub_copy": "",
        "layers": {
            "product": {"x": 20, "y": 20, "scale": 75},
            "logo":    {"x": 830, "y": 10, "scale": 20},
            "main_text": {"x": 440, "y": 70},
            "sub_text":  {"x": 440, "y": 145},
        },
        "product_image": img,
        "logo_image": None,
    }
    save_project(state)
    loaded = load_project("no_path_keys")
    assert "product_image_path" not in loaded
    assert "logo_image_path" not in loaded
