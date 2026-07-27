import streamlit as st
from views.home import load_model_ranking_data, load_review_data, section_title, DEFAULT_CAR_IMAGE
from views.brand_ranking import render_filter
from dialogs import show_review_dialog  # 프로젝트 구조에 맞춰 수정


def _format_mom_increase(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return "➖ 0 대"

    if value > 0:
        return f"🟢 ▲{value:,} 대"
    elif value < 0:
        return f"🔴 ▼{abs(value):,} 대"
    else:
        return "➖ 0 대"


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
    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    # 연도/월이 "전체"로 선택된 경우(ALL, "-MM", "YYYY-") 해당 기간을 모델 기준으로 합산해서 보여준다.
    agg_cols = {"registration_count": "sum"}
    for col in ["model_id", "logo", "car_image"]:
        if col in filtered_df.columns:
            agg_cols[col] = "first"

    if target_ym == "ALL":
        agg_source = filtered_df.sort_values("standard_ym", ascending=False)
        display_df = agg_source.groupby(["brand_name", "car_name"], as_index=False).agg(agg_cols)
        display_df["mom_increase"] = 0
    elif target_ym and (target_ym.endswith("-") or target_ym.startswith("-")):
        if target_ym.endswith("-"):
            year_prefix = target_ym.split("-")[0]
            sub_df = filtered_df[filtered_df["standard_ym"].str.startswith(year_prefix)]
        else:
            month_suffix = target_ym.split("-")[1]
            sub_df = filtered_df[filtered_df["standard_ym"].str.endswith(month_suffix)]
        agg_source = sub_df.sort_values("standard_ym", ascending=False)
        display_df = agg_source.groupby(["brand_name", "car_name"], as_index=False).agg(agg_cols)
        display_df["mom_increase"] = 0
    else:
        display_df = filtered_df[filtered_df["standard_ym"] == target_ym].copy()

    if display_df.empty:
        st.info("선택한 조건에 해당하는 모델 랭킹 데이터가 없습니다.")
        return

    top10_df = display_df.sort_values(by="registration_count", ascending=False).head(10).reset_index(drop=True)

    if "mom_increase" in top10_df.columns:
        top10_df["mom_increase_display"] = top10_df["mom_increase"].apply(_format_mom_increase)

    display_cols = ["logo", "brand_name", "car_name", "registration_count", "mom_increase_display"]
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
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d 대"),
            "mom_increase_display": "전월 대비",
        },
    )

    download_df = top10_df[existing_cols].rename(
        columns={
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "registration_count": "등록대수",
            "mom_increase_display": "전월대비 증가량",
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
