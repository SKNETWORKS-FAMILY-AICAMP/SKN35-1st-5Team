import streamlit as st
from views.home import section_title
from data_loader import load_faq_data

def faq_view():
    faq_df = load_faq_data()
    section_title("자주 묻는 질문 (FAQ)", "자동차 등록, 명의 변경 및 이전 관련 궁금증을 해결해 드립니다.")

    if faq_df.empty:
        st.info("등록된 FAQ 데이터가 없습니다.")
        return

    for _, row in faq_df.iterrows():
        with st.expander(f"Q. {row['question']}"):
            st.markdown(f"**A.** {row['answer']}")