import streamlit as st


def render_controls(layers: dict, num_products: int) -> dict:
    """Render layer adjustment sliders in sidebar. Returns updated layers dict."""
    updated = dict(layers)

    # Logo — narrow range (Option A: top-left area only)
    with st.sidebar.expander("🖼 로고 위치", expanded=False):
        updated["logo"] = {
            "x": st.slider("로고 X", 0, 200, layers["logo"]["x"], key="logo_x"),
            "y": st.slider("로고 Y", 0, 80, layers["logo"]["y"], key="logo_y"),
            "scale": st.slider("로고 크기(%)", 5, 60, layers["logo"]["scale"], key="logo_scale"),
        }

    # Product images — one expander per image
    product_layers = list(layers.get("products", []))
    for i in range(num_products):
        defaults = product_layers[i] if i < len(product_layers) else {"x": 30, "y": 50, "scale": 75}
        with st.sidebar.expander(f"📷 상품 이미지 {i + 1} 위치", expanded=(i == 0)):
            product_layers_item = {
                "x": st.slider(f"이미지{i+1} X", 0, 1100, defaults["x"], key=f"prod_x_{i}"),
                "y": st.slider(f"이미지{i+1} Y", 0, 550, defaults["y"], key=f"prod_y_{i}"),
                "scale": st.slider(f"이미지{i+1} 크기(%)", 10, 200, defaults["scale"], key=f"prod_scale_{i}"),
            }
            if i < len(product_layers):
                product_layers[i] = product_layers_item
            else:
                product_layers.append(product_layers_item)
    updated["products"] = product_layers

    # Text positions
    with st.sidebar.expander("✏️ 메인 카피 위치", expanded=False):
        updated["main_text"] = {
            "x": st.slider("메인카피 X", 0, 1100, layers["main_text"]["x"], key="main_x"),
            "y": st.slider("메인카피 Y", 0, 500, layers["main_text"]["y"], key="main_y"),
        }

    with st.sidebar.expander("✏️ 서브 카피 위치", expanded=False):
        updated["sub_text"] = {
            "x": st.slider("서브카피 X", 0, 1100, layers["sub_text"]["x"], key="sub_x"),
            "y": st.slider("서브카피 Y", 0, 500, layers["sub_text"]["y"], key="sub_y"),
        }

    return updated
