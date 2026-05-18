import json
from pathlib import Path
from PIL import Image

PROJECTS_DIR = Path("projects")


def save_project(state: dict) -> None:
    name = state["name"]
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)

    serializable = {k: v for k, v in state.items() if not isinstance(v, Image.Image)}

    if state.get("product_image") is not None:
        product_path = project_dir / "product.png"
        state["product_image"].save(str(product_path), "PNG")
        serializable["product_image_path"] = str(product_path)

    if state.get("logo_image") is not None:
        logo_path = project_dir / "logo.png"
        state["logo_image"].save(str(logo_path), "PNG")
        serializable["logo_image_path"] = str(logo_path)

    json_path = project_dir / "project.json"
    json_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(name: str) -> dict:
    json_path = PROJECTS_DIR / name / "project.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if "product_image_path" in data:
        path = Path(data.pop("product_image_path"))
        data["product_image"] = Image.open(path).convert("RGBA") if path.exists() else None
    else:
        data["product_image"] = None

    if "logo_image_path" in data:
        path = Path(data.pop("logo_image_path"))
        data["logo_image"] = Image.open(path).convert("RGBA") if path.exists() else None
    else:
        data["logo_image"] = None

    return data


def list_projects() -> list[str]:
    if not PROJECTS_DIR.exists():
        return []
    return [
        d.name for d in sorted(PROJECTS_DIR.iterdir())
        if d.is_dir() and (d / "project.json").exists()
    ]
