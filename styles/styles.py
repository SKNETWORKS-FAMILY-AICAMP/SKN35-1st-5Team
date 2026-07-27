import streamlit as st


def apply_custom_styles() -> None:
    """애플리케이션 전용 Custom CSS 스타일을 적용합니다."""
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 2rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            }
            [data-testid="stSidebar"] * {
                color: white !important;
            }
            .hero {
                padding: 1.2rem 1.3rem;
                border-radius: 18px;
                background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%);
                border: 1px solid #dbeafe;
                margin-bottom: 1rem;
            }
            .subtext {
                font-size: 0.95rem;
                color: #475569;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# 사이드바 옵션 메뉴 스타일 딕셔너리 분리
SIDEBAR_MENU_STYLES = {
    "container": {"padding": "0!important", "background-color": "#0f172a"},
    "icon": {"color": "#e2e8f0", "font-size": "15px"},
    "nav-link": {
        "font-size": "14px",
        "color": "#f1f5f9",
        "text-align": "left",
        "margin": "0px",
        "background-color": "transparent",
        "--hover-color": "rgba(59, 130, 246, 0.3)",
    },
    "nav-link-selected": {
        "background-color": "#3b82f6",
        "color": "#ffffff",
    },
}