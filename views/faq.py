

import streamlit as st
from views.home import section_title
from data_loader import load_faq_data

def faq_view():
    faq_df = load_faq_data()
    
    # 1. 상단 타이틀 및 설명
    section_title(
        "자주 묻는 질문 (FAQ)", 
        "어디스카(ATHISCar) 웹사이트 이용 및 데이터 관련 궁금증을 해결해 드립니다."
    )

    # 2. FAQ 데이터 유무 확인 및 아코디언 출력
    if faq_df.empty:
        st.info("등록된 FAQ 데이터가 없습니다.")
    else:
        for _, row in faq_df.iterrows():
            with st.expander(f"Q. {row['question']}"):
                st.markdown(f"**A.** {row['answer']}")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 3. 하단 1:1 문의하기 안내 카드 및 버튼 영역
    with st.container():
        st.info("💡 **원하는 답변을 찾지 못하셨나요?**\n\n1:1 문의를 남겨주시면 담당자가 확인 후 빠른 시일 내에 안내해 드리겠습니다.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # 구글 폼 문의 버튼 (링크는 실제 구글 폼 URL로 수정)
            st.link_button("📄 구글 폼으로 문의하기", "https://forms.google.com", use_container_width=True)
        with col2:
            # 어디스카 공식 메일로 바로 연결
            st.link_button("✉️ 이메일로 문의하기", "mailto:support@ATHISCar.com", use_container_width=True)

faq_view_with_link = faq_view