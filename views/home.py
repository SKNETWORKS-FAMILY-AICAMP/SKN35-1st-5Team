import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import random
from db import get_engine
from dialogs import show_review_dialog
from data_loader import load_registration_data, load_model_ranking_data, load_review_data, load_faq_data
from constants import LOGO_URL_MAP, DEFAULT_CAR_IMAGE

ATHISCAR_LOGO_PATH = Path(__file__).resolve().parent.parent / "image" / "athiscar.png"


@st.cache_data
def _load_logo_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _flatten_html(html):
    """st.markdown은 Markdown 파서를 거치므로, 빈 줄 뒤에 들여쓰기된 줄이 오면
    코드블록으로 오인되어 태그가 그대로 노출된다(예: logo_html이 빈 문자열일 때).
    각 줄의 선행 공백을 제거하고 빈 줄은 아예 없애 이를 방지한다."""
    lines = (line.strip() for line in html.strip().splitlines())
    return "\n".join(line for line in lines if line)


def section_title(title, caption, logo_path: Path | None = None):
    logo_html = ""
    if logo_path and logo_path.exists():
        logo_b64 = _load_logo_base64(logo_path)
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo" alt="로고"/>'

    html = f"""
        <div class="hero">
            <div class="hero-content-row">
                {logo_html}
                <div class="hero-text-block">
                    <h1>{title}</h1>
                    <div class="subtext">{caption}</div>
                </div>
            </div>
        </div>
        """
    st.markdown(_flatten_html(html), unsafe_allow_html=True)

@st.fragment(run_every=2)
def rotating_logos():
    shuffled_logos = list(LOGO_URL_MAP.items())
    random.shuffle(shuffled_logos)
    cols = st.columns(len(shuffled_logos))
    for idx, (brand, url) in enumerate(shuffled_logos):
        with cols[idx % len(cols)]:
            st.image(url, width=45)

def home_view():
    registration_df = load_registration_data()
    model_ranking_df = load_model_ranking_data()
    review_df = load_review_data()
    faq_df = load_faq_data()

    section_title(
        "전국 자동차 등록 현황 대시보드 (Home)",
        "주요 통계 요약 및 월별 등록 추이, 차량 리뷰 검색 기능을 제공합니다.",
        logo_path=ATHISCAR_LOGO_PATH,
    )

    total_count = (
        int(registration_df["registration_count"].sum())
        if not registration_df.empty and "registration_count" in registration_df.columns
        else 0
    )
    manufacturer_count = (
        registration_df["manufacturer"].nunique()
        if not registration_df.empty and "manufacturer" in registration_df.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("전체 등록대수", f"{total_count:,}대")
    with c2:
        st.metric("제조사 수", f"{manufacturer_count}개")
    with c3:
        st.metric("FAQ 수", f"{len(faq_df)}건")

    st.divider()

    st.markdown("### 주요 제조사 로고")
    rotating_logos()

    st.divider()

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### 📈 월별 총 등록 추이")
        if not registration_df.empty and "standard_ym" in registration_df.columns:
            month_df = (
                registration_df.groupby("standard_ym", as_index=False)["registration_count"]
                .sum()
                .sort_values("standard_ym")
            )
            st.line_chart(month_df.set_index("standard_ym"), use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with right_col:
        st.markdown("### 🔍 차량 리뷰 및 평가 검색")
        st.caption("리뷰 내용(제목, 내용 등)에 포함된 키워드를 입력해보세요.")

        review_keyword = st.text_input(
            "리뷰 검색어 입력",
            placeholder="예: 소음, 가속, 현대, 승차감",
            key="home_review_search",
        )

        if not review_keyword.strip():
            st.info("💡 검색어를 입력하시면 관련 차량 리뷰 목록이 표출됩니다.")
        else:
            if review_df.empty:
                st.info("연동된 리뷰 데이터가 없습니다.")
            else:
                mask = False
                for col in ["performance", "issues", "brand_name", "price"]:
                    if col in review_df.columns:
                        mask = mask | review_df[col].astype(str).str.contains(review_keyword, case=False, na=False)

                result_review = review_df[mask].copy()

                if result_review.empty:
                    st.warning(f"'{review_keyword}'에 대한 검색 결과가 없습니다.")
                else:
                    st.caption(f"총 **{len(result_review)}건**의 리뷰가 검색되었습니다.")

                    display_cols = ["logo", "brand_name", "performance", "issues"]

                    event = st.dataframe(
                        result_review[display_cols],
                        use_container_width=True,
                        hide_index=True,
                        selection_mode="single-row",
                        on_select="rerun",
                        key="home_review_search_table",
                        column_config={
                            "logo": st.column_config.ImageColumn("로고", width="small"),
                            "brand_name": "차명(모델명)",
                            "performance": "리뷰 내용",
                            "issues": "제목",
                        },
                    )

                    selected_rows = event.selection.get("rows", [])
                    if selected_rows:
                        selected_idx = selected_rows[0]
                        selected_data = result_review.iloc[selected_idx]
                        model_id = selected_data["model_id"]

                        matched_model = model_ranking_df[model_ranking_df["model_id"] == model_id]

                        if not matched_model.empty:
                            car_name = matched_model.iloc[0]["car_name"]
                            car_image_url = matched_model.iloc[0]["car_image"]
                        else:
                            car_name = f"{selected_data['brand_name']} 차량"
                            car_image_url = DEFAULT_CAR_IMAGE

                        logo_url = selected_data["logo"]
                        matched_reviews = review_df[review_df["model_id"] == model_id]

                        show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)