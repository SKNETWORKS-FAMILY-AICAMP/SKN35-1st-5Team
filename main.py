
import os
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from sqlalchemy import text
import random
import time

# db.py에서 SQLAlchemy 엔진 가져오기
from db import get_engine

# Page Config Configuration
st.set_page_config(
    page_title="자동차 등록 현황 통합 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 매핑 딕셔너리
# ---------------------------------------------------------

# 브랜드 로고 URL 매핑 딕셔너리
LOGO_URL_MAP = {
    "현대": "https://cdn.simpleicons.org/hyundai",
    "기아": "https://cdn.simpleicons.org/kia",
    "제네시스": "https://autoimg.danawa.com/photo/brand/304_90.png",
    "르노코리아": "https://cdn.simpleicons.org/renault",
    "BMW": "https://cdn.simpleicons.org/bmw",
    "벤츠": "https://upload.wikimedia.org/wikipedia/commons/9/90/Mercedes-Logo.svg",
    "테슬라": "https://cdn.simpleicons.org/tesla",
    "아우디": "https://cdn.simpleicons.org/audi",
    "볼보": "https://cdn.simpleicons.org/volvo",
    "렉서스": "https://autoimg.danawa.com/photo/brand/486_90.png",
    "미니": "https://cdn.simpleicons.org/mini",
    "토요타" : "https://file.carisyou.com/upload/2017/02/16/FILE_201702160632058010.png",
    "비야디" : "https://file.carisyou.com/upload/2025/01/16/FILE_202501160159046160.png",
    "Porsche": "https://cdn.simpleicons.org/porsche",
    "Volkswagen": "https://cdn.simpleicons.org/volkswagen",
    "Land Rover": "https://autoimg.danawa.com/photo/brand/399_90.png",
}

# 차량 이미지 URL 매핑 딕셔너리
CAR_IMAGE_URL_MAP = {
    "테슬라 모델 Y": "https://file.carisyou.com/upload/2025/03/28/thumb/FILE_202503280326303300.png",
    "비야디 돌핀": "https://file.carisyou.com/upload/2026/02/05/thumb/FILE_202602050221397310.png",
    "BMW 5시리즈": "https://file.carisyou.com/upload/2023/09/06/thumb/FILE_202309061102221390.png",
    "벤츠 E클래스": "https://file.carisyou.com/upload/2024/01/04/thumb/FILE_202401040227284180.png",
    "벤츠 GLC": "https://file.carisyou.com/upload/2026/07/09/thumb/FILE_202607090356077700.png",
    "비야디 씨라이언 7": "https://file.carisyou.com/upload/2025/09/08/thumb/FILE_202509080508098370.png",
    "테슬라 모델 X": "https://file.carisyou.com/upload/2025/06/18/thumb/FILE_202506180914009330.png",
    "볼보 EX30": "https://file.carisyou.com/upload/2023/11/20/thumb/FILE_202311201005517060.png",
    "토요타 RAV4": "https://file.carisyou.com/upload/2026/05/08/thumb/FILE_202605080932156420.png",
    "벤츠 GLE": "https://file.carisyou.com/upload/2023/08/28/thumb/FILE_202308280216070440.png",
    "테슬라 모델 3": "https://file.carisyou.com/upload/2024/04/03/thumb/FILE_202404030359257140.png",
    "BMW X3": "https://file.carisyou.com/upload/2024/10/14/thumb/FILE_202410140313144470.png",
    "아우디 A6": "https://file.carisyou.com/upload/2026/04/22/thumb/FILE_202604220319265610.png",
    "렉서스 ES": "https://file.carisyou.com/upload/2024/01/18/thumb/FILE_202401180100060120.png",
    "BMW X5": "https://file.carisyou.com/upload/2023/07/05/thumb/FILE_202307050208496140.png",
    "폴스타 폴스타 4": "https://file.carisyou.com/upload/2024/08/13/thumb/FILE_202408130246035850.png",
    "비야디 아토 3": "https://file.carisyou.com/upload/2025/01/16/thumb/FILE_202501160330016950.png",
    "렉서스 NX": "https://file.carisyou.com/upload/2023/03/23/thumb/FILE_202303230243469280.png",
    "볼보 XC60": "https://file.carisyou.com/upload/2025/07/31/thumb/FILE_202507310406214750.png",
    "벤츠 S클래스": "https://file.carisyou.com/upload/2026/05/18/thumb/FILE_202605180506519330.png",
    "미니 미니 쿠퍼": "https://file.carisyou.com/upload/2025/04/21/thumb/FILE_202504210353341500.png",
    "현대 그랜저": "https://file.carisyou.com/upload/2026/05/14/thumb/FILE_202605140405014280.png",
    "기아 쏘렌토": "https://file.carisyou.com/upload/2023/09/07/thumb/FILE_202309070441362840.png",
    "기아 카니발": "https://file.carisyou.com/upload/2024/02/05/thumb/FILE_202402050415167530.png",
    "기아 스포티지": "https://file.carisyou.com/upload/2024/11/08/thumb/FILE_202411081136590820.png",
    "기아 셀토스": "https://file.carisyou.com/upload/2026/02/26/thumb/FILE_202602260119043900.png",
    "현대 쏘나타": "https://file.carisyou.com/upload/2023/04/24/thumb/FILE_202304241052430090.png",
    "기아 레이": "https://file.carisyou.com/upload/2023/08/29/thumb/FILE_202308291058138900.png",
    "현대 아반떼": "https://file.carisyou.com/upload/2023/03/13/thumb/FILE_202303130931074190.png",
    "현대 싼타페": "https://file.carisyou.com/upload/2023/08/14/thumb/FILE_202308141019512170.png",
    "현대 팰리세이드": "https://file.carisyou.com/upload/2024/12/20/thumb/FILE_202412200435289480.png",
    "현대 투싼": "https://file.carisyou.com/upload/2023/12/06/thumb/FILE_202312060215369920.png",
    "기아 EV3": "https://file.carisyou.com/upload/2024/06/04/thumb/FILE_202406041058132380.png",
    "현대 코나": "https://file.carisyou.com/upload/2023/01/18/thumb/FILE_202301181038184400.png",
    "제네시스 G80": "https://autoimg.danawa.com/photo/brand/304_90.png",
}

DEFAULT_LOGO = "https://cdn.simpleicons.org/simpleicons"
DEFAULT_CAR_IMAGE = ""

# Custom Styling (CSS)
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
# DB 데이터 로드 함수 (실제 DB 컬럼명 적용)
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def load_registration_data():
    """1. car_registration 테이블 데이터 로드"""
    engine = get_engine()
    query = """
    SELECT regist_id, company_type, company_name, model_name, count_car_month, standard_month
    FROM car_registration
    ORDER BY standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["count_car_month"], errors="coerce").fillna(0).astype(int)
        df["manufacturer"] = df["company_name"]
        df["car_model_type"] = df["model_name"]
        df["standard_ym"] = df["standard_month"]
        df["manufacturer_type"] = df["company_type"]
        df["logo"] = df["manufacturer"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
        df["car_image"] = df["car_model_type"].map(CAR_IMAGE_URL_MAP).fillna(DEFAULT_CAR_IMAGE)
    return df

@st.cache_data(ttl=3600)
def load_brand_ranking_data():
    """2. car_brand_rank 테이블 데이터 로드"""
    engine = get_engine()
    query = """
    SELECT b.brand_id, 
           b.regist_id, 
           b.brand_name, 
           b.brand_standard_month AS standard_ym, 
           b.compare_car_month AS mom_increase,
           r.count_car_month AS registration_count,
           r.company_type AS manufacturer_type
    FROM car_brand_rank b
    LEFT JOIN car_registration r ON b.regist_id = r.regist_id
    ORDER BY b.brand_standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["mom_increase"] = pd.to_numeric(df["mom_increase"], errors="coerce").fillna(0).astype(int)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data(ttl=3600)
def load_model_ranking_data():
    """3. car_model_ranking 테이블 데이터 로드 (테이블명: car_model_ranking)"""
    engine = get_engine()
    query = """
    SELECT m.model_id, 
           m.regist_id, 
           m.brand_name, 
           m.standard_month AS standard_ym, 
           m.compare_car_month AS mom_increase,
           r.model_name AS car_name,
           r.count_car_month AS registration_count,
           r.company_type AS manufacturer_type,
           '휘발유/디젤/전기' AS fuel_type  -- 기본 표시용
    FROM car_model_ranking m
    LEFT JOIN car_registration r ON m.regist_id = r.regist_id
    ORDER BY m.standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["mom_increase"] = pd.to_numeric(df["mom_increase"], errors="coerce").fillna(0).astype(int)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
        df["car_image"] = df["car_name"].map(CAR_IMAGE_URL_MAP).fillna(DEFAULT_CAR_IMAGE)
    return df

@st.cache_data(ttl=3600)
def load_review_data():
    """4. review 테이블 데이터 로드"""
    engine = get_engine()
    query = """
    SELECT review_id, 
           model_id, 
           regist_id, 
           total_review AS overall_rating, 
           performance_review AS performance, 
           price_review AS price, 
           problem_review AS issues, 
           brand_name_review AS brand_name
    FROM review
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data(ttl=3600)
def load_faq_data():
    """5. faq 테이블 데이터 로드"""
    engine = get_engine()
    query = "SELECT faq_id, question, answer FROM faq ORDER BY faq_id ASC"
    return pd.read_sql(query, con=engine)

# 데이터 로드 실행
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
        }
    )

    st.divider()
    st.caption("SKN35_1st_Project_Group5")

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

