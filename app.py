import streamlit as st
from streamlit_option_menu import option_menu

from data_loader import (
    load_registration_data,
    load_brand_ranking_data,
    load_model_ranking_data,
    load_review_data,
    load_faq_data,
)
from views.home import home_view
from views.registration import registration_status_view
from views.brand_ranking import brand_ranking_view
from views.model_ranking import model_ranking_view
from views.faq import faq_view

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="자동차 등록 현황 통합 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Styling (CSS)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 데이터 로드
# ---------------------------------------------------------
registration_df = load_registration_data()
brand_ranking_df = load_brand_ranking_data()
model_ranking_df = load_model_ranking_data()
review_df = load_review_data()
faq_df = load_faq_data()

# ---------------------------------------------------------
# 사이드바 메뉴 구성
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🚗 Auto Insight")
    st.caption("자동차 등록 현황 통합 시스템")
    st.divider()

    active_tab = option_menu(
        menu_title=None,
        options=[
            "Home",
            "자동차 등록 현황",
            "브랜드별 랭킹",
            "모델별 랭킹",
            "FAQ",
        ],
        icons=[
            "house",
            "clipboard-data",
            "trophy",
            "car-front",
            "question-circle",
        ],
        default_index=0,
        styles={
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
        },
    )

    st.divider()
    st.caption("SKN35_1st_Project_Group5")

# ---------------------------------------------------------
# Tab Routing
# ---------------------------------------------------------
if active_tab == "Home":
    home_view(registration_df, faq_df, review_df, model_ranking_df)
elif active_tab == "자동차 등록 현황":
    registration_status_view(registration_df)
elif active_tab == "브랜드별 랭킹":
    brand_ranking_view(brand_ranking_df, registration_df)
elif active_tab == "모델별 랭킹":
    model_ranking_view(model_ranking_df, review_df)
elif active_tab == "FAQ":
    faq_view(faq_df)
