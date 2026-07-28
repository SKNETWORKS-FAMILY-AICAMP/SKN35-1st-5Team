import pandas as pd
import streamlit as st
from sqlalchemy import text

from constants import CAR_IMAGE_URL_MAP, DEFAULT_CAR_IMAGE, DEFAULT_LOGO, LOGO_URL_MAP
from db import get_engine
from sql import select_tables

# ---------------------------------------------------------
# DB 데이터 로드 함수 (실제 DB 컬럼명 적용)
# ---------------------------------------------------------


def _resolve_brand_logo(brand_text):
    """review.brand_name은 '테슬라 모델 3'처럼 브랜드+모델명이 섞여 있어
    정확히 일치하는 키가 없으므로, 텍스트에 포함된 브랜드명을 찾아 로고를 매칭한다."""
    text_value = str(brand_text) if brand_text else ""
    for brand, logo_url in LOGO_URL_MAP.items():
        if brand in text_value:
            return logo_url
    return DEFAULT_LOGO


@st.cache_data(ttl=3600)
def load_registration_data():
    """1. car_registration 테이블 데이터 로드"""
    engine = get_engine()
    df = pd.read_sql(select_tables.SELECT_REGISTRATION_QUERY, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["count_car_month"], errors="coerce").fillna(0).astype(int)
        df["manufacturer"] = df["company_name"]
        df["car_model_type"] = df["model_name"]
        df["standard_ym"] = df["standard_month"]
        df["manufacturer_type"] = df["company_type"]
        df["logo"] = df["manufacturer"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
        df["car_image"] = df["car_model_type"].map(CAR_IMAGE_URL_MAP).fillna(DEFAULT_CAR_IMAGE)
    return df


@st.cache_data(ttl=3600)
def load_brand_ranking_data():
    """2. car_brand_rank 테이블 데이터 로드"""
    engine = get_engine()
    df = pd.read_sql(select_tables.SELECT_BRAND_RANKING_QUERY, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["mom_increase"] = pd.to_numeric(df["mom_increase"], errors="coerce").fillna(0).astype(int)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df


@st.cache_data(ttl=3600)
def load_model_ranking_data():
    """3. car_model_ranking 테이블 데이터 로드"""
    engine = get_engine()
    df = pd.read_sql(select_tables.SELECT_MODEL_RANKING_QUERY, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["mom_increase"] = pd.to_numeric(df["mom_increase"], errors="coerce").fillna(0).astype(int)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
        df["car_image"] = df["car_name"].map(CAR_IMAGE_URL_MAP).fillna(DEFAULT_CAR_IMAGE)
    return df


@st.cache_data(ttl=3600)
def load_review_data():
    """4. review 및 total_review 테이블 조인 데이터 로드"""
    engine = get_engine()
    df = pd.read_sql(select_tables.SELECT_REVIEW_QUERY, con=engine)
    if not df.empty:
        df["logo"] = df["brand_name"].apply(_resolve_brand_logo)
        for score_col in ["overall_rating", "perform_score", "price_score", "fault_score"]:
            df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_faq_data():
    """5. faq 테이블 데이터 로드"""
    engine = get_engine()
    return pd.read_sql(select_tables.SELECT_FAQ_QUERY, con=engine)


# 모델 랭킹에서 리뷰 가져오는 퍼지 매칭 데이터
@st.cache_data(ttl=3600)
def load_review_model_match_data():
    engine = get_engine()
    return pd.read_sql(text(select_tables.SELECT_REVIEW_MODEL_MATCH_QUERY), con=engine)