from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, \
    StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



options = Options()
options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.encar.com/mocha.do'


def click_until_hidden(driver, timeout=10):
    button_locator = (By.CSS_SELECTOR, "#btnInfoMore")

    while True:
        try:
            button = driver.find_element(*button_locator)

            is_displayed = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).display !== 'none';", button
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

def for_in_print(elem_lists,title):
    for elem in elem_lists:
        text = elem.text.strip()
        if text:
            print(f"[{title}:] {text}")

def print_detail_texts(driver):
    try:
        # 0. 차명 가져오기





        # 1. 기존 상세 영역 (area_detail)의 strong, p 가져오기
        car_name_selector = "#mocha_car > h3 > a"
        area_detail = "#depth_main > div > div.box_g.box_total > div.area_detail"
        area_review = "#depth_main > div > div.box_g.box_total > div.area_review"
        perform_detail = "#depth_main > div > div.box_g.box_perform > div.area_summary"
        price_detail = "#depth_main > div > div.box_g.box_price > div.area_summary"
        fault_detail = "#depth_main > div > div.box_g.box_faulty > div.area_summary"

        car_name_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, car_name_selector)))
        area_detail_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, area_detail)))
        area_review_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, area_review)))
        perform_detail_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, perform_detail)))
        price_detail_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, price_detail)))
        fault_detail_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, fault_detail)))


        area_detail_elements = area_detail_container.find_elements(By.CSS_SELECTOR, "strong, p")
        area_review_elements = area_review_container.find_elements(By.CSS_SELECTOR, "strong")
        perform_detail_elements = perform_detail_container.find_elements(By.CSS_SELECTOR, "strong, span")
        price_detail_elements = price_detail_container.find_elements(By.CSS_SELECTOR, "strong, span")
        fault_detail_container = fault_detail_container.find_elements(By.CSS_SELECTOR, "strong, span")

        #종합 평가
        for elem in area_detail_elements:
            text = elem.text.strip()
            if text:
                print(f"[{elem.tag_name}] {text}")

        # 종합 리뷰
        for_in_print(area_review_elements,"종합 리뷰")
        # 성능
        for_in_print(perform_detail_elements[0:2],"성능")
        # 가격
        for_in_print(price_detail_elements[0:2],"가격")
        # 문제점
        for_in_print(fault_detail_container[0:2],"문제점")

        car_name = car_name_elem.text.strip()

        detail_title = area_detail_elements[0].text.strip()
        detail_content = area_detail_elements[1].text.strip()
        detail_num = area_review_elements[0].text.strip()

        perform_title = perform_detail_elements[0].text.strip()
        perform_num = perform_detail_elements[1].text.strip()

        price_title = price_detail_elements[0].text.strip()
        price_num = price_detail_elements[1].text.strip()

        fault_title = fault_detail_container[0].text.strip()
        fault_num = fault_detail_container[1].text.strip()

    except TimeoutException:
        print("가격 요약 영역 로딩 시간 초과")




def open_links_and_scrape(driver):
    # 1. 메인 창 핸들 기억
    main_window = driver.current_window_handle

    # 2. 모든 href 주소를 리스트로 추출 (Stale Element 예방)
    links = driver.find_elements(By.CSS_SELECTOR, "#list_mocha li a")
    href_list = [link.get_attribute("href") for link in links if link.get_attribute("href")]

    print(f"총 {len(href_list)}개의 링크를 발견했습니다.")

    for idx, href in enumerate(href_list, 1):
        print(f"\n--- [{idx}/{len(href_list)}] 링크 처리 중 ---")

        # 3. 새 탭 열기 및 이동 (JS 활용)
        driver.execute_script("window.open(arguments[0], '_blank');", href)

        # 새 탭으로 포커스 이동 (가장 마지막 핸들)
        all_windows = driver.window_handles
        driver.switch_to.window(all_windows[-1])

        # 4. 데이터 수집
        print_detail_texts(driver)
        # 5. 새 탭 닫고 메인 창으로 완전 복귀
        driver.close()
        driver.switch_to.window(main_window)
        time.sleep(0.3)


# 메인 실행 루프
try:
    for i in range(1, 7):
        if i == 6:
            continue
        target_url = f"{url}?mnfccd=00{i}"
        print(f"\n==========================================")
        print(f"페이지 이동: {target_url}")
        print(f"==========================================")

        driver.get(target_url)
        time.sleep(1)  # 페이지 최초 전환 대기

        click_until_hidden(driver)
        open_links_and_scrape(driver)

finally:
    driver.quit()