import streamlit as st
import plotly.express as px

from data_loader import load_registration_data
from constants import CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE


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

    
def _flatten_html(html):
    """st.markdown은 Markdown 파서를 거치므로, 줄 앞의 들여쓰기가 4칸 이상이면
    코드블록으로 오인되어 태그가 그대로 노출된다. 각 줄의 선행 공백을 제거해 방지한다."""
    return "\n".join(line.strip() for line in html.strip().splitlines())


def _safe_float(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result else None  # NaN 체크


def _dark_stars(score, max_score=5.0, size="1.05rem", text_color="#e5e7eb", empty_color="#39415a"):
    """0.5점 단위 실수 평점을 별 아이콘 바(HTML)로 변환합니다. text_color/empty_color로 밝은/어두운 배경 모두 대응."""
    score = _safe_float(score)
    if score is None:
        return "<span style='color:#8b93a7;'>평점 없음</span>"

    score = max(0.0, min(max_score, score))
    percent = (score / max_score) * 100

    return f"""
    <span style="display: inline-flex; align-items: center; gap: 6px;">
        <span style="position: relative; display: inline-block; font-size: {size}; line-height: 1; letter-spacing: 2px;">
            <span style="color: {empty_color};">★★★★★</span>
            <span style="position: absolute; top: 0; left: 0; width: {percent}%; overflow: hidden; white-space: nowrap; color: #fbbf24;">★★★★★</span>
        </span>
        <span style="font-weight: 700; color: {text_color}; font-size: 0.85rem;">{score:.1f} / {max_score:.1f}</span>
    </span>
    """


def _dark_bar_row(label, score, max_score=5.0):
    score = _safe_float(score)
    percent = 0 if score is None else max(0.0, min(max_score, score)) / max_score * 100
    score_text = "-" if score is None else f"{score:.1f}"

    return f"""
    <div style="display:flex; align-items:center; gap:10px; margin:6px 0;">
        <span style="width:52px; flex-shrink:0; font-size:0.78rem; color:#6b7280; letter-spacing:0.5px;">{label}</span>
        <div style="flex:1; height:6px; border-radius:4px; background:#e5e7eb; overflow:hidden;">
            <div style="width:{percent}%; height:100%; background:linear-gradient(90deg,#3b6fe0,#5b8def); border-radius:4px;"></div>
        </div>
        <span style="width:28px; flex-shrink:0; text-align:right; font-size:0.78rem; color:#374151;">{score_text}</span>
    </div>
    """


@st.dialog("📝 차량 상세 리뷰", width="large")
def show_review_dialog(car_name, logo_url, car_image_url, matched_reviews):
    review_count = len(matched_reviews)
    avg_overall = _safe_float(matched_reviews["overall_rating"].mean()) if review_count else None
    avg_perform = _safe_float(matched_reviews["perform_score"].mean()) if review_count else None
    avg_price = _safe_float(matched_reviews["price_score"].mean()) if review_count else None
    avg_fault = _safe_float(matched_reviews["fault_score"].mean()) if review_count else None
    overall_text = "-" if avg_overall is None else f"{avg_overall:.1f}"

    logo_img = f'<img src="{logo_url}" style="width:44px;height:44px;object-fit:contain;"/>' if logo_url else ""
    car_img = f'<img src="{car_image_url}" style="width:100%;max-width:170px;border-radius:12px;object-fit:contain;"/>' if car_image_url else ""

    header_html = f"""
    <style>
    .rv-card {{ background:#ffffff; border:1px solid #e5e7eb;
        border-radius:16px; padding:20px 22px; margin-bottom:18px; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
    .rv-header {{ display:flex; flex-wrap:wrap; align-items:center; gap:20px; }}
    .rv-logo {{ width:64px; height:64px; border-radius:50%; background:#fff; border:1px solid #e5e7eb;
        display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
    .rv-name-block {{ min-width:130px; }}
    .rv-car-name {{ color:#111827; font-weight:700; font-size:1.05rem; }}
    .rv-car-count {{ color:#6b7280; font-size:0.8rem; margin-top:2px; }}
    .rv-car-img-wrap {{ flex-shrink:0; }}
    .rv-rating-panel {{ flex:1; min-width:180px; background:#f8fafc; border:1px solid #e5e7eb;
        border-radius:12px; padding:12px 16px; }}
    .rv-rating-title {{ display:flex; align-items:center; justify-content:space-between;
        font-size:0.72rem; letter-spacing:1px; color:#6b7280; font-weight:700; }}
    .rv-rating-badge {{ background:#eef2ff; color:#3b6fe0; border:1px solid #c7d7fb;
        border-radius:999px; padding:2px 10px; font-size:0.75rem; font-weight:700; }}
    </style>
    <div class="rv-card">
        <div class="rv-header">
            <div class="rv-logo">{logo_img}</div>
            <div class="rv-name-block">
                <div class="rv-car-name">{car_name}</div>
                <div class="rv-car-count">등록된 실사용자 리뷰: {review_count}개</div>
            </div>
            <div class="rv-car-img-wrap">{car_img}</div>
            <div class="rv-rating-panel">
                <div class="rv-rating-title">OVERALL RATING <span class="rv-rating-badge">{overall_text} / 5.0</span></div>
                <div style="margin:8px 0 10px 0;">{_dark_stars(avg_overall, size="1.3rem", text_color="#1f2937", empty_color="#e5e7eb")}</div>
                {_dark_bar_row("성능", avg_perform)}
                {_dark_bar_row("가격", avg_price)}
                {_dark_bar_row("문제점", avg_fault)}
            </div>
        </div>
    </div>
    """
    st.markdown(_flatten_html(header_html), unsafe_allow_html=True)

    st.markdown(
        _flatten_html(
            """
            <div style="display:flex; align-items:center; gap:8px; margin:4px 0 12px 0;">
                <div style="width:4px; height:16px; background:#5b8def; border-radius:2px;"></div>
                <span style="color:#111827; font-weight:700; font-size:0.85rem; letter-spacing:1px;">USER REVIEWS</span>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    if matched_reviews.empty:
        st.info(f"'{car_name}'에 대한 등록된 상세 리뷰가 없습니다.")
    else:
        for idx, row in matched_reviews.reset_index(drop=True).iterrows():
            performance = row.get("performance") or "-"
            issues = row.get("issues") or "-"
            fault_title = row.get("fault_title") or "-"

            stars_html = _dark_stars(row.get("overall_rating"), text_color="#1f2937", empty_color="#e5e7eb")

            review_html = f"""
            <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:14px;
                padding:16px 18px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:10px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="width:34px; height:34px; border-radius:50%; background:#eef2ff;
                            display:flex; align-items:center; justify-content:center; color:#4f46e5; font-weight:700; font-size:0.8rem;">
                            R{idx + 1}
                        </div>
                        <div>
                            <div style="color:#111827; font-weight:700; font-size:0.9rem;">리뷰 #{idx + 1}</div>
                            <div style="margin-top:2px;">{stars_html}</div>
                        </div>
                    </div>
                    <div style="background:#fff7e6; border:1px solid #fde3a7; flex:0 0 auto; min-width:max-content;
                        border-radius:10px; padding:8px 14px; font-size:1.05rem; font-weight:700; color:#92600a; white-space:nowrap;">
                        🚗 제목: &quot;{issues}&quot;
                    </div>
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:12px; margin-top:14px;">
                    <div style="flex:1; min-width:220px; background:#FAEAFF; border-radius:10px; padding:12px 14px;">
                        <div style="color:#9333ea; font-weight:800; font-size:1rem; margin-bottom:6px;">🚀 리뷰 내용</div>
                        <div style="color:#3f2a4a; font-size:0.85rem; line-height:1.5;">{performance}</div>
                    </div>
                    <div style="flex:1; min-width:220px; background:#F1FFF5; border-radius:10px; padding:12px 14px;">
                        <div style="color:#16a34a; font-weight:800; font-size:1rem; margin-bottom:6px;">⚠️ 문제점/특이사항</div>
                        <div style="color:#2a4a35; font-size:0.85rem; line-height:1.5;">{fault_title}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(_flatten_html(review_html), unsafe_allow_html=True)


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
