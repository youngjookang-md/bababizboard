import streamlit as st


def _ctrl(label: str, key: str, min_val: int, max_val: int, default: int, step: int = 5) -> int:
    """Number input with ± step buttons and direct typing."""
    val = int(st.session_state.get(key, default))
    val = max(min_val, min(max_val, val))
    return int(st.number_input(label, min_value=min_val, max_value=max_val,
                               value=val, step=step, key=key))


def render_controls(layers: dict, num_products: int) -> dict:
    updated = dict(layers)

    with st.sidebar.expander("🖼 로고 위치", expanded=False):
        updated["logo"] = {
            "x": _ctrl("로고 X", "logo_x", 0, 950, layers["logo"]["x"]),
            "y": _ctrl("로고 Y", "logo_y", 0, 230, layers["logo"]["y"]),
            "scale": _ctrl("로고 크기(%)", "logo_scale", 5, 60, layers["logo"]["scale"]),
        }

    product_layers = list(layers.get("products", []))
    for i in range(num_products):
        defaults = product_layers[i] if i < len(product_layers) else {"x": 600, "y": 10, "scale": 80}
        with st.sidebar.expander(f"📷 상품 이미지 {i + 1} 위치", expanded=(i == 0)):
            item = {
                "x": _ctrl(f"이미지{i+1} X", f"prod_x_{i}", 0, 950, defaults["x"]),
                "y": _ctrl(f"이미지{i+1} Y", f"prod_y_{i}", 0, 230, defaults["y"]),
                "scale": _ctrl(f"이미지{i+1} 크기(%)", f"prod_scale_{i}", 10, 200, defaults["scale"]),
            }
            if i < len(product_layers):
                product_layers[i] = item
            else:
                product_layers.append(item)
    updated["products"] = product_layers

    with st.sidebar.expander("✏️ 메인 카피", expanded=False):
        updated["main_text"] = {
            "x": _ctrl("메인 X", "main_x", 0, 950, layers["main_text"]["x"]),
            "y": _ctrl("메인 Y", "main_y", 0, 200, layers["main_text"]["y"]),
            "size": _ctrl("메인 크기(pt)", "main_size", 20, 100, layers["main_text"].get("size", 48), step=1),
        }

    with st.sidebar.expander("✏️ 서브 카피", expanded=False):
        updated["sub_text"] = {
            "x": _ctrl("서브 X", "sub_x", 0, 950, layers["sub_text"]["x"]),
            "y": _ctrl("서브 Y", "sub_y", 0, 220, layers["sub_text"]["y"]),
            "size": _ctrl("서브 크기(pt)", "sub_size", 14, 70, layers["sub_text"].get("size", 39), step=1),
        }

    return updated


def render_extra_copy_controls(extra_copies: list) -> list:
    updated = [dict(ec) for ec in extra_copies]
    for ci, ec in enumerate(extra_copies):
        if ec.get("enabled"):
            with st.sidebar.expander(f"✏️ 카피 {ci+3} 위치", expanded=False):
                updated[ci]["x"]    = _ctrl(f"카피{ci+3} X",    f"ec_{ci}_x",    0, 950, ec.get("x", 50))
                updated[ci]["y"]    = _ctrl(f"카피{ci+3} Y",    f"ec_{ci}_y",    0, 230, ec.get("y", 100))
                updated[ci]["size"] = _ctrl(f"카피{ci+3} 크기", f"ec_{ci}_size", 14,  80, ec.get("size", 36), step=1)
    return updated
