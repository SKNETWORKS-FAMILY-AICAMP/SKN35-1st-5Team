import pandas as pd
import streamlit as st

from db import get_engine
from constants import LOGO_URL_MAP, CAR_IMAGE_URL_MAP, DEFAULT_LOGO, DEFAULT_CAR_IMAGE

# ---------------------------------------------------------
# DB 데이터 로드 함수 (실제 DB 컬럼명 적용)
# ---------------------------------------------------------


@st.cache_data(ttl=3600)
def load_registration_data():
    """1. car_registration 테이블 데이터 로드"""
    engine = get_engine()
    query = """
    SELECT regist_id, company_type, company_name, model_name, count_car_month, standard_month
    FROM car_registration
    ORDER BY standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
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
    query = """
    SELECT b.brand_id, 
           b.regist_id, 
           b.brand_name, 
           b.brand_standard_month AS standard_ym, 
           b.compare_car_month AS mom_increase,
           r.count_car_month AS registration_count,
           r.company_type AS manufacturer_type
    FROM car_brand_rank b
    LEFT JOIN car_registration r ON b.regist_id = r.regist_id
    ORDER BY b.brand_standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["registration_count"] = pd.to_numeric(df["registration_count"], errors="coerce").fillna(0).astype(int)
        df["mom_increase"] = pd.to_numeric(df["mom_increase"], errors="coerce").fillna(0).astype(int)
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df


@st.cache_data(ttl=3600)
def load_model_ranking_data():
    """3. car_model_ranking 테이블 데이터 로드 (테이블명: car_model_ranking)"""
    engine = get_engine()
    query = """
    SELECT m.model_id, 
           m.regist_id, 
           m.brand_name, 
           m.standard_month AS standard_ym, 
           m.compare_car_month AS mom_increase,
           r.model_name AS car_name,
           r.count_car_month AS registration_count,
           r.company_type AS manufacturer_type,
           '휘발유/디젤/전기' AS fuel_type  -- 기본 표시용
    FROM car_model_ranking m
    LEFT JOIN car_registration r ON m.regist_id = r.regist_id
    ORDER BY m.standard_month DESC
    """
    df = pd.read_sql(query, con=engine)
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
    query = """
    SELECT r.review_id,
           r.model_id,
           r.regist_id,
           r.brand_name_review AS brand_name,
           t.total_score AS overall_rating,
           t.total_review_content AS performance,
           t.domain_type AS price,
           t.total_review_title AS issues
    FROM review r
    LEFT JOIN total_review t ON r.review_id = t.review_id2
    """
    df = pd.read_sql(query, con=engine)
    if not df.empty:
        df["logo"] = df["brand_name"].map(LOGO_URL_MAP).fillna(DEFAULT_LOGO)
    return df


@st.cache_data(ttl=3600)
def load_faq_data():
    """5. faq 테이블 데이터 로드"""
    engine = get_engine()
    query = "SELECT faq_id, question, answer FROM faq ORDER BY faq_id ASC"
    return pd.read_sql(query, con=engine)
