# 1. 자동차 등록 현황 조회 쿼리
SELECT_REGISTRATION_QUERY = """
SELECT regist_id, company_type, company_name, model_name, count_car_month, standard_month
FROM car_registration
ORDER BY standard_month DESC
"""

# 2. 브랜드 랭킹 조회 쿼리
SELECT_BRAND_RANKING_QUERY = """
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

# 3. 모델 랭킹 조회 쿼리
SELECT_MODEL_RANKING_QUERY = """
SELECT m.model_id, 
        m.regist_id, 
        m.brand_name, 
        m.standard_month AS standard_ym, 
        m.compare_car_month AS mom_increase,
        r.model_name AS car_name,
        r.count_car_month AS registration_count,
        r.company_type AS manufacturer_type,
        '휘발유/디젤/전기' AS fuel_type
FROM car_model_ranking m
LEFT JOIN car_registration r ON m.regist_id = r.regist_id
ORDER BY m.standard_month DESC
"""

# 4. 리뷰 및 리뷰 상세 조인 조회 쿼리 (domain_type: 1=종합, 2=성능, 3=가격, 4=문제점)
SELECT_REVIEW_QUERY = """
SELECT r.review_id,
       r.model_id,
       r.regist_id,
       r.brand_name_review AS brand_name,
       MAX(CASE WHEN t.domain_type = '1' THEN t.total_score END) AS overall_rating,
       MAX(CASE WHEN t.domain_type = '1' THEN t.total_review_content END) AS performance,
       MAX(CASE WHEN t.domain_type = '1' THEN t.total_review_title END) AS issues,
       MAX(CASE WHEN t.domain_type = '2' THEN t.total_score END) AS perform_score,
       MAX(CASE WHEN t.domain_type = '2' THEN t.total_review_title END) AS perform_title,
       MAX(CASE WHEN t.domain_type = '3' THEN t.total_score END) AS price_score,
       MAX(CASE WHEN t.domain_type = '3' THEN t.total_review_title END) AS price_title,
       MAX(CASE WHEN t.domain_type = '4' THEN t.total_score END) AS fault_score,
       MAX(CASE WHEN t.domain_type = '4' THEN t.total_review_title END) AS fault_title
FROM review r
LEFT JOIN total_review t ON r.review_id = t.review_id2
GROUP BY r.review_id, r.model_id, r.regist_id, r.brand_name_review
"""

# 5. FAQ 조회 쿼리
SELECT_FAQ_QUERY = """
SELECT faq_id, question, answer 
FROM faq 
ORDER BY faq_id ASC
"""

# 6. 모델 랭킹 및 리뷰 퍼지 매칭 조회 쿼리
SELECT_REVIEW_MODEL_MATCH_QUERY = """
SELECT DISTINCT
    r.review_id,
    r.brand_name_review AS 리뷰브랜드명,
    cm.model_id,
    cm.brand_name AS 모델별브랜드명,
    cr.model_name AS 자동차등록제조사
FROM
    review r
LEFT JOIN 
    car_model_ranking cm 
    ON REPLACE(r.brand_name_review, ' ', '') LIKE CONCAT('%', REPLACE(cm.brand_name, ' ', ''), '%')
    OR REPLACE(cm.brand_name, ' ', '') LIKE CONCAT('%', REPLACE(r.brand_name_review, ' ', ''), '%')
LEFT JOIN
    car_registration cr
    ON REPLACE(r.brand_name_review, ' ', '') LIKE CONCAT('%', REPLACE(cr.model_name, ' ', ''), '%')
    OR REPLACE(cr.model_name, ' ', '') LIKE CONCAT('%', REPLACE(cr.model_name, ' ', ''), '%')
"""