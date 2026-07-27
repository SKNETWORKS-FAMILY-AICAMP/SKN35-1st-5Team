import streamlit as st
<<<<<<< Updated upstream
from views.home import load_model_ranking_data, load_review_data, section_title, DEFAULT_CAR_IMAGE
from views.brand_ranking import render_filter
from dialogs import show_review_dialog  # 프로젝트 구조에 맞춰 수정
=======
import math
from views.home import (
    load_model_ranking_data,
    load_review_data,
    section_title,
    show_review_dialog,
)
from views.brand_ranking import render_filter
from constants import CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE
>>>>>>> Stashed changes

def model_ranking_view():
    # 함수 내부에서 직접 데이터 로드
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
    if target_ym and "standard_ym" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["standard_ym"] == target_ym]
    if target_type != "전체" and "manufacturer_type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["manufacturer_type"] == target_type]

<<<<<<< Updated upstream
    if filtered_df.empty:
        st.info("선택한 조건에 해당하는 모델 랭킹 데이터가 없습니다.")
        return

    top10_df = filtered_df.sort_values(by="registration_count", ascending=False).head(10).reset_index(drop=True)

    display_cols = ["logo", "brand_name", "car_name", "fuel_type", "registration_count", "mom_increase"]
    existing_cols = [c for c in display_cols if c in top10_df.columns]

    event = st.dataframe(
        top10_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="model_rank_table",
        column_config={
            "logo": st.column_config.ImageColumn("로고", width="small"),
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "fuel_type": "연료",
            "registration_count": st.column_config.NumberColumn("등록대수", format="%d 대"),
            "mom_increase": st.column_config.NumberColumn("전월 대비", format="%+d 대"),
        },
    )

    download_df = top10_df[existing_cols].rename(
        columns={
            "brand_name": "브랜드",
            "car_name": "차량이름",
            "fuel_type": "연료",
            "registration_count": "등록대수",
            "mom_increase": "전월대비 증가량",
        }
    ).drop(columns=["logo"], errors="ignore")
    
    st.download_button(
        "모델별 Top 10 데이터 다운로드 (CSV)",
        download_df.to_csv(index=False).encode("utf-8-sig"),
        f"모델_Top10_{target_type}_{target_ym}.csv",
        "text/csv",
        use_container_width=True,
=======
    agg_cols = {"registration_count": "sum"}
    for col in ["model_id", "logo", "car_image"]:
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
>>>>>>> Stashed changes
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
            f"<div style='text-align: center; font-weight: bold; padding-top: 6px;'>페이지 {st.session_state.model_rank_page} / {total_pages} (총 {total_items}개 모델)</div>",
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

    # 카드형태 UI 커스텀 스타일
    st.markdown(
        """
        <style>
        .car-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
        }
        .car-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 6px rgba(59,130,246,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 10개 항목 카드 리스트 렌더링
    for idx, row in page_df.iterrows():
        global_rank = start_idx + idx + 1
        brand_name = row.get("brand_name", "")
        car_name = row.get("car_name", "")
        logo_url = row.get("logo", "")
        car_image_url = row.get("car_image", DEFAULT_CAR_IMAGE)
        reg_count = row.get("registration_count", 0)
        model_id = row.get("model_id")

        with st.container():
            st.markdown(f"<div class='car-card'>", unsafe_allow_html=True)
            
            # 레이아웃: [순위(1)] [로고/브랜드(2)] [차량사진(3)] [차량이름 및 대수(4)] [리뷰 버튼(2)]
            col_rank, col_brand, col_img, col_info, col_action = st.columns([1, 2, 3, 3, 2])

            with col_rank:
                st.markdown(f"<h3 style='margin: 0; color: #2563eb;'>{global_rank}위</h3>", unsafe_allow_html=True)

            with col_brand:
                if logo_url:
                    st.image(logo_url, width=45)
                st.markdown(f"<b style='font-size: 0.95rem; color: #4b5563;'>{brand_name}</b>", unsafe_allow_html=True)

            with col_img:
                if car_image_url:
                    st.image(car_image_url, width=130)

            with col_info:
                st.markdown(f"<h4 style='margin: 5px 0 0 0;'>{car_name}</h4>", unsafe_allow_html=True)
                st.caption(f"등록 대수: {reg_count:,} 대")

            with col_action:
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                if st.button("💬 리뷰 보기", key=f"btn_review_{global_rank}_{model_id}"):
                    matched_reviews = (
                        review_df[review_df["model_id"] == model_id]
                        if not review_df.empty and "model_id" in review_df.columns
                        else review_df.iloc[0:0]
                    )
                    show_review_dialog(car_name, logo_url, car_image_url, matched_reviews)

            st.markdown("</div>", unsafe_allow_html=True)

    # 하단 페이징 버튼 한번 더 제공 (편의성)
    st.markdown("<br>", unsafe_allow_html=True)
    c_b1, c_b2, c_b3 = st.columns([2, 6, 2])
    with c_b1:
        if st.button("◀ 이전 페이지", use_container_width=True, key="bottom_prev", disabled=(st.session_state.model_rank_page <= 1)):
            st.session_state.model_rank_page -= 1
            st.rerun()
    with c_b2:
        st.markdown(f"<div style='text-align: center; color: #6b7280;'>{st.session_state.model_rank_page} / {total_pages} 페이지</div>", unsafe_allow_html=True)
    with c_b3:
        if st.button("다음 페이지 ▶", use_container_width=True, key="bottom_next", disabled=(st.session_state.model_rank_page >= total_pages)):
            st.session_state.model_rank_page += 1
            st.rerun()