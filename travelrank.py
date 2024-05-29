from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import re

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")

# 한글 지역명과 영어 지역명 대응하는 딕셔너리 생성
korean_administrative_units_list = {
    "Seoul": {
        "서울강남구": "Gangnam-gu"
    }
}

# 현재 날짜로 된 폴더 생성
base_folder_path = os.path.join(os.getcwd(), "travelrank_list", current_date)
os.makedirs(base_folder_path, exist_ok=True)

# 웹드라이브 설치
service = ChromeService(executable_path=ChromeDriverManager().install())

for city, districts in korean_administrative_units_list.items():
    city_folder_path = os.path.join(base_folder_path, city)
    os.makedirs(city_folder_path, exist_ok=True)

    for district_korean, district_english in districts.items():
        # URL 생성
        url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={district_korean}+여행"
        filename = f"chart_travel_{district_english}-{current_date}.json"
        district_folder_path = os.path.join(city_folder_path, district_english)
        os.makedirs(district_folder_path, exist_ok=True)

        # 웹드라이버 초기화
        options = ChromeOptions()
        options.add_argument("--headless")
        browser = webdriver.Chrome(service=service, options=options)
        browser.get(url)

        # 페이지가 완전히 로드될 때까지 대기
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "main_pack")))

        # 페이지 소스를 가져와서 파싱
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
            
            # 링크에서 번호 부분만 추출
            place_id_match = re.search(r'place/(\d+)', link_tag)
            place_id = place_id_match.group(1) if place_id_match else ""
            
            travel_data.append({
                'ranking': ranking,
                'title': title,
                'image_url': img_tag,
                'link': place_id
            })

        # 각 링크에 접속하여 추가 데이터 추출
        for travel in travel_data:
            place_id = travel['link']
            new_url = f"https://pcmap.place.naver.com/place/{place_id}/home"
            browser.get(new_url)
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "app-root")))

            detail_html_source = browser.page_source
            detail_soup = BeautifulSoup(detail_html_source, 'html.parser')

            # lnJFt 클래스명의 span 태그에서 텍스트 한 번만 추출
            span_text = ""
            span_element = detail_soup.find('span', class_='lnJFt')
            if span_element:
                span_text = span_element.text.strip()

            # PXMot 클래스명의 span 태그에서 a 태그의 텍스트 추출
            reviews = detail_soup.find_all('span', class_='PXMot')
            human_review = ""
            blog_review = ""
            for review in reviews:
                a_tag = review.find('a')
                if a_tag:
                    review_text = ''.join(a_tag.stripped_strings)
                    if '방문자리뷰' in review_text:
                        human_review = review_text.replace('방문자리뷰', '').strip()
                    elif '블로그리뷰' in review_text:
                        blog_review = review_text.replace('블로그리뷰', '').strip()

            # LDgIH 클래스명의 span 태그에서 텍스트 한 번만 추출
            addresses_text = ""
            addresses_element = detail_soup.find('span', class_='LDgIH')
            if addresses_element:
                addresses_text = addresses_element.text.strip()

            travel['title_cate'] = span_text
            travel['human_review'] = human_review
            travel['blog_review'] = blog_review
            travel['addresses'] = addresses_text


        filename = os.path.join(district_folder_path, f"chart_travel_{district_english}-{current_date}.json")

        # 데이터를 JSON 파일로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(travel_data, f, ensure_ascii=False, indent=4)

        # 브라우저 종료
        browser.quit()
