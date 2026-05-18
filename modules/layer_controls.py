import streamlit as st
from PIL import Image

def render_controls(default_layers: dict) -> dict:
    """Render layer adjustment sliders in sidebar, return current values."""
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
