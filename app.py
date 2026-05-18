import io
import streamlit as st
from PIL import Image

from modules.canvas import render, CANVAS_W, CANVAS_H
from modules.bg_remover import remove_background
from modules.templates import get_template, template_label_map, TEMPLATE_NAMES
from modules.layer_controls import render_controls
from modules.storage import save_project, load_project, list_projects

st.set_page_config(page_title="카카오 비즈보드 제작 툴", layout="wide")
st.title("📢 카카오 비즈보드 배너 제작 툴")


def _sync_sliders(layers: dict, num_products: int) -> None:
    """Sync all slider session keys after template change or project load."""
    st.session_state["logo_x"] = layers["logo"]["x"]
    st.session_state["logo_y"] = layers["logo"]["y"]
    st.session_state["logo_scale"] = layers["logo"]["scale"]
    st.session_state["main_x"] = layers["main_text"]["x"]
    st.session_state["main_y"] = layers["main_text"]["y"]
    st.session_state["sub_x"] = layers["sub_text"]["x"]
    st.session_state["sub_y"] = layers["sub_text"]["y"]
    for i, p in enumerate(layers.get("products", [])):
        st.session_state[f"prod_x_{i}"] = p["x"]
        st.session_state[f"prod_y_{i}"] = p["y"]
        st.session_state[f"prod_scale_{i}"] = p["scale"]


def _default_layers(template_name: str) -> dict:
    t = get_template(template_name)
    return {
        "logo": t["logo"],
        "main_text": t["main_text"],
        "sub_text": t["sub_text"],
        "products": [],
    }


# ── Session state init ────────────────────────────────────────────
if "template" not in st.session_state:
    st.session_state.template = "left_image"
if "product_images" not in st.session_state:
    st.session_state.product_images = []  # list of {image, x, y, scale}
if "logo_image" not in st.session_state:
    st.session_state.logo_image = None
if "layers" not in st.session_state:
    st.session_state.layers = _default_layers("left_image")
if "show_guidelines" not in st.session_state:
    st.session_state.show_guidelines = True

# ── Top toolbar ───────────────────────────────────────────────────
col_tmpl, col_name, col_save, col_load = st.columns([2, 2, 1, 1])

