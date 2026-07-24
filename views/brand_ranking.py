import streamlit as st

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

def brand_ranking_view(brand_ranking_df):
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">브랜드별 랭킹 순위</h1>
            <div class="subtext">조회하고자 하는 연월 조건을 선택하여 브랜드 등록 순위를 확인합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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