import streamlit as st
import pandas as pd
import random
import time
from sqlalchemy import text
from db import get_engine

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
    "폴스타" : "https://file.carisyou.com/upload/2019/02/28/FILE_201902280235576730.png",
}

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

@st.cache_data(ttl=3600)
def load_registration_data():
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
def load_model_ranking_data():
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
           '휘발유/디젤/전기' AS fuel_type
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
    engine = get_engine()
    query = """
    SELECT r.review_id, 
           r.model_id, 
           r.regist_id, 
           r.brand_name_review AS brand_name,
           t.total_score AS overall_rating, 
           t.total_review_content AS performance, 
           t.domain_type AS price, 
           t.total_review_title AS issues
    FROM review r
    LEFT JOIN total_review t ON r.review_id = t.review_id2
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df

@st.cache_data(ttl=3600)
def load_review_model_match_data():
    engine = get_engine()
    query = """
    SELECT DISTINCT
    r.review_id,
    r.brand_name_review AS 리뷰브랜드명,
    cm.model_id,
    cm.brand_name AS 모델별브랜드명,
    cr.model_name AS 자동차등록제조사
FROM
    review r
LEFT JOIN 
    car_model_ranking cm 
    ON REPLACE(r.brand_name_review, ' ', '') LIKE CONCAT('%', REPLACE(cm.brand_name, ' ', ''), '%')
    OR REPLACE(cm.brand_name, ' ', '') LIKE CONCAT('%', REPLACE(r.brand_name_review, ' ', ''), '%')
LEFT JOIN
    car_registration cr
    ON REPLACE(r.brand_name_review, ' ', '') LIKE CONCAT('%', REPLACE(cr.model_name, ' ', ''), '%')
    OR REPLACE(cr.model_name, ' ', '') LIKE CONCAT('%', REPLACE(r.brand_name_review, ' ', ''), '%');
    """
    return pd.read_sql(text(query), con=engine)

@st.cache_data(ttl=3600)
def load_faq_data():
    engine = get_engine()
    query = "SELECT faq_id, question, answer FROM faq ORDER BY faq_id ASC"
    return pd.read_sql(query, con=engine)

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
                st.info(f"**🚀 리뷰 내용**\n\n{performance}")
            with c2:
                st.success(f"**💰 도메인 유형**\n\n{price}")
            with c3:
                st.warning(f"**⚠️ 제목**\n\n{issues}")
                
            if idx < len(matched_reviews) - 1:
                st.markdown("<hr style='margin: 12px 0; border: 0.5px solid #e2e8f0;'>", unsafe_allow_html=True)

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

def home_view():
    registration_df = load_registration_data()
    model_ranking_df = load_model_ranking_data()
    review_df = load_review_data()
    faq_df = load_faq_data()

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
        st.caption("리뷰 내용(제목, 내용 등)에 포함된 키워드를 입력해보세요.")

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

                    display_cols = ["logo", "brand_name", "performance", "issues"]

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
                            "performance": "리뷰 내용",
                            "issues": "제목",
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

    if not review_keyword.strip():
        time.sleep(2)
        st.rerun()