import streamlit as st
from streamlit_option_menu import option_menu
from config import dataclasses,enums
from styles import styles
from views.brand_ranking import brand_ranking_view
from views.faq import faq_view
from views.home import home_view
from views.model_ranking import model_ranking_view
from views.registration import registration_status_view

# 설정 객체 생성
config = dataclasses.AppConfig()

# Page Config Configuration
st.set_page_config(
    page_title=config.page_title,
    page_icon=config.page_icon,
    layout=config.layout,
    initial_sidebar_state=config.initial_sidebar_state,
)

# Custom Styling & HTML Tags 적용
styles.apply_custom_styles()

# ---------------------------------------------------------
# 사이드바 메뉴 구성
# ---------------------------------------------------------
with st.sidebar:
    # 1. 이미지만 단독으로 크게 배치 (width를 조절해 크기를 키우거나 줄일 수 있습니다)
    # 중앙 정렬이 필요하다면 st.columns를 활용해 가운데에 넣을 수도 있습니다.
    st.image(config.sidebar_logo, width=180)  # 예: 180px (필요에 따라 150~220 사이로 조절)
    
    st.caption(config.sidebar_caption)
    st.divider()

    active_tab = option_menu(
        menu_title=None,
        options=enums.MenuOption.labels(),
        icons=enums.MenuOption.icons(),
        default_index=0,
        styles=styles.SIDEBAR_MENU_STYLES,
    )

    st.divider()
    st.caption(config.footer_caption)
# ---------------------------------------------------------
# 라우팅 맵핑
# ---------------------------------------------------------
view_mapping = {
    enums.MenuOption.HOME.label: home_view,
    enums.MenuOption.REGISTRATION.label: registration_status_view,
    enums.MenuOption.BRAND_RANKING.label: brand_ranking_view,
    enums.MenuOption.MODEL_RANKING.label: model_ranking_view,
    enums.MenuOption.FAQ.label: faq_view,
}

# 선택된 탭에 맞는 뷰 실행
if active_tab in view_mapping:
    view_mapping[active_tab]()
