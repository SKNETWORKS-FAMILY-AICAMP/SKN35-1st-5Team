import pandas as pd
import streamlit as st
import pydeck as pdk
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="자동차 등록 및 전기차 정보 통합 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        .section-card {
            padding: 1rem 1rem 0.8rem 1rem;
            border-radius: 16px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        }
        .small-label {
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 0.2rem;
        }
        .big-number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.1;
        }
        .subtext {
            font-size: 0.95rem;
            color: #475569;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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

registration_df = pd.DataFrame([
    {"기준연월": "2026-02", "제조사구분": "국산차", "제조사": "현대", "시도": "서울", "차종": "승용", "연료": "휘발유", "등록대수": 3050000},
    {"기준연월": "2026-02", "제조사구분": "국산차", "제조사": "기아", "시도": "경기", "차종": "승용", "연료": "하이브리드", "등록대수": 4200000},
    {"기준연월": "2026-02", "제조사구분": "국산차", "제조사": "제네시스", "시도": "부산", "차종": "승용", "연료": "휘발유", "등록대수": 610000},
    {"기준연월": "2026-02", "제조사구분": "국산차", "제조사": "르노코리아", "시도": "인천", "차종": "승용", "연료": "LPG", "등록대수": 450000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "BMW", "시도": "서울", "차종": "승용", "연료": "휘발유", "등록대수": 520000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Mercedes-Benz", "시도": "경기", "차종": "승용", "연료": "휘발유", "등록대수": 490000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Tesla", "시도": "제주", "차종": "승용", "연료": "전기", "등록대수": 150000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Audi", "시도": "대구", "차종": "승용", "연료": "휘발유", "등록대수": 120000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Volvo", "시도": "인천", "차종": "승용", "연료": "하이브리드", "등록대수": 95000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Lexus", "시도": "부산", "차종": "승용", "연료": "하이브리드", "등록대수": 88000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Mini", "시도": "서울", "차종": "승용", "연료": "휘발유", "등록대수": 76000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Porsche", "시도": "경기", "차종": "승용", "연료": "휘발유", "등록대수": 45000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Volkswagen", "시도": "대구", "차종": "승용", "연료": "디젤", "등록대수": 110000},
    {"기준연월": "2026-02", "제조사구분": "수입차", "제조사": "Land Rover", "시도": "인천", "차종": "승용", "연료": "디젤", "등록대수": 52000},
    {"기준연월": "2026-01", "제조사구분": "국산차", "제조사": "현대", "시도": "서울", "차종": "승용", "연료": "휘발유", "등록대수": 3020000},
    {"기준연월": "2026-01", "제조사구분": "국산차", "제조사": "기아", "시도": "경기", "차종": "승용", "연료": "하이브리드", "등록대수": 4150000},
])

brand_ranking_df = pd.DataFrame([
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "현대", "등록대수": 115000, "전월대비증가": 4500},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "기아", "등록대수": 108000, "전월대비증가": 3200},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "제네시스", "등록대수": 14000, "전월대비증가": -300},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "르노코리아", "등록대수": 6500, "전월대비증가": 200},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "BMW", "등록대수": 7200, "전월대비증가": 800},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Mercedes-Benz", "등록대수": 6800, "전월대비증가": 400},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Tesla", "등록대수": 3100, "전월대비증가": 1200},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Audi", "등록대수": 1800, "전월대비증가": -150},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Volvo", "등록대수": 1600, "전월대비증가": 100},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Lexus", "등록대수": 1400, "전월대비증가": 50},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Mini", "등록대수": 1100, "전월대비증가": -80},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Porsche", "등록대수": 950, "전월대비증가": 220},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Volkswagen", "등록대수": 800, "전월대비증가": -300},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Land Rover", "등록대수": 500, "전월대비증가": 30},
    {"기준연월": "2026-01", "제조사구분": "국산차", "브랜드": "현대", "등록대수": 110500, "전월대비증가": 1500},
    {"기준연월": "2026-01", "제조사구분": "국산차", "브랜드": "기아", "등록대수": 104800, "전월대비증가": 2100},
    {"기준연월": "2026-01", "제조사구분": "국산차", "브랜드": "제네시스", "등록대수": 14300, "전월대비증가": 400},
    {"기준연월": "2026-01", "제조사구분": "국산차", "브랜드": "르노코리아", "등록대수": 6300, "전월대비증가": -100},
    {"기준연월": "2026-01", "제조사구분": "수입차", "브랜드": "BMW", "등록대수": 6400, "전월대비증가": -200},
    {"기준연월": "2026-01", "제조사구분": "수입차", "브랜드": "Mercedes-Benz", "등록대수": 6400, "전월대비증가": 100},
    {"기준연월": "2026-01", "제조사구분": "수입차", "브랜드": "Tesla", "등록대수": 1900, "전월대비증가": 400},
])

