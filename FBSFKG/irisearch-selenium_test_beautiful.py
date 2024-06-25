import requests
from bs4 import BeautifulSoup

# 対象のURL
url = "https://www.iri-search.net/estate_search/index?page_start_num=0&area_code=1&prefectural_code=13&contract_confirm[]=31&order_by=6&hotlist=1"

# Requestsを使用してHTMLコンテンツを取得
response = requests.get(url)
response.encoding = response.apparent_encoding  # 必要に応じてエンコーディングを設定

# BeautifulSoupオブジェクトを作成
soup = BeautifulSoup(response.text, 'html.parser')

# 沿線情報を抽出（例）
station_route_text = soup.select_one("tr:contains('沿線') td").text
print(f"沿線: {station_route_text}")
