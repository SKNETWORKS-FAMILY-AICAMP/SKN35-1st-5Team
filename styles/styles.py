import streamlit as st


def apply_custom_styles() -> None:
    """애플리케이션 전용 Custom CSS 스타일을 적용합니다."""
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 2rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            }
            [data-testid="stSidebar"] * {
                color: white !important;
            }
            :root {
              --hero-bg: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%);
              --hero-border: #dbeafe;
              --hero-text: #0f172a;        /* 메인 글자색 */
              --hero-subtext: #475569;     /* 설명글/보조 글자색 */
            }
            
            /* 2. 다크 모드 변수 재정의 (시스템 설정에 따라 자동 전환) */
            @media (prefers-color-scheme: dark) {
              :root {
                --hero-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 55%, #020617 100%);
                --hero-border: #334155;    /* 톤다운된 어두운 테두리 */
                --hero-text: #f8fafc;      /* 다크모드 메인 글자색 */
                --hero-subtext: #94a3b8;   /* 다크모드 보조 글자색 */
              }
            }
            
            /* 3. .hero 클래스에 적용 */
            .hero {
                padding: 1.2rem 1.3rem;
                border-radius: 18px;
                background: var(--hero-bg);
                border: 1px solid var(--hero-border);
                color: var(--hero-text);
                margin-bottom: 1rem;
            }
            
            /* 스타일 세부 가독성을 위한 내부 요소 예시 */
            .hero p, .hero .subtext {
                color: var(--hero-subtext);
            }
            .subtext {
                font-size: 0.95rem;
                color: #475569;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# 사이드바 옵션 메뉴 스타일 딕셔너리 분리
SIDEBAR_MENU_STYLES = {
    "container": {"padding": "0!important", "background-color": "#0f172a","border-radius":"0"},
    "icon": {"color": "#e2e8f0", "font-size": "15px"},
    "nav-link": {
        "font-size": "14px",
        "color": "#f1f5f9",
        "text-align": "left",
        "margin": "0px",
        "background-color": "transparent",
        "--hover-color": "rgba(59, 130, 246, 0.3)",
    },
    "nav-link-selected": {
        "background-color": "#3b82f6",
        "color": "#ffffff",
    },
}