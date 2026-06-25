from pathlib import Path
import json

PRESETS_DIR = Path("presets")


def save_preset(name: str, layers: dict) -> None:
    PRESETS_DIR.mkdir(exist_ok=True)
    preset = {
        "name": name,
        "logo": dict(layers["logo"]),
        "main_text": dict(layers["main_text"]),
        "sub_text": dict(layers["sub_text"]),
    }
    path = PRESETS_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(preset, f, ensure_ascii=False, indent=2)


def load_preset(name: str) -> dict:
    path = PRESETS_DIR / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_presets() -> list:
    if not PRESETS_DIR.exists():
        return []
    return sorted(p.stem for p in PRESETS_DIR.glob("*.json"))


def delete_preset(name: str) -> None:
    path = PRESETS_DIR / f"{name}.json"
    if path.exists():
        path.unlink()
