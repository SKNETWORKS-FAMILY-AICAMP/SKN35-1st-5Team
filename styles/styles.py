import streamlit as st


def apply_custom_styles() -> None:
    """애플리케이션 전용 Custom CSS 스타일을 적용합니다.

    views/ 하위 각 페이지에서 개별적으로 선언하던 <style> 블록을 이곳으로 모아
    중복을 제거하고, 페이지들은 여기서 정의한 클래스만 참조합니다.
    app.py에서 라우팅 전에 한 번 호출되므로 모든 뷰에 적용됩니다.
    """
    st.markdown(
        """
        <style>
            /* ---------------------------------------------------------
               공통 레이아웃
            --------------------------------------------------------- */
            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 2rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0ea5e9 0%, #38bdf8 100%);
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

            /* views/home.py: section_title()가 사용하는 타이틀 박스 */
            .hero {
                padding: 1.2rem 1.3rem;
                border-radius: 18px;
                background: var(--hero-bg);
                border: 1px solid var(--hero-border);
                color: var(--hero-text);
                margin-bottom: 1rem;
            }
            .hero h1 {
                margin-bottom: 0.2rem;
            }
            .hero p, .hero .subtext {
                color: var(--hero-subtext);
            }
            .subtext {
                font-size: 0.95rem;
                color: #475569;
            }

            /* ---------------------------------------------------------
               views/registration.py
            --------------------------------------------------------- */
            .stMetric {
                background-color: #f8fafc;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }

            /* 페이지네이션 안내 문구: registration.py, brand_ranking.py 공용 */
            .page-info {
                color: #64748b;
                font-size: 0.9rem;
                font-weight: 500;
                text-align: right;
                align-self: center;
                margin-top: 5px;
            }

            /* ---------------------------------------------------------
               views/model_ranking.py: 모델 랭킹 리스트 행
            --------------------------------------------------------- */
            .model-row-divider {
                margin: 15px 0;
                border: none;
                border-top: 1px solid #e5e7eb;
            }
            .model-rank-number {
                margin: 0;
                color: #2563eb;
            }
            .model-brand-name {
                font-size: 0.95rem;
                color: #4b5563;
            }
            .model-car-name {
                margin: 5px 0 0 0;
            }
            .model-page-indicator {
                text-align: center;
                font-weight: bold;
                padding-top: 6px;
            }
            .model-page-indicator-sub {
                text-align: center;
                color: #6b7280;
            }

            /* ---------------------------------------------------------
               views/brand_ranking.py: 브랜드 랭킹 리스트 행
            --------------------------------------------------------- */
            .brand-name {
                font-weight: 600;
                font-size: 1rem;
                padding-top: 8px;
            }
            .brand-count {
                font-size: 0.95rem;
                padding-top: 10px;
                color: #1e293b;
            }
            .brand-mom {
                font-size: 0.95rem;
                padding-top: 10px;
                font-weight: 600;
            }
            .brand-mom-up {
                color: #10b981;
            }
            .brand-mom-down {
                color: #ef4444;
            }
            .brand-mom-flat {
                color: #64748b;
            }
            .brand-date {
                font-size: 0.9rem;
                padding-top: 10px;
                color: #64748b;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# 사이드바 옵션 메뉴 스타일 딕셔너리 분리
SIDEBAR_MENU_STYLES = {
    "container": {"padding": "0!important", "background-color": "#0f172a"},
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