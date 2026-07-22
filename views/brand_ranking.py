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
def load_brand_ranking_data():
    try:
        return pd.read_sql("SELECT * FROM brand_ranking_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["기준연월", "제조사구분", "브랜드", "등록대수", "전월대비증가"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">브랜드별 랭킹 순위</h1>
            <div style="font-size: 0.95rem; color: #475569;">수입/국산 및 연도(월) 조건을 선택하여 브랜드 등록 순위를 확인합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    brand_ranking_df = load_brand_ranking_data()

    if brand_ranking_df.empty:
        st.warning("연동된 데이터베이스에 브랜드 랭킹 데이터가 존재하지 않습니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        maker_type = st.selectbox("제조사 구분 선택", ["국산차", "수입차"])
    with c2:
        available_months = sorted(brand_ranking_df["기준연월"].unique(), reverse=True)
        selected_month = st.selectbox("기준 연월 선택", available_months)

    filtered = brand_ranking_df[
        (brand_ranking_df["제조사구분"] == maker_type) & 
        (brand_ranking_df["기준연월"] == selected_month)
    ].copy()

    if not filtered.empty:
        filtered = filtered.sort_values(by="등록대수", ascending=False).reset_index(drop=True)
        filtered.index = filtered.index + 1
        filtered.insert(0, "순위", filtered.index)
        filtered["증감률(%)"] = (filtered["전월대비증가"] / (filtered["등록대수"] - filtered["전월대비증가"]) * 100).round(2)
        filtered["브랜드 로고"] = filtered["브랜드"].map(logo_url_map)

    st.markdown(f"### 📌 [{selected_month}] {maker_type} 브랜드 등록 랭킹")
    
    if not filtered.empty:
        display_df = filtered[["순위", "브랜드 로고", "브랜드", "등록대수", "전월대비증가", "증감률(%)"]].rename(
            columns={"전월대비증가": "전월대비 증가량"}
        )
        st.dataframe(
            display_df,
            column_config={
                "브랜드 로고": st.column_config.ImageColumn("브랜드 로고", width="small")
            },
            use_container_width=True,
            hide_index=True,
        )

        download_df = display_df.drop(columns=["브랜드 로고"])
        st.download_button(
            "브랜드 랭킹 데이터 다운로드 (CSV)",
            download_df.to_csv(index=False).encode("utf-8-sig"),
            f"브랜드_랭킹_{selected_month}.csv",
            "text/csv",
            use_container_width=True,
        )
    else:
        st.info("조건에 해당하는 브랜드 데이터가 없습니다.")