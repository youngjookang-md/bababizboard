import io
import streamlit as st
from PIL import Image

from modules.canvas import render, CANVAS_W, CANVAS_H
from modules.bg_remover import remove_background
from modules.templates import get_template, template_label_map, TEMPLATE_NAMES
from modules.layer_controls import render_controls
from modules.storage import save_project, load_project, list_projects

st.set_page_config(page_title="카카오 비즈보드 제작 툴", layout="wide")


def _sync_sliders(layers: dict, num_products: int) -> None:
    st.session_state["logo_x"] = layers["logo"]["x"]
    st.session_state["logo_y"] = layers["logo"]["y"]
    st.session_state["logo_scale"] = layers["logo"]["scale"]
    st.session_state["main_x"] = layers["main_text"]["x"]
    st.session_state["main_y"] = layers["main_text"]["y"]
    st.session_state["main_size"] = layers["main_text"].get("size", 48)
    st.session_state["sub_x"] = layers["sub_text"]["x"]
    st.session_state["sub_y"] = layers["sub_text"]["y"]
    st.session_state["sub_size"] = layers["sub_text"].get("size", 39)
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


def _add_product_image(img: Image.Image, apply_rembg: bool) -> None:
    """Add a product image to session state, optionally removing background."""
    if apply_rembg:
        with st.spinner("배경 제거 중..."):
            try:
                img = remove_background(img)
            except Exception as e:
                st.warning(f"배경 제거 실패, 원본 이미지로 추가합니다. ({e})")

    dp = get_template(st.session_state.template)["default_product"]
    offset = len(st.session_state.product_images) * 30
    st.session_state.product_images.append({
        "image": img,
        "x": min(dp["x"] + offset, 950),
        "y": min(dp["y"] + offset, 230),
        "scale": dp["scale"],
    })
    st.session_state.layers["products"] = [
        {"x": p["x"], "y": p["y"], "scale": p["scale"]}
        for p in st.session_state.product_images
    ]


# ── Session state init ────────────────────────────────────────────
if "template" not in st.session_state:
    st.session_state.template = "right_image"
if "product_images" not in st.session_state:
    st.session_state.product_images = []
if "logo_image" not in st.session_state:
    st.session_state.logo_image = None
if "layers" not in st.session_state:
    st.session_state.layers = _default_layers("right_image")
if "show_guidelines" not in st.session_state:
    st.session_state.show_guidelines = True
if "product_upload_key" not in st.session_state:
    st.session_state.product_upload_key = 0
if "logo_upload_key" not in st.session_state:
    st.session_state.logo_upload_key = 0

# ── Tabs ──────────────────────────────────────────────────────────
tab_make, tab_projects = st.tabs(["🎨 제작", "📁 저장된 프로젝트"])

