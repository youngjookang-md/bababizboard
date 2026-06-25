# BabaBizBoard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit 기반 카카오 비즈보드(1029×258px) 배너 소재 제작 툴 — 누끼 처리, 카피 입력, 레이어 위치 조정, 템플릿, 저장/불러오기, PNG 다운로드 지원.

**Architecture:** PIL로 레이어(배경→상품이미지→로고→텍스트)를 순서대로 합성하는 canvas.py가 핵심 엔진. 사이드바 슬라이더 값이 변경될 때마다 전체 파이프라인을 재실행해 `st.image()`로 미리보기를 갱신한다. 프로젝트 상태는 JSON 파일로 직렬화해 `projects/` 폴더에 저장한다.

**Tech Stack:** streamlit, Pillow, rembg, pytest

---

## 파일 맵

| 파일 | 역할 |
|------|------|
| `requirements.txt` | 의존성 목록 |
| `app.py` | Streamlit 진입점, 레이아웃 조립 |
| `modules/canvas.py` | PIL 레이어 합성 엔진 |
| `modules/bg_remover.py` | rembg 배경 제거 래퍼 |
| `modules/templates.py` | 레이아웃 템플릿 정의 |
| `modules/layer_controls.py` | 사이드바 슬라이더 UI |
| `modules/storage.py` | 프로젝트 JSON 저장/불러오기 |
| `assets/fonts/SpoqaHanSansBold.ttf` | 메인 카피 폰트 |
| `assets/fonts/SpoqaHanSansRegular.ttf` | 서브 카피 폰트 |
| `tests/test_canvas.py` | canvas.py 단위 테스트 |
| `tests/test_templates.py` | templates.py 단위 테스트 |
| `tests/test_storage.py` | storage.py 단위 테스트 |

---

## Task 1: 프로젝트 초기 설정

**Files:**
- Create: `requirements.txt`
- Create: `modules/__init__.py`
- Create: `tests/__init__.py`
- Create: `assets/fonts/` (디렉토리)
- Create: `projects/` (디렉토리)

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p modules tests assets/fonts projects
touch modules/__init__.py tests/__init__.py
```

- [ ] **Step 2: requirements.txt 작성**

```
streamlit>=1.35.0
Pillow>=10.0.0
rembg>=2.0.50
onnxruntime>=1.17.0
pytest>=8.0.0
```

- [ ] **Step 3: Spoqa Han Sans 폰트 다운로드**

아래 명령으로 TTF 파일 2개를 `assets/fonts/`에 저장한다.

```bash
# PowerShell
$bold = "https://github.com/spoqa/spoqa-han-sans/raw/master/Subset/SpoqaHanSansNeo/SpoqaHanSansNeo-Bold.ttf"
$regular = "https://github.com/spoqa/spoqa-han-sans/raw/master/Subset/SpoqaHanSansNeo/SpoqaHanSansNeo-Regular.ttf"

Invoke-WebRequest -Uri $bold -OutFile "assets/fonts/SpoqaHanSansBold.ttf"
Invoke-WebRequest -Uri $regular -OutFile "assets/fonts/SpoqaHanSansRegular.ttf"
```

- [ ] **Step 4: 의존성 설치**

```bash
pip install -r requirements.txt
```

Expected: 오류 없이 설치 완료. rembg 최초 실행 시 모델 다운로드는 bg_remover.py 테스트 시 발생.

- [ ] **Step 5: 커밋**

```bash
git init
git add requirements.txt modules/__init__.py tests/__init__.py
git commit -m "chore: project scaffolding"
```

---

## Task 2: 템플릿 정의 (templates.py)

**Files:**
- Create: `modules/templates.py`
- Create: `tests/test_templates.py`

캔버스 크기: 1029×258. 각 템플릿은 레이어별 기본 x, y, scale 값을 딕셔너리로 반환한다.

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_templates.py`:

```python
import pytest
from modules.templates import get_template, TEMPLATE_NAMES

def test_template_names_has_three():
    assert len(TEMPLATE_NAMES) == 3

def test_left_image_template_keys():
    t = get_template("left_image")
    for layer in ("product", "logo", "main_text", "sub_text"):
        assert layer in t

def test_right_image_product_x_is_right_side():
    t = get_template("right_image")
    assert t["product"]["x"] >= 500

def test_text_focus_main_text_x_is_left():
    t = get_template("text_focus")
    assert t["main_text"]["x"] < 300

def test_invalid_template_raises():
    with pytest.raises(KeyError):
        get_template("nonexistent")
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_templates.py -v
```