model_ranking_df = pd.DataFrame([
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "현대", "차량이름": "그랜저", "연료": "휘발유", "등록대수": 9800, "전월대비증가": 450},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "현대", "차량이름": "아반떼", "연료": "하이브리드", "등록대수": 7500, "전월대비증가": 210},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "현대", "차량이름": "싼타페", "연료": "하이브리드", "등록대수": 6800, "전월대비증가": -120},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "기아", "차량이름": "쏘렌토", "연료": "디젤", "등록대수": 8900, "전월대비증가": -150},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "기아", "차량이름": "카니발", "연료": "디젤", "등록대수": 8200, "전월대비증가": 300},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "제네시스", "차량이름": "G80", "연료": "휘발유", "등록대수": 4500, "전월대비증가": -50},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "제네시스", "차량이름": "GV80", "연료": "휘발유", "등록대수": 4200, "전월대비증가": 120},
    {"기준연월": "2026-02", "제조사구분": "국산차", "브랜드": "르노코리아", "차량이름": "그랑 콜레오스", "연료": "하이브리드", "등록대수": 3500, "전월대비증가": 410},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "BMW", "차량이름": "5시리즈", "연료": "휘발유", "등록대수": 2100, "전월대비증가": 180},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "BMW", "차량이름": "3시리즈", "연료": "디젤", "등록대수": 1200, "전월대비증가": -50},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Mercedes-Benz", "차량이름": "E-Class", "연료": "휘발유", "등록대수": 2400, "전월대비증가": 220},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Tesla", "차량이름": "Model Y", "연료": "전기", "등록대수": 2300, "전월대비증가": 950},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Audi", "차량이름": "A6", "연료": "휘발유", "등록대수": 920, "전월대비증가": -40},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Volvo", "차량이름": "XC60", "연료": "하이브리드", "등록대수": 850, "전월대비증가": 70},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Lexus", "차량이름": "ES", "연료": "하이브리드", "등록대수": 900, "전월대비증가": 40},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Mini", "차량이름": "Cooper", "연료": "휘발유", "등록대수": 750, "전월대비증가": -15},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Porsche", "차량이름": "Cayenne", "연료": "휘발유", "등록대수": 550, "전월대비증가": 120},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Volkswagen", "차량이름": "Tiguan", "연료": "디젤", "등록대수": 500, "전월대비증가": -90},
    {"기준연월": "2026-02", "제조사구분": "수입차", "브랜드": "Land Rover", "차량이름": "Range Rover", "연료": "디젤", "등록대수": 300, "전월대비증가": 15},
])

faq_df = pd.DataFrame([
    {"카테고리": "차량 등록", "질문": "신규 자동차 등록은 어떻게 하나요?", "답변": "필요 서류를 준비해 관할 등록기관에 신청합니다."},
    {"카테고리": "통계 데이터", "질문": "등록 현황 데이터의 기준일은 언제인가요?", "답변": "공개된 월별 기준 통계를 바탕으로 제공합니다."},
    {"카테고리": "법인 차량", "질문": "법인 차량도 지역별 조회가 가능한가요?", "답변": "향후 법인 및 개인 구분 필터를 제공할 예정입니다."},
])

