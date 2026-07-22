import pandas as pd
import streamlit as st
from db import get_engine

engine = get_engine()

logo_url_map = {
    "현대": "https://cdn.simpleicons.org/hyundai",
    "기아": "https://cdn.simpleicons.org/kia",
    "제네시스": "https://autoimg.danawa.com/photo/brand/304_90.png",
    "르노코리아": "https://cdn.simpleicons.org/renault",
    "BMW": "https://cdn.simpleicons.org/bmw",
    "Mercedes-Benz": "https://upload.wikimedia.org/wikipedia/commons/9/90/Mercedes-Logo.svg",
    "Tesla": "https://cdn.simpleicons.org/tesla",
    "Audi": "https://cdn.simpleicons.org/audi",
    "Volvo": "https://cdn.simpleicons.org/volvo",
    "Lexus": "https://autoimg.danawa.com/photo/brand/486_90.png",
    "Mini": "https://cdn.simpleicons.org/mini",
    "Porsche": "https://cdn.simpleicons.org/porsche",
    "Volkswagen": "https://cdn.simpleicons.org/volkswagen",
    "Land Rover": "https://autoimg.danawa.com/photo/brand/399_90.png"
}

@st.cache_data
def load_registration_data():
    try:
        return pd.read_sql("SELECT * FROM car_registration_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["기준연월", "제조사구분", "제조사", "시도", "차종", "연료", "등록대수"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">자동차 등록 현황 조회</h1>
            <div style="font-size: 0.95rem; color: #475569;">수입차 및 국산차 구분, 지역, 연료별 자동차 등록 통계 데이터를 상세히 필터링하고 확인합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    registration_df = load_registration_data()

    if registration_df.empty:
        st.warning("연동된 데이터베이스에 등록 현황 데이터가 존재하지 않습니다.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_maker_type = st.selectbox("제조사 구분 (국산/수입)", ["전체", "국산차", "수입차"])
    with c2:
        selected_region = st.selectbox("시도 필터", ["전체"] + sorted(registration_df["시도"].unique().tolist()))
    with c3:
        selected_fuel = st.selectbox("연료 필터", ["전체"] + sorted(registration_df["연료"].unique().tolist()))

    filtered_reg = registration_df.copy()
    if selected_maker_type != "전체":
        filtered_reg = filtered_reg[filtered_reg["제조사구분"] == selected_maker_type]
    if selected_region != "전체":
        filtered_reg = filtered_reg[filtered_reg["시도"] == selected_region]
    if selected_fuel != "전체":
        filtered_reg = filtered_reg[filtered_reg["연료"] == selected_fuel]

    display_reg = filtered_reg.copy()
    display_reg["브랜드 로고"] = display_reg["제조사"].map(logo_url_map)
    
    cols = ["기준연월", "제조사구분", "브랜드 로고", "제조사", "시도", "차종", "연료", "등록대수"]
    display_reg = display_reg[[c for c in cols if c in display_reg.columns]]

    st.markdown(f"### 📋 필터링된 등록 현황 목록 (총 {len(display_reg)}건)")
    
    st.dataframe(
        display_reg,
        column_config={
            "브랜드 로고": st.column_config.ImageColumn("브랜드 로고", width="small")
        },
        use_container_width=True,
        hide_index=True,
    )

    if not display_reg.empty:
        download_df = display_reg.drop(columns=["브랜드 로고"])
        st.download_button(
            "등록 현황 데이터 다운로드 (CSV)",
            download_df.to_csv(index=False).encode("utf-8-sig"),
            "자동차_등록_현황.csv",
            "text/csv",
            use_container_width=True,
        )