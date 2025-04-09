import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

wb = Workbook()

# 기본 시트 삭제
std = wb['Sheet'] # 기본 시트 이름이 'Sheet'인 경우
wb.remove(std)

# KBO 팀 기록 링크 (웹 스크래핑 대상)
url_dict = {
    '수비' : "https://www.koreabaseball.com/Record/Team/Defense/Basic.aspx", # 수비 기록 링크
    '주루' : "https://www.koreabaseball.com/Record/Team/Runner/Basic.aspx", # 주루 기록 링크
    '타자' : "https://www.koreabaseball.com/Record/Team/Hitter/Basic1.aspx", # 타자 기록 링크
    '투수' : "https://www.koreabaseball.com/Record/Team/Pitcher/BasicOld.aspx" # 투수 기록 링크
}


driver = webdriver.Chrome()
driver.implicitly_wait(3)


dfs = {}


for part, url in url_dict.items():
    # 시트 생성
    ws = wb.create_sheet('{} 팀 기록'.format(part))

    # 웹페이지 열기
    driver.get(url)
    sleep(3)

    # KBO 기록실 홈페이지에서 'KBO 정규시즌' 선택
    select_s = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeries_ddlSeries'))
    select_s.select_by_visible_text('KBO 정규시즌')
    sleep(1)

    # 열 제목 생성
    record_page = driver.page_source
    soup = BeautifulSoup(record_page, 'html.parser')

    th_tag = soup.select('div.record_result thead th')

    title1 = ['연도']

    for th in th_tag :
        title1.append(th.get_text())

    title1 = pd.DataFrame(title1)


    # 연도별 선택 후 데이터 스크래핑 (2002~2024년)
    for y in range(2002, 2025) :

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
            row1 = []
            for td in td_tag :
                row1.append(td.get_text())
            df1 = pd.DataFrame([row1])
            df = pd.concat([title1, df1], ignore_index=True)

        sleep(1)

    # 타자, 투수의 경우 '다음' 페이지 넘어가서 데이터 추가 스크래핑 필요
    if part in ['타자', '투수'] :

        # 기록보기 '다음' 클릭
        driver.find_element(by=By.CSS_SELECTOR, value='next').click()
        sleep(1)

        # 열 제목 생성
        record_page = driver.page_source
        soup = BeautifulSoup(record_page, 'html.parser')
        th_tag = soup.select('div.record_result thead th')

        title2 = []
        for th in th_tag[3:] :
            title2.append(th.get_text())

        # 첫 페이지 데이터 프레임 생성
        title2 = pd.DataFrame([title2])

        # 연도별 선택 후 데이터 스크래핑 (2002~2024년)
        for y in range(2002, 2025) :

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
                for td in td_tag[3:] :
                    row2.append(td.get_text())
                df2 = pd.DataFrame([row2])
                df2 = pd.concat([title2, df2], ignore_index=True)

                # 첫 페이지 데이터와 두 번째 페이지 데이터를 합친 후
                df = pd.concat([df, df2], ignore_index=True)

    # 데이터프레임 저장
    dfs[part] = df

    sleep(3)

    # 드라이버 종료
    driver.quit()

# 엑셀 파일로 저장
with pd.ExcelWriter('KBO 팀기록.xlsx', engine='openpyxl') as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("엑셀 파일로 저장 완료!")

