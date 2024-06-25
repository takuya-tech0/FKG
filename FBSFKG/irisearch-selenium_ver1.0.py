import csv
import re
import time
import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
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
    def __init__(self, email, password, base_url, max_pages):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.max_pages = max_pages
        self.driver = None
        self.data_samples = []

    def setup_driver(self):
        options = Options()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()

    def login(self, login_url):
        try:
            self.driver.get(login_url)

            # クッキー同意のボタンが存在するかチェックし、存在すればクリック
            try:
                cookie_agree_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".cookie-agree"))
                )
                cookie_agree_button.click()
            except TimeoutException:
                print("クッキー同意のポップアップが見つかりません。")

            # メールアドレスとパスワードを入力
            self.driver.find_element(By.NAME, 'data[AuthMember][mail_address]').send_keys(self.email)
            self.driver.find_element(By.NAME, 'data[AuthMember][password]').send_keys(self.password)

            # ログインボタンをクリック
            login_button = self.driver.find_element(By.XPATH, "//input[@type='image'][@alt='ログイン']")
            login_button.click()
        except Exception as e:
            print(f"ログイン中にエラーが発生しました: {e}")
            self.close_driver()
            raise

    def scrape(self):
        # スクレイピング実行日を取得

        for page in range(1, self.max_pages + 1):
            url = f"{self.base_url}&hotlist={page}"
            self.driver.get(url)
            time.sleep(30)

            #スクレイプする親要素ごとにスクロールする
            actions = ActionChains(self.driver)
            #スクレイプする親要素名を指定する
            estate_items = self.driver.find_elements(By.XPATH, '//table[@summary="物件詳細1"]')

            for item in estate_items:
                actions.move_to_element(item).perform()
                time.sleep(0.5)

                property_data = self.get_property_data(item)
                if property_data:
                    self.data_samples.append(list(property_data.values()))

    def get_property_data(self, item):
        try:
            # 物件番号の抽出
            property_id = item.find_element(By.CSS_SELECTOR, 'th > div.estate_link_title > a').get_attribute('href').split('=')[-1].strip()

            # 物件名称の抽出
            property_name = item.find_element(By.CSS_SELECTOR, 'th > div.estate_link_title > a').text.strip()

            # 賃料と坪単価の抽出（例: "1,684,760円(税込) (坪単価　30,805円)"）
            rent_info = item.find_element(By.XPATH, './following-sibling::tr[1]//th[text()="賃料"]/following-sibling::td').text.strip()
            rent = rent_info.split('円')[0].replace(',', '').strip()  # 賃料の数値部分のみ抽出
            size_in_tsubo = rent_info.split('坪')[0].split()[-1]  # 坪単価の前の数値部分のみ抽出

            # 沿線・駅名・徒歩分数の抽出
            station_info = item.find_element(By.XPATH, './following-sibling::tr[2]//th[text()="沿線"]/following-sibling::td').text.strip()
            station_route = station_info.split(' ')[0]  # 最初の空白までが路線名
            station_name = station_info.split(' ')[1]  # 2番目の空白までが駅名
            station_near = station_info.split('徒歩')[1].split('分')[0].strip()  # "徒歩"と"分"の間の数値

            # その他の情報の抽出
            address = item.find_element(By.XPATH, './following-sibling::tr[3]//th[text()="所在"]/following-sibling::td').text.strip()
            floor_info = item.find_element(By.XPATH, './following-sibling::tr[4]//th[text()="フロア"]/following-sibling::td').text.strip()
            current_status = ""  # 現状の情報は提供されたHTMLからは直接抽出できないため、空文字列または適切な代替値を設定
            detail_link = f"https://www.iri-search.net/estate_search/detail?id={property_id}"

            # 画像URLの抽出
            image_src = item.find_element(By.CSS_SELECTOR, 'div.est_photos > a > img').get_attribute('src')

            scraping_date = datetime.now().strftime('%Y-%m-%d')

            return {
                "property_name": property_name,
                "rent": rent,
                "rent_tax_classification": "",  # 税込み情報はrent_infoから抽出可能
                "station_route": station_route,
                "station_name": station_name,
                "station_near": station_near,
                "floor": floor_info,
                "size_in_tsubo": size_in_tsubo,
                "address": address,
                "current_status": current_status,
                "property_id": property_id,
                "property_site": "テンポスマート",
                "detail_link": detail_link,
                "detail_contact": "",  # 詳細問い合わせリンクが特定できればここに設定
                "image_src": image_src,
                "first_published_date": scraping_date
            }
        except Exception as e:
            print(f"Error extracting property data: {e}")
            return None


    def save_to_csv(self, filename):
        headers = ["property_name", "rent", "rent_tax_classification", "station_route", "station_name", "station_near", "floor", "size_in_tsubo", "address", "current_status", "property_id", "property_site", "detail_link", "detail_contact", "image_src", "first_published_date"]
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            for data in self.data_samples:
                csvwriter.writerow(data)

    def update_properties_table(self, c):
        # 一時テーブルからデータを取得
        c.execute('SELECT * FROM temp_properties')
        temp_properties = c.fetchall()

        for row in temp_properties:
            property_id = row[10]  # property_idの位置を適切に設定してください
            c.execute('SELECT first_published_date FROM properties WHERE property_id = ?', (property_id,))
            result = c.fetchone()

            if result is None:
                # 新規物件の場合、first_published_dateを含めて挿入
                c.execute('INSERT INTO properties VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', row)
            else:
                # 既存物件の場合、first_published_dateを除いて他のデータを更新
                update_data = row[:10] + row[11:15] + (property_id,)
                c.execute('UPDATE properties SET property_name=?, rent=?, rent_tax_classification=?, station_route=?, station_name=?, station_near=?, floor=?, size_in_tsubo=?, address=?, current_status=?, property_site=?, detail_link=?, detail_contact=?, image_src=? WHERE property_id=?', update_data)

    def save_to_db(self, db_filename):
        try:
            conn = sqlite3.connect(db_filename)
            c = conn.cursor()

            # 一時テーブルを作成（存在しない場合）
            c.execute('''CREATE TABLE IF NOT EXISTS temp_properties (
                property_name TEXT, 
                rent TEXT, 
                rent_tax_classification TEXT, 
                station_route TEXT, 
                station_name TEXT, 
                station_near TEXT, 
                floor TEXT, 
                size_in_tsubo TEXT, 
                address TEXT, 
                current_status TEXT, 
                property_id TEXT PRIMARY KEY, 
                property_site TEXT, 
                detail_link TEXT, 
                detail_contact TEXT, 
                image_src TEXT, 
                first_published_date DATE DEFAULT CURRENT_DATE
            )''')

            # 一時テーブルを空にする
            c.execute('DELETE FROM temp_properties')

            # 一時テーブルにスクレイピングしたデータを挿入
            for data in self.data_samples:
                c.execute('INSERT OR IGNORE INTO temp_properties VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

            # メインテーブルを更新（存在しない場合は作成）
            c.execute('''CREATE TABLE IF NOT EXISTS properties (
                property_name TEXT, 
                rent TEXT, 
                rent_tax_classification TEXT, 
                station_route TEXT, 
                station_name TEXT, 
                station_near TEXT, 
                floor TEXT, 
                size_in_tsubo TEXT, 
                address TEXT, 
                current_status TEXT, 
                property_id TEXT PRIMARY KEY, 
                property_site TEXT, 
                detail_link TEXT, 
                detail_contact TEXT, 
                image_src TEXT,
                first_published_date DATE DEFAULT CURRENT_DATE
            )''')

            # update_properties_tableを呼び出し
            self.update_properties_table(c)

            # 掲載終了した物件を削除
            c.execute('''DELETE FROM properties 
                        WHERE property_id NOT IN (SELECT property_id FROM temp_properties)''')

            conn.commit()

        except sqlite3.Error as e:
            print(f"データベースへの保存中にエラーが生じました: {e}")
        finally:
            if conn:
                conn.close()

    def export_db_to_csv(self, db_filename, csv_filename):
        # データベースに接続
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        # 全データを選択するクエリを実行
        cursor.execute("SELECT * FROM properties")
        rows = cursor.fetchall()

        # CSVファイルを開いてデータを書き込む
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            # CSVのヘッダーを書き込む
            csvwriter.writerow(["property_name", "rent", "rent_tax_classification", "station_route", "station_name", "station_near", "floor", "size_in_tsubo", "address", "current_status", "property_id", "property_site", "detail_link", "detail_contact", "image_src", "first_published_date"])
            # データベースから読み込んだ行をCSVに書き込む
            csvwriter.writerows(rows)

        # データベース接続を閉じる
        conn.close()

    def close_driver(self):
        self.driver.quit()

# 使い方
load_dotenv()
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
#Web上で指定した条件で発行されるURLを指定する
base_url = "https://www.iri-search.net/estate_search/index?page_start_num=0&area_code=1&prefectural_code=13&contract_confirm[]=31&order_by=6"

scraper = WebScraper(email, password, base_url, max_pages=1)
scraper.setup_driver()
scraper.login("https://www.iri-search.net/pages/login/")
scraper.scrape()
scraper.save_to_db('fbsfkg.db')
scraper.export_db_to_csv('fbsfkg.db', 'exported_data.csv')
scraper.close_driver()