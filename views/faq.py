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
            <div style="font-size: 0.95rem; color: #475569;">카테고리를 먼저 선택한 후 관련 내용을 확인하세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    faq_df = load_faq_data()

    if faq_df.empty:
        st.warning("연동된 데이터베이스에 FAQ 데이터가 존재하지 않습니다.")
        return

    # 1. 카테고리 선택 UI (차량 등록 vs 전기차) - 라디오 버튼 활용
    categories = ["전체"] + sorted(faq_df["카테고리"].unique().tolist())
    selected_category = st.radio(
        "관심 있는 주제를 선택하세요:",
        options=["전체", "차량 등록", "전기차"],
        horizontal=True
    )

    st.markdown("---")

    # 2. 검색어 입력창 배치
    keyword = st.text_input("검색어 입력", placeholder="예: 신차, 보조금, 명의 변경")

    # 3. 카테고리 및 검색어 필터링 로직 적용
    result_faq = faq_df.copy()
    
    if selected_category != "전체":
        result_faq = result_faq[result_faq["카테고리"] == selected_category]
        
    if keyword:
        matched = (
            result_faq["질문"].str.contains(keyword, case=False, na=False) | 
            result_faq["답변"].str.contains(keyword, case=False, na=False)
        )
        result_faq = result_faq[matched]

    # 4. 결과 출력
    st.caption(f"총 {len(result_faq)}건의 FAQ가 검색되었습니다.")
    
    if result_faq.empty:
        st.info("조건에 일치하는 FAQ가 없습니다.")
        return

    for _, faq in result_faq.iterrows():
        with st.expander(f"[{faq['카테고리']}] {faq['질문']}"):
            st.write(faq["답변"])


if __name__ == "__main__":
    render()