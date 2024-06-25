import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def get_text(item, class_name):
    try:
        return item.find_element(By.CLASS_NAME, class_name).text.strip()
    except NoSuchElementException:
        return ''

def get_property_data(item):
    area_text = get_text(item, 'estateItem__estateArea')
    size_in_tsubo_match = re.search(r'(\d+\.\d+|\d+)坪', area_text)
    size_in_tsubo = size_in_tsubo_match.group(1) if size_in_tsubo_match else ''

    # 詳細ページのリンクを取得
    detail_link_element = item.find_element(By.CLASS_NAME, 'estateItem__detail')
    detail_link = detail_link_element.get_attribute('href')

    # 問い合わせリンクを取得
    detail_link_contact = item.find_element(By.CLASS_NAME, 'estateItem__contact')
    detail_contact = detail_link_contact.get_attribute('href')

    # 画像URLの取得
    image_element = item.find_element(By.CSS_SELECTOR, '.estateItem__image img')
    image_src = image_element.get_attribute('src')

    property_site = "テンポスマート"

    return {
        "property_name": get_text(item, 'estateItem__estateTitle'),
        "rent": get_text(item, 'estateItem__estatePrice--value'),
        "rent_tax_classification": get_text(item, 'estateItem__estatePrice--tax'),
        "station_route": get_text(item, 'stationInfo__route'),
        "station_name": get_text(item, 'stationInfo__name--link'),
        "station_near": get_text(item, 'stationInfo__near--value'),
        "floor": get_text(item, 'estateItem__estateFloor'),
        "size_in_tsubo": size_in_tsubo,
        "address": get_text(item, 'estateItem__estateAddress'),
        "current_status": get_text(item, 'estateItem__estatePurpose--link'),
        "property_id": get_text(item, 'estateItem__estateId--value'),
        "property_site": property_site,
        "detail_link": detail_link,
        "detail_contact":detail_contact,
        "image_src": image_src
    }

# WebDriverの設定
options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ログイン処理
email = "let.smakeawish1230@gmail.com"
password = "gs5T76aAR3R3X"
driver.get("https://www.temposmart.jp/login")
driver.find_element(By.NAME, 'email').send_keys(email)
driver.find_element(By.NAME, 'password').send_keys(password)
driver.find_element(By.XPATH, "//input[@type='submit']").click()

# スクレイピング設定
base_url = "https://www.temposmart.jp/estates?parent_current_purpose%5B0%5D=159&child_current_purpose%5B0%5D=180&child_current_purpose%5B1%5D=183&child_current_purpose%5B2%5D=188&child_current_purpose%5B3%5D=194&child_current_purpose%5B4%5D=198&child_current_purpose%5B5%5D=209&child_current_purpose%5B6%5D=221&child_current_purpose%5B7%5D=225&child_current_purpose%5B8%5D=230&child_current_purpose%5B9%5D=250&child_current_purpose%5B10%5D=256&child_current_purpose%5B11%5D=258&child_current_purpose%5B12%5D=160&child_current_purpose%5B13%5D=164&child_current_purpose%5B14%5D=166&child_current_purpose%5B15%5D=170"
max_pages = 10
data_samples = []

for page in range(1, max_pages + 1):
    url = f"{base_url}&page={page}"
    driver.get(url)
    time.sleep(2)

    estate_items = driver.find_elements(By.CLASS_NAME, 'estateItem')

    for item in estate_items:
        property_data = get_property_data(item)
        # データをリストに追加
        data_samples.append(list(property_data.values()))

# CSVファイルにデータを書き込む
csv_filename = 'temposmart_data.csv'
headers = ["property_name", "rent", "rent_tax_classification", "station_route", "station_name", "station_near", "floor", "size_in_tsubo", "address", "current_status", "detail_link", "property_id", "property_site", "image_src"]

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    for data in data_samples:
        csvwriter.writerow(data)

driver.quit()
