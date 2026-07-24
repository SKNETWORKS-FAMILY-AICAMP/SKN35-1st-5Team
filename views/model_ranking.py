import streamlit as st
from views.brand_ranking import render_filter
from views.home import show_review_dialog

def model_ranking_view(model_ranking_df, review_df):
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">모델별 랭킹 순위 및 리뷰</h1>
            <div class="subtext">조회하려는 연월 및 국산/수입 구분을 선택한 후 차종별 등록 순위를 확인하세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if model_ranking_df.empty:
        st.warning("모델별 랭킹 데이터가 존재하지 않습니다.")
        return

    selected_ym, selected_type = render_filter(model_ranking_df, show_type_filter=True, key_prefix="model_rank")
    filtered_df = model_ranking_df.copy()
    if selected_ym:
        filtered_df = filtered_df[filtered_df["standard_ym"] == selected_ym]
    if selected_type != "전체":
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == selected_type]

    type_label = f"[{selected_type}] " if selected_type != "전체" else ""
    st.markdown(f"### 📋 **{selected_ym}** {type_label}모델별 등록 랭킹 (행을 선택하면 팝업 리뷰가 출력됩니다)")
    
    if filtered_df.empty:
        st.info(f"선택한 조건({selected_ym}, {selected_type})에 일치하는 모델 데이터가 존재하지 않습니다.")
        return

    cols_order = ["logo", "brand_name", "car_name", "car_image", "registration_count", "mom_increase"]
    event = st.dataframe(
        filtered_df[cols_order],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="model_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "brand_name": "브랜드명",
            "car_name": "모델명",
            "car_image": st.column_config.ImageColumn("차량 이미지", width="medium"),
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d대"),
            "mom_increase": st.column_config.NumberColumn("전월대비(%)", format="%.1f%%"),
        }
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_index = selected_rows[0]
        selected_row_data = filtered_df.iloc[selected_index]
        selected_car_name = selected_row_data.get("car_name")
        selected_model_id = selected_row_data.get("model_id")
        selected_logo = selected_row_data.get("logo")
        selected_car_image = selected_row_data.get("car_image")

        matched_reviews = review_df[review_df["model_id"] == selected_model_id] if not review_df.empty else pd.DataFrame()
        show_review_dialog(selected_car_name, selected_logo, selected_car_image, matched_reviews)