ev_stations_df = pd.DataFrame([
    {"충전소명": "서울역 공영주차장 충전소", "지역": "서울", "lat": 37.5559, "lon": 126.9723, "급속충전기수": 5, "완속충전기수": 10, "운영상태": "정상운영"},
    {"충전소명": "강남구청 급속충전소", "지역": "서울", "lat": 37.5173, "lon": 127.0473, "급속충전기수": 8, "완속충전기수": 4, "운영상태": "정상운영"},
    {"충전소명": "판교 테크노밸리 충전소", "지역": "경기", "lat": 37.4019, "lon": 127.1086, "급속충전기수": 10, "완속충전기수": 20, "운영상태": "점검중"},
    {"충전소명": "수원시청 전기차 충전터", "지역": "경기", "lat": 37.2636, "lon": 127.0286, "급속충전기수": 4, "완속충전기수": 8, "운영상태": "정상운영"},
    {"충전소명": "부산역 후광 충전소", "지역": "부산", "lat": 35.1150, "lon": 129.0422, "급속충전기수": 6, "완속충전기수": 12, "운영상태": "정상운영"},
    {"충전소명": "제주공항 전기차 충전 스테이션", "지역": "제주", "lat": 33.5066, "lon": 126.4930, "급속충전기수": 15, "완속충전기수": 30, "운영상태": "정상운영"},
])

ev_price_df = pd.DataFrame([
    {"브랜드": "현대", "모델명": "아이오닉 5", "차량가격(원)": 52000000, "정부보조금(원)": 6500000, "배터리용량(kWh)": 77.4, "주행거리(km)": 458, "전비(km/kWh)": 5.1},
    {"브랜드": "현대", "모델명": "아이오닉 6", "차량가격(원)": 54000000, "정부보조금(원)": 6800000, "배터리용량(kWh)": 77.4, "주행거리(km)": 524, "전비(km/kWh)": 6.0},
    {"브랜드": "기아", "모델명": "EV6", "차량가격(원)": 52600000, "정부보조금(원)": 6400000, "배터리용량(kWh)": 77.4, "주행거리(km)": 475, "전비(km/kWh)": 5.4},
    {"브랜드": "기아", "모델명": "EV9", "차량가격(원)": 73370000, "정부보조금(원)": 3100000, "배터리용량(kWh)": 99.8, "주행거리(km)": 501, "전비(km/kWh)": 4.2},
    {"브랜드": "Tesla", "모델명": "Model Y", "차량가격(원)": 52990000, "정부보조금(원)": 2000000, "배터리용량(kWh)": 60.0, "주행거리(km)": 350, "전비(km/kWh)": 5.8},
    {"브랜드": "Tesla", "모델명": "Model 3", "차량가격(원)": 51990000, "정부보조금(원)": 2200000, "배터리용량(kWh)": 60.0, "주행거리(km)": 382, "전비(km/kWh)": 6.1},
    {"브랜드": "BMW", "모델명": "i4 eDrive40", "차량가격(원)": 82900000, "정부보조금(원)": 2900000, "배터리용량(kWh)": 83.9, "주행거리(km)": 429, "전비(km/kWh)": 4.6},
    {"브랜드": "Volvo", "모델명": "EX30", "차량가격(원)": 49450000, "정부보조금(원)": 6200000, "배터리용량(kWh)": 69.0, "주행거리(km)": 404, "전비(km/kWh)": 5.8}
])
ev_price_df["최종실구매가(원)"] = ev_price_df["차량가격(원)"] - ev_price_df["정부보조금(원)"]


# --- 사이드바 통합 메뉴 구성 (배경색 통일 및 아이콘/글자 가독성 개선) ---
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
            "데이터 · ERD 안내",
            "전기차 충전소 정보",
            "전기차 가격 및 제원 비교",
            "FAQ",
            "QnA",
        ],
        icons=[
            "house",
            "clipboard-data",
            "trophy",
            "car-front",
            "database",
            "ev-station",
            "cash-coin",
            "question-circle",
            "chat-dots",
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
        }
    )

    st.divider()
    st.caption("SKN35_1st_Project_Group5")
    st.caption("김경민, 손채영, 유지호, 차윤정")


