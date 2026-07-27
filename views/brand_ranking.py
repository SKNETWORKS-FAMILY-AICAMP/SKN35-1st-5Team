import streamlit as st
import pandas as pd
from db import get_engine
from views.home import section_title
from constants import LOGO_URL_MAP, DEFAULT_LOGO
from dialogs import show_brand_trend_dialog

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