with col_tmpl:
    label_map = template_label_map()
    tmpl_labels = [label_map[k] for k in TEMPLATE_NAMES]
    selected_label = st.selectbox("템플릿", tmpl_labels, key="tmpl_select")
    selected_key = TEMPLATE_NAMES[tmpl_labels.index(selected_label)]
    if selected_key != st.session_state.template:
        st.session_state.template = selected_key
        new_layers = _default_layers(selected_key)
        # keep existing product position slots count
        dp = get_template(selected_key)["default_product"]
        new_layers["products"] = [dict(dp) for _ in st.session_state.product_images]
        st.session_state.layers = new_layers
        _sync_sliders(new_layers, len(st.session_state.product_images))
        st.session_state["tmpl_select"] = label_map[selected_key]
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
                "product_images": st.session_state.product_images,
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
            st.session_state.product_images = loaded.get("product_images", [])
            st.session_state.logo_image = loaded.get("logo_image")
            st.session_state["main_copy"] = loaded.get("main_copy", "")
            st.session_state["sub_copy"] = loaded.get("sub_copy", "")
            st.session_state["tmpl_select"] = template_label_map()[loaded["template"]]
            _sync_sliders(loaded["layers"], len(loaded.get("product_images", [])))
            st.rerun()

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("소재 설정")

    # ── Product images ──────────────────────────────────────────
    st.subheader("📷 상품 이미지")

    # Paste button (clipboard)
    try:
        from streamlit_paste_button import paste_image_button as pbutton
        paste_result = pbutton("📋 클립보드에서 붙여넣기", key="paste_btn")
        if paste_result.image_data is not None:
            pasted = paste_result.image_data.convert("RGBA")
            dp = get_template(st.session_state.template)["default_product"]
            offset = len(st.session_state.product_images) * 30
            st.session_state.product_images.append({
                "image": pasted,
                "x": dp["x"] + offset,
                "y": dp["y"] + offset,
                "scale": dp["scale"],
            })
            st.session_state.layers["products"] = [
                {"x": p["x"], "y": p["y"], "scale": p["scale"]}
                for p in st.session_state.product_images
            ]
            st.rerun()
    except ImportError:
        st.info("streamlit-paste-button 설치 필요: pip install streamlit-paste-button")

    # File uploader
    uploaded_file = st.file_uploader("파일 업로드", type=["png", "jpg", "jpeg"], key="product_upload")
    if uploaded_file:
        raw = Image.open(uploaded_file).convert("RGBA")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("그대로 추가", key="add_raw"):
                dp = get_template(st.session_state.template)["default_product"]
                offset = len(st.session_state.product_images) * 30
                st.session_state.product_images.append({
                    "image": raw,
                    "x": dp["x"] + offset,
                    "y": dp["y"] + offset,
                    "scale": dp["scale"],
                })
                st.session_state.layers["products"] = [
                    {"x": p["x"], "y": p["y"], "scale": p["scale"]}
                    for p in st.session_state.product_images
                ]
                st.rerun()
        with col_b:
            if st.button("누끼 제거 후 추가", key="add_rembg"):
                with st.spinner("배경 제거 중..."):
                    result = remove_background(raw)
                dp = get_template(st.session_state.template)["default_product"]
                offset = len(st.session_state.product_images) * 30
                st.session_state.product_images.append({
                    "image": result,
                    "x": dp["x"] + offset,
                    "y": dp["y"] + offset,
                    "scale": dp["scale"],
                })
                st.session_state.layers["products"] = [
                    {"x": p["x"], "y": p["y"], "scale": p["scale"]}
                    for p in st.session_state.product_images
                ]
                st.rerun()

    # Manage existing images
    if st.session_state.product_images:
        st.caption(f"등록된 이미지: {len(st.session_state.product_images)}개")
        for i, item in enumerate(st.session_state.product_images):
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"이미지 {i + 1}")
            with cols[1]:
                if st.button("삭제", key=f"del_img_{i}"):
                    st.session_state.product_images.pop(i)
                    st.session_state.layers["products"] = [
                        {"x": p["x"], "y": p["y"], "scale": p["scale"]}
                        for p in st.session_state.product_images
                    ]
                    st.rerun()

    st.divider()

    # ── Logo ─────────────────────────────────────────────────────
    st.subheader("🖼 로고")
    logo_file = st.file_uploader("로고 업로드", type=["png", "jpg", "jpeg"], key="logo_upload")
    if logo_file:
        raw_logo = Image.open(logo_file).convert("RGBA")
        remove_logo_bg = st.checkbox("로고 배경 제거", key="logo_rembg_check")
        if remove_logo_bg and st.button("누끼 실행", key="logo_rembg_btn"):
            with st.spinner("배경 제거 중..."):
                st.session_state.logo_image = remove_background(raw_logo)
            st.success("완료!")
        else:
            if st.session_state.logo_image is None:
                st.session_state.logo_image = raw_logo

    st.divider()

    # ── Copy ─────────────────────────────────────────────────────
    st.subheader("✏️ 카피")
    st.text_input("메인 카피", value=st.session_state.get("main_copy", ""), key="main_copy")
    st.text_input("서브 카피", value=st.session_state.get("sub_copy", ""), key="sub_copy")

    st.divider()

    # ── Layer controls ───────────────────────────────────────────
    num_products = len(st.session_state.product_images)
    updated_layers = render_controls(st.session_state.layers, num_products)

    # sync layer positions back to product_images list
    for i, pos in enumerate(updated_layers.get("products", [])):
        if i < len(st.session_state.product_images):
            st.session_state.product_images[i]["x"] = pos["x"]
            st.session_state.product_images[i]["y"] = pos["y"]
            st.session_state.product_images[i]["scale"] = pos["scale"]

    st.session_state.layers = updated_layers

    st.divider()

    # ── Guidelines toggle ────────────────────────────────────────
    st.session_state.show_guidelines = st.toggle(
        "가이드라인 표시", value=st.session_state.show_guidelines, key="guideline_toggle"
    )

# ── Canvas render ─────────────────────────────────────────────────
layers = st.session_state.layers
canvas_img = render(
    product_images=st.session_state.product_images,
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
    show_guidelines=st.session_state.show_guidelines,
)

st.image(canvas_img, caption=f"미리보기 ({CANVAS_W}×{CANVAS_H}px)", use_container_width=True)

# ── Download ──────────────────────────────────────────────────────
# download version: always without guidelines
download_img = render(
    product_images=st.session_state.product_images,
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
    show_guidelines=False,
)

buf = io.BytesIO()
download_img.save(buf, format="PNG", optimize=True)
png_bytes = buf.getvalue()
size_kb = len(png_bytes) / 1024

col_dl, col_size = st.columns([1, 3])
with col_dl:
    fname = (project_name.strip() or "bizboard") + ".png"
    st.download_button("⬇ PNG 다운로드", data=png_bytes, file_name=fname, mime="image/png")
with col_size:
    if size_kb <= 500:
        st.success(f"파일 크기: {size_kb:.1f}KB ✅ (500KB 이하)")
    else:
        st.warning(f"파일 크기: {size_kb:.1f}KB ⚠️ (500KB 초과 — 이미지 크기를 줄여 주세요)")
