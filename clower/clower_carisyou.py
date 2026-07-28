import time
import uuid
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import text

# db.py에서 SQLAlchemy 엔진 가져오기
from db import get_engine

def generate_month_list(start_ym: str, count: int):
    year, month = map(int, start_ym.split("-"))
    month_list = []
    
    for _ in range(count):
        month_list.append(f"{year}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
            
    return month_list

def save_multi_crawling_to_db():
    # 1. 277부터 255까지 2씩 감소하는 ID 리스트 (총 12개)
    page_ids = list(range(276, 253, -2))
    
    # 2. 2026-06부터 2025-07까지 12개월 연월 리스트 생성
    month_list = generate_month_list("2026-06", len(page_ids))
    
    # URL ID와 연월 짝지어 매핑
    target_tasks = list(zip(page_ids, month_list))

    # DB 엔진 가져오기
    engine = get_engine()
    driver = webdriver.Chrome()

    try:
        print(f"🚀 총 {len(target_tasks)}개 페이지 데이터 수집 및 DB 저장 시작...\n")

        for page_id, standard_month in target_tasks:
            target_url = f"https://www.carisyou.com/theme/top10/{page_id}"
            company_type = "국산"

            print(f"📌 [처리 중] ID: {page_id} | 기준월: {standard_month}")
            driver.get(target_url)
            time.sleep(2)  # 페이지 로딩 대기

            items = driver.find_elements(By.CSS_SELECTOR, "div.sale_rank_list ol > li")
            car_data_list = []

            for item in items:
                try:
                    # 1. 모델명 추출
                    car_info_element = item.find_element(By.CSS_SELECTOR, "span.car_info")
                    model_name = car_info_element.text.strip()

                    # 2. 월별 등록 개수 추출 (DB 타입이 VARCHAR이므로 문자열 형태 그대로 저장)
                    sale_count_element = item.find_element(By.CSS_SELECTOR, "span.sale_count span")
                    count_car_month = sale_count_element.text.strip().replace(",", "")

                    # 3. 제조사 추출
                    company_name = model_name.split()[0] if " " in model_name else model_name

                    # 4. regist_id 고유값 생성 (UUID 활용)
                    # PK인 regist_id가 VARCHAR(255) 지정되었으므로 중복 없는 고유 문자열 생성
                    regist_id = str(uuid.uuid4())

                    car_data_list.append({
                        "regist_id": regist_id,             # PK 고유 키
                        "company_type": company_type,         # '수입'
                        "company_name": company_name,         # '테슬라', 'BMW' 등
                        "model_name": model_name,             # '테슬라 모델 Y'
                        "count_car_month": count_car_month,   # '9188' (VARCHAR)
                        "standard_month": standard_month      # '2026-06'
                    })

                except Exception:
                    continue

            if car_data_list:
                df = pd.DataFrame(car_data_list)
                with engine.begin() as conn:
                    # 재실행 시 중복 적재 방지를 위해 동일 기준월 & 구분 데이터 삭제
                    conn.execute(
                        text("""
                            DELETE FROM car_registration 
                            WHERE standard_month = :s_month AND company_type = :c_type
                        """),
                        {"s_month": standard_month, "c_type": company_type}
                    )

                df.to_sql(
                    name="car_registration",
                    con=engine,
                    if_exists="append",
                    index=False
                )

                print(f"   └  [{standard_month}] {len(df)}건 DB 저장 완료!")
            else:
                print(f"   └ ⚠️ 수집된 데이터가 없습니다.")

            print("-" * 65)
            time.sleep(1)

        print("\n🎉 모든 기간 데이터의 크롤링 및 DB 저장이 완벽하게 완료되었습니다!")

    except Exception as e:
        print(f"❌ 작업 중 오류 발생: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    save_multi_crawling_to_db()