import streamlit as st
from views.home import section_title
from data_loader import load_registration_data
from dialogs import show_registration_trend_dialog

def registration_status_view():
    registration_df = load_registration_data()
    section_title("자동차 등록 현황 조회", "월별로 등록된 자동차 현황입니다. 행을 클릭하면 월별 등록 추이 그래프를 확인할 수 있습니다.")
    
    if registration_df.empty:
        st.warning("등록 현황 데이터가 존재하지 않습니다.")
        return

    page_size = 10
    total_items = len(registration_df)
    total_pages = max((total_items + page_size - 1) // page_size, 1)

    c_page, c_info = st.columns([3, 7])
    with c_page:
        page_number = st.number_input(
            f"페이지 선택 (총 {total_pages} 페이지)", 
            min_value=1, 
            max_value=total_pages, 
            value=1,
            step=1,
            key="reg_page_number"
        )
    with c_info:
        st.markdown(f"<br><span style='color: #64748b; font-size: 0.9rem;'>총 <b>{total_items:,}</b>건 중 {((page_number-1)*page_size)+1} ~ {min(page_number*page_size, total_items)}번째 항목 표출</span>", unsafe_allow_html=True)

    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    
    page_df = registration_df.iloc[start_idx:end_idx].copy().reset_index(drop=True)

    display_cols = ["logo", "manufacturer", "car_model_type", "registration_count", "standard_ym"]
    existing_cols = [col for col in display_cols if col in page_df.columns]

    event = st.dataframe(
        page_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="reg_status_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "manufacturer": "제조사",
            "car_model_type": "차종/모델",
            "registration_count": st.column_config.NumberColumn("등록개수", format="%d 대"),
            "standard_ym": "등록 월(Month)",
        }
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_row = page_df.iloc[selected_idx]
        
        car_name = selected_row["car_model_type"]
        manufacturer = selected_row["manufacturer"]
        logo_url = selected_row.get("logo", "")
        car_image_url = selected_row.get("car_image", "")

        car_history_df = registration_df[registration_df["car_model_type"] == car_name]
        show_registration_trend_dialog(car_name, manufacturer, logo_url, car_image_url, car_history_df)