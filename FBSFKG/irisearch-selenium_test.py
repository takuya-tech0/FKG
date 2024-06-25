from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
from webdriver_manager.chrome import ChromeDriverManager

# Chrome WebDriverのセットアップ
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 対象のURLにアクセス
    driver.get("https://www.iri-search.net/estate_search/index?page_start_num=0&area_code=1&prefectural_code=13&contract_confirm[]=31&order_by=6&hotlist=1")
    
    # ページのロード完了を待つために少し待機（必要に応じて調整）
    driver.implicitly_wait(10)
    
    # 最初の物件ブロックを見つける
    item = driver.find_element(By.CSS_SELECTOR, 'table[summary="物件詳細1"]')
    
    # # 物件情報を抽出
    # try:
    #     # 物件名称
    #     property_name_element = item.find_element(By.XPATH, ".//th[text()='名称']/following-sibling::td")
    #     property_name_full_text = property_name_element.text
    #     if '&' in property_name_full_text:
    #         property_name = property_name_full_text.split('&')[0].strip()
    #     else:
    #         property_name = property_name_full_text.strip()
    # except NoSuchElementException:
    #     print("物件名称の要素が見つかりません。")
    #     property_name = ""

    # 賃料
    try:
        rent_element = item.find_element(By.XPATH, ".//th[text()='賃料']/following-sibling::td/span[@class='b_red']")
        rent = rent_element.text.strip()
    except NoSuchElementException:
        print("賃料の要素が見つかりません。")
        rent = "0"

    # # 沿線と駅名、徒歩距離
    try:
        station_route_element = item.find_element(By.XPATH, "//*[@id='search_result']/table[1]/tbody/tr[2]/td[2]/table/tbody/tr[4]/td")
        station_route_text = station_route_element.text
    #     station_route = station_route_element.text.split()[0].strip()
    #     station_name_element = item.find_element(By.XPATH, ".//tr[contains(.,'沿線')]//td/span[@class='b_red']")
    #     station_name = station_name_element.text.replace('駅', '').strip()
    #     station_info_text = station_route_element.text
    #     station_near_match = re.search(r'徒歩(\d+)分', station_info_text)
    #     if station_near_match:
    #         station_near = station_near_match.group(1)
    #     else:
    #         station_near = ""
    except NoSuchElementException:
        print("沿線の要素が見つかりません。")
    #     station_route = ""
    #     station_name = ""
    #     station_near = ""

    # # フロア
    # try:
    #     floor_text = item.find_element(By.XPATH, ".//th[text()='フロア']/following-sibling::td").text
    #     floor = floor_text.split('&')[0].strip() if '&' in floor_text else floor_text.strip()
    # except NoSuchElementException:
    #     print("階数の要素が見つかりません。")
    #     floor = ""

    # # 坪数
    # try:
    #     size_in_tsubo_element = item.find_element(By.XPATH, ".//th[contains(text(),'建物面積')]/following-sibling::td/span[@class='b_red']")
    #     size_in_tsubo = size_in_tsubo_element.text.strip()
    # except NoSuchElementException:
    #     print("坪数の要素が見つかりません。")
    #     size_in_tsubo = ""

    # # 住所
    # try:
    #     address_element = item.find_element(By.XPATH, ".//th[contains(text(),'所在')]/following-sibling::td")
    #     address = address_element.text.strip()
    # except NoSuchElementException:
    #     print("住所の要素が見つかりません。")
    #     address = ""

    # # 現況
    # try:
    #     current_status_element = item.find_element(By.XPATH, ".//th[contains(text(),'以前の業態')]/following-sibling::td")
    #     current_status = current_status_element.text.strip()
    # except NoSuchElementException:
    #     print("現況の要素が見つかりません。")
    #     current_status = ""

    # # 物件ID
    # try:
    #     property_id_element = item.find_element(By.XPATH, ".//th[contains(text(),'物件番号')]/following-sibling::td/a/span[@class='b_red']")
    #     property_id = property_id_element.text.strip()
    # except NoSuchElementException:
    #     print("物件IDの要素が見つかりません。")
    #     property_id = ""

    # # 物件リンク
    # try:
    #     detail_link_element = item.find_element(By.XPATH, ".//td[contains(@class, 'center underbtn')]/a")
    #     detail_link = detail_link_element.get_attribute('href')
    #     if detail_link.startswith("/"):
    #         detail_link = "https://www.iri-search.net" + detail_link
    # except NoSuchElementException:
    #     print("物件リンクの要素が見つかりません。")
    #     detail_link = ""

    # # 画像リンク
    # try:
    #     image_element = item.find_element(By.XPATH, ".//div[contains(@class, 'est_photos')]/a/img")
    #     image_src = image_element.get_attribute('src')
    #     if image_src.startswith("/"):
    #         image_src = "https://www.iri-search.net" + image_src
    # except NoSuchElementException:
    #     print("画像リンクの要素が見つかりません。")
    #     image_src = ""

    # 抽出した情報の表示
    # print(f"物件名称: {property_name}")
    print(f"賃料: {rent}")
    print(f"沿線: {station_route_text}")
    # print(f"フロア: {floor}")
    # print(f"坪数: {size_in_tsubo}")
    # print(f"住所: {address}")
    # print(f"現況: {current_status}")
    # print(f"物件ID: {property_id}")
    # print(f"物件リンク: {detail_link}")
    # print(f"画像リンク: {image_src}")

finally:
    # ドライバーを閉じてリソースを解放
    driver.quit()
