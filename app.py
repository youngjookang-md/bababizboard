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
    """Sync slider session keys after template change or project load."""
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


# ── Session state init ────────────────────────────────────────────
if "template" not in st.session_state:
    st.session_state.template = "left_image"
if "product_image" not in st.session_state:
    st.session_state.product_image = None
if "logo_image" not in st.session_state:
    st.session_state.logo_image = None
if "layers" not in st.session_state:
    st.session_state.layers = get_template("left_image")

# ── Top toolbar ───────────────────────────────────────────────────
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

# ── Sidebar ───────────────────────────────────────────────────────
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

# ── Canvas render ─────────────────────────────────────────────────
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

# ── Download ──────────────────────────────────────────────────────
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
