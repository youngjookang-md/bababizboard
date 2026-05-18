import json
from pathlib import Path
from PIL import Image

PROJECTS_DIR = Path("projects")


def save_project(state: dict) -> None:
    name = state["name"]
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)

    serializable = {k: v for k, v in state.items()
                    if k not in ("product_images", "logo_image")}

    # save product images list
    product_paths = []
    for i, item in enumerate(state.get("product_images") or []):
        if item.get("image") is not None:
            p = project_dir / f"product_{i}.png"
            item["image"].save(str(p), "PNG")
            product_paths.append({
                "path": str(p),
                "x": item.get("x", 0),
                "y": item.get("y", 0),
                "scale": item.get("scale", 75),
            })
    serializable["product_image_entries"] = product_paths

    # save logo
    if state.get("logo_image") is not None:
        logo_path = project_dir / "logo.png"
        state["logo_image"].save(str(logo_path), "PNG")
        serializable["logo_image_path"] = str(logo_path)

    json_path = project_dir / "project.json"
    json_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(name: str) -> dict:
    json_path = PROJECTS_DIR / name / "project.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # load product images list
    product_images = []
    for entry in data.pop("product_image_entries", []):
        p = Path(entry["path"])
        img = Image.open(p).convert("RGBA") if p.exists() else None
        product_images.append({
            "image": img,
            "x": entry.get("x", 0),
            "y": entry.get("y", 0),
            "scale": entry.get("scale", 75),
        })
    data["product_images"] = product_images

    # load logo
    if "logo_image_path" in data:
        p = Path(data.pop("logo_image_path"))
        data["logo_image"] = Image.open(p).convert("RGBA") if p.exists() else None
    else:
        data["logo_image"] = None

    return data


def list_projects() -> list:
    if not PROJECTS_DIR.exists():
        return []
    return [
        d.name for d in sorted(PROJECTS_DIR.iterdir())
        if d.is_dir() and (d / "project.json").exists()
    ]
