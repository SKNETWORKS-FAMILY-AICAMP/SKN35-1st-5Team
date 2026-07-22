import streamlit as st
from streamlit_option_menu import option_menu

from views import home, registration, brand_ranking, model_ranking, faq, ev_station, ev_price

st.set_page_config(
    page_title="자동차 등록 및 전기차 정보 통합 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 1.1rem; padding-bottom: 2rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); }
        [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🚗 Auto Insight")
    st.caption("자동차 통합 정보 시스템")
    st.divider()

    active_tab = option_menu(
        menu_title=None,
        options=[
            "Home",
            "자동차 등록 현황",
            "브랜드별 랭킹",
            "모델별 랭킹",
            "전기차 충전소 정보",
            "전기차 가격 및 제원 비교",
            "FAQ",  # FAQ를 제일 아래로 이동
        ],
        icons=[
            "house", "clipboard-data", "trophy", "car-front", 
            "ev-station", "cash-coin", "question-circle"  # 아이콘 순서도 맞춤
        ],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0f172a"},
            "icon": {"color": "#e2e8f0", "font-size": "15px"},
            "nav-link": {
                "font-size": "14px", "color": "#f1f5f9", "text-align": "left", "margin": "0px",
                "background-color": "transparent", "--hover-color": "rgba(59, 130, 246, 0.3)",
            },
            "nav-link-selected": {"background-color": "#3b82f6", "color": "#ffffff"},
        }
    )

    st.divider()
    st.caption("SKN35_1st_Project_Group5")
    st.caption("김경민, 손채영, 유지호, 차윤정")

if active_tab == "Home":
    home.render()
elif active_tab == "자동차 등록 현황":
    registration.render()
elif active_tab == "브랜드별 랭킹":
    brand_ranking.render()
elif active_tab == "모델별 랭킹":
    model_ranking.render()
elif active_tab == "전기차 충전소 정보":
    ev_station.render()
elif active_tab == "전기차 가격 및 제원 비교":
    ev_price.render()
elif active_tab == "FAQ":  # 라우팅 조건문도 맨 아래로 이동
    faq.render()