Expected: `ImportError` 또는 5개 FAILED.

- [ ] **Step 3: templates.py 구현**

`modules/templates.py`:

```python
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
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_templates.py -v
```

Expected: 5개 PASSED.

- [ ] **Step 5: 커밋**

```bash
git add modules/templates.py tests/test_templates.py
git commit -m "feat: bizboard layout templates"
```

---

## Task 3: 캔버스 합성 엔진 (canvas.py)

**Files:**
- Create: `modules/canvas.py`
- Create: `tests/test_canvas.py`

PIL로 레이어를 합성해 `PIL.Image` 객체를 반환하는 순수 함수.

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_canvas.py`:

```python
import pytest
from PIL import Image
from modules.canvas import render

def _white_img(w, h):
    return Image.new("RGBA", (w, h), (255, 255, 255, 255))

def test_render_returns_correct_size():
    img = render()
    assert img.size == (1029, 258)

def test_render_is_rgb():
    img = render()
    assert img.mode == "RGB"

def test_render_with_product_image():
    product = _white_img(200, 200)
    img = render(product_image=product, product_x=10, product_y=10, product_scale=50)
    assert img.size == (1029, 258)

def test_render_with_main_copy():
    img = render(main_copy="테스트 카피")
    assert img.size == (1029, 258)

def test_render_with_all_layers():
    product = _white_img(200, 200)
    logo = _white_img(100, 50)
    img = render(
        product_image=product, product_x=20, product_y=20, product_scale=70,
        logo_image=logo, logo_x=800, logo_y=10, logo_scale=20,
        main_copy="메인 카피", main_x=440, main_y=70,
        sub_copy="서브 카피", sub_x=440, sub_y=145,
    )
    assert img.size == (1029, 258)
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_canvas.py -v
```

Expected: `ImportError` 또는 5개 FAILED.

- [ ] **Step 3: canvas.py 구현**

`modules/canvas.py`:

```python
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1029
CANVAS_H = 258
BG_COLOR = (255, 255, 255)

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_FONT_BOLD = _FONT_DIR / "SpoqaHanSansBold.ttf"
_FONT_REGULAR = _FONT_DIR / "SpoqaHanSansRegular.ttf"

MAIN_COPY_SIZE = 48
SUB_COPY_SIZE = 39
MAIN_COPY_COLOR = (76, 76, 76)      # #4C4C4C
SUB_COPY_COLOR = (119, 119, 119)    # #777777


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _paste_image(canvas: Image.Image, layer: Image.Image, x: int, y: int, scale: int) -> None:
    if layer is None:
        return
    new_w = max(1, int(layer.width * scale / 100))
    new_h = max(1, int(layer.height * scale / 100))
    resized = layer.resize((new_w, new_h), Image.LANCZOS)
    if resized.mode == "RGBA":
        canvas.paste(resized, (x, y), resized)
    else:
        canvas.paste(resized, (x, y))


def render(
    product_image: Image.Image | None = None,
    product_x: int = 20,
    product_y: int = 20,
    product_scale: int = 75,
    logo_image: Image.Image | None = None,
    logo_x: int = 830,
    logo_y: int = 10,
    logo_scale: int = 20,
    main_copy: str = "",
    main_x: int = 440,
    main_y: int = 70,
    sub_copy: str = "",
    sub_x: int = 440,
    sub_y: int = 145,
) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

    _paste_image(canvas, product_image, product_x, product_y, product_scale)
    _paste_image(canvas, logo_image, logo_x, logo_y, logo_scale)

    draw = ImageDraw.Draw(canvas)

    if main_copy:
        font = _load_font(_FONT_BOLD, MAIN_COPY_SIZE)
        draw.text((main_x, main_y), main_copy, font=font, fill=MAIN_COPY_COLOR)

    if sub_copy:
        font = _load_font(_FONT_REGULAR, SUB_COPY_SIZE)
        draw.text((sub_x, sub_y), sub_copy, font=font, fill=SUB_COPY_COLOR)

    return canvas
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_canvas.py -v
```

Expected: 5개 PASSED.

- [ ] **Step 5: 커밋**

```bash
git add modules/canvas.py tests/test_canvas.py
git commit -m "feat: PIL canvas compositing engine"
```

---

## Task 4: 프로젝트 저장/불러오기 (storage.py)

**Files:**
- Create: `modules/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_storage.py`:

```python
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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_storage.py -v
```

Expected: `ImportError` 또는 4개 FAILED.

- [ ] **Step 3: storage.py 구현**

`modules/storage.py`:

```python
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
        path = Path(data["product_image_path"])
        data["product_image"] = Image.open(path).convert("RGBA") if path.exists() else None
    else:
        data["product_image"] = None

    if "logo_image_path" in data:
        path = Path(data["logo_image_path"])
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
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_storage.py -v
```

Expected: 4개 PASSED.

- [ ] **Step 5: 커밋**

```bash
git add modules/storage.py tests/test_storage.py
git commit -m "feat: project save/load with JSON serialization"
```

---

## Task 5: 배경 제거 래퍼 (bg_remover.py)

**Files:**
- Create: `modules/bg_remover.py`

rembg는 최초 호출 시 모델을 자동 다운로드(~170MB)하므로 단위 테스트 대신 수동 연기 테스트로 검증한다.

- [ ] **Step 1: bg_remover.py 구현**

`modules/bg_remover.py`:

```python
from PIL import Image
import io

