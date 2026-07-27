import streamlit as st
from views.home import show_trend_dialog

def registration_status_view(registration_df, CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE):
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">자동차 등록 현황 조회</h1>
            <div class="subtext">월별로 등록된 자동차 모델의 상세 현황입니다. 행을 클릭하면 해당 차량의 월별 등록 추이 그래프와 이미지가 출력됩니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if registration_df.empty:
        st.warning("등록 현황 데이터가 존재하지 않습니다.")
        return

    display_cols = ["logo", "manufacturer", "car_name", "registration_count", "standard_ym"]
    view_df = registration_df[display_cols].copy()

    PAGE_SIZE = 10
    total_rows = len(view_df)
    total_pages = (total_rows + PAGE_SIZE - 1) // PAGE_SIZE if total_rows > 0 else 1

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_df = view_df.iloc[start_idx:end_idx]

    event = st.dataframe(
        page_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key=f"registration_table_p{st.session_state.current_page}",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "manufacturer": "제조사",
            "car_name": "차 이름",
            "registration_count": st.column_config.NumberColumn("등록개수", format="%d 대"),
            "standard_ym": "등록 월(Month)",
        }
    )

    st.markdown("---")
    p_col1, p_col2, p_col3 = st.columns([2, 3, 2])

    with p_col1:
        if st.button("⬅️ 이전 페이지", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1
            st.rerun()

    with p_col2:
        st.markdown(
            f"<div style='text-align: center; padding-top: 5px; font-weight: bold;'>"
            f"Page {st.session_state.current_page} of {total_pages} (총 {total_rows}건)"
            f"</div>",
            unsafe_allow_html=True
        )

    with p_col3:
        if st.button("다음 페이지 ➡️", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_car = page_df.iloc[selected_idx]
        car_name = selected_car["car_name"]
        logo_url = selected_car["logo"]
        car_image_url = CAR_IMAGE_URL_MAP.get(car_name, DEFAULT_CAR_IMAGE)
        show_trend_dialog(car_name, logo_url, car_image_url, registration_df)