# --- 필터 컴포넌트 ---
def render_filter(df, show_type_filter=False, key_prefix="filter"):
    if df.empty or "standard_ym" not in df.columns:
        return None, None

    available_yms = sorted(df["standard_ym"].dropna().unique(), reverse=True)
    years = sorted(list(set([ym.split("-")[0] for ym in available_yms if "-" in ym])), reverse=True)

    if not years:
        return None, None

    if show_type_filter:
        c1, c2, c3, _ = st.columns([2, 2, 2, 4])
    else:
        c1, c2, _ = st.columns([2, 2, 6])

    with c1:
        selected_year = st.selectbox("📅 연도 선택", years, key=f"{key_prefix}_year")

    available_months = sorted(list(set([ym.split("-")[1] for ym in available_yms if ym.startswith(selected_year)])), reverse=True)
    with c2:
        selected_month = st.selectbox("📆 월 선택", available_months, key=f"{key_prefix}_month")

    selected_target_ym = f"{selected_year}-{selected_month}"

    selected_type = "전체"
    if show_type_filter:
        with c3:
            selected_type = st.selectbox("🚘 구분 선택", ["전체", "국산", "수입"], key=f"{key_prefix}_type")

    return selected_target_ym, selected_type

# --- 📌 월별 등록 추이 + 이미지 출력 팝업 (Dialog) ---
@st.dialog("📈 월별 등록 추이 분석", width="large")
def show_trend_dialog(car_name, logo_url, car_image_url, full_df):
    c_logo, c_title, c_img = st.columns([1, 4, 3])

    with c_logo:
        if logo_url:
            st.image(logo_url, width=45)

    with c_title:
        st.markdown(f"### **{car_name}**")
        st.caption("월별 총 등록대수 변동 추이 그래프입니다.")

    with c_img:
        if car_image_url:
            st.image(car_image_url, width=160)

    st.divider()

    car_trend_df = full_df[full_df["car_name"] == car_name].sort_values("standard_ym").copy()

    if car_trend_df.empty:
        st.info("해당 차종의 등록 추이 데이터가 없습니다.")
    else:
        chart_data = car_trend_df.set_index("standard_ym")[["registration_count"]]
        chart_data.columns = ["등록 대수"]

        st.line_chart(chart_data, use_container_width=True)

        latest_count = car_trend_df.iloc[-1]["registration_count"]
        first_count = car_trend_df.iloc[0]["registration_count"]
        diff = latest_count - first_count

        m1, m2 = st.columns(2)
        with m1:
            st.metric("최근 월 등록 대수", f"{latest_count:,} 대")
        with m2:
            st.metric("기간 내 변동 폭", f"{diff:+,} 대")

