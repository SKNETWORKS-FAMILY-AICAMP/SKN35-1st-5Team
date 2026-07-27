from enum import Enum
from typing import List

class MenuOption(Enum):
    HOME = ("Home", "house")
    REGISTRATION = ("자동차 등록 현황", "clipboard-data")
    BRAND_RANKING = ("브랜드별 랭킹", "trophy")
    MODEL_RANKING = ("모델별 랭킹", "car-front")
    FAQ = ("FAQ", "question-circle")

    def __init__(self, label: str, icon: str):
        self._label = label
        self._icon = icon

    @property
    def label(self) -> str:
        return self._label

    @property
    def icon(self) -> str:
        return self._icon

    @classmethod
    def labels(cls) -> List[str]:
        return [item.label for item in cls]

    @classmethod
    def icons(cls) -> List[str]:
        return [item.icon for item in cls]