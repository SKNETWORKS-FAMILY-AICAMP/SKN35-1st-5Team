import pandas as pd
import streamlit as st
from db import get_engine

engine = get_engine()

@st.cache_data
def load_faq_data():
    try:
        return pd.read_sql("SELECT * FROM faq_table", con=engine)
    except Exception:
        return pd.DataFrame(columns=["카테고리", "질문", "답변"])

def render():
    st.markdown(
        """
        <div style="padding: 1.2rem 1.3rem; border-radius: 18px; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%); border: 1px solid #dbeafe; margin-bottom: 1rem;">
            <h1 style="margin-bottom:0.2rem;">자주 하는 질문 (FAQ)</h1>
            <div style="font-size: 0.95rem; color: #475569;">키워드와 카테고리로 업무 문의를 빠르게 찾습니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    faq_df = load_faq_data()

    if faq_df.empty:
        st.warning("연동된 데이터베이스에 FAQ 데이터가 존재하지 않습니다.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        keyword = st.text_input("검색어", placeholder="예: 법인, 등록, 기준일")
    with c2:
        category = st.selectbox("카테고리", ["전체"] + sorted(faq_df["카테고리"].unique().tolist()))

    result_faq = faq_df.copy()
    if category != "전체":
        result_faq = result_faq[result_faq["카테고리"] == category]
    if keyword:
        matched = result_faq["질문"].str.contains(keyword, case=False, na=False) | result_faq["답변"].str.contains(keyword, case=False, na=False)
        result_faq = result_faq[matched]

    st.caption(f"{len(result_faq)}건의 FAQ 검색됨")
    for _, faq in result_faq.iterrows():
        with st.expander(f"[{faq['카테고리']}] {faq['질문']}"):
            st.write(faq["답변"])