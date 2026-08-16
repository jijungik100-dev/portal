"""Data Portal - Frontend (Streamlit)."""

import streamlit as st

from app import api_client

st.set_page_config(
    page_title="Data Portal",
    page_icon="📊",
    layout="wide",
)

# --- Sidebar ---
with st.sidebar:
    st.title("Data Portal")

    # Backend 연결 상태 표시
    if api_client.health_check():
        st.success("Backend 연결됨")
    else:
        st.error("Backend 연결 실패")

# --- Main: 중앙 정렬 ---
st.markdown(
    """
    <style>
        .center-message {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 70vh;
            font-size: 4rem;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    result = api_client.get("/admin/home")
    message = result.get("data", {}).get("message", "")
except Exception:
    message = "Backend 연결 실패"

st.markdown(f'<div class="center-message">{message}</div>', unsafe_allow_html=True)
