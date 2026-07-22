import pandas as pd
import streamlit as st
from db import get_engine

engine = get_engine()

@st.cache_data
def load_registration_data():
    try:
        return pd.read_sql("SELECT * FROM car_registration_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["기준연월", "제조사구분", "제조사", "시도", "차종", "연료", "등록대수"])

@st.cache_data
def load_faq_data():
    try:
        return pd.read_sql("SELECT * FROM faq_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["카테고리", "질문", "답변"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">전국 자동차 등록 현황 대시보드 (Home)</h1>
            <div style="font-size: 0.95rem; color: #475569;">주요 통계 요약 및 지역별/월별 등록 현황표를 확인합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    registration_df = load_registration_data()
    faq_df = load_faq_data()
    
    total_count = int(registration_df["등록대수"].sum()) if not registration_df.empty and "등록대수" in registration_df.columns else 0
    region_count = registration_df['시도'].nunique() if not registration_df.empty and "시도" in registration_df.columns else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("전체 등록대수", f"{total_count:,}대")
    with c2:
        st.metric("조회 지역 수", f"{region_count}개")
    with c3:
        st.metric("FAQ 수", f"{len(faq_df)}건")

    st.divider()
    tab1, tab2 = st.tabs(["📊 지역별 등록 요약", "📈 월별 데이터 추이"])

    with tab1:
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("### 시도별 총 등록대수 차트")
            if not registration_df.empty and "시도" in registration_df.columns:
                chart_df = registration_df.groupby("시도", as_index=False)["등록대수"].sum().sort_values("등록대수", ascending=False)
                st.bar_chart(chart_df.set_index("시도"), use_container_width=True)
            else:
                st.info("DB에 데이터가 없습니다.")
        with right:
            st.markdown("### 📋 지역별 등록 현황 요약 표")
            if not registration_df.empty and "시도" in registration_df.columns:
                st.dataframe(chart_df, use_container_width=True, hide_index=True)
            else:
                st.info("DB에 데이터가 없습니다.")

    with tab2:
        st.markdown("### 월별 총 등록 추이")
        if not registration_df.empty and "기준연월" in registration_df.columns:
            month_df = registration_df.groupby("기준연월", as_index=False)["등록대수"].sum().sort_values("기준연월")
            st.line_chart(month_df.set_index("기준연월"), use_container_width=True)
        else:
            st.info("DB에 데이터가 없습니다.")