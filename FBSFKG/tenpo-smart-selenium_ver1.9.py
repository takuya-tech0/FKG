import csv
import re
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class WebScraper:
    def __init__(self, driver):
        self.driver = driver

    def get_text(self, item, class_name):
        elements = item.find_elements(By.CLASS_NAME, class_name)
        if elements:
            text = elements[0].text.strip()
            if class_name == 'estateItem__estateFloor':
                return re.match(r'(.+?)階', text).group(1) if '階' in text else text
            elif class_name == 'stationInfo__near--value':
                return re.match(r'(.+?)分', text).group(1) if '分' in text else text
            else:
                return text
        return ''

    def get_property_data(self, item):
        try:
            image_element = WebDriverWait(item, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.estateItem__image img'))
            )
            image_src = image_element.get_attribute('src')
        except TimeoutException:
            print("画像のロード中にタイムアウトしました。")
            return None

        area_text = self.get_text(item, 'estateItem__estateArea')
        size_in_tsubo_match = re.search(r'(\d+\.\d+|\d+)坪', area_text)
        size_in_tsubo = size_in_tsubo_match.group(1) if size_in_tsubo_match else ''

        detail_link = item.find_element(By.CLASS_NAME, 'estateItem__detail').get_attribute('href')
        detail_contact = item.find_element(By.CLASS_NAME, 'estateItem__contact').get_attribute('href')

        return {
            "property_name": self.get_text(item, 'estateItem__estateTitle'),
            "rent": self.get_text(item, 'estateItem__estatePrice--value'),
            "rent_tax_classification": self.get_text(item, 'estateItem__estatePrice--tax'),
            "station_route": self.get_text(item, 'stationInfo__route'),
            "station_name": self.get_text(item, 'stationInfo__name--link'),
            "station_near": self.get_text(item, 'stationInfo__near--value'),
            "floor": self.get_text(item, 'estateItem__estateFloor'),
            "size_in_tsubo": size_in_tsubo,
            "address": self.get_text(item, 'estateItem__estateAddress'),
            "current_status": self.get_text(item, 'estateItem__estatePurpose--link'),
            "property_id": self.get_text(item, 'estateItem__estateId--value'),
            "property_site": "テンポスマート",
            "detail_link": detail_link,
            "detail_contact": detail_contact,
            "image_src": image_src
        }

# .envファイルから環境変数を読み込む
load_dotenv()
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
scraper = WebScraper(driver)

driver.get("https://www.temposmart.jp/login")
driver.find_element(By.NAME, 'email').send_keys(email)
driver.find_element(By.NAME, 'password').send_keys(password)
driver.find_element(By.XPATH, "//input[@type='submit']").click()

#base_urlを指定した条件のURLへ変更すると該当の条件で検索可能
base_url = "https://www.temposmart.jp/estates?parent_current_purpose%5B0%5D=159&child_current_purpose%5B0%5D=180&child_current_purpose%5B1%5D=183&child_current_purpose%5B2%5D=188&child_current_purpose%5B3%5D=194&child_current_purpose%5B4%5D=198&child_current_purpose%5B5%5D=209&child_current_purpose%5B6%5D=221&child_current_purpose%5B7%5D=225&child_current_purpose%5B8%5D=230&child_current_purpose%5B9%5D=250&child_current_purpose%5B10%5D=256&child_current_purpose%5B11%5D=258&child_current_purpose%5B12%5D=160&child_current_purpose%5B13%5D=164&child_current_purpose%5B14%5D=166&child_current_purpose%5B15%5D=170"
max_pages = 1
data_samples = []

for page in range(1, max_pages + 1):
    url = f"{base_url}&page={page}"
    driver.get(url)
    time.sleep(2)

    actions = ActionChains(driver)
    estate_items = driver.find_elements(By.CLASS_NAME, 'estateItem')

    for item in estate_items:
        actions.move_to_element(item).perform()
        time.sleep(0.5)

        property_data = scraper.get_property_data(item)
        if property_data:
            data_samples.append(list(property_data.values()))

   # 追加されたデータを確認するために、各ページごとにdata_samplesの内容を表示
    print("データサンプル（ページ " + str(page) + "）:", data_samples)

csv_filename = 'temposmart_data.csv'
headers = ["property_name", "rent", "rent_tax_classification", "station_route", "station_name", "station_near", "floor", "size_in_tsubo", "address", "current_status", "property_id", "property_site", "detail_link", "detail_contact", "image_src"]

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    for data in data_samples:
        csvwriter.writerow(data)

driver.quit()