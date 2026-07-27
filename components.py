import streamlit as st


def section_title(title, caption):
    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">{title}</h1>
            <div class="subtext">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filter(df, show_type_filter=False, key_prefix="filter"):
    """연도/월(+구분) 선택 필터 컴포넌트"""
    if df.empty or "standard_ym" not in df.columns:
        return None, None

    available_yms = sorted(df["standard_ym"].dropna().unique(), reverse=True)
    years = sorted(list(set([ym.split("-")[0] for ym in available_yms if "-" in ym])), reverse=True)

    if not years:
        return None, None

    if show_type_filter:
        c1, c2, c3, _ = st.columns([2, 2, 2, 4])
    else:
        c1, c2, _ = st.columns([2, 2, 6])

    with c1:
        selected_year = st.selectbox("📅 연도 선택", years, key=f"{key_prefix}_year")

    available_months = sorted(
        list(set([ym.split("-")[1] for ym in available_yms if ym.startswith(selected_year)])),
        reverse=True,
    )
    with c2:
        selected_month = st.selectbox("📆 월 선택", available_months, key=f"{key_prefix}_month")

    selected_target_ym = f"{selected_year}-{selected_month}"

    selected_type = "전체"
    if show_type_filter:
        with c3:
            selected_type = st.selectbox("🚘 구분 선택", ["전체", "국산", "수입"], key=f"{key_prefix}_type")

    return selected_target_ym, selected_type
