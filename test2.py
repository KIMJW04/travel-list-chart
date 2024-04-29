from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"chart_naverWebtoon_{current_date}.json"

# 웹 드라이버 설정
options = ChromeOptions()
options.add_argument("--headless")  # 브라우저 창을 띄우지 않는 옵션
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://comic.naver.com/webtoon")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "component_wrap.type2"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 웹툰 목록 추출
webtoon_list = soup.find_all('li', class_='DailyListItem__item--LP6_T')

# # 웹툰 정보를 담을 리스트 초기화
# webtoons_info = []
# # 각 웹툰 항목을 순회하며 정보 추출
# for webtoon in webtoon_list:
#     # 타이틀 추출
#     title_tag = webtoon.find('a', class_='ContentTitle__title_area--x24vt')
#     # img = webtoon.find('img', class_='Poster__image--d9XTI')['src']
#     if title_tag:
#         title = title_tag.find('span', class_='text').text.strip()
#     else:
#         title = "Title not found"

#     # 추출한 정보를 딕셔너리로 저장
#     webtoons_info.append({'title': title})
print(webtoon_list)
# 브라우저 종료
browser.quit()

# 추출한 정보를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoons_info, f, ensure_ascii=False, indent=4)

print(f"JSON 파일이 저장되었습니다: {filename}")