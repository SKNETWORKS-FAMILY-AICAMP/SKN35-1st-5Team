import streamlit as st

from components import section_title, render_filter
from dialogs import show_review_dialog


def model_ranking_view(model_ranking_df, review_df):
    section_title(
        "모델별 랭킹 순위",
        "기준 연월과 국산/수입 구분을 선택하면 등록대수 기준 상위 10개 모델을 조회합니다.",
    )

    if model_ranking_df.empty:
        st.warning("모델별 랭킹 데이터가 존재하지 않습니다.")
        return

    target_ym, target_type = render_filter(model_ranking_df, show_type_filter=True, key_prefix="model_rank")

    filtered_df = model_ranking_df.copy()
    if target_ym and "standard_ym" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["standard_ym"] == target_ym]
    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    if filtered_df.empty:
        st.info("선택한 조건에 해당하는 모델 랭킹 데이터가 없습니다.")
        return

    top10_df = filtered_df.sort_values(by="registration_count", ascending=False).head(10).reset_index(drop=True)

    display_cols = ["logo", "brand_name", "car_name", "fuel_type", "registration_count", "mom_increase"]
    existing_cols = [c for c in display_cols if c in top10_df.columns]

    event = st.dataframe(
        top10_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="model_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "fuel_type": "연료",
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d 대"),
            "mom_increase": st.column_config.NumberColumn("전월 대비", format="%+d 대"),
        },
    )

    download_df = top10_df[existing_cols].rename(
        columns={
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "fuel_type": "연료",
            "registration_count": "등록대수",
            "mom_increase": "전월대비 증가량",
        }
    ).drop(columns=["logo"], errors="ignore")
    st.download_button(
        "모델별 Top 10 데이터 다운로드 (CSV)",
        download_df.to_csv(index=False).encode("utf-8-sig"),
        f"모델_Top10_{target_type}_{target_ym}.csv",
        "text/csv",
        use_container_width=True,
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_data = top10_df.iloc[selected_idx]

        car_name = selected_data.get("car_name", "차량")
        logo_url = selected_data.get("logo", "")
        car_image_url = selected_data.get("car_image", "")
        model_id = selected_data.get("model_id")

        matched_reviews = (
            review_df[review_df["model_id"] == model_id]
            if not review_df.empty and "model_id" in review_df.columns
            else review_df.iloc[0:0]
        )

        show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)