# --- 📌 모델별 랭킹용 리뷰 팝업 (Dialog) ---
@st.dialog("📝 차량 상세 리뷰", width="large")
def show_review_dialog(car_name, logo_url, car_image_url, matched_reviews):
    c_logo, c_title, c_img = st.columns([1, 4, 3])

    with c_logo:
        if logo_url:
            st.image(logo_url, width=45)

    with c_title:
        st.markdown(f"### **{car_name}**")
        st.caption(f"등록된 실사용자 리뷰: **{len(matched_reviews)}개**")

    with c_img:
        if car_image_url:
            st.image(car_image_url, width=160)

    st.divider()

    if matched_reviews.empty:
        st.info(f"'{car_name}'에 대한 등록된 상세 리뷰가 없습니다.")
    else:
        for idx, row in matched_reviews.reset_index(drop=True).iterrows():
            st.markdown(f"**리뷰 #{idx + 1}**")

            performance = row.get("performance", "-")
            price = row.get("price", "-")
            issues = row.get("issues", "-")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"**🚀 주행/성능**\n\n{performance}")
            with c2:
                st.success(f"**💰 가격/가성비**\n\n{price}")
            with c3:
                st.warning(f"**⚠️ 단점/아쉬운 점**\n\n{issues}")

            if idx < len(matched_reviews) - 1:
                st.markdown("<hr style='margin: 12px 0; border: 0.5px solid #e2e8f0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 화면 뷰 함수들
# ---------------------------------------------------------

def home_view():
    section_title(
        "전국 자동차 등록 현황 대시보드 (Home)",
        "주요 통계 요약 및 월별 등록 추이, 차량 리뷰 검색 기능을 제공합니다.",
    )

    total_count = (
        int(registration_df["registration_count"].sum())
        if not registration_df.empty and "registration_count" in registration_df.columns
        else 0
    )
    manufacturer_count = (
        registration_df["manufacturer"].nunique()
        if not registration_df.empty and "manufacturer" in registration_df.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("전체 등록대수", f"{total_count:,}대")
    with c2:
        st.metric("제조사 수", f"{manufacturer_count}개")
    with c3:
        st.metric("FAQ 수", f"{len(faq_df)}건")

    st.divider()

    # --- 📌 2초 간격 랜덤 브랜드 로고 영역 ---
    st.markdown("### 🏆 주요 제조사 로고")

    shuffled_logos = list(LOGO_URL_MAP.items())
    random.shuffle(shuffled_logos)
    cols = st.columns(len(shuffled_logos))
    for idx, (brand, url) in enumerate(shuffled_logos):
        with cols[idx % len(cols)]:
            st.image(url, width=45)

    st.divider()

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### 📈 월별 총 등록 추이")
        if not registration_df.empty and "standard_ym" in registration_df.columns:
            month_df = (
                registration_df.groupby("standard_ym", as_index=False)["registration_count"]
                .sum()
                .sort_values("standard_ym")
            )
            st.line_chart(month_df.set_index("standard_ym"), use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with right_col:
        st.markdown("### 🔍 차량 리뷰 및 평가 검색")
        st.caption("리뷰 내용(성능, 문제점, 브랜드명 등)에 포함된 키워드를 입력해보세요.")

        review_keyword = st.text_input(
            "리뷰 검색어 입력",
            placeholder="예: 소음, 가속, 현대, 승차감",
            key="home_review_search",
        )

        if not review_keyword.strip():
            st.info("💡 검색어를 입력하시면 관련 차량 리뷰 목록이 표출됩니다.")
        else:
            if review_df.empty:
                st.info("연동된 리뷰 데이터가 없습니다.")
            else:
                mask = False
                for col in ["performance", "issues", "brand_name", "price"]:
                    if col in review_df.columns:
                        mask = mask | review_df[col].astype(str).str.contains(review_keyword, case=False, na=False)

                result_review = review_df[mask].copy()

                if result_review.empty:
                    st.warning(f"'{review_keyword}'에 대한 검색 결과가 없습니다.")
                else:
                    st.caption(f"총 **{len(result_review)}건**의 리뷰가 검색되었습니다.")

                    display_cols = ["logo", "brand_name", "performance", "price", "issues"]

                    event = st.dataframe(
                        result_review[display_cols],
                        use_container_width=True,
                        hide_index=True,
                        selection_mode="single-row",
                        on_select="rerun",
                        key="home_review_search_table",
                        column_config={
                            "logo": st.column_config.ImageColumn("로고", width="small"),
                            "brand_name": "브랜드",
                            "performance": "주행/성능",
                            "price": "가격/가성비",
                            "issues": "단점/아쉬운점",
                        },
                    )

                    selected_rows = event.selection.get("rows", [])
                    if selected_rows:
                        selected_idx = selected_rows[0]
                        selected_data = result_review.iloc[selected_idx]
                        model_id = selected_data["model_id"]

                        matched_model = model_ranking_df[model_ranking_df["model_id"] == model_id]

                        if not matched_model.empty:
                            car_name = matched_model.iloc[0]["car_name"]
                            car_image_url = matched_model.iloc[0]["car_image"]
                        else:
                            car_name = f"{selected_data['brand_name']} 차량"
                            car_image_url = DEFAULT_CAR_IMAGE

                        logo_url = selected_data["logo"]
                        matched_reviews = review_df[review_df["model_id"] == model_id]

                        show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)

    # 검색어를 입력하고 있을 때 타자 입력이 방해받거나 무한 루프가 끊기는 현상을 방지
    # 사용자가 검색 상자에 입력 중이 아닐 때만 2초 후 rerun 실행
    if not review_keyword.strip():
        time.sleep(2)
        st.rerun()

@st.dialog("📊 월별 등록 대수 추이 분석", width="large")
def show_registration_trend_dialog(car_name, manufacturer, logo_url, car_image_url, car_history_df):
    # 1. 팝업 헤더 영역 (로고, 차종명, 이미지)
    c_logo, c_title, c_img = st.columns([1, 4, 3])

    with c_logo:
        if logo_url:
            st.image(logo_url, width=45)

    with c_title:
        st.markdown(f"### **[{manufacturer}] {car_name}**")
        st.caption("월별 신규 등록 대수 변화 추이")

    with c_img:
        if car_image_url:
            st.image(car_image_url, width=150)

    st.divider()

    # 2. 데이터가 없는 경우 예외 처리
    if car_history_df.empty:
        st.info(f"'{car_name}' 모델에 대한 월별 등록 추이 데이터가 없습니다.")
        return

    # 3. 날짜순 정렬 (standard_ym 오름차순)
    trend_df = car_history_df.sort_values(by="standard_ym", ascending=True).copy()

    # 주요 요약 지표 (Metrics)
    total_count = trend_df["registration_count"].sum()
    avg_count = int(trend_df["registration_count"].mean())
    latest_count = trend_df.iloc[-1]["registration_count"]
    latest_month = trend_df.iloc[-1]["standard_ym"]

    m1, m2, m3 = st.columns(3)
    m1.metric("총 누적 등록 대수", f"{total_count:,} 대")
    m2.metric("월평균 등록 대수", f"{avg_count:,} 대")
    m3.metric(f"최근 등록 ({latest_month})", f"{latest_count:,} 대")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Plotly 선 그래프(Line Chart) 생성
    fig = px.line(
        trend_df,
        x="standard_ym",
        y="registration_count",
        markers=True,
        title=f"📈 {car_name} 월별 등록 대수 추이",
        labels={"standard_ym": "등록 월", "registration_count": "등록 대수(대)"},
        text="registration_count"
    )

    # 그래프 스타일링
    fig.update_traces(
        line=dict(color="#2563eb", width=3),
        marker=dict(size=8, color="#1e40af"),
        textposition="top center",
        texttemplate="%{text:,.0f}대"
    )

    fig.update_layout(
        xaxis_type="category",  # 월별 라벨 깔끔하게 표시
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)


def registration_status_view():
    section_title("자동차 등록 현황 조회", "월별로 등록된 자동차 현황입니다. 행을 클릭하면 월별 등록 추이 그래프를 확인할 수 있습니다.")

    if registration_df.empty:
        st.warning("등록 현황 데이터가 존재하지 않습니다.")
        return

    # 1. 10개씩 페이징 처리
    page_size = 10
    total_items = len(registration_df)
    total_pages = max((total_items + page_size - 1) // page_size, 1)

    c_page, c_info = st.columns([3, 7])
    with c_page:
        page_number = st.number_input(
            f"페이지 선택 (총 {total_pages} 페이지)", 
            min_value=1, 
            max_value=total_pages, 
            value=1,
            step=1,
            key="reg_page_number"
        )
    with c_info:
        st.markdown(f"<br><span style='color: #64748b; font-size: 0.9rem;'>총 <b>{total_items:,}</b>건 중 {((page_number-1)*page_size)+1} ~ {min(page_number*page_size, total_items)}번째 항목 표출</span>", unsafe_allow_html=True)

    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size

    # 📌 클릭 인덱스 오작동 방지를 위한 reset_index
    page_df = registration_df.iloc[start_idx:end_idx].copy().reset_index(drop=True)

    display_cols = ["logo", "manufacturer", "car_model_type", "registration_count", "standard_ym"]
    existing_cols = [col for col in display_cols if col in page_df.columns]

    # 2. 10개 행 출력 및 클릭 이벤트 감지
    event = st.dataframe(
        page_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="reg_status_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "manufacturer": "제조사",
            "car_model_type": "차종/모델",
            "registration_count": st.column_config.NumberColumn("등록개수", format="%d 대"),
            "standard_ym": "등록 월(Month)",
        }
    )

    # 3. 행 선택 시 월별 등록 추이 그래프 팝업 출력
    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_row = page_df.iloc[selected_idx]

        car_name = selected_row["car_model_type"]
        manufacturer = selected_row["manufacturer"]
        logo_url = selected_row.get("logo", "")
        car_image_url = selected_row.get("car_image", "")

        # 📌 전체 registration_df에서 해당 차종/모델의 월별 이력 데이터 전체를 추출
        car_history_df = registration_df[registration_df["car_model_type"] == car_name]

        # 팝업 호출
        show_registration_trend_dialog(car_name, manufacturer, logo_url, car_image_url, car_history_df)

# --- 📌 브랜드별 랭킹 뷰 ---
def brand_ranking_view():
    section_title("브랜드별 랭킹", "월별 국산/수입 브랜드 등록 순위 현황입니다. 클릭 시 브랜드 등록 추이를 확인할 수 있습니다.")

    # 1. 데이터 검증 (car_brand_rank 또는 관련 데이터프레임 확인)
    target_df = brand_ranking_df if 'brand_ranking_df' in globals() else registration_df

    if target_df.empty:
        st.warning("브랜드 랭킹 데이터가 존재하지 않습니다.")
        return

    # 2. 필터링 (필요시)
    target_ym, target_type = render_filter(target_df, show_type_filter=True, key_prefix="brand_rank")

    filtered_df = target_df.copy()
    if target_ym and "standard_ym" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["standard_ym"] == target_ym]
    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    if filtered_df.empty:
        st.info("선택한 조건에 해당하는 브랜드 랭킹 데이터가 없습니다.")
        return

    # 인덱스 초기화
    display_df = filtered_df.reset_index(drop=True)

    # 3. 테이블 출력용 컬럼 설정
    display_cols = ["logo", "brand_name", "registration_count", "mom_increase"]
    existing_cols = [c for c in display_cols if c in display_df.columns]

    event = st.dataframe(
        display_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="brand_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "brand_name": "브랜드명",
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d 대"),
            "mom_increase": st.column_config.NumberColumn("전월 대비", format="%+d 대"),
        }
    )

    # 4. 행 클릭 시 처리
    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_data = display_df.iloc[selected_idx]

        brand_name = selected_data.get("brand_name", "브랜드")
        logo_url = selected_data.get("logo", "")

        # 해당 브랜드의 전체 월별 데이터 추출
        brand_history_df = target_df[target_df["brand_name"] == brand_name] if "brand_name" in target_df.columns else pd.DataFrame()

        # 등록 추이 팝업 호출 (이전에 만든 show_registration_trend_dialog 활용)
        show_registration_trend_dialog(brand_name, "브랜드", logo_url, "", brand_history_df)

