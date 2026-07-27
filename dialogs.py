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
