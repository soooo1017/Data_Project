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

ws = wb.create_sheet('팀 기록')

url = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

driver = webdriver.Chrome()
driver.implicitly_wait(1.5)

driver.get(url)
sleep(1.5)

# KBO 기록실 홈페이지에서 'KBO 정규시즌' 선택
select_s = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeries'))
select_s.select_by_visible_text('정규시즌')
sleep(1)


# 열 제목 생성
record_page = driver.page_source
soup = BeautifulSoup(record_page, 'html.parser')

table_tag = soup.select_one('table.tData')
th_tag = table_tag.select('thead th')

title = ['연도']
for th in th_tag:
    title.append(th.get_text())

ws.append(title)


# 연도별 선택 후 데이터 스크래핑 range(2001, 2026)
for y in range(2001, 2025) :

    # 연도 옵션 선택자에서 해당 연도 선택
    select_y = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlYear'))
    select_y.select_by_value('{}'.format(y))
    sleep(1.5)

    # 연도 선택한 페이지의 HTML 코드 가져오기
    record_page = driver.page_source
    soup = BeautifulSoup(record_page, 'html.parser')

    table_tag = soup.select_one('table.tData')

    # 순위별 데이터 가져오기
    for tr_tag in table_tag.select('tbody tr')[0:] :
        td_tag = tr_tag.select('td')
        row = [y]
        for td in td_tag :
            row.append(td.get_text())

    ws.append(row)

    sleep(2)


wb.save('팀기록.xlsx')


sleep(1.5)
driver.quit()