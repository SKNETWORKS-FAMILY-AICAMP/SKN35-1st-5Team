import streamlit as st

from components import section_title


def faq_view(faq_df):
    section_title("자주 묻는 질문 (FAQ)", "차량 등록 및 절차와 관련된 주요 FAQ 목록입니다.")

    if faq_df.empty:
        st.info("등록된 FAQ 데이터가 없습니다.")
        return

    for _, row in faq_df.iterrows():
        with st.expander(f"❓ {row['question']}"):
            st.write(row["answer"])