# ════════════════════════════════════════════════════════════════
# TAB 1: 제작
# ════════════════════════════════════════════════════════════════
with tab_make:
    st.title("📢 카카오 비즈보드 배너 제작 툴")

    # ── Top toolbar ───────────────────────────────────────────────
    col_tmpl, col_name, col_save, col_load = st.columns([2, 2, 1, 1])

    with col_tmpl:
        label_map = template_label_map()
        tmpl_labels = [label_map[k] for k in TEMPLATE_NAMES]
        selected_label = st.selectbox("템플릿", tmpl_labels, key="tmpl_select")
        selected_key = TEMPLATE_NAMES[tmpl_labels.index(selected_label)]
        if selected_key != st.session_state.template:
            st.session_state.template = selected_key
            new_layers = _default_layers(selected_key)
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

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.header("소재 설정")

        # ── Product images ────────────────────────────────────────
        st.subheader("📷 상품 이미지")

        auto_rembg = st.checkbox("업로드 시 자동 배경 제거 (누끼)", key="auto_rembg")

        # File uploader — key rotates after each successful add to reset widget
        uploaded_file = st.file_uploader(
            "이미지 업로드 (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            key=f"product_upload_{st.session_state.product_upload_key}",
            help="파일을 드래그하거나 클릭해서 업로드하세요.",
        )

        if uploaded_file is not None:
            raw = Image.open(uploaded_file).convert("RGBA")
            st.image(raw, width=120, caption="업로드된 이미지")
            if st.button("✅ 추가", key="btn_add_product", use_container_width=True):
                _add_product_image(raw, auto_rembg)
                st.session_state.product_upload_key += 1  # reset uploader
                st.rerun()

        # Clipboard paste (optional — requires browser support)
        with st.expander("📋 클립보드에서 붙여넣기", expanded=False):
            st.caption("Chrome/Edge에서만 지원됩니다.")
            try:
                from streamlit_paste_button import paste_image_button as pbutton
                paste_result = pbutton("클립보드 이미지 붙여넣기", key="paste_btn")
                if paste_result.image_data is not None:
                    pasted = paste_result.image_data.convert("RGBA")
                    _add_product_image(pasted, auto_rembg)
                    st.rerun()
            except ImportError:
                st.info("streamlit-paste-button 패키지가 없습니다.")
            except Exception as e:
                st.warning(f"붙여넣기를 사용할 수 없습니다: {e}")

        # Thumbnail list
        if st.session_state.product_images:
            st.caption(f"등록된 이미지 {len(st.session_state.product_images)}개")
            for i, item in enumerate(st.session_state.product_images):
                col_thumb, col_del = st.columns([4, 1])
                with col_thumb:
                    if item.get("image"):
                        st.image(item["image"], width=70, caption=f"이미지 {i+1}")
                with col_del:
                    st.write("")
                    if st.button("✕", key=f"del_img_{i}"):
                        st.session_state.product_images.pop(i)
                        st.session_state.layers["products"] = [
                            {"x": p["x"], "y": p["y"], "scale": p["scale"]}
                            for p in st.session_state.product_images
                        ]
                        st.rerun()

        st.divider()

        # ── Logo ──────────────────────────────────────────────────
        st.subheader("🖼 로고")
        logo_rembg = st.checkbox("업로드 시 배경 제거", key="logo_rembg_check")
        logo_file = st.file_uploader(
            "로고 업로드",
            type=["png", "jpg", "jpeg"],
            key=f"logo_upload_{st.session_state.logo_upload_key}",
        )
        if logo_file is not None:
            raw_logo = Image.open(logo_file).convert("RGBA")
            st.image(raw_logo, width=80, caption="업로드된 로고")
            if st.button("✅ 로고 적용", key="btn_add_logo", use_container_width=True):
                if logo_rembg:
                    with st.spinner("배경 제거 중..."):
                        try:
                            st.session_state.logo_image = remove_background(raw_logo)
                        except Exception as e:
                            st.warning(f"배경 제거 실패: {e}")
                            st.session_state.logo_image = raw_logo
                else:
                    st.session_state.logo_image = raw_logo
                st.session_state.logo_upload_key += 1  # reset uploader
                st.rerun()

        if st.session_state.logo_image is not None:
            st.image(st.session_state.logo_image, width=80, caption="현재 로고")
            if st.button("로고 제거", key="btn_del_logo"):
                st.session_state.logo_image = None
                st.rerun()

        st.divider()

        # ── Copy ──────────────────────────────────────────────────
        st.subheader("✏️ 카피")
        st.text_input("메인 카피", value=st.session_state.get("main_copy", ""), key="main_copy")
        st.text_input("서브 카피", value=st.session_state.get("sub_copy", ""), key="sub_copy")

        st.divider()

        # ── Layer controls ────────────────────────────────────────
        num_products = len(st.session_state.product_images)
        updated_layers = render_controls(st.session_state.layers, num_products)

        for i, pos in enumerate(updated_layers.get("products", [])):
            if i < len(st.session_state.product_images):
                st.session_state.product_images[i]["x"] = pos["x"]
                st.session_state.product_images[i]["y"] = pos["y"]
                st.session_state.product_images[i]["scale"] = pos["scale"]

        st.session_state.layers = updated_layers

        st.divider()
        st.session_state.show_guidelines = st.toggle(
            "가이드라인 표시", value=st.session_state.show_guidelines, key="guideline_toggle"
        )

    # ── Canvas render ─────────────────────────────────────────────
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
        main_copy_size=layers["main_text"].get("size", 48),
        sub_copy=st.session_state.get("sub_copy", ""),
        sub_x=layers["sub_text"]["x"],
        sub_y=layers["sub_text"]["y"],
        sub_copy_size=layers["sub_text"].get("size", 39),
        show_guidelines=st.session_state.show_guidelines,
    )

    st.image(canvas_img, caption=f"미리보기 ({CANVAS_W}×{CANVAS_H}px)", width=700)

    # Download (always without guidelines)
    download_img = render(
        product_images=st.session_state.product_images,
        logo_image=st.session_state.logo_image,
        logo_x=layers["logo"]["x"],
        logo_y=layers["logo"]["y"],
        logo_scale=layers["logo"]["scale"],
        main_copy=st.session_state.get("main_copy", ""),
        main_x=layers["main_text"]["x"],
        main_y=layers["main_text"]["y"],
        main_copy_size=layers["main_text"].get("size", 48),
        sub_copy=st.session_state.get("sub_copy", ""),
        sub_x=layers["sub_text"]["x"],
        sub_y=layers["sub_text"]["y"],
        sub_copy_size=layers["sub_text"].get("size", 39),
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
        if size_kb <= 300:
            st.success(f"파일 크기: {size_kb:.1f}KB ✅ (300KB 이하)")
        else:
            st.warning(f"파일 크기: {size_kb:.1f}KB ⚠️ (300KB 초과)")

# ════════════════════════════════════════════════════════════════
# TAB 2: 저장된 프로젝트 목록
# ════════════════════════════════════════════════════════════════
with tab_projects:
    st.title("📁 저장된 프로젝트")

    projects = list_projects()
    if not projects:
        st.info("저장된 프로젝트가 없습니다. 제작 탭에서 저장해 주세요.")
    else:
        st.caption(f"총 {len(projects)}개의 프로젝트")
        for proj_name in projects:
            with st.container(border=True):
                col_info, col_actions = st.columns([4, 1])
                with col_info:
                    st.write(f"**{proj_name}**")
                with col_actions:
                    if st.button("불러오기", key=f"load_proj_{proj_name}"):
                        loaded = load_project(proj_name)
                        st.session_state.template = loaded["template"]
                        st.session_state.layers = loaded["layers"]
                        st.session_state.product_images = loaded.get("product_images", [])
                        st.session_state.logo_image = loaded.get("logo_image")
                        st.session_state["main_copy"] = loaded.get("main_copy", "")
                        st.session_state["sub_copy"] = loaded.get("sub_copy", "")
                        st.session_state["tmpl_select"] = template_label_map()[loaded["template"]]
                        _sync_sliders(loaded["layers"], len(loaded.get("product_images", [])))
                        st.success(f"'{proj_name}' 불러오기 완료! 제작 탭으로 이동하세요.")
