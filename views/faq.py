import streamlit as st

def faq_view(faq_df):
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin-bottom:0.2rem;">자주 하는 질문 (FAQ)</h1>
            <div class="subtext">차량 등록 관련 궁금한 점을 검색해 보세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if faq_df.empty:
        st.warning("FAQ 데이터가 존재하지 않습니다.")
        return

    keyword = st.text_input("검색어 입력", placeholder="예: 신차, 명의, 취득세")
    result_faq = faq_df.copy()
    
    if keyword:
        matched = (
            result_faq["question"].str.contains(keyword, case=False, na=False) | 
            result_faq["answer"].str.contains(keyword, case=False, na=False)
        )
        result_faq = result_faq[matched]

    st.caption(f"총 {len(result_faq)}건의 FAQ가 검색되었습니다.")
    if result_faq.empty:
        st.info("조건에 일치하는 FAQ가 없습니다.")
        return

    for _, faq in result_faq.iterrows():
        with st.expander(f"Q. {faq['question']}"):
            st.write(faq["answer"])