def section_title(title, caption):
    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">{title}</h1>
            <div class="subtext">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def dashboard_metric(label, value, desc):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="small-label">{label}</div>
            <div class="big-number">{value}</div>
            <div class="subtext">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- 화면 뷰 함수들 ---

def home_view():
    section_title("전국 자동차 등록 현황 대시보드 (Home)", "주요 통계 요약 및 지역별/월별 등록 현황표를 확인합니다.")
    total_count = int(registration_df["등록대수"].sum())
    c1, c2, c3 = st.columns(3)
    with c1:
        dashboard_metric("전체 등록대수", f"{total_count:,}대", "주요 브랜드 및 지역 집계 기준")
    with c2:
        dashboard_metric("조회 지역 수", f"{registration_df['시도'].nunique()}개", "등록된 시도 개수")
    with c3:
        dashboard_metric("FAQ 수", f"{len(faq_df)}건", "업무 문의 항목 수")

    st.divider()
    tab1, tab2 = st.tabs(["📊 지역별 등록 요약", "📈 월별 데이터 추이"])

    with tab1:
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("### 시도별 총 등록대수 차트")
            chart_df = registration_df.groupby("시도", as_index=False)["등록대수"].sum().sort_values("등록대수", ascending=False)
            st.bar_chart(chart_df.set_index("시도"), use_container_width=True)
        with right:
            st.markdown("### 📋 지역별 등록 현황 요약 표")
            st.dataframe(chart_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 월별 총 등록 추이")
        month_df = registration_df.groupby("기준연월", as_index=False)["등록대수"].sum().sort_values("기준연월")
        st.line_chart(month_df.set_index("기준연월"), use_container_width=True)

    st.info("현재 화면은 실시간 통계 시스템의 샘플 대시보드입니다.")

def registration_status_view():
    section_title("자동차 등록 현황 조회", "수입차 및 국산차 구분, 지역, 연료별 자동차 등록 통계 데이터를 상세히 필터링하고 확인합니다.")

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

def brand_ranking_view():
    section_title("브랜드별 랭킹 순위", "수입/국산 및 연도(월) 조건을 선택하여 브랜드 등록 순위를 확인합니다.")

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

    filtered = filtered.sort_values(by="등록대수", ascending=False).reset_index(drop=True)
    filtered.index = filtered.index + 1
    filtered.insert(0, "순위", filtered.index)

    filtered["증감률(%)"] = (filtered["전월대비증가"] / (filtered["등록대수"] - filtered["전월대비증가"]) * 100).round(2)
    filtered["브랜드 로고"] = filtered["브랜드"].map(logo_url_map)

    st.markdown(f"### 📌 [{selected_month}] {maker_type} 브랜드 등록 랭킹")

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

def model_ranking_view():
    section_title("모델별 랭킹 순위", "기준 연월과 수입/국산 선택 후 브랜드를 지정하여 차종별 상세 등록 랭킹을 조회합니다.")

    c1, c2 = st.columns(2)
    with c1:
        available_months = sorted(model_ranking_df["기준연월"].unique(), reverse=True)
        selected_month = st.selectbox("기준 연월 선택", available_months, key="model_month")
    with c2:
        maker_type = st.selectbox("제조사 구분 선택", ["국산차", "수입차"], key="model_maker_type")

    sub_df = model_ranking_df[
        (model_ranking_df["기준연월"] == selected_month) &
        (model_ranking_df["제조사구분"] == maker_type)
    ]
    raw_brands = sorted(sub_df["브랜드"].unique()) if not sub_df.empty else []

    st.markdown("#### 🔍 브랜드 선택")

    if raw_brands:
        if "selected_brand" not in st.session_state or st.session_state["selected_brand"] not in raw_brands:
            st.session_state["selected_brand"] = raw_brands[0]

        cols = st.columns(len(raw_brands))
        for idx, brand in enumerate(raw_brands):
            with cols[idx]:
                is_selected = (st.session_state["selected_brand"] == brand)
                if st.button(f"{'✅ ' if is_selected else ''}{brand}", key=f"btn_{brand}", use_container_width=True):
                    st.session_state["selected_brand"] = brand
                    st.rerun()

        selected_brand = st.session_state["selected_brand"]
    else:
        selected_brand = None
        st.warning("선택 가능한 브랜드가 없습니다.")

    filtered = sub_df[sub_df["브랜드"] == selected_brand].copy() if selected_brand else pd.DataFrame()

    if not filtered.empty:
        filtered = filtered.sort_values(by="등록대수", ascending=False).reset_index(drop=True)
        filtered.index = filtered.index + 1
        filtered.insert(0, "순위", filtered.index)
        filtered["브랜드 로고"] = filtered["브랜드"].map(logo_url_map)

    st.markdown(f"### 🚗 [{selected_month}] [{selected_brand if selected_brand else '선택 없음'}] 모델별 등록 랭킹")

    if not filtered.empty:
        display_df = filtered[["순위", "브랜드 로고", "브랜드", "차량이름", "연료", "등록대수", "전월대비증가"]].rename(
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
            "모델별 랭킹 데이터 다운로드 (CSV)",
            download_df.to_csv(index=False).encode("utf-8-sig"),
            f"모델_랭킹_{selected_brand}_{selected_month}.csv",
            "text/csv",
            use_container_width=True,
        )
    else:
        st.warning("선택하신 조건에 해당하는 모델 데이터가 없습니다.")

def data_erd_view():
    section_title("데이터 및 ERD 구조 안내", "시스템 스키마 및 테이블 구조 안내")
    st.info("데이터베이스 구조 및 ERD 정보 화면입니다.")

def faq_view():
    section_title("자주 하는 질문 (FAQ)", "키워드와 카테고리로 업무 문의를 빠르게 찾습니다.")

    c1, c2 = st.columns([2, 1])
    with c1:
        keyword = st.text_input("검색어", placeholder="예: 법인, 등록, 기준일")
    with c2:
        category = st.selectbox("카테고리", ["전체"] + sorted(faq_df["카테고리"].unique().tolist()))

    result_faq = faq_df.copy()
    if category != "전체":
        result_faq = result_faq[result_faq["카테고리"] == category]
    if keyword:
        matched = result_faq["질문"].str.contains(keyword, case=False, na=False) | result_faq["답변"].str.contains(keyword, case=False, na=False)
        result_faq = result_faq[matched]

    st.caption(f"{len(result_faq)}건의 FAQ 검색됨")
    for _, faq in result_faq.iterrows():
        with st.expander(f"[{faq['카테고리']}] {faq['질문']}"):
            st.write(faq["답변"])

def qna_view():
    section_title("QnA", "궁금한 점을 남기고 답변을 받아보는 QnA 게시판입니다.")
    st.info("QnA 화면입니다. 세부 기능은 추후 구현 예정입니다.")

def ev_station_map_view():
    section_title("전기차 충전소 정보 및 상태 조회", "지역별 전기차 충전소 위치, 충전기 대수 및 실시간 운영 상태를 확인합니다.")

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

def ev_price_and_spec_view():
    section_title("전기차 가격 및 제원 비교", "전기차 모델별 가격, 정부 보조금, 실구매가뿐만 아니라 배터리 용량 및 1회 충전 주행거리 제원을 비교합니다.")

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


# --- 메뉴 라우팅 연결 ---
if active_tab == "Home":
    home_view()
elif active_tab == "자동차 등록 현황":
    registration_status_view()
elif active_tab == "브랜드별 랭킹":
    brand_ranking_view()
elif active_tab == "모델별 랭킹":
    model_ranking_view()
elif active_tab == "데이터 · ERD 안내":
    data_erd_view()
elif active_tab == "FAQ":
    faq_view()
elif active_tab == "QnA":
    qna_view()
elif active_tab == "전기차 충전소 정보":
    ev_station_map_view()
elif active_tab == "전기차 가격 및 제원 비교":
    ev_price_and_spec_view()
