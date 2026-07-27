import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_engine
from views.home import section_title, LOGO_URL_MAP, DEFAULT_LOGO, CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE, load_registration_data

@st.cache_data(ttl=3600)
def load_brand_ranking_data():
    engine = get_engine()
    query = """
    SELECT 
        b.brand_name, 
        b.brand_standard_month AS standard_ym, 
        SUM(CAST(r.count_car_month AS UNSIGNED)) AS registration_count,
        MAX(r.company_type) AS manufacturer_type
    FROM car_brand_rank b
    LEFT JOIN car_registration r ON b.regist_id = r.regist_id
    GROUP BY b.brand_name, b.brand_standard_month
    ORDER BY b.brand_standard_month DESC, registration_count DESC
    """
    df = pd.read_sql(query, con=engine)
    
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["standard_ym_dt"] = pd.to_datetime(df["standard_ym"], format="%Y-%m")
        df = df.sort_values(by=["brand_name", "standard_ym_dt"])     
        df["prev_count"] = df.groupby("brand_name")["registration_count"].shift(1)
        df["real_mom"] = (df["registration_count"] - df["prev_count"]).fillna(0).astype(int)
        df = df.sort_values(by=["standard_ym", "registration_count"], ascending=[False, False])
        df.drop(columns=["standard_ym_dt", "prev_count"], inplace=True)

        def format_mom_display(val):
            if val > 0:
                return f"🟢 ▲ {val:,} 대"
            elif val < 0:
                return f"🔴 ▼ {abs(val):,} 대"
            else:
                return "➖ 0 대"

        df["mom_display"] = df["real_mom"].apply(format_mom_display)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
        
    return df

def render_filter(df, show_type_filter=False, key_prefix="filter"):
    if df.empty or "standard_ym" not in df.columns:
        return None, None
    
    available_yms = sorted(df["standard_ym"].dropna().unique(), reverse=True)
    years = ["전체"] + sorted(list(set([ym.split("-")[0] for ym in available_yms if "-" in ym])), reverse=True)

    if show_type_filter:
        c1, c2, c3, _ = st.columns([2, 2, 2, 4])
    else:
        c1, c2, _ = st.columns([2, 2, 6])

    with c1:
        selected_year = st.selectbox("📅 연도 선택", years, key=f"{key_prefix}_year")
    
    if selected_year == "전체":
        months = ["전체"] + sorted(list(set([ym.split("-")[1] for ym in available_yms if "-" in ym])), reverse=True)
    else:
        months = ["전체"] + sorted(list(set([ym.split("-")[1] for ym in available_yms if ym.startswith(selected_year)])), reverse=True)
        
    with c2:
        selected_month = st.selectbox("📆 월 선택", months, key=f"{key_prefix}_month")

    if selected_year == "전체" and selected_month == "전체":
        selected_target_ym = "ALL"
    elif selected_year == "전체":
        selected_target_ym = f"-{selected_month}"
    elif selected_month == "전체":
        selected_target_ym = f"{selected_year}-"
    else:
        selected_target_ym = f"{selected_year}-{selected_month}"
    
    selected_type = "전체"
    if show_type_filter:
        with c3:
            selected_type = st.selectbox("🚘 구분 선택", ["전체", "국산", "수입"], key=f"{key_prefix}_type")

    return selected_target_ym, selected_type

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

def brand_ranking_view():
    brand_ranking_df = load_brand_ranking_data()
    section_title("브랜드별 랭킹", "월별 및 누적 브랜드 등록 순위 현황입니다. 행을 클릭하면 해당 브랜드의 상세 분석 창이 열립니다.")
    
    target_df = brand_ranking_df
    
    if target_df.empty:
        st.warning("브랜드 랭킹 데이터가 존재하지 않습니다.")
        return

    target_ym, target_type = render_filter(target_df, show_type_filter=True, key_prefix="brand_rank")
    
    filtered_df = target_df.copy()

    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    if target_ym == "ALL":
        display_df = (
            filtered_df.groupby(["brand_name", "manufacturer_type", "logo"], as_index=False)
            .agg({"registration_count": "sum"})
            .sort_values(by="registration_count", ascending=False)
        )
        display_df["standard_ym"] = "전체 기간"
        display_df["mom_display"] = "➖ 0 대"
        
    elif target_ym and (target_ym.endswith("-") or target_ym.startswith("-")):
        if target_ym.endswith("-"):
            year_prefix = target_ym.split("-")[0]
            sub_df = filtered_df[filtered_df["standard_ym"].str.startswith(year_prefix)]
            period_label = f"{year_prefix}년 전체"
        else:
            month_suffix = target_ym.split("-")[1]
            sub_df = filtered_df[filtered_df["standard_ym"].str.endswith(month_suffix)]
            period_label = f"전체 연도 {month_suffix}월"

        display_df = (
            sub_df.groupby(["brand_name", "manufacturer_type", "logo"], as_index=False)
            .agg({"registration_count": "sum"})
            .sort_values(by="registration_count", ascending=False)
        )
        display_df["standard_ym"] = period_label
        display_df["mom_display"] = "➖ 0 대"
        
    else:
        display_df = filtered_df[filtered_df["standard_ym"] == target_ym].copy()
        display_df = display_df.sort_values(by="registration_count", ascending=False)

    if display_df.empty:
        st.info("선택한 조건에 해당하는 브랜드 랭킹 데이터가 없습니다.")
        return

    display_df = display_df.reset_index(drop=True)

    display_cols = ["logo", "brand_name", "registration_count", "mom_display", "standard_ym"]
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
            "registration_count": st.column_config.NumberColumn("등록대수 (합계)", format="%d 대"),
            "mom_display": st.column_config.TextColumn("전월 대비 증감"),
            "standard_ym": "조회 기간",
        }
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_data = display_df.iloc[selected_idx]
        brand_name = selected_data["brand_name"]
        logo_url = selected_data.get("logo", "")

        brand_history_df = brand_ranking_df[brand_ranking_df["brand_name"] == brand_name]
        
        # 새로운 팝업창 열기 전 세션 초기화
        state_key_target = f"trend_target_{brand_name}"
        if state_key_target not in st.session_state:
            st.session_state[state_key_target] = "BRAND_TOTAL"

        show_brand_trend_dialog(brand_name, logo_url, brand_history_df)