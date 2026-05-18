import streamlit as st


def render_controls(layers: dict, num_products: int) -> dict:
    """Render layer adjustment sliders in sidebar. Returns updated layers dict."""
    updated = dict(layers)

    # Logo — narrow range (top-left area)
    with st.sidebar.expander("🖼 로고 위치", expanded=False):
        updated["logo"] = {
            "x": st.slider("로고 X", 0, 200, layers["logo"]["x"], key="logo_x"),
            "y": st.slider("로고 Y", 0, 80, layers["logo"]["y"], key="logo_y"),
            "scale": st.slider("로고 크기(%)", 5, 60, layers["logo"]["scale"], key="logo_scale"),
        }

    # Product images — one expander per image
    product_layers = list(layers.get("products", []))
    for i in range(num_products):
        defaults = product_layers[i] if i < len(product_layers) else {"x": 600, "y": 10, "scale": 80}
        with st.sidebar.expander(f"📷 상품 이미지 {i + 1} 위치", expanded=(i == 0)):
            item = {
                "x": st.slider(f"이미지{i+1} X", 0, 950, defaults["x"], key=f"prod_x_{i}"),
                "y": st.slider(f"이미지{i+1} Y", 0, 230, defaults["y"], key=f"prod_y_{i}"),
                "scale": st.slider(f"이미지{i+1} 크기(%)", 10, 200, defaults["scale"], key=f"prod_scale_{i}"),
            }
            if i < len(product_layers):
                product_layers[i] = item
            else:
                product_layers.append(item)
    updated["products"] = product_layers

    # Text positions + font sizes
    with st.sidebar.expander("✏️ 메인 카피", expanded=False):
        updated["main_text"] = {
            "x": st.slider("메인 X", 0, 950, layers["main_text"]["x"], key="main_x"),
            "y": st.slider("메인 Y", 0, 200, layers["main_text"]["y"], key="main_y"),
            "size": st.slider("메인 크기(pt)", 20, 100, layers["main_text"].get("size", 48), key="main_size"),
        }

    with st.sidebar.expander("✏️ 서브 카피", expanded=False):
        updated["sub_text"] = {
            "x": st.slider("서브 X", 0, 950, layers["sub_text"]["x"], key="sub_x"),
            "y": st.slider("서브 Y", 0, 220, layers["sub_text"]["y"], key="sub_y"),
            "size": st.slider("서브 크기(pt)", 14, 70, layers["sub_text"].get("size", 39), key="sub_size"),
        }

    return updated
