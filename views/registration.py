import streamlit as st
from views.home import load_registration_data, section_title, DEFAULT_CAR_IMAGE

@st.dialog("📊 월별 등록 대수 추이 분석", width="large")
def show_registration_trend_dialog(car_name, manufacturer, logo_url, car_image_url, car_history_df):
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

    if car_history_df.empty:
        st.info(f"'{car_name}' 모델에 대한 월별 등록 추이 데이터가 없습니다.")
        return

    trend_df = car_history_df.sort_values(by="standard_ym", ascending=True).copy()

    total_count = trend_df["registration_count"].sum()
    avg_count = int(trend_df["registration_count"].mean())
    latest_count = trend_df.iloc[-1]["registration_count"]
    latest_month = trend_df.iloc[-1]["standard_ym"]

    m1, m2, m3 = st.columns(3)
    m1.metric("총 누적 등록 대수", f"{total_count:,} 대")
    m2.metric("월평균 등록 대수", f"{avg_count:,} 대")
    m3.metric(f"최근 등록 ({latest_month})", f"{latest_count:,} 대")

    st.markdown("<br>", unsafe_allow_html=True)

    import plotly.express as px
    fig = px.line(
        trend_df,
        x="standard_ym",
        y="registration_count",
        markers=True,
        title=f"📈 {car_name} 월별 등록 대수 추이",
        labels={"standard_ym": "등록 월", "registration_count": "등록 대수(대)"},
        text="registration_count"
    )

    fig.update_traces(
        line=dict(color="#2563eb", width=3),
        marker=dict(size=8, color="#1e40af"),
        textposition="top center",
        texttemplate="%{text:,.0f}대"
    )
    
    fig.update_layout(
        xaxis_type="category",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)

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