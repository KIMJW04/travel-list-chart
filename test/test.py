from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"chart_travel_Gangnam_gu-{current_date}.json"

# 웹드라이브 설치
options = ChromeOptions()
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%EA%B0%95%EB%82%A8%EA%B5%AC%EC%97%AC%ED%96%89")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 5).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "main_pack"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
travel_data = []
travels_list = soup.select("#nxTsDo > div > div > div.do_content > div > div:nth-child(5) > div.ScrollBox-mso6a.Poi_filteredPoi-vqFVt.Poi_filteredPoi-HVLwu > div.information-iiK8v > ul > li.item-wJaHc")

for travel in travels_list:
    ranking = travel.find('div', class_='rank-kEDoI').text.strip()
    title = travel.find('span', class_='name-K_anJ').text.strip()
    img_tag = travel.find('img', class_='img-q5u9H')['src']
    link_tag = travel.find('a', class_='anchor-X0MS6')['href']

    travel_data.append({
        'ranking': ranking,
        'title': title,
        'image_url': img_tag,
        'link': link_tag
    })
print(travels_list)

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(travel_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()