def remove_background(image: Image.Image) -> Image.Image:
    from rembg import remove
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    result_bytes = remove(img_bytes.read())
    return Image.open(io.BytesIO(result_bytes)).convert("RGBA")
```

- [ ] **Step 2: 수동 동작 확인용 스크립트 실행**

```bash
python -c "
from PIL import Image
from modules.bg_remover import remove_background
img = Image.new('RGB', (100, 100), (255, 0, 0))
result = remove_background(img)
print('mode:', result.mode, 'size:', result.size)
assert result.mode == 'RGBA'
print('OK')
"
```

Expected: `mode: RGBA size: (100, 100)` 출력 (최초 실행 시 모델 다운로드 발생).

- [ ] **Step 3: 커밋**

```bash
git add modules/bg_remover.py
git commit -m "feat: rembg background removal wrapper"
```

---

## Task 6: 사이드바 레이어 컨트롤 (layer_controls.py)

**Files:**
- Create: `modules/layer_controls.py`

Streamlit 사이드바에 슬라이더를 렌더링하고 현재 레이어 값 딕셔너리를 반환하는 함수.

- [ ] **Step 1: layer_controls.py 구현**

`modules/layer_controls.py`:

```python
import streamlit as st
from PIL import Image

def render_controls(default_layers: dict) -> dict:
    """사이드바에 레이어 조정 컨트롤을 렌더링하고 현재 값을 반환한다."""
    layers = {}

    with st.sidebar.expander("🎛 상품 이미지 위치", expanded=True):
        layers["product"] = {
            "x": st.slider("상품 X", 0, 900, default_layers["product"]["x"], key="product_x"),
            "y": st.slider("상품 Y", 0, 200, default_layers["product"]["y"], key="product_y"),
            "scale": st.slider("상품 크기(%)", 10, 200, default_layers["product"]["scale"], key="product_scale"),
        }

    with st.sidebar.expander("🖼 로고 위치", expanded=False):
        layers["logo"] = {
            "x": st.slider("로고 X", 0, 900, default_layers["logo"]["x"], key="logo_x"),
            "y": st.slider("로고 Y", 0, 200, default_layers["logo"]["y"], key="logo_y"),
            "scale": st.slider("로고 크기(%)", 10, 100, default_layers["logo"]["scale"], key="logo_scale"),
        }

    with st.sidebar.expander("✏️ 메인 카피 위치", expanded=False):
        layers["main_text"] = {
            "x": st.slider("메인카피 X", 0, 900, default_layers["main_text"]["x"], key="main_x"),
            "y": st.slider("메인카피 Y", 0, 200, default_layers["main_text"]["y"], key="main_y"),
        }

    with st.sidebar.expander("✏️ 서브 카피 위치", expanded=False):
        layers["sub_text"] = {
            "x": st.slider("서브카피 X", 0, 900, default_layers["sub_text"]["x"], key="sub_x"),
            "y": st.slider("서브카피 Y", 0, 200, default_layers["sub_text"]["y"], key="sub_y"),
        }

    return layers
```

- [ ] **Step 2: 커밋**

```bash
git add modules/layer_controls.py
git commit -m "feat: sidebar layer position controls"
```

---

## Task 7: 메인 앱 조립 (app.py)

**Files:**
- Create: `app.py`

모든 모듈을 연결하는 Streamlit 진입점.

- [ ] **Step 1: app.py 구현**

`app.py`:

```python
import io
import streamlit as st
from PIL import Image

