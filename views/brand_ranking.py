import streamlit as st

from components import section_title, render_filter
from dialogs import show_registration_trend_dialog


def brand_ranking_view(brand_ranking_df, registration_df):
    section_title(
        "브랜드별 랭킹",
        "월별 국산/수입 브랜드 등록 순위 현황입니다. 클릭 시 브랜드 등록 추이를 확인할 수 있습니다.",
    )

    # 1. 데이터 검증 (car_brand_rank 또는 관련 데이터프레임 확인)
    target_df = brand_ranking_df if not brand_ranking_df.empty else registration_df

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
        },
    )

    # 4. 행 클릭 시 처리
    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_data = display_df.iloc[selected_idx]

        brand_name = selected_data.get("brand_name", "브랜드")
        logo_url = selected_data.get("logo", "")

        # 해당 브랜드의 전체 월별 데이터 추출
        brand_history_df = (
            target_df[target_df["brand_name"] == brand_name] if "brand_name" in target_df.columns else target_df.iloc[0:0]
        )

        # 등록 추이 팝업 호출
        show_registration_trend_dialog(brand_name, "브랜드", logo_url, "", brand_history_df)
