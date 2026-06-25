import io
import streamlit as st
from PIL import Image

from modules.canvas import render, CANVAS_W, CANVAS_H, FONT_FAMILIES, KAKAO_TEXT_COLORS
from modules.bg_remover import remove_background
from modules.templates import get_template, template_label_map, TEMPLATE_NAMES
from modules.layer_controls import render_controls, render_extra_copy_controls
from modules.storage import save_project, load_project, list_projects
from modules.presets import save_preset, load_preset, list_presets, delete_preset
from components.canvas_drag import canvas_drag

BADGE_COLORS = {
    "초록": {"bg": (29, 158, 117), "text": (255, 255, 255)},
    "빨강": {"bg": (226, 75, 74), "text": (255, 255, 255)},
    "노랑": {"bg": (239, 159, 39), "text": (255, 255, 255)},
    "파랑": {"bg": (55, 138, 221), "text": (255, 255, 255)},
    "보라": {"bg": (127, 119, 221), "text": (255, 255, 255)},
    "어두운": {"bg": (68, 68, 65), "text": (255, 255, 255)},
}

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
if "badges" not in st.session_state:
    st.session_state.badges = []
if "drag_pending" not in st.session_state:
    st.session_state.drag_pending = None
if "extra_copies" not in st.session_state:
    st.session_state.extra_copies = [
        {"enabled": False, "text": "", "x": 50,  "y": 130, "size": 36, "bold": False},
        {"enabled": False, "text": "", "x": 300, "y": 130, "size": 36, "bold": False},
        {"enabled": False, "text": "", "x": 550, "y": 130, "size": 36, "bold": False},
        {"enabled": False, "text": "", "x": 800, "y": 130, "size": 36, "bold": False},
    ]
else:
    # 기존 세션에 슬롯이 2개뿐이면 2개 추가
    while len(st.session_state.extra_copies) < 4:
        st.session_state.extra_copies.append(
            {"enabled": False, "text": "", "x": 50, "y": 130, "size": 36, "bold": False}
        )

