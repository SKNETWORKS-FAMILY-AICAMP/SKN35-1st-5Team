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
def load_model_ranking_data():
    try:
        return pd.read_sql("SELECT * FROM model_ranking_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["기준연월", "제조사구분", "브랜드", "차량이름", "연료", "등록대수", "전월대비증가"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">모델별 랭킹 순위</h1>
            <div style="font-size: 0.95rem; color: #475569;">기준 연월과 국산/수입 구분을 선택하면 등록대수 기준 상위 10개 모델을 조회합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    model_ranking_df = load_model_ranking_data()

    if model_ranking_df.empty:
        st.warning("연동된 데이터베이스에 모델별 랭킹 데이터가 존재하지 않습니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        available_months = sorted(
            m for m in model_ranking_df["기준연월"].unique() if "2025-06" <= m <= "2026-06"
        )[::-1]
        selected_month = st.selectbox("기준 연월 선택", available_months, key="model_month")
    with c2:
        maker_type = st.selectbox("제조사 구분 선택", ["국산차", "수입차"], key="model_maker_type")

    sub_df = model_ranking_df[
        (model_ranking_df["기준연월"] == selected_month) &
        (model_ranking_df["제조사구분"] == maker_type)
    ]

    st.markdown(f"### 🏆 [{selected_month}] [{maker_type}] 전체 모델 등록 Top 10")

    if not sub_df.empty:
        top10_df = sub_df.sort_values(by="등록대수", ascending=False).head(10).reset_index(drop=True)
        top10_df.index = top10_df.index + 1
        top10_df.insert(0, "순위", top10_df.index)
        top10_df["브랜드 로고"] = top10_df["브랜드"].map(logo_url_map)
        display_df = top10_df[["순위", "브랜드 로고", "브랜드", "차량이름", "연료", "등록대수", "전월대비증가"]].rename(
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
            "모델별 Top 10 데이터 다운로드 (CSV)",
            download_df.to_csv(index=False).encode("utf-8-sig"),
            f"모델_Top10_{maker_type}_{selected_month}.csv",
            "text/csv",
            use_container_width=True,
        )
    else:
        st.warning("선택하신 연월/제조사구분에 해당하는 모델 데이터가 없습니다.")