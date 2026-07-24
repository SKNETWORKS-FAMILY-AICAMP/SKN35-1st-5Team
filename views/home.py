import streamlit as st

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

def home_view(registration_df, brand_ranking_df, model_ranking_df, review_df, faq_df, LOGO_URL_MAP):
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">전국 자동차 등록 현황 대시보드 (Home)</h1>
            <div class="subtext">주요 통계 요약 및 월별 등록 추이, 차량 리뷰 검색 기능을 제공합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_count = int(registration_df["registration_count"].sum()) if not registration_df.empty and "registration_count" in registration_df.columns else 0
    manufacturer_count = registration_df["manufacturer"].nunique() if not registration_df.empty and "manufacturer" in registration_df.columns else 0

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
        st.caption("리뷰 내용(성능, 문제점, 브랜드명 등)에 포함된 키워드를 입력해보세요.")
        review_keyword = st.text_input("리뷰 검색어 입력", placeholder="예: 소음, 가속, 현대, 승차감", key="home_review_search")

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
                    st.caption(f"총 **{len(result_review)}건**의 리뷰가 검색되었습니다. (행을 클릭하면 상세 리뷰 팝업이 뜹니다)")
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
                            car_image_url = ""
                        logo_url = selected_data["logo"]
                        matched_reviews = review_df[review_df["model_id"] == model_id]
                        show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)