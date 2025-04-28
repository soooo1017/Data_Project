from bs4 import BeautifulSoup
from openpyxl import Workbook
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


wb = Workbook()

# 기본 시트 삭제
std = wb['Sheet']  # 기본 시트 이름이 'Sheet'인 경우
wb.remove(std)

ws = wb.create_sheet('SSG_쇼츠')

url = "https://www.youtube.com/@SSGLANDERS/shorts"

driver = webdriver.Chrome()
driver.implicitly_wait(3)

driver.get(url)
sleep(3)

title = ['NO', '제목', '조회수']
ws.append(title)

# 현재 페이지 높이 = last_height
last_height = driver.execute_script("return document.documentElement.scrollHeight")

while True:
    # 스크롤 끝까지 내리기
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    # 스크롤 내린 후 페이지 로딩을 위한 시간이 필요하다면, PAUSE_SEC에 숫자 입력
    time.sleep(PAUSE_SEC)

    # 스크롤 내린 후의 페이지 높이 = new_height
    new_height = driver.execute_script("return document.documentElement.scrollHeight")

    # 더 이상 스크롤이 내려가지 않으면 스크롤 내리는 반복문 멈춤 (=last_height와 new_height 같으면 멈춤)
    if new_height == last_height :
        break

    # 스크롤 내린 후의 페이지 높이(new_height)를 현재 페이지 높이(last_height) 변수에 저장
    last_height = new_height

# 페이지의 HTML 코드 가져오기
record_page = driver.page_source
soup = BeautifulSoup(record_page, 'html.parser')



# 쇼츠별 데이터 가져오기
for tr_tag in soup.select('div.content tbody tr')[0:] :
    td_tag = tr_tag.select('td')
    row = [y]
    for td in td_tag :
        row.append(td.get_text())
    ws.append(row)