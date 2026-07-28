# 🚗 Auto Insight — 자동차 등록 현황 통합 시스템

## 👥 팀

SKN35 1기 5조 (SKNETWORKS-FAMILY-AICAMP)

<table>
  <tr>
    <td align="center"><img src="image/p1.png" width="120"/></td>
    <td align="center"><img src="image/p2.png" width="120"/></td>
    <td align="center"><img src="image/p3.png" width="120"/></td>
    <td align="center"><img src="image/p4.png" width="120"/></td>
  </tr>
  <tr>
    <td align="center"><b>손채영</b><br/>DB 설계<br/>(모델별, 리뷰)데이터 연동<br/>모델별 랭킹 · 리뷰 Dialog<br/>Git 관리<br/>프로젝트 폴더 정리<br/>UI/CSS 수정</td>
    <td align="center"><b>차윤정</b><br/>DB설계<br/>PPT 작성<br/>Git 관리<br/>FAQ 데이터 연동 및 관리</td>
    <td align="center"><b>유지호</b><br/>웹 크롤링(엔카 사이트)<br/>db설계(리뷰)<br/>Git 관리<br/>최종 ui  수정</td>
    <td align="center"><b>김경민</b><br/>DB설계<br/>DB데이터 저장(차 등록 현황)<br/>Streamlit<br/> UI 설정<br/>Git 관리<br/>웹 크롤링(카이즈유)</td>
  </tr>
</table>


<br>
국내 월별 자동차 신규 등록 데이터를 수집·적재하고, 브랜드/모델별 랭킹과 실사용자 리뷰를 한눈에 볼 수 있는 Streamlit 대시보드입니다.
</br>

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://skn35-1st-5team-4la6aeyjw9ycv3cwhetdj9.streamlit.app/)

### 🔗 배포 링크

**https://skn35-1st-5team-4la6aeyjw9ycv3cwhetdj9.streamlit.app/**

> SKN35_1st_Project_Group5

## ✨ 주요 기능

| 메뉴 | 설명 |
| --- | --- |
| 🏠 Home | 전체 등록대수·제조사 수 요약, 월별 등록 추이 그래프, 리뷰 키워드 검색 |
| 📋 자동차 등록 현황 | 월별 등록 데이터 조회, 행 클릭 시 모델별 등록 추이 팝업 |
| 🏆 브랜드별 랭킹 | 연/월/국산·수입 구분 필터, 전월 대비 증감 표시 |
| 🚘 모델별 랭킹 | 등록대수 기준 모델 순위, 모델별 실사용자 리뷰(평점/성능/가격/문제점) 보기 |
| ❓ FAQ | 자주 묻는 질문 아코디언, 1:1 문의 링크 |

## 🛠️ 기술 스택

- **Frontend/App**: Streamlit, streamlit-option-menu, Plotly
- **Data**: pandas, SQLAlchemy, PyMySQL
- **DB**: TiDB Cloud (MySQL 호환)
- **크롤링**: Selenium, webdriver-manager
- **패키지 관리**: [uv](https://docs.astral.sh/uv/)

## 📦 필요한 라이브러리 / 설치

### 실행 환경

- Python 3.12 이상
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (패키지 매니저)

### 앱 실행에 필요한 라이브러리 (`uv sync`로 자동 설치)

`pyproject.toml`에 정의되어 있으며 `pandas`는 Streamlit의 의존성으로 함께 설치됩니다.

| 라이브러리 | 용도 |
| --- | --- |
| streamlit | 웹 앱 프레임워크 |
| streamlit-option-menu | 사이드바 메뉴 UI |
| plotly | 추이/상세 차트 |
| sqlalchemy | DB 엔진/쿼리 실행 |
| pymysql | MySQL(TiDB) 드라이버 |
| mysql-connector-python | MySQL 접속 보조 드라이버 |
| python-dotenv | `.env` 환경 변수 로드 |
| certifi | TiDB Cloud SSL 인증서 |

## 📁 프로젝트 구조

```text
SKN35-1st-5Team/
├── app.py                        # 진입점: 페이지 설정, 사이드바 라우팅
├── db.py                         # SQLAlchemy 엔진 및 DB 초기화
├── data_loader.py                # 화면별 데이터 로드 (st.cache_data)
├── dialogs.py                    # 상세 추이 / 리뷰 팝업(dialog) 모음
├── constants.py                  # 브랜드 로고 · 차량 이미지 매핑
├── config/
│   ├── dataclasses.py            # 앱 메타 설정(AppConfig)
│   └── enums.py                  # 사이드바 메뉴 정의
├── styles/
│   └── styles.py                 # 전역 커스텀 CSS, 사이드바 메뉴 스타일
├── sql/
│   ├── select_tables.py          # 조회 쿼리 모음
│   └── test_qna_table.py         # 테이블 생성 DDL, FAQ 초기 데이터
├── views/
│   ├── home.py                   # 홈 화면
│   ├── registration.py           # 자동차 등록 현황
│   ├── brand_ranking.py          # 브랜드별 랭킹
│   ├── model_ranking.py          # 모델별 랭킹
│   └── faq.py                    # FAQ
├── clower/                       # Selenium 크롤링 스크립트
│   ├── clower_carisyou.py        # carisyou.com → 월별 등록 현황 수집
│   └── clower_review_encar.py    # encar.com → 실사용자 리뷰 수집
└── image/                        # 로고 · ERD 등 문서/에셋 이미지
    ├── athiscar.png
    └── erd.png
```

## 🗄️ ERD

![ERD](image/erd.png)

## 🚀 로컬에서 실행하기

바로 사용해보려면 위 배포 링크로 접속하면 됩니다. 아래는 코드를 직접 실행/개발할 때의 절차입니다.

### 1. 클론 및 라이브러리 설치

```bash
git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN35-1st-5Team.git
cd SKN35-1st-5Team
uv sync
```

### 2. DB 테이블 초기화 (최초 1회)

```bash
uv run python db.py
```

### 3. 앱 실행

```bash
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## 📊 데이터 파이프라인

1. `clower/` 스크립트가 carisyou.com(등록 현황), encar.com(리뷰) 데이터를 크롤링
2. `db.py` / `sql/`을 통해 TiDB에 적재
3. `data_loader.py`가 `@st.cache_data`로 조회 결과를 캐싱해 각 화면에 전달
4. `views/` 각 화면이 필터링·페이지네이션 후 표 및 카드 UI로 렌더링
