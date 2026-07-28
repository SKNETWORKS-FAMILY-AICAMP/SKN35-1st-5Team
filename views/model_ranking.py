import streamlit as st
import math
from views.home import section_title
from data_loader import load_model_ranking_data, load_review_data
from views.brand_ranking import render_filter
from dialogs import show_review_dialog
from constants import CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE


def _match_reviews_by_car_name(review_df, car_name):
    """regist_id/model_id는 등록 월마다 새로 발급되는 스냅샷 ID라 리뷰와 매칭이 안 되므로,
    브랜드+모델명 텍스트를 정규화해 양방향 부분일치로 매칭한다."""
    if review_df.empty or "brand_name" not in review_df.columns or not car_name:
        return review_df.iloc[0:0]

    target = str(car_name).replace(" ", "").strip()
    if not target:
        return review_df.iloc[0:0]

    normalized = review_df["brand_name"].fillna("").astype(str).str.replace(" ", "", regex=False)
    mask = normalized.apply(lambda name: bool(name) and (name in target or target in name))
    return review_df[mask]


def model_ranking_view():
    model_ranking_df = load_model_ranking_data()
    review_df = load_review_data()

    # 상단 타이틀과 우측 상단 CSV 다운로드 버튼 배치
    c_title, c_btn = st.columns([4, 1])
    with c_title:
        section_title(
            "모델별 랭킹 순위",
            "기준 연월과 국산/수입 구분을 선택하면 등록대수 기준 모델 순위를 조회합니다. (페이지당 10개 표시)",
        )

    if model_ranking_df.empty:
        st.warning("모델별 랭킹 데이터가 존재하지 않습니다.")
        return

    target_ym, target_type = render_filter(model_ranking_df, show_type_filter=True, key_prefix="model_rank")

    filtered_df = model_ranking_df.copy()
    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

    agg_cols = {"registration_count": "sum"}
    for col in ["model_id", "regist_id", "logo", "car_image"]:
        if col in filtered_df.columns:
            agg_cols[col] = "first"

    if target_ym == "ALL":
        agg_source = filtered_df.sort_values("standard_ym", ascending=False)
        display_df = agg_source.groupby(["brand_name", "car_name"], as_index=False).agg(agg_cols)
        display_df["mom_increase"] = 0
    elif target_ym and (target_ym.endswith("-") or target_ym.startswith("-")):
        if target_ym.endswith("-"):
            year_prefix = target_ym.split("-")[0]
            sub_df = filtered_df[filtered_df["standard_ym"].str.startswith(year_prefix)]
        else:
            month_suffix = target_ym.split("-")[1]
            sub_df = filtered_df[filtered_df["standard_ym"].str.endswith(month_suffix)]
        agg_source = sub_df.sort_values("standard_ym", ascending=False)
        display_df = agg_source.groupby(["brand_name", "car_name"], as_index=False).agg(agg_cols)
        display_df["mom_increase"] = 0
    else:
        display_df = filtered_df[filtered_df["standard_ym"] == target_ym].copy()

    if display_df.empty:
        st.info("선택한 조건에 해당하는 모델 랭킹 데이터가 없습니다.")
        return

    # 전체 정렬 (등록대수 기준 내림차순)
    sorted_df = display_df.sort_values(by="registration_count", ascending=False).reset_index(drop=True)
    sorted_df["car_image"] = sorted_df["car_name"].map(CAR_IMAGE_URL_MAP).fillna(DEFAULT_CAR_IMAGE)

    # CSV 다운로드용 데이터 준비
    download_df = sorted_df[["brand_name", "car_name", "registration_count"]].rename(
        columns={
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "registration_count": "등록대수"
        }
    )

    with c_btn:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "📥 CSV 다운로드",
            download_df.to_csv(index=False).encode("utf-8-sig"),
            f"모델_랭킹전체_{target_type}_{target_ym}.csv",
            "text/css",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 페이징 처리 (1페이지당 10개)
    items_per_page = 10
    total_items = len(sorted_df)
    total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

    # 세션 상태 기반 페이지 관리
    if "model_rank_page" not in st.session_state:
        st.session_state.model_rank_page = 1

    # 페이지 번호가 범위를 벗어날 경우 보정
    if st.session_state.model_rank_page > total_pages:
        st.session_state.model_rank_page = total_pages

    # 상단 페이징 컨트롤러 영역
    col_p1, col_p2, col_p3 = st.columns([2, 6, 2])
    with col_p1:
        if st.button("◀ 이전", use_container_width=True, disabled=(st.session_state.model_rank_page <= 1)):
            st.session_state.model_rank_page -= 1
            st.rerun()
    with col_p2:
        st.markdown(
            f"<div class='model-page-indicator'>페이지 {st.session_state.model_rank_page} / {total_pages} (총 {total_items}개 모델)</div>",
            unsafe_allow_html=True
        )
    with col_p3:
        if st.button("다음 ▶", use_container_width=True, disabled=(st.session_state.model_rank_page >= total_pages)):
            st.session_state.model_rank_page += 1
            st.rerun()

    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    # 현재 페이지에 해당하는 데이터 추출
    start_idx = (st.session_state.model_rank_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_df = sorted_df.iloc[start_idx:end_idx].reset_index(drop=True)

    # 10개 항목 리스트 렌더링 (구분선 스타일 적용)
    for idx, row in page_df.iterrows():
        global_rank = start_idx + idx + 1
        brand_name = row.get("brand_name", "")
        car_name = row.get("car_name", "")
        logo_url = row.get("logo", "")
        car_image_url = row.get("car_image", DEFAULT_CAR_IMAGE)
        reg_count = row.get("registration_count", 0)
        model_id = row.get("model_id")

        with st.container():
            # 카드 배경 대신 항목들 사이에 은은한 구분선 추가 (첫 번째 항목 위에는 생략 가능)
            if idx > 0:
                st.markdown("<hr class='model-row-divider'>", unsafe_allow_html=True)

            # 레이아웃: [순위(1)] [로고/브랜드(2)] [차량사진(3)] [차량이름 및 대수(4)] [리뷰 버튼(2)]
            col_rank, col_brand, col_img, col_info, col_action = st.columns([1, 2, 3, 3, 2])

            with col_rank:
                st.markdown(f"<h3 class='model-rank-number'>{global_rank}위</h3>", unsafe_allow_html=True)

            with col_brand:
                if logo_url:
                    st.image(logo_url, width=45)
                st.markdown(f"<b class='model-brand-name'>{brand_name}</b>", unsafe_allow_html=True)

            with col_img:
                if car_image_url:
                    st.image(car_image_url, width=130)

            with col_info:
                st.markdown(f"<h4 class='model-car-name'>{car_name}</h4>", unsafe_allow_html=True)
                st.caption(f"등록 대수: {reg_count:,} 대")

            with col_action:
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                if st.button("💬 리뷰 보기", key=f"btn_review_{global_rank}_{model_id}"):
                    matched_reviews = _match_reviews_by_car_name(review_df, car_name)
                    show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)

    # 하단 페이징 버튼 한번 더 제공 (편의성)
    st.markdown("<br>", unsafe_allow_html=True)
    c_b1, c_b2, c_b3 = st.columns([2, 6, 2])
    with c_b1:
        if st.button("◀ 이전 페이지", use_container_width=True, key="bottom_prev", disabled=(st.session_state.model_rank_page <= 1)):
            st.session_state.model_rank_page -= 1
            st.rerun()
    with c_b2:
        st.markdown(f"<div class='model-page-indicator-sub'>{st.session_state.model_rank_page} / {total_pages} 페이지</div>", unsafe_allow_html=True)
    with c_b3:
        if st.button("다음 페이지 ▶", use_container_width=True, key="bottom_next", disabled=(st.session_state.model_rank_page >= total_pages)):
            st.session_state.model_rank_page += 1
            st.rerun()