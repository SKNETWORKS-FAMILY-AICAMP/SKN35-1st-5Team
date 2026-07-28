import streamlit as st
import pandas as pd
from views.home import section_title
from data_loader import load_registration_data
from dialogs import show_registration_trend_dialog
from constants import LOGO_URL_MAP

# 이 파일의 CSS(.stMetric, .page-info)는 styles/styles.py의 apply_custom_styles()로 이동했습니다.


def render_registration_metrics(registration_df):
    """상단 요약 지표 카드 출력"""
    total_registrations = registration_df["registration_count"].sum()
    unique_models = registration_df["car_model_type"].nunique()
    
    if "fuel_type" in registration_df.columns:
        electric_share = (registration_df[registration_df["fuel_type"].str.contains("EV", case=False)]["registration_count"].sum() / total_registrations * 100) if total_registrations > 0 else 0
    else:
        electric_share = (registration_df[registration_df["car_model_type"].str.contains("EV", case=False)]["registration_count"].sum() / total_registrations * 100) if total_registrations > 0 else 0

    average_quota = total_registrations / unique_models if unique_models > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="총 등록 대수", value=f"{total_registrations:,} 대",)
    with col2:
        st.metric(label="신규 모델", value=f"{unique_models}",)
    with col3:
        st.metric(label="평균 등록 수", value=f"{average_quota:,.0f} 대",)

def registration_status_view():
    # --- Data Loading ---
    registration_df = load_registration_data()
    section_title("자동차 등록 현황 조회", "월별로 등록된 자동차 현황입니다. 행을 클릭하면 월별 등록 추이 그래프를 확인할 수 있습니다.")
    
    if registration_df.empty:
        st.warning("등록 현황 데이터가 존재하지 않습니다.")
        return

    # --- Render Metrics ---
    render_registration_metrics(registration_df)
    st.markdown("---")

    # --- Pagination Logic ---
    page_size = 10
    total_items = len(registration_df)
    total_pages = max((total_items + page_size - 1) // page_size, 1)

    #c_page, c_info = st.columns([1, 4])
    c_page, c_info, _ = st.columns([1, 3, 2], vertical_alignment="center")
    with c_page:
        page_number = st.number_input(
            "페이지 선택", 
            min_value=1, 
            max_value=total_pages, 
            value=1,
            step=1,
            key="reg_page_number",
            label_visibility="collapsed",
        )
    with c_info:
        st.markdown(f"<p class='page-info'>총 <b>{total_items:,}</b>건 중 {((page_number-1)*page_size)+1} ~ {min(page_number*page_size, total_items)}번째 항목 표출</p>", unsafe_allow_html=True)

    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    page_df = registration_df.iloc[start_idx:end_idx].copy().reset_index(drop=True)

    # --- Logo URL Mapping 적용 ---
    if "logo" not in page_df.columns or page_df["logo"].isnull().all():
        page_df["logo"] = page_df["manufacturer"].map(LOGO_URL_MAP).fillna("")
    else:
        # 기존 로고 값이 비어있는 경우에만 상단 맵핑 적용
        page_df["logo"] = page_df.apply(
            lambda row: row["logo"] if pd.notna(row["logo"]) and row["logo"] != "" else LOGO_URL_MAP.get(row["manufacturer"], ""), 
            axis=1
        )

    # --- 데이터프레임 컬럼 순서 및 이름 한글화 정렬 ---
    display_cols = ["logo", "manufacturer", "car_model_type", "registration_count", "standard_ym"]
    existing_cols = [col for col in display_cols if col in page_df.columns]
    
    view_df = page_df[existing_cols].copy()
    
    # 컬럼명을 한글로 변경
    view_df.columns = ["로고", "제조사", "차종/모델", "등록개수", "등록 월"]

    # --- Streamlit 기본 데이터프레임 & 이벤트 처리 (st.dataframe 활용) ---
    event = st.dataframe(
        view_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="reg_status_table",
        column_config={
            "로고": st.column_config.ImageColumn("로고", width="small"),
            "제조사": st.column_config.TextColumn("제조사"),
            "차종/모델": st.column_config.TextColumn("차종/모델"),
            "등록개수": st.column_config.NumberColumn("등록개수", format="%d 대",alignment="left"),
            "등록 월": st.column_config.TextColumn("등록 월"),
        }
    )

    # --- Handle Row Selection ---
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

if __name__ == "__main__":
    registration_status_view()