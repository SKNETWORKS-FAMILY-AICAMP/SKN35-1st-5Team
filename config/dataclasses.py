from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    page_title: str = "자동차 등록 현황 통합 시스템"
    page_icon: str = "🚗"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    sidebar_title: str = "🚗 Auto Insight"
    sidebar_caption: str = "자동차 등록 현황 통합 시스템"
    footer_caption: str = "SKN35_1st_Project_Group5"