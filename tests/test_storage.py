import json
import pytest
from pathlib import Path
from PIL import Image
from modules.storage import save_project, load_project, list_projects


@pytest.fixture
def tmp_projects(tmp_path, monkeypatch):
    monkeypatch.setattr("modules.storage.PROJECTS_DIR", tmp_path)
    return tmp_path


def _base_state(name="test_project", product_images=None, logo_image=None):
    return {
        "name": name,
        "template": "left_image",
        "main_copy": "안녕",
        "sub_copy": "반가워",
        "layers": {
            "logo": {"x": 20, "y": 15, "scale": 20},
            "main_text": {"x": 520, "y": 200},
            "sub_text": {"x": 520, "y": 330},
            "products": [],
        },
        "product_images": product_images or [],
        "logo_image": logo_image,
    }


def test_save_creates_json(tmp_projects):
    save_project(_base_state())
    assert (tmp_projects / "test_project" / "project.json").exists()


def test_load_project_roundtrip(tmp_projects):
    state = _base_state("roundtrip")
    state["main_copy"] = "카피"
    state["layers"]["logo"]["x"] = 30
    save_project(state)
    loaded = load_project("roundtrip")
    assert loaded["main_copy"] == "카피"
    assert loaded["layers"]["logo"]["x"] == 30


def test_list_projects_returns_saved_names(tmp_projects):
    for name in ("proj_a", "proj_b"):
        (tmp_projects / name).mkdir()
        (tmp_projects / name / "project.json").write_text(json.dumps({"name": name}))
    names = list_projects()
    assert "proj_a" in names and "proj_b" in names


def test_save_with_product_images(tmp_projects):
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    state = _base_state("with_images", product_images=[{"image": img, "x": 10, "y": 10, "scale": 75}])
    save_project(state)
    assert (tmp_projects / "with_images" / "product_0.png").exists()


def test_load_restores_product_images(tmp_projects):
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    state = _base_state("restore_test", product_images=[{"image": img, "x": 50, "y": 60, "scale": 80}])
    save_project(state)
    loaded = load_project("restore_test")
    assert len(loaded["product_images"]) == 1
    assert loaded["product_images"][0]["x"] == 50
    assert loaded["product_images"][0]["image"] is not None


def test_load_no_path_keys_in_result(tmp_projects):
    save_project(_base_state("clean_keys"))
    loaded = load_project("clean_keys")
    assert "product_image_entries" not in loaded
    assert "logo_image_path" not in loaded