def model_ranking_view():
    section_title("모델별 랭킹", "월별 차량 모델별 등록순위 현황입니다. 클릭 시 리뷰를 확인할 수 있습니다.")

    if model_ranking_df.empty:
        st.warning("모델 랭킹 데이터가 존재하지 않습니다.")
        return

    target_ym, target_type = render_filter(model_ranking_df, show_type_filter=True, key_prefix="model_rank")

    filtered_df = model_ranking_df.copy()
    if target_ym:
        filtered_df = filtered_df[filtered_df["standard_ym"] == target_ym]
    if target_type != "전체":
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    if filtered_df.empty:
        st.info("선택한 조건에 해당하는 모델 랭킹 데이터가 없습니다.")
        return

    # 📌 핵심 수정 1: 클릭 인덱스와 데이터프레임 인덱스 일치를 위해 reset_index 수행
    display_df = filtered_df.reset_index(drop=True)

    display_cols = ["logo", "car_name", "brand_name", "fuel_type", "registration_count", "mom_increase"]
    existing_cols = [c for c in display_cols if c in display_df.columns]

    event = st.dataframe(
        display_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="model_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "car_name": "차량명",
            "brand_name": "브랜드",
            "fuel_type": "연료",
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d 대"),
            "mom_increase": st.column_config.NumberColumn("전월 대비", format="%+d 대"),
        }
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]

        # 📌 핵심 수정 2: reset_index가 적용된 display_df에서 정확한 행을 가져옴
        selected_data = display_df.iloc[selected_idx]

        model_id = selected_data.get("model_id")
        car_name = selected_data.get("car_name", "차량 정보 없음")
        logo_url = selected_data.get("logo", DEFAULT_LOGO)
        car_image_url = selected_data.get("car_image", DEFAULT_CAR_IMAGE)

        # 📌 핵심 수정 3: review_df 매핑 (model_id 또는 brand_name 매핑)
        matched_reviews = review_df[review_df["model_id"] == model_id] if "model_id" in review_df.columns else pd.DataFrame()

        show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)

def faq_view():
    section_title("자주 묻는 질문 (FAQ)", "차량 등록 및 절차와 관련된 주요 FAQ 목록입니다.")

    if faq_df.empty:
        st.info("등록된 FAQ 데이터가 없습니다.")
        return

    for _, row in faq_df.iterrows():
        with st.expander(f"❓ {row['question']}"):
            st.write(row['answer'])

# ---------------------------------------------------------
# Tab Routing
# ---------------------------------------------------------
if active_tab == "Home":
    home_view()
elif active_tab == "자동차 등록 현황":
    registration_status_view()
elif active_tab == "브랜드별 랭킹":
    brand_ranking_view()
elif active_tab == "모델별 랭킹":
    model_ranking_view()
elif active_tab == "FAQ":
    faq_view()
