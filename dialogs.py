import streamlit as st
import plotly.express as px


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
        text="registration_count",
    )

    # 그래프 스타일링
    fig.update_traces(
        line=dict(color="#2563eb", width=3),
        marker=dict(size=8, color="#1e40af"),
        textposition="top center",
        texttemplate="%{text:,.0f}대",
    )

    fig.update_layout(
        xaxis_type="category",  # 월별 라벨 깔끔하게 표시
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)
<<<<<<< Updated upstream
=======


def _render_star_rating(score, max_score=5.0):
    """0.5점 단위 실수 평점을 별 아이콘 바(HTML)로 변환합니다."""
    try:
        score = float(score)
    except (TypeError, ValueError):
        return ""

    score = max(0.0, min(max_score, score))
    percent = (score / max_score) * 100

    return f"""
    <div style="display: flex; align-items: center; gap: 6px; margin: 4px 0 10px 0;">
        <div style="position: relative; display: inline-block; font-size: 1.15rem; line-height: 1; letter-spacing: 2px;">
            <div style="color: #d1d5db;">★★★★★</div>
            <div style="position: absolute; top: 0; left: 0; width: {percent}%; overflow: hidden; white-space: nowrap; color: #f59e0b;">★★★★★</div>
        </div>
        <span style="font-weight: bold; color: #4b5563;">{score:.1f} / {max_score:.1f}</span>
    </div>
    """


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

            star_html = _render_star_rating(row.get("overall_rating"))
            if star_html:
                st.markdown(star_html, unsafe_allow_html=True)

            performance = row.get("performance", "-")
            issues = row.get("issues", "-")

            # --- 상하 구조로 변경 (제목 -> 내용 순서) ---
            st.warning(f"**⚠️ 제목**\n\n{issues}")
            st.info(f"**🚀 리뷰 내용**\n\n{performance}")
            # ---------------------------------------------

            if idx < len(matched_reviews) - 1:
                st.markdown("<hr style='margin: 12px 0; border: 0.5px solid #e2e8f0;'>", unsafe_allow_html=True)


@st.dialog("📊 브랜드 분석 및 모델별 순위", width="large")
def show_brand_trend_dialog(brand_name, logo_url, brand_history_df):
    # 상단 브랜드 정보 표시
    c_logo, c_title = st.columns([1, 6])
    with c_logo:
        if logo_url:
            st.image(logo_url, width=45)
    with c_title:
        st.markdown(f"### **{brand_name}**")
        st.caption("브랜드 전체 월별 등록 추이 및 소속 모델별 랭킹 (차량 이미지를 누르면 해당 차량의 추이로 변경됩니다)")

    st.divider()

    if brand_history_df.empty:
        st.info(f"'{brand_name}' 브랜드의 등록 추이 데이터가 없습니다.")
        return

    # 세션 상태를 활용하여 현재 그래프에 표시할 대상 관리 (브랜드 전체 vs 특정 모델)
    state_key_target = f"trend_target_{brand_name}"
    if state_key_target not in st.session_state:
        st.session_state[state_key_target] = "BRAND_TOTAL"

    # 전체 등록 데이터 가져오기 (소속 모델별 추이 확인용)
    reg_df = load_registration_data()
    # 해당 브랜드에 속하는 모델 데이터 필터링 (manufacturer 또는 company_name 기준)
    brand_models_df = reg_df[reg_df["manufacturer"] == brand_name].copy()

    # 좌우 레이아웃 분할 (좌측: 그래프, 우측: 소속 모델 이미지 랭킹)
    left_chart_col, right_models_col = st.columns([7, 3], gap="medium")

    with right_models_col:
        st.markdown("#### 🚗 소속 모델 랭킹")
        st.caption("클릭시 좌측 그래프가 변경됩니다.")

        if brand_models_df.empty:
            st.info("등록된 소속 모델 데이터가 없습니다.")
        else:
            # 모델별 누적 등록대수 기준으로 정렬하여 상위 모델 추출
            model_ranked = (
                brand_models_df.groupby("car_model_type", as_index=False)["registration_count"]
                .sum()
                .sort_values(by="registration_count", ascending=False)
                .reset_index(drop=True)
            )

            # 버튼 초기화용 선택 버튼
            if st.button("🔄 브랜드 전체 보기로 복구", use_container_width=True, key=f"btn_reset_{brand_name}"):
                st.session_state[state_key_target] = "BRAND_TOTAL"
                st.rerun()

            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

            # 스크롤 영역 구현을 위한 container
            with st.container(height=380):
                for idx, row in model_ranked.iterrows():
                    m_name = row["car_model_type"]
                    m_count = row["registration_count"]
                    # 이미지 매핑 (없으면 기본 이미지)
                    m_img = CAR_IMAGE_URL_MAP.get(m_name, DEFAULT_CAR_IMAGE)

                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if m_img:
                            st.image(m_img, width=70)
                        else:
                            st.markdown("📷 이미지 없음")
                    with col_txt:
                        st.markdown(f"**{idx+1}위 {m_name}**")
                        st.caption(f"{m_count:,} 대")
                        if st.button("선택", key=f"select_model_{brand_name}_{idx}"):
                            st.session_state[state_key_target] = m_name
                            st.rerun()
                    st.markdown("<hr style='margin: 4px 0; border: 0.3px solid #f1f5f9;'>", unsafe_allow_html=True)

    with left_chart_col:
        current_target = st.session_state.get(state_key_target, "BRAND_TOTAL")

        if current_target == "BRAND_TOTAL":
            # 브랜드 전체 월별 추이
            trend_df = (
                brand_history_df.groupby("standard_ym", as_index=False)["registration_count"]
                .sum()
                .sort_values(by="standard_ym", ascending=True)
            )
            chart_title = f"📈 {brand_name} 브랜드 월별 전체 등록 대수 추이"
            line_color = "#10b981"
            marker_color = "#047857"
        else:
            # 특정 차량 모델 월별 추이
            sub_model_df = brand_models_df[brand_models_df["car_model_type"] == current_target]
            trend_df = (
                sub_model_df.groupby("standard_ym", as_index=False)["registration_count"]
                .sum()
                .sort_values(by="standard_ym", ascending=True)
            )
            chart_title = f"🚗 [{brand_name}] {current_target} 월별 등록 대수 추이"
            line_color = "#2563eb"
            marker_color = "#1e40af"

        if not trend_df.empty:
            total_count = trend_df["registration_count"].sum()
            latest_count = trend_df.iloc[-1]["registration_count"]
            latest_month = trend_df.iloc[-1]["standard_ym"]

            m1, m2 = st.columns(2)
            m1.metric("선택 대상 누적 등록", f"{total_count:,} 대")
            m2.metric(f"최근 등록 ({latest_month})", f"{latest_count:,} 대")

            st.markdown("<br>", unsafe_allow_html=True)

            fig = px.line(
                trend_df,
                x="standard_ym",
                y="registration_count",
                markers=True,
                title=chart_title,
                labels={"standard_ym": "등록 월", "registration_count": "등록 대수(대)"},
                text="registration_count"
            )

            fig.update_traces(
                line=dict(color=line_color, width=3),
                marker=dict(size=8, color=marker_color),
                textposition="top center",
                texttemplate="%{text:,.0f}대"
            )

            fig.update_layout(
                xaxis_type="category",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=50, b=20),
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("해당 조건의 추이 데이터가 없습니다.")
>>>>>>> Stashed changes
