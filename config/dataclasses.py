from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    page_title: str = "자동차 등록 현황 통합 시스템"
    page_icon: str = "🚗"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    sidebar_title: str = "어디스카(ATHISCar)"
    sidebar_logo: str = "image/athiscar.png"  # 이미지 경로는 여기에 따로 분리합니다.
    sidebar_caption: str = "자동차 등록 현황 통합 시스템"
    footer_caption: str = "SKN35_1st_Project_Group5"