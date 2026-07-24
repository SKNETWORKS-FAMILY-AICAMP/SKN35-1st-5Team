
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# Page Config Configuration
st.set_page_config(
    page_title="자동차 등록 현황 통합 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 브랜드 로고 URL 매핑 딕셔너리
LOGO_URL_MAP = {
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

DEFAULT_LOGO = "https://cdn.simpleicons.org/simpleicons"

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
        .review-card {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Mock 데이터 생성 함수 ---
@st.cache_data
def load_registration_data():
    data = [
        {"regist_id": 1, "manufacturer_type": "국산", "manufacturer": "현대", "car_model_type": "승용", "fuel_type": "가솔린", "registration_count": 12500, "standard_ym": "2024-01"},
        {"regist_id": 2, "manufacturer_type": "국산", "manufacturer": "기아", "car_model_type": "SUV", "fuel_type": "하이브리드", "registration_count": 14200, "standard_ym": "2024-01"},
        {"regist_id": 3, "manufacturer_type": "수입", "manufacturer": "BMW", "car_model_type": "승용", "fuel_type": "가솔린", "registration_count": 6100, "standard_ym": "2024-01"},
        {"regist_id": 4, "manufacturer_type": "수입", "manufacturer": "Mercedes-Benz", "car_model_type": "승용", "fuel_type": "디젤", "registration_count": 5300, "standard_ym": "2024-01"},
        {"regist_id": 5, "manufacturer_type": "국산", "manufacturer": "현대", "car_model_type": "승용", "fuel_type": "전기", "registration_count": 3200, "standard_ym": "2024-02"},
        {"regist_id": 6, "manufacturer_type": "국산", "manufacturer": "기아", "car_model_type": "SUV", "fuel_type": "하이브리드", "registration_count": 15800, "standard_ym": "2024-02"},
        {"regist_id": 7, "manufacturer_type": "수입", "manufacturer": "Tesla", "car_model_type": "승용", "fuel_type": "전기", "registration_count": 4800, "standard_ym": "2024-02"},
        {"regist_id": 8, "manufacturer_type": "국산", "manufacturer": "제네시스", "car_model_type": "승용", "fuel_type": "가솔린", "registration_count": 8900, "standard_ym": "2024-03"},
        {"regist_id": 9, "manufacturer_type": "수입", "manufacturer": "BMW", "car_model_type": "SUV", "fuel_type": "가솔린", "registration_count": 6700, "standard_ym": "2024-03"},
    ]
    df = pd.DataFrame(data)
    df["logo"] = df["manufacturer"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data
def load_brand_ranking_data():
    data = [
        {"brand_id": 10, "regist_id": 10, "manufacturer_type": "국산", "standard_ym": "2024-02", "brand_name": "기아", "registration_count": 44000, "mom_increase": 3.0},
        {"brand_id": 11, "regist_id": 11, "manufacturer_type": "국산", "standard_ym": "2024-02", "brand_name": "현대", "registration_count": 40000, "mom_increase": 1.5},
        {"brand_id": 12, "regist_id": 12, "manufacturer_type": "수입", "standard_ym": "2024-02", "brand_name": "BMW", "registration_count": 6100, "mom_increase": 2.2},
        {"brand_id": 13, "regist_id": 13, "manufacturer_type": "수입", "standard_ym": "2024-02", "brand_name": "Mercedes-Benz", "registration_count": 5800, "mom_increase": -0.5},
        {"brand_id": 1, "regist_id": 1, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "기아", "registration_count": 48200, "mom_increase": 5.2},
        {"brand_id": 2, "regist_id": 2, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "현대", "registration_count": 41500, "mom_increase": 2.1},
        {"brand_id": 3, "regist_id": 3, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "제네시스", "registration_count": 12800, "mom_increase": -1.4},
        {"brand_id": 4, "regist_id": 4, "manufacturer_type": "수입", "standard_ym": "2024-03", "brand_name": "BMW", "registration_count": 6700, "mom_increase": 9.8},
        {"brand_id": 5, "regist_id": 5, "manufacturer_type": "수입", "standard_ym": "2024-03", "brand_name": "Mercedes-Benz", "registration_count": 5900, "mom_increase": 1.1},
        {"brand_id": 6, "regist_id": 6, "manufacturer_type": "수입", "standard_ym": "2024-03", "brand_name": "Tesla", "registration_count": 4800, "mom_increase": 45.2},
    ]
    df = pd.DataFrame(data)
    df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data
def load_model_ranking_data():
    data = [
        {"model_id": 101, "regist_id": 10, "manufacturer_type": "국산", "standard_ym": "2024-02", "brand_name": "기아", "car_name": "쏘렌토", "fuel_type": "하이브리드", "registration_count": 8100, "mom_increase": 2.0},
        {"model_id": 104, "regist_id": 11, "manufacturer_type": "국산", "standard_ym": "2024-02", "brand_name": "현대", "car_name": "그랜저", "fuel_type": "가솔린", "registration_count": 6800, "mom_increase": 1.1},
        {"model_id": 101, "regist_id": 1, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "기아", "car_name": "쏘렌토", "fuel_type": "하이브리드", "registration_count": 8900, "mom_increase": 4.5},
        {"model_id": 102, "regist_id": 2, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "현대", "car_name": "싼타페", "fuel_type": "하이브리드", "registration_count": 7800, "mom_increase": 3.1},
        {"model_id": 103, "regist_id": 3, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "기아", "car_name": "카니발", "fuel_type": "가솔린", "registration_count": 7200, "mom_increase": -0.8},
        {"model_id": 104, "regist_id": 4, "manufacturer_type": "국산", "standard_ym": "2024-03", "brand_name": "현대", "car_name": "그랜저", "fuel_type": "가솔린", "registration_count": 6500, "mom_increase": -2.3},
        {"model_id": 105, "regist_id": 5, "manufacturer_type": "수입", "standard_ym": "2024-03", "brand_name": "Tesla", "car_name": "Model Y", "fuel_type": "전기", "registration_count": 4200, "mom_increase": 38.5},
        {"model_id": 106, "regist_id": 6, "manufacturer_type": "수입", "standard_ym": "2024-03", "brand_name": "BMW", "car_name": "5 시리즈", "fuel_type": "가솔린", "registration_count": 2100, "mom_increase": 12.4},
    ]
    df = pd.DataFrame(data)
    df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data
def load_review_data():
    # 📌 총 10개의 상세 리뷰 데이터
    data = [
        {"review_id": 1, "model_id": 101, "regist_id": 1, "overall_rating": 4.8, "performance": "연비가 훌륭하고 주행 시 소음이 거의 없습니다.", "price": "옵션 추가 시 다소 비쌈", "issues": "인포테인먼트 시스템 잔오류", "brand_name": "기아"},
        {"review_id": 2, "model_id": 101, "regist_id": 1, "overall_rating": 4.7, "performance": "하이브리드 모드 전환 시 이질감이 거의 없고 부드럽습니다.", "price": "적정 수준", "issues": "출고 대기 기간이 너무 깁니다.", "brand_name": "기아"},
        {"review_id": 3, "model_id": 101, "regist_id": 1, "overall_rating": 4.9, "performance": "실내 공간이 패밀리카로 최고입니다. 2열 승차감이 우수합니다.", "price": "가성비 무난함", "issues": "순정 타이어 마모가 다소 빠릅니다.", "brand_name": "기아"},
        {"review_id": 4, "model_id": 102, "regist_id": 2, "overall_rating": 4.5, "performance": "실내 공간이 매우 넓고 가속력이 우수합니다.", "price": "적정 가격대", "issues": "후면 디자인 호불호 및 풍절음", "brand_name": "현대"},
        {"review_id": 5, "model_id": 102, "regist_id": 2, "overall_rating": 4.4, "performance": "고속 도로 안정성이 탁월하고 HDA2 기능이 편리합니다.", "price": "옵션가가 살짝 부담됨", "issues": "C필러 쪽 디자인 세차가 다소 불편함", "brand_name": "현대"},
        {"review_id": 6, "model_id": 103, "regist_id": 3, "overall_rating": 4.6, "performance": "패밀리카로 최적, 승차감이 부드럽습니다.", "price": "가성비 좋음", "issues": "차체가 커서 주차 시 불편함", "brand_name": "기아"},
        {"review_id": 7, "model_id": 104, "regist_id": 4, "overall_rating": 4.7, "performance": "승차감이 정숙하며 정체 구간 차선 유지 보조가 탁월합니다.", "price": "높은 편", "issues": "핸들 버튼 터치 감도 미흡", "brand_name": "현대"},
        {"review_id": 8, "model_id": 104, "regist_id": 4, "overall_rating": 4.8, "performance": "프리미엄 세단다운 정숙성과 그립감이 인상적입니다.", "price": "대형 세단 치고는 합리적", "issues": "트렁크 깊이가 약간 아쉽습니다.", "brand_name": "현대"},
        {"review_id": 9, "model_id": 105, "regist_id": 5, "overall_rating": 4.3, "performance": "초반 가속 응답성이 엄청나고 오토파일럿이 매우 유용합니다.", "price": "보조금 미적용 시 부담", "issues": "승차감이 다소 단단함, 단차 문제", "brand_name": "Tesla"},
        {"review_id": 10, "model_id": 106, "regist_id": 6, "overall_rating": 4.7, "performance": "고속 안정성이 뛰어나고 핸들링 정밀도가 좋습니다.", "price": "프로모션 적용 시 양호", "issues": "뒷좌석 공간이 다소 협소", "brand_name": "BMW"},
    ]
    df = pd.DataFrame(data)
    df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data
def load_faq_data():
    data = [
        {"faq_id": 1, "question": "신차 구매 후 등록 기한은 어떻게 되나요?", "answer": "임시운행허가기간(통상 10일) 이내에 관할 구청 또는 차량등록사업소에 등록해야 합니다."},
        {"faq_id": 2, "question": "자동차 명의 변경 시 준비 서류는 무엇인가요?", "answer": "양도인/양수인 신분증, 자동차양도증명서, 이전등록신청서, 자동차보험 가입증명서가 필요합니다."},
        {"faq_id": 3, "question": "자동차 등록 세금(취득세) 계산 기준은 어떻게 되나요?", "answer": "승용차 기준으로 차량 공급가액의 7%가 취득세로 부과되며, 경차는 4% (감면혜택 적용) 입니다."},
        {"faq_id": 4, "question": "전기차 구매 시 받는 혜택은 어떤 것들이 있나요?", "answer": "국고 및 지자체 보조금 지원, 취득세 감면(최대 140만원), 공영주차장 및 고속도로 통행료 50% 할인 혜택이 있습니다."},
    ]
    return pd.DataFrame(data)

# 데이터 로드
registration_df = load_registration_data()
brand_ranking_df = load_brand_ranking_data()
model_ranking_df = load_model_ranking_data()
review_df = load_review_data()
faq_df = load_faq_data()

# --- 사이드바 메뉴 구성 ---
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

# --- 공통 연/월 및 국산/수입 선택 필터 컴포넌트 ---
def render_filter(df, show_type_filter=False, key_prefix="filter"):
    if df.empty or "standard_ym" not in df.columns:
        return None, None

    available_yms = sorted(df["standard_ym"].unique(), reverse=True)
    years = sorted(list(set([ym.split("-")[0] for ym in available_yms])), reverse=True)

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

# 📌 새 창(모달/Dialog) 팝업 함수 정의
@st.dialog("📝 차량 상세 리뷰", width="large")
def show_review_modal(car_name, model_id, logo_url):
    c1, c2 = st.columns([8, 2])
    with c1:
        st.subheader(f"[{car_name}] 사용자 상세 리뷰")
    with c2:
        if logo_url:
            st.image(logo_url, width=60)

    st.divider()

    matched_reviews = review_df[review_df["model_id"] == model_id] if not review_df.empty else pd.DataFrame()

    if matched_reviews.empty:
        st.info(f"등록된 '{car_name}'의 상세 리뷰가 없습니다.")
    else:
        st.write(f"총 **{len(matched_reviews)}개**의 리뷰가 등록되어 있습니다.")

        # 리뷰 리스트 출력
        for idx, row in matched_reviews.reset_index().iterrows():
            rating = row.get("overall_rating", "N/A")
            performance = row.get("performance", "-")
            price = row.get("price", "-")
            issues = row.get("issues", "-")

            st.markdown(
                f"""
                <div class="review-card">
                    <div style="font-weight: bold; font-size: 1.05rem; margin-bottom: 6px; color: #1e293b;">
                        리뷰 #{idx + 1} &nbsp;|&nbsp; ⭐ 평점: <span style="color: #f59e0b;">{rating}</span> / 5.0
                    </div>
                    <div style="margin-bottom: 4px;">🚀 <b>주행/성능:</b> {performance}</div>
                    <div style="margin-bottom: 4px;">💰 <b>가격/가성비:</b> {price}</div>
                    <div>⚠️ <b>단점/아쉬운 점:</b> {issues}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# --- 화면 뷰 함수들 ---
def home_view():
    section_title("전국 자동차 등록 현황 대시보드 (Home)", "주요 통계 요약 및 월별 등록 추이, 차량 리뷰 검색 기능을 제공합니다.")

    total_count = int(registration_df["registration_count"].sum()) if not registration_df.empty and "registration_count" in registration_df.columns else 0
    manufacturer_count = registration_df['manufacturer'].nunique() if not registration_df.empty and "manufacturer" in registration_df.columns else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("전체 등록대수", f"{total_count:,}대")
    with c2:
        st.metric("제조사 수", f"{manufacturer_count}개")
    with c3:
        st.metric("FAQ 수", f"{len(faq_df)}건")

    st.divider()

    st.markdown("### 🏆 인기 제조사 로고")
    cols = st.columns(len(LOGO_URL_MAP))
    for idx, (brand, url) in enumerate(LOGO_URL_MAP.items()):
        with cols[idx % len(cols)]:
            st.image(url, width=45)

    st.divider()

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### 📈 월별 총 등록 추이")
        if not registration_df.empty and "standard_ym" in registration_df.columns:
            month_df = registration_df.groupby("standard_ym", as_index=False)["registration_count"].sum().sort_values("standard_ym")
            st.line_chart(month_df.set_index("standard_ym"), use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with right_col:
        st.markdown("### 🔍 차량 리뷰 및 평가 검색")
        st.caption("리뷰 내용(성능, 문제점, 브랜드명 등)에 포함된 단어로 검색해 보세요.")

        review_keyword = st.text_input("리뷰 검색어 입력", placeholder="예: 소음, 가속, 현대, 승차감", key="home_review_search")

        if review_df.empty:
            st.info("연동된 리뷰 데이터가 없습니다.")
        else:
            result_review = review_df.copy()
            if review_keyword:
                mask = False
                for col in ["performance", "issues", "brand_name"]:
                    if col in result_review.columns:
                        mask = mask | result_review[col].astype(str).str.contains(review_keyword, case=False, na=False)
                result_review = result_review[mask]

            st.caption(f"총 {len(result_review)}건의 리뷰가 검색되었습니다.")

            if result_review.empty:
                st.warning("검색 결과와 일치하는 리뷰 내용이 없습니다.")
            else:
                cols_order = ["logo"] + [col for col in result_review.columns if col != "logo"]
                st.dataframe(
                    result_review[cols_order], 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "logo": st.column_config.ImageColumn("로고", width="small")
                    }
                )

def registration_status_view():
    section_title("자동차 등록 현황 조회", "수입차 및 국산차 구분, 연료별 자동차 등록 통계 데이터를 상세히 필터링하고 확인합니다.")
    if registration_df.empty:
        st.warning("등록 현황 데이터가 존재하지 않습니다.")
        return

    cols_order = ["logo"] + [col for col in registration_df.columns if col != "logo"]
    st.dataframe(
        registration_df[cols_order], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small")
        }
    )

def brand_ranking_view():
    section_title("브랜드별 랭킹 순위", "조회하고자 하는 연월 조건을 선택하여 브랜드 등록 순위를 확인합니다.")

    if brand_ranking_df.empty:
        st.warning("브랜드 랭킹 데이터가 존재하지 않습니다.")
        return

    selected_ym, _ = render_filter(brand_ranking_df, show_type_filter=False, key_prefix="brand_rank")

    filtered_df = brand_ranking_df.copy()
    if selected_ym:
        filtered_df = filtered_df[filtered_df["standard_ym"] == selected_ym]

    st.markdown(f"#### 📊 **{selected_ym}** 등록 기준 브랜드 순위")
    st.divider()

    display_cols = ["logo", "brand_name", "registration_count", "mom_increase"]

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### 🇰🇷 국산차 브랜드 랭킹")
        domestic_df = filtered_df[filtered_df["manufacturer_type"] == "국산"].copy()

        if domestic_df.empty:
            st.info(f"선택한 연월({selected_ym})의 국산차 브랜드 데이터가 없습니다.")
        else:
            st.dataframe(
                domestic_df[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "logo": st.column_config.ImageColumn("로고", width="small"),
                    "brand_name": "브랜드명",
                    "registration_count": st.column_config.NumberColumn("등록대수", format="%d대"),
                    "mom_increase": st.column_config.NumberColumn("전월대비(%)", format="%.1f%%"),
                }
            )

    with right_col:
        st.markdown("### 🌐 수입차 브랜드 랭킹")
        imported_df = filtered_df[filtered_df["manufacturer_type"] == "수입"].copy()

        if imported_df.empty:
            st.info(f"선택한 연월({selected_ym})의 수입차 브랜드 데이터가 없습니다.")
        else:
            st.dataframe(
                imported_df[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "logo": st.column_config.ImageColumn("로고", width="small"),
                    "brand_name": "브랜드명",
                    "registration_count": st.column_config.NumberColumn("등록대수", format="%d대"),
                    "mom_increase": st.column_config.NumberColumn("전월대비(%)", format="%.1f%%"),
                }
            )

def model_ranking_view():
    section_title("모델별 랭킹 순위 및 리뷰", "조회하려는 연월 및 국산/수입 구분을 선택한 후 차종별 등록 순위를 확인하세요.")
    if model_ranking_df.empty:
        st.warning("모델별 랭킹 데이터가 존재하지 않습니다.")
        return

    selected_ym, selected_type = render_filter(model_ranking_df, show_type_filter=True, key_prefix="model_rank")

    filtered_df = model_ranking_df.copy()

    if selected_ym:
        filtered_df = filtered_df[filtered_df["standard_ym"] == selected_ym]

    if selected_type != "전체":
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == selected_type]

    type_label = f"[{selected_type}] " if selected_type != "전체" else ""
    st.markdown(f"### 📋 **{selected_ym}** {type_label}모델별 등록 랭킹 (행을 선택하면 팝업으로 리뷰가 표시됩니다)")

    if filtered_df.empty:
        st.info(f"선택한 조건({selected_ym}, {selected_type})에 일치하는 모델 데이터가 존재하지 않습니다.")
        return

    cols_order = ["logo", "brand_name", "car_name", "fuel_type", "registration_count", "mom_increase"]

    event = st.dataframe(
        filtered_df[cols_order],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="model_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "brand_name": "브랜드명",
            "car_name": "모델명",
            "fuel_type": "연료",
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d대"),
            "mom_increase": st.column_config.NumberColumn("전월대비(%)", format="%.1f%%"),
        }
    )

    # 행 선택 시 새 창(Dialog 팝업) 띄우기
    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_index = selected_rows[0]
        selected_row_data = filtered_df.iloc[selected_index]

        car_name = selected_row_data.get("car_name")
        model_id = selected_row_data.get("model_id")
        logo_url = selected_row_data.get("logo")

        # 팝업 호출
        show_review_modal(car_name, model_id, logo_url)

def faq_view():
    section_title("자주 하는 질문 (FAQ)", "차량 등록 관련 궁금한 점을 검색해 보세요.")

    if faq_df.empty:
        st.warning("FAQ 데이터가 존재하지 않습니다.")
        return

    keyword = st.text_input("검색어 입력", placeholder="예: 신차, 명의, 취득세")

    result_faq = faq_df.copy()

    if keyword:
        matched = (
            result_faq["question"].str.contains(keyword, case=False, na=False) | 
            result_faq["answer"].str.contains(keyword, case=False, na=False)
        )
        result_faq = result_faq[matched]

    st.caption(f"총 {len(result_faq)}건의 FAQ가 검색되었습니다.")

    if result_faq.empty:
        st.info("조건에 일치하는 FAQ가 없습니다.")
        return

    for _, faq in result_faq.iterrows():
        with st.expander(f"Q. {faq['question']}"):
            st.write(faq["answer"])

# --- 라우팅 ---
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
