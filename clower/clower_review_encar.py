import os
import time
import pymysql
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_DATABASE", "cars_db")

url = "https://www.encar.com/mocha.do"


def get_db_connection():
  return pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      port=int(DB_PORT),
      charset="utf8mb4",
  )


def click_until_hidden(driver, timeout=10):
  button_locator = (By.CSS_SELECTOR, "#btnInfoMore")

  while True:
    try:
      button = driver.find_element(*button_locator)

      is_displayed = driver.execute_script(
          "return window.getComputedStyle(arguments[0]).display !== 'none';",
          button,
      )

      if not is_displayed:
        print("버튼이 display: none 상태가 되어 클릭을 중단합니다.")
        break

      try:
        button.click()
      except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", button)

      print("더보기 버튼 클릭 완료")
      time.sleep(0.5)

    except (NoSuchElementException, StaleElementReferenceException):
      print("더보기 버튼을 찾을 수 없거나 끝까지 로딩되었습니다.")
      break


def for_in_print(elem_lists, title):
  for elem in elem_lists:
    text = elem.text.strip()
    if text:
      print(f"[{title}:] {text}")


def insert_review_datas(
    index, cursor, title, content, score, domain_type
):
  sql_total_review = """
                       INSERT INTO total_review
                       (total_review_id, review_id2, total_review_title, total_review_content, total_score, domain_type)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """
  total_review_id = f"{index}_{domain_type}"
  total_review_data = (
      total_review_id,
      str(index),
      title,
      content,
      score,
      domain_type,
  )
  cursor.execute(sql_total_review, total_review_data)


def print_detail_texts(driver, index,car_name):
  connection = get_db_connection()
  try:
    #car_name_selector = "#mocha_car > h3 > a"
    area_detail = "#depth_main > div > div.box_g.box_total > div.area_detail"
    area_review = "#depth_main > div > div.box_g.box_total > div.area_review"
    perform_detail = (
        "#depth_main > div > div.box_g.box_perform > div.area_summary"
    )
    price_detail = "#depth_main > div > div.box_g.box_price > div.area_summary"
    fault_detail = "#depth_main > div > div.box_g.box_faulty > div.area_summary"

    # car_name_elem = WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, car_name_selector))
    # )
    area_detail_container = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, area_detail))
    )
    area_review_container = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, area_review))
    )
    perform_detail_container = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, perform_detail))
    )
    price_detail_container = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, price_detail))
    )
    fault_detail_container = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, fault_detail))
    )

    area_detail_elements = area_detail_container.find_elements(
        By.CSS_SELECTOR, "strong, p"
    )
    area_review_elements = area_review_container.find_elements(
        By.CSS_SELECTOR, "strong"
    )
    perform_detail_elements = perform_detail_container.find_elements(
        By.CSS_SELECTOR, "strong, span"
    )
    price_detail_elements = price_detail_container.find_elements(
        By.CSS_SELECTOR, "strong, span"
    )
    fault_detail_elements = fault_detail_container.find_elements(
        By.CSS_SELECTOR, "strong, span"
    )

    # 콘솔 출력용
    for elem in area_detail_elements:
      text = elem.text.strip()
      if text:
        print(f"[{elem.tag_name}] {text}")

    for_in_print(area_review_elements, "종합 리뷰")
    for_in_print(perform_detail_elements[0:2], "성능")
    for_in_print(price_detail_elements[0:2], "가격")
    for_in_print(fault_detail_elements[0:2], "문제점")

    # 데이터 파싱
    car_name = car_name.split("(")[0].replace("-"," ").strip()

    detail_title = (
        area_detail_elements[0].text.strip()
        if len(area_detail_elements) > 0
        else ""
    )
    detail_content = (
        area_detail_elements[1].text.strip()
        if len(area_detail_elements) > 1
        else ""
    )
    detail_score = (
        area_review_elements[0].text.strip()
        if len(area_review_elements) > 0
        else "0"
    )

    perform_title = (
        perform_detail_elements[0].text.strip()
        if len(perform_detail_elements) > 0
        else ""
    )
    perform_score = (
        perform_detail_elements[1].text.strip()
        if len(perform_detail_elements) > 1
        else "0"
    )

    price_title = (
        price_detail_elements[0].text.strip()
        if len(price_detail_elements) > 0
        else ""
    )
    price_score = (
        price_detail_elements[1].text.strip()
        if len(price_detail_elements) > 1
        else "0"
    )

    fault_title = (
        fault_detail_elements[0].text.strip()
        if len(fault_detail_elements) > 0
        else ""
    )
    fault_score = (
        fault_detail_elements[1].text.strip()
        if len(fault_detail_elements) > 1
        else "0"
    )

    try:
      with connection.cursor() as cursor:
        # 1. review 테이블 INSERT (중복 발생 시 에러 방지용 ON DUPLICATE KEY UPDATE 추가)
        sql_review = """
                     INSERT INTO review (review_id, model_id, regist_id, brand_name_review)
                     VALUES (%s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE brand_name_review = VALUES(brand_name_review)
                     """
        review_data = (str(index), "1", "1", car_name)
        cursor.execute(sql_review, review_data)

        # 2. total_review 테이블 INSERT (영역별 4개 데이터 입력)
        insert_review_datas(
            index, cursor, detail_title, detail_content, detail_score, "1"
        )
        insert_review_datas(
            index, cursor, perform_title, "", perform_score, "2"
        )
        insert_review_datas(index, cursor, price_title, "", price_score, "3")
        insert_review_datas(index, cursor, fault_title, "", fault_score, "4")

        connection.commit()
        print(f"[{index}번째 차량] 모든 테이블 데이터 삽입 완료!")

    except Exception as e:
      connection.rollback()
      print(f"데이터 삽입 실패: {e}")

  except TimeoutException:
    print("페이지 요소 로딩 시간 초과")
  finally:
    connection.close()


def open_links_and_scrape(driver, start_idx):
  main_window = driver.current_window_handle
  links = driver.find_elements(By.CSS_SELECTOR, "#list_mocha li a")
  href_list = [link.get_attribute("href") for link in links if link.get_attribute("href")]

  print(f"총 {len(href_list)}개의 링크를 발견했습니다.")
  current_idx = start_idx

  for href in [link for link in links if link.get_attribute("href")]:
    alink = href.get_attribute("href")
    car_name =  href.find_elements(By.CSS_SELECTOR, "strong")
    car_name =  car_name[0].text

    print(f"\n--- [전체 순번: {current_idx}] 링크 처리 중 ---")
    driver.execute_script("window.open(arguments[0], '_blank');", alink)
    all_windows = driver.window_handles
    driver.switch_to.window(all_windows[-1])
    print_detail_texts(driver, current_idx, car_name)

    driver.close()
    driver.switch_to.window(main_window)
    current_idx += 1
    time.sleep(0.3)

  return current_idx  # 다음 페이지를 위해 마지막 인덱스 반환


# 메인 실행 루프
try:
  global_idx = 1  # 전체 크롤링 과정에서 유일한 번호를 유지할 변수

  for i in ["001","003","087","013","012","035","017","031","011","054"]:
    if i == 6:
      continue
    target_url = f"{url}?mnfccd={i}"
    print(f"\n==========================================")
    print(f"페이지 이동: {target_url}")
    print(f"==========================================")

    driver.get(target_url)
    time.sleep(1)

    click_until_hidden(driver)
    # 반환된 누적 인덱스를 다시 global_idx에 반영
    global_idx = open_links_and_scrape(driver, global_idx)

finally:
  driver.quit()