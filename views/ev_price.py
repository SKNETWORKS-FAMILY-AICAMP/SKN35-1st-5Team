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
def load_ev_price_data():
    try:
        df = pd.read_sql("SELECT * FROM ev_price_table", con=engine)
    except Exception:
        df = pd.DataFrame(columns=["브랜드", "모델명", "차량가격(원)", "정부보조금(원)", "배터리용량(kWh)", "주행거리(km)", "전비(km/kWh)"])
    
    if not df.empty and "차량가격(원)" in df.columns and "정부보조금(원)" in df.columns:
        df["최종실구매가(원)"] = df["차량가격(원)"] - df["정부보조금(원)"]
    else:
        df["최종실구매가(원)"] = []
    return df

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">전기차 가격 및 제원 비교</h1>
            <div style="font-size: 0.95rem; color: #475569;">전기차 모델별 가격, 정부 보조금, 실구매가뿐만 아니라 배터리 용량 및 1회 충전 주행거리 제원을 비교합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    ev_price_df = load_ev_price_data()

    if ev_price_df.empty:
        st.warning("연동된 데이터베이스에 전기차 가격 및 제원 데이터가 존재하지 않습니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        selected_brand = st.selectbox("브랜드 필터", ["전체"] + sorted(ev_price_df["브랜드"].unique().tolist()))
    with c2:
        sort_option = st.selectbox("정렬 기준", ["최종실구매가 낮은순", "주행거리 긴순", "배터리 용량 큰순"])

    filtered_ev = ev_price_df.copy()
    if selected_brand != "전체":
        filtered_ev = filtered_ev[filtered_ev["브랜드"] == selected_brand]

    if sort_option == "최종실구매가 낮은순":
        filtered_ev = filtered_ev.sort_values("최종실구매가(원)", ascending=True)
    elif sort_option == "주행거리 긴순":
        filtered_ev = filtered_ev.sort_values("주행거리(km)", ascending=False)
    else:
        filtered_ev = filtered_ev.sort_values("배터리용량(kWh)", ascending=False)

    display_ev = filtered_ev.copy()
    display_ev["브랜드 로고"] = display_ev["브랜드"].map(logo_url_map)
    display_ev["차량가격"] = display_ev["차량가격(원)"].apply(lambda x: f"{x:,}원")
    display_ev["정부보조금"] = display_ev["정부보조금(원)"].apply(lambda x: f"-{x:,}원")
    display_ev["최종 실구매가"] = display_ev["최종실구매가(원)"].apply(lambda x: f"{x:,}원")
    display_ev["배터리 용량"] = display_ev["배터리용량(kWh)"].apply(lambda x: f"{x} kWh")
    display_ev["1회 주행거리"] = display_ev["주행거리(km)"].apply(lambda x: f"{x} km")

    cols = ["브랜드 로고", "브랜드", "모델명", "차량가격", "정부보조금", "최종 실구매가", "배터리 용량", "1회 주행거리", "전비(km/kWh)"]
    display_ev = display_ev[cols]

    st.markdown(f"### 💰 전기차 가격·보조금 및 상세 제원 비교 (총 {len(display_ev)}건)")
    
    st.dataframe(
        display_ev,
        column_config={
            "브랜드 로고": st.column_config.ImageColumn("브랜드 로고", width="small")
        },
        use_container_width=True,
        hide_index=True,
    )

    st.info("💡 보조금 및 실구매가는 지자체 예산 소진 상황에 따라 변동될 수 있습니다.")