from modules.canvas import render
from modules.bg_remover import remove_background
from modules.templates import get_template, template_label_map, TEMPLATE_NAMES
from modules.layer_controls import render_controls
from modules.storage import save_project, load_project, list_projects

st.set_page_config(page_title="카카오 비즈보드 제작 툴", layout="wide")
st.title("📢 카카오 비즈보드 배너 제작 툴")


def _sync_sliders(layers: dict) -> None:
    """템플릿 변경/불러오기 후 슬라이더 세션 키를 덮어써 값을 동기화한다."""
    st.session_state["product_x"] = layers["product"]["x"]
    st.session_state["product_y"] = layers["product"]["y"]
    st.session_state["product_scale"] = layers["product"]["scale"]
    st.session_state["logo_x"] = layers["logo"]["x"]
    st.session_state["logo_y"] = layers["logo"]["y"]
    st.session_state["logo_scale"] = layers["logo"]["scale"]
    st.session_state["main_x"] = layers["main_text"]["x"]
    st.session_state["main_y"] = layers["main_text"]["y"]
    st.session_state["sub_x"] = layers["sub_text"]["x"]
    st.session_state["sub_y"] = layers["sub_text"]["y"]


# ── 세션 상태 초기화 ──────────────────────────────────────────────
if "template" not in st.session_state:
    st.session_state.template = "left_image"
if "product_image" not in st.session_state:
    st.session_state.product_image = None
if "logo_image" not in st.session_state:
    st.session_state.logo_image = None
if "layers" not in st.session_state:
    st.session_state.layers = get_template("left_image")

# ── 상단 툴바 ─────────────────────────────────────────────────────
col_tmpl, col_name, col_save, col_load = st.columns([2, 2, 1, 1])

with col_tmpl:
    label_map = template_label_map()
    tmpl_labels = [label_map[k] for k in TEMPLATE_NAMES]
    selected_label = st.selectbox("템플릿", tmpl_labels, key="tmpl_select")
    selected_key = TEMPLATE_NAMES[tmpl_labels.index(selected_label)]
    if selected_key != st.session_state.template:
        st.session_state.template = selected_key
        new_layers = get_template(selected_key)
        st.session_state.layers = new_layers
        _sync_sliders(new_layers)
        st.rerun()

with col_name:
    project_name = st.text_input("프로젝트명", value="내_비즈보드", key="project_name")

with col_save:
    if st.button("💾 저장"):
        if not project_name.strip():
            st.warning("프로젝트명을 입력해 주세요.")
        else:
            save_project({
                "name": project_name.strip(),
                "template": st.session_state.template,
                "main_copy": st.session_state.get("main_copy", ""),
                "sub_copy": st.session_state.get("sub_copy", ""),
                "layers": st.session_state.layers,
                "product_image": st.session_state.product_image,
                "logo_image": st.session_state.logo_image,
            })
            st.success(f"'{project_name}' 저장 완료!")

with col_load:
    projects = list_projects()
    if projects:
        load_name = st.selectbox("불러오기", ["— 선택 —"] + projects, key="load_select")
        if load_name != "— 선택 —":
            loaded = load_project(load_name)
            st.session_state.template = loaded["template"]
            st.session_state.layers = loaded["layers"]
            st.session_state.product_image = loaded.get("product_image")
            st.session_state.logo_image = loaded.get("logo_image")
            st.session_state["main_copy"] = loaded.get("main_copy", "")
            st.session_state["sub_copy"] = loaded.get("sub_copy", "")
            _sync_sliders(loaded["layers"])
            st.rerun()

st.divider()

