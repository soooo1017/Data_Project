import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


url_1 = "https://www.koreabaseball.com/Record/Team/Pitcher/BasicOld.aspx"


driver = webdriver.Chrome()
driver.implicitly_wait(3)

driver.get(url_1)
sleep(3)

# KBO 기록실 홈페이지에서 'KBO 정규시즌' 선택
select_s = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeries_ddlSeries'))
select_s.select_by_visible_text('KBO 정규시즌')
sleep(1)


# 첫페이지 스크래핑

# 열 제목 생성
record_page = driver.page_source
soup = BeautifulSoup(record_page, 'html.parser')

th_tag = soup.select('div.record_result thead th')

title1 = ['연도']
for th in th_tag:
    title1.append(th.get_text())

# 첫 페이지 데이터 프레임 생성
df1 = pd.DataFrame([title1])

# 연도별 선택 후 데이터 스크래핑 range(2001, 2026)
for y in range(2001, 2025) :

    # 연도 옵션 선택자에서 해당 연도 선택
    select_y = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeason_ddlSeason'))
    select_y.select_by_value('{}'.format(y))
    sleep(2)

    # 연도 선택한 페이지의 HTML 코드 가져오기
    record_page = driver.page_source
    soup = BeautifulSoup(record_page, 'html.parser')

    # 순위별 데이터 가져오기
    for tr_tag in soup.select('div.record_result tbody tr')[0:] :
        td_tag = tr_tag.select('td')
        row1 = [y]
        for td in td_tag:
            row1.append(td.get_text())
        df1_1 = pd.DataFrame([row1])
        df1 = pd.concat([df1,df1_1])


sleep(1)

# 기록보기 '다음' 클릭
driver.find_element(by=By.CSS_SELECTOR, value='.next').click()
sleep(1)

# 열 제목 생성
record_page = driver.page_source
soup = BeautifulSoup(record_page, 'html.parser')

th_tag = soup.select('div.record_result thead th')

title2 = []
for th in th_tag[3:]:
    title2.append(th.get_text())

# 첫 페이지 데이터 프레임 생성
df2 = pd.DataFrame([title2])

# 연도별 선택 후 데이터 스크래핑 range(2001, 2026)
for y in range(2001, 2025) :

    # 연도 옵션 선택자에서 해당 연도 선택
    select_y = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeason_ddlSeason'))
    select_y.select_by_value('{}'.format(y))
    sleep(2)

    # 연도 선택한 페이지의 HTML 코드 가져오기
    record_page = driver.page_source
    soup = BeautifulSoup(record_page, 'html.parser')

    # 순위별 데이터 가져오기
    for tr_tag in soup.select('div.record_result tbody tr')[0:] :
        td_tag = tr_tag.select('td')
        row2 = []
        for td in td_tag[3:]:
            row2.append(td.get_text())
        df2_1 = pd.DataFrame([row2])
        df2 = pd.concat([df2,df2_1])

df = pd.concat([df1, df2], axis=1)

df.to_excel('투수기록.xlsx', sheet_name='투수 팀 기록', index=False, header=False)

sleep(3)
driver.quit()