# ── Apply drag result BEFORE sidebar renders ──────────────────────
# (widget key assignment after render raises StreamlitAPIException)
if st.session_state.drag_pending is not None:
    _r = st.session_state.drag_pending
    st.session_state.drag_pending = None
    _id     = _r["id"]
    _action = _r.get("action", "move")

    if _action == "resize":
        _s = int(_r.get("scale", 100))
        if _id.startswith("product_"):
            _i = int(_id.split("_")[1])
            if _i < len(st.session_state.product_images):
                st.session_state.product_images[_i]["scale"] = _s
                _prods = st.session_state.layers.get("products", [])
                if _i < len(_prods):
                    _prods[_i]["scale"] = _s
                st.session_state[f"prod_scale_{_i}"] = _s
        elif _id == "logo":
            st.session_state.layers["logo"]["scale"] = _s
            st.session_state["logo_scale"] = _s
    else:
        _x, _y = _r["x"], _r["y"]
        if _id.startswith("product_"):
            _i = int(_id.split("_")[1])
            if _i < len(st.session_state.product_images):
                st.session_state.product_images[_i]["x"] = _x
                st.session_state.product_images[_i]["y"] = _y
                _prods = st.session_state.layers.get("products", [])
                if _i < len(_prods):
                    _prods[_i]["x"] = _x
                    _prods[_i]["y"] = _y
                st.session_state[f"prod_x_{_i}"] = _x
                st.session_state[f"prod_y_{_i}"] = _y
        elif _id == "logo":
            st.session_state.layers["logo"]["x"] = _x
            st.session_state.layers["logo"]["y"] = _y
            st.session_state["logo_x"] = _x
            st.session_state["logo_y"] = _y
        elif _id == "main_text":
            st.session_state.layers["main_text"]["x"] = _x
            st.session_state.layers["main_text"]["y"] = _y
            st.session_state["main_x"] = _x
            st.session_state["main_y"] = _y
        elif _id == "sub_text":
            st.session_state.layers["sub_text"]["x"] = _x
            st.session_state.layers["sub_text"]["y"] = _y
            st.session_state["sub_x"] = _x
            st.session_state["sub_y"] = _y
        elif _id.startswith("badge_"):
            _i = int(_id.split("_")[1])
            if _i < len(st.session_state.badges):
                st.session_state.badges[_i]["x"] = _x
                st.session_state.badges[_i]["y"] = _y
        elif _id.startswith("extra_copy_"):
            _ci = int(_id.split("_")[2])
            if _ci < len(st.session_state.extra_copies):
                st.session_state.extra_copies[_ci]["x"] = _x
                st.session_state.extra_copies[_ci]["y"] = _y
                st.session_state[f"ec_{_ci}_x"] = _x
                st.session_state[f"ec_{_ci}_y"] = _y
    # Clear cached component value so next render returns None (prevents loop)
    st.session_state["drag_canvas"] = None

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
        cur_idx = TEMPLATE_NAMES.index(st.session_state.template) if st.session_state.template in TEMPLATE_NAMES else 0
        selected_label = st.selectbox("템플릿", tmpl_labels, index=cur_idx)
        selected_key = TEMPLATE_NAMES[tmpl_labels.index(selected_label)]
        if selected_key != st.session_state.template:
            st.session_state.template = selected_key
            new_layers = _default_layers(selected_key)
            dp = get_template(selected_key)["default_product"]
            new_layers["products"] = [dict(dp) for _ in st.session_state.product_images]
            st.session_state.layers = new_layers
            _sync_sliders(new_layers, len(st.session_state.product_images))
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
        _font_options = list(FONT_FAMILIES.keys())
        _color_options = list(KAKAO_TEXT_COLORS.keys())

        def _color_picker(label, key_preset, key_custom, default_color):
            preset = st.selectbox(label, _color_options, key=key_preset)
            if preset == "커스텀":
                hex_default = "#{:02X}{:02X}{:02X}".format(*default_color)
                picked = st.color_picker("색상 선택", value=hex_default, key=key_custom)
                r, g, b = int(picked[1:3],16), int(picked[3:5],16), int(picked[5:7],16)
                return (r, g, b)
            return KAKAO_TEXT_COLORS[preset]

        st.text_input("메인 카피 (필수)", value=st.session_state.get("main_copy", ""), key="main_copy")
        with st.expander("메인 카피 스타일", expanded=False):
            st.selectbox("폰트", _font_options, key="main_font_family",
                         index=_font_options.index(st.session_state.get("main_font_family", "Spoqa Han Sans")))
            _main_color = _color_picker("색상", "main_color_preset", "main_color_custom", (76, 76, 76))
            st.session_state["main_color"] = list(_main_color)

        st.text_input("서브 카피 (필수)", value=st.session_state.get("sub_copy", ""), key="sub_copy")
        with st.expander("서브 카피 스타일", expanded=False):
            st.selectbox("폰트", _font_options, key="sub_font_family",
                         index=_font_options.index(st.session_state.get("sub_font_family", "Spoqa Han Sans")))
            _sub_color = _color_picker("색상", "sub_color_preset", "sub_color_custom", (119, 119, 119))
            st.session_state["sub_color"] = list(_sub_color)

        with st.expander("➕ 추가 카피 (선택)", expanded=False):
            for _ci in range(len(st.session_state.extra_copies)):
                _ec = st.session_state.extra_copies[_ci]
                st.markdown(f"**카피 {_ci+3}**")
                _enabled = st.checkbox("사용", value=_ec["enabled"], key=f"ec_{_ci}_enabled")
                st.session_state.extra_copies[_ci]["enabled"] = _enabled
                if _enabled:
                    _txt = st.text_input("텍스트", value=_ec.get("text",""), key=f"ec_{_ci}_text")
                    st.session_state.extra_copies[_ci]["text"] = _txt
                    _ec_font = st.selectbox("폰트", _font_options, key=f"ec_{_ci}_font",
                                            index=_font_options.index(_ec.get("font_family","Spoqa Han Sans")))
                    st.session_state.extra_copies[_ci]["font_family"] = _ec_font
                    _ec_color = _color_picker("색상", f"ec_{_ci}_color_preset", f"ec_{_ci}_color_custom", (76, 76, 76))
                    st.session_state.extra_copies[_ci]["color"] = list(_ec_color)
                    _bold = st.checkbox("볼드", value=_ec.get("bold", False), key=f"ec_{_ci}_bold")
                    st.session_state.extra_copies[_ci]["bold"] = _bold
                if _ci < len(st.session_state.extra_copies) - 1:
                    st.divider()

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

        updated_ec = render_extra_copy_controls(st.session_state.extra_copies)
        for _ci, _ec in enumerate(updated_ec):
            st.session_state.extra_copies[_ci].update(_ec)

        st.divider()

        # ── Layout presets ────────────────────────────────────────
        st.subheader("📐 레이아웃 프리셋")

        saved_presets = list_presets()
        if saved_presets:
            for pname in saved_presets:
                col_pname, col_apply, col_del = st.columns([4, 2, 1])
                with col_pname:
                    st.markdown(f"<div style='padding-top:6px;font-size:14px'>📌 {pname}</div>", unsafe_allow_html=True)
                with col_apply:
                    if st.button("적용", key=f"apply_preset_{pname}", use_container_width=True):
                        preset = load_preset(pname)
                        st.session_state.layers["logo"] = preset["logo"]
                        st.session_state.layers["main_text"] = preset["main_text"]
                        st.session_state.layers["sub_text"] = preset["sub_text"]
                        preset_prods = preset.get("products", [])
                        cur_prods = st.session_state.layers.get("products", [])
                        for i in range(len(cur_prods)):
                            if i < len(preset_prods):
                                cur_prods[i] = dict(preset_prods[i])
                            elif preset_prods:
                                last = preset_prods[-1]
                                cur_prods[i] = {"x": min(last["x"] + (i - len(preset_prods) + 1) * 30, 950),
                                                "y": last["y"], "scale": last["scale"]}
                        st.session_state.layers["products"] = cur_prods
                        for i, pos in enumerate(cur_prods):
                            if i < len(st.session_state.product_images):
                                st.session_state.product_images[i].update(pos)
                        _sync_sliders(st.session_state.layers, len(st.session_state.product_images))
                        st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_preset_{pname}"):
                        delete_preset(pname)
                        st.rerun()
        else:
            st.caption("저장된 프리셋이 없습니다.")

        with st.expander("현재 위치를 프리셋으로 저장"):
            preset_name = st.text_input("프리셋 이름", key="preset_name_input", placeholder="예: 여름세일 레이아웃")
            if st.button("💾 프리셋 저장", key="btn_save_preset", use_container_width=True):
                if not preset_name.strip():
                    st.warning("이름을 입력해 주세요.")
                else:
                    save_preset(preset_name.strip(), st.session_state.layers)
                    st.success(f"'{preset_name}' 저장 완료!")
                    st.rerun()

        st.divider()

        # ── Badge text ────────────────────────────────────────────
        st.subheader("🏷 뱃지 텍스트")

        with st.expander("새 뱃지 추가", expanded=len(st.session_state.badges) == 0):
            badge_text = st.text_input("뱃지 텍스트", key="badge_text_input", placeholder="예: ~30%")
            badge_color_name = st.selectbox("배경 색상", list(BADGE_COLORS.keys()), key="badge_color_select")
            badge_size = st.slider("글자 크기(pt)", 14, 60, 28, key="badge_size_slider")
            col_bx, col_by = st.columns(2)
            with col_bx:
                badge_x = st.slider("뱃지 X", 0, 950, 200, key="badge_x_slider")
            with col_by:
                badge_y = st.slider("뱃지 Y", 0, 220, 150, key="badge_y_slider")
            if st.button("➕ 뱃지 추가", key="btn_add_badge", use_container_width=True):
                if not badge_text.strip():
                    st.warning("텍스트를 입력해 주세요.")
                else:
                    color = BADGE_COLORS[badge_color_name]
                    st.session_state.badges.append({
                        "text": badge_text.strip(),
                        "bg_color": list(color["bg"]),
                        "text_color": list(color["text"]),
                        "font_size": badge_size,
                        "x": badge_x,
                        "y": badge_y,
                    })
                    st.rerun()

        if st.session_state.badges:
            st.caption(f"등록된 뱃지 {len(st.session_state.badges)}개")
            for i, badge in enumerate(st.session_state.badges):
                col_bi, col_bdel = st.columns([5, 1])
                with col_bi:
                    color_hex = "#{:02X}{:02X}{:02X}".format(*badge["bg_color"])
                    st.markdown(
                        f'<span style="background:{color_hex};color:#fff;padding:2px 8px;border-radius:4px;font-size:13px">'
                        f'{badge["text"]}</span> '
                        f'<span style="font-size:12px;color:gray">({badge["x"]}, {badge["y"]})</span>',
                        unsafe_allow_html=True,
                    )
                with col_bdel:
                    if st.button("✕", key=f"del_badge_{i}"):
                        st.session_state.badges.pop(i)
                        st.rerun()

        st.divider()
        st.session_state.show_guidelines = st.toggle(
            "가이드라인 표시", value=st.session_state.show_guidelines, key="guideline_toggle"
        )

    # ── Canvas render ─────────────────────────────────────────────
    layers = st.session_state.layers
    _main_color = tuple(st.session_state.get("main_color", [76, 76, 76]))
    _sub_color  = tuple(st.session_state.get("sub_color",  [119, 119, 119]))
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
        main_font_family=st.session_state.get("main_font_family", "Spoqa Han Sans"),
        main_color=_main_color,
        sub_copy=st.session_state.get("sub_copy", ""),
        sub_x=layers["sub_text"]["x"],
        sub_y=layers["sub_text"]["y"],
        sub_copy_size=layers["sub_text"].get("size", 39),
        sub_font_family=st.session_state.get("sub_font_family", "Spoqa Han Sans"),
        sub_color=_sub_color,
        badges=st.session_state.badges,
        extra_copies=st.session_state.extra_copies,
        show_guidelines=st.session_state.show_guidelines,
    )

    # ── Drag canvas ───────────────────────────────────────────────
    drag_elements = []
    prods = layers.get("products", [])
    for i, item in enumerate(st.session_state.product_images):
        _pscale = prods[i]["scale"] if i < len(prods) else item.get("scale", 75)
        px = prods[i]["x"] if i < len(prods) else item.get("x", 600)
        py = prods[i]["y"] if i < len(prods) else item.get("y", 10)
        _img = item.get("image")
        _pw = int(_img.width  * _pscale / 100) if _img else 100
        _ph = int(_img.height * _pscale / 100) if _img else 100
        drag_elements.append({"id": f"product_{i}", "type": "product", "label": f"P{i+1}",
                               "x": px, "y": py, "w": _pw, "h": _ph, "scale": _pscale})

    _logo_img = st.session_state.logo_image
    _lscale = layers["logo"]["scale"]
    _lw = int(_logo_img.width  * _lscale / 100) if _logo_img else 80
    _lh = int(_logo_img.height * _lscale / 100) if _logo_img else 40
    drag_elements.append({"id": "logo", "type": "logo", "label": "L",
                           "x": layers["logo"]["x"], "y": layers["logo"]["y"],
                           "w": _lw, "h": _lh, "scale": _lscale})

    _main_str = st.session_state.get("main_copy", "")
    _msz = layers["main_text"].get("size", 48)
    drag_elements.append({"id": "main_text", "type": "main_text", "label": "M",
                           "x": layers["main_text"]["x"], "y": layers["main_text"]["y"],
                           "w": max(60, int(len(_main_str) * _msz * 0.55)),
                           "h": int(_msz * 1.3)})

    _sub_str = st.session_state.get("sub_copy", "")
    _ssz = layers["sub_text"].get("size", 39)
    drag_elements.append({"id": "sub_text", "type": "sub_text", "label": "S",
                           "x": layers["sub_text"]["x"], "y": layers["sub_text"]["y"],
                           "w": max(60, int(len(_sub_str) * _ssz * 0.55)),
                           "h": int(_ssz * 1.3)})

    for _bi, _badge in enumerate(st.session_state.badges):
        drag_elements.append({"id": f"badge_{_bi}", "type": "badge", "label": f"B{_bi+1}",
                               "x": _badge["x"], "y": _badge["y"]})

    for _ci, _ec in enumerate(st.session_state.extra_copies):
        if _ec.get("enabled") and _ec.get("text"):
            _ecsz = _ec.get("size", 36)
            drag_elements.append({"id": f"extra_copy_{_ci}", "type": "extra_copy", "label": f"C{_ci+3}",
                                   "x": _ec.get("x", 50), "y": _ec.get("y", 100),
                                   "w": max(60, int(len(_ec["text"]) * _ecsz * 0.55)),
                                   "h": int(_ecsz * 1.3)})

    st.caption("🔴상품  🟢로고  🔵메인  🟣서브  🟡뱃지  🩵추가카피 — 요소를 직접 드래그·크기조절")
    drag_result = canvas_drag(canvas_img, drag_elements, CANVAS_W, CANVAS_H, 700, key="drag_canvas")
    if drag_result and st.session_state.drag_pending is None:
        st.session_state.drag_pending = drag_result
        st.rerun()

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
        main_font_family=st.session_state.get("main_font_family", "Spoqa Han Sans"),
        main_color=_main_color,
        sub_copy=st.session_state.get("sub_copy", ""),
        sub_x=layers["sub_text"]["x"],
        sub_y=layers["sub_text"]["y"],
        sub_copy_size=layers["sub_text"].get("size", 39),
        sub_font_family=st.session_state.get("sub_font_family", "Spoqa Han Sans"),
        sub_color=_sub_color,
        badges=st.session_state.badges,
        extra_copies=st.session_state.extra_copies,
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
                        _sync_sliders(loaded["layers"], len(loaded.get("product_images", [])))
                        st.success(f"'{proj_name}' 불러오기 완료! 제작 탭으로 이동하세요.")
