import pandas as pd
import streamlit as st
import pydeck as pdk
from db import get_engine

engine = get_engine()

@st.cache_data
def load_ev_stations_data():
    try:
        return pd.read_sql("SELECT * FROM ev_stations_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["충전소명", "지역", "lat", "lon", "급속충전기수", "완속충전기수", "운영상태"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">전기차 충전소 정보 및 상태 조회</h1>
            <div style="font-size: 0.95rem; color: #475569;">지역별 전기차 충전소 위치, 충전기 대수 및 실시간 운영 상태를 확인합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    ev_stations_df = load_ev_stations_data()

    if ev_stations_df.empty:
        st.warning("연동된 데이터베이스에 충전소 정보 데이터가 존재하지 않습니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        selected_region = st.selectbox("지역 선택", ["전체"] + sorted(ev_stations_df["지역"].unique().tolist()))
    with c2:
        selected_status = st.selectbox("운영 상태 필터", ["전체", "정상운영", "점검중"])

    filtered_stations = ev_stations_df.copy()
    if selected_region != "전체":
        filtered_stations = filtered_stations[filtered_stations["지역"] == selected_region]
    if selected_status != "전체":
        filtered_stations = filtered_stations[filtered_stations["운영상태"] == selected_status]

    st.markdown(f"### 🗺️ 충전소 위치 지도 (검색 결과: {len(filtered_stations)}개)")

    lat_center = filtered_stations["lat"].mean() if not filtered_stations.empty else 37.5559
    lon_center = filtered_stations["lon"].mean() if not filtered_stations.empty else 126.9723

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_stations,
        get_position=["lon", "lat"],
        get_color=[0, 128, 255, 160],
        get_radius=3000,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=9 if selected_region != "전체" else 6.5,
        pitch=30,
    )

    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "충전소명: {충전소명}\n급속: {급속충전기수}기 / 완속: {완속충전기수}기\n상태: {운영상태}"})
    st.pydeck_chart(r)

    st.markdown("### 📋 충전소 상세 운영 목록")
    st.dataframe(filtered_stations[["지역", "충전소명", "급속충전기수", "완속충전기수", "운영상태"]], use_container_width=True, hide_index=True)