# ── 사이드바 ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("소재 설정")

    st.subheader("📷 상품 이미지")
    product_file = st.file_uploader("상품 이미지 업로드", type=["png", "jpg", "jpeg"], key="product_upload")
    if product_file:
        raw = Image.open(product_file).convert("RGBA")
        if st.button("누끼 제거 실행", key="product_rembg"):
            with st.spinner("배경 제거 중..."):
                st.session_state.product_image = remove_background(raw)
            st.success("완료!")
        else:
            if st.session_state.product_image is None:
                st.session_state.product_image = raw

    st.subheader("🖼 로고")
    logo_file = st.file_uploader("로고 업로드", type=["png", "jpg", "jpeg"], key="logo_upload")
    if logo_file:
        raw_logo = Image.open(logo_file).convert("RGBA")
        remove_logo_bg = st.checkbox("로고 배경 제거", key="logo_rembg_check")
        if remove_logo_bg and st.button("로고 누끼 실행", key="logo_rembg_btn"):
            with st.spinner("배경 제거 중..."):
                st.session_state.logo_image = remove_background(raw_logo)
            st.success("완료!")
        else:
            if st.session_state.logo_image is None:
                st.session_state.logo_image = raw_logo

    st.subheader("✏️ 카피")
    main_copy = st.text_input(
        "메인 카피 (Spoqa Bold 48pt #4C4C4C)",
        value=st.session_state.get("main_copy", ""),
        key="main_copy",
    )
    sub_copy = st.text_input(
        "서브 카피 (Spoqa Regular 39pt #777777)",
        value=st.session_state.get("sub_copy", ""),
        key="sub_copy",
    )

    st.divider()
    updated_layers = render_controls(st.session_state.layers)
    st.session_state.layers = updated_layers

# ── 캔버스 렌더링 ─────────────────────────────────────────────────
layers = st.session_state.layers
canvas_img = render(
    product_image=st.session_state.product_image,
    product_x=layers["product"]["x"],
    product_y=layers["product"]["y"],
    product_scale=layers["product"]["scale"],
    logo_image=st.session_state.logo_image,
    logo_x=layers["logo"]["x"],
    logo_y=layers["logo"]["y"],
    logo_scale=layers["logo"]["scale"],
    main_copy=st.session_state.get("main_copy", ""),
    main_x=layers["main_text"]["x"],
    main_y=layers["main_text"]["y"],
    sub_copy=st.session_state.get("sub_copy", ""),
    sub_x=layers["sub_text"]["x"],
    sub_y=layers["sub_text"]["y"],
)

st.image(canvas_img, caption="미리보기 (1029×258px)", use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────────────
buf = io.BytesIO()
canvas_img.save(buf, format="PNG", optimize=True)
png_bytes = buf.getvalue()
size_kb = len(png_bytes) / 1024

col_dl, col_size = st.columns([1, 2])
with col_dl:
    st.download_button(
        label="⬇ PNG 다운로드",
        data=png_bytes,
        file_name=f"{project_name.strip() or 'bizboard'}.png",
        mime="image/png",
    )
with col_size:
    if size_kb <= 300:
        st.success(f"파일 크기: {size_kb:.1f}KB ✅ (300KB 이하)")
    else:
        st.warning(f"파일 크기: {size_kb:.1f}KB ⚠️ (300KB 초과 — 이미지 크기를 줄여 주세요)")
```

- [ ] **Step 2: 앱 실행 확인**

```bash
streamlit run app.py
```

Expected: 브라우저에서 `http://localhost:8501` 열림. 캔버스에 흰 배경(1029×258 비율)이 표시됨.

- [ ] **Step 3: 골든 패스 테스트 (수동)**

1. 템플릿 "우측 이미지형" 선택 → 슬라이더 기본값이 바뀌는지 확인
2. 메인 카피 입력 → 캔버스에 텍스트 표시 확인
3. 상품 이미지 업로드 → 캔버스에 배치 확인
4. 슬라이더 이동 → 이미지 위치 실시간 변경 확인
5. 프로젝트명 입력 후 저장 → `projects/` 폴더에 JSON 생성 확인
6. 불러오기 셀렉트박스로 저장된 프로젝트 복원 확인
7. PNG 다운로드 버튼 → 파일 저장 및 크기 표시 확인

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
pytest tests/ -v
```

Expected: 전체 PASSED (bg_remover 제외한 단위 테스트).

- [ ] **Step 5: 최종 커밋**

```bash
git add app.py modules/layer_controls.py
git commit -m "feat: main Streamlit app — full integration"
```

---

## 전체 테스트 커버리지 요약

```bash
pytest tests/ -v --tb=short
```

| 테스트 파일 | 커버하는 모듈 | 테스트 수 |
|------------|-------------|---------|
| test_templates.py | modules/templates.py | 5 |
| test_canvas.py | modules/canvas.py | 5 |
| test_storage.py | modules/storage.py | 4 |

bg_remover.py는 모델 다운로드가 필요해 단위 테스트 제외, Task 5 Step 2에서 수동 검증.
