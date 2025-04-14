import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


# KBO 팀 기록 링크 (웹 스크래핑 대상)
url_dict = {
    '수비' : "https://www.koreabaseball.com/Record/Team/Defense/Basic.aspx", # 수비 기록 링크
    '주루' : "https://www.koreabaseball.com/Record/Team/Runner/Basic.aspx", # 주루 기록 링크
    '타자' : "https://www.koreabaseball.com/Record/Team/Hitter/Basic1.aspx", # 타자 기록 링크
    '투수' : "https://www.koreabaseball.com/Record/Team/Pitcher/Basic1.aspx" # 투수 기록 링크
}


driver = webdriver.Chrome()
driver.implicitly_wait(3)


dfs = {}


for part, url in url_dict.items():

    # 웹페이지 열기
    driver.get(url)
    sleep(3)

    # KBO 기록실 홈페이지에서 'KBO 정규시즌' 선택
    select_s = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeries_ddlSeries'))
    select_s.select_by_visible_text('KBO 정규시즌')
    sleep(1)

    # 첫 번째 페이지 열 제목 생성
    record_page = driver.page_source
    soup = BeautifulSoup(record_page, 'html.parser')

    th_tag = soup.select('div.record_result thead th')

    title1 = ['연도']

    for th in th_tag :
        title1.append(th.get_text())

    df1 = pd.DataFrame([title1])

    # '타자', '투수'의 경우 '다음' 페이지 열 제목 생성
    if part in ['타자', '투수'] :

        # 기록보기 '다음' 클릭
        driver.find_element(by=By.CSS_SELECTOR, value='.next').click()
        sleep(1)

        # 열 제목 생성
        record_page = driver.page_source
        soup = BeautifulSoup(record_page, 'html.parser')
        th_tag = soup.select('div.record_result thead th')

        title2 = []
        for th in th_tag[3:] :
            title2.append(th.get_text())

        # '다음' 페이지 데이터 프레임 생성
        df2 = pd.DataFrame([title2])

        # 다시 이전 페이지로 돌아가기
        '''
        <a href="/Record/Team/Pitcher/Basic1.aspx" class="prev">이전</a>
        '''
        driver.find_element(by=By.CSS_SELECTOR, value='.prev').click()
        sleep(1)


    # 연도별 선택 후 데이터 스크래핑 (2002~2024년)
    for y in range(2002, 2025) :

        # 연도 옵션 선택자에서 해당 연도 선택
        select_y = Select(driver.find_element(By.ID, 'cphContents_cphContents_cphContents_ddlSeason_ddlSeason'))
        select_y.select_by_value('{}'.format(y))
        sleep(1)

        # 연도 선택한 페이지의 HTML 코드 가져오기
        record_page = driver.page_source
        soup = BeautifulSoup(record_page, 'html.parser')


        # 순위별 데이터 가져오기
        for tr_tag in soup.select('div.record_result tbody tr')[0:] :
            td_tag = tr_tag.select('td')
            row1 = [y]
            for td in td_tag :
                row1.append(td.get_text())
            df1_1 = pd.DataFrame([row1])
            df1 = pd.concat([df1, df1_1], ignore_index=True, axis = 0)

        sleep(2)

        df = df1

        # 타자, 투수의 경우 '다음' 페이지 넘어가서 데이터 추가 스크래핑 필요
        if part in ['타자', '투수'] :

            # 기록보기 '다음' 클릭
            '''
            <a href="/Record/Team/Pitcher/Basic2.aspx" class="next">다음</a>
            '''

            driver.find_element(by=By.CSS_SELECTOR, value='.next').click()
            sleep(1)


            # '다음'으로 넘어간 페이지의 HTML 코드 가져오기
            record_page = driver.page_source
            soup = BeautifulSoup(record_page, 'html.parser')

            # 순위별 데이터 가져오기
            for tr_tag in soup.select('div.record_result tbody tr')[0:] :
                td_tag = tr_tag.select('td')
                row2 = []
                for td in td_tag[3:] :
                    row2.append(td.get_text())
                df2_1 = pd.DataFrame([row2])
                df2 = pd.concat([df2, df2_1], ignore_index=True)

            sleep(2)

            # 다시 이전 페이지로 돌아가기
            '''
            <a href="/Record/Team/Pitcher/Basic1.aspx" class="prev">이전</a>
            '''
            driver.find_element(by=By.CSS_SELECTOR, value='.prev').click()
            sleep(1)



            # '타자, 투수'의 경우 첫 페이지 데이터와 다음 페이지 데이터 합침
            df = pd.concat([df1, df2], axis=1)


    # 각 분야별 데이터프레임을 dfs 딕셔너리에 매칭하여 저장
    dfs[part] = df

    sleep(3)

    print("{} 작업 완료".format(part))

# 드라이버 종료
driver.quit()


# 팀 기록(순위, 승률 등) 스크래핑
team_url = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

driver = webdriver.Chrome()
driver.get(team_url)
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

title3 = ['연도']
for th in th_tag:
    title3.append(th.get_text())

df3 = pd.DataFrame([title3])

# 연도별 선택 후 데이터 스크래핑 range(2001, 2026)
for y in range(2002, 2025) :

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
        row3 = [y]
        for td in td_tag :
            row3.append(td.get_text())
        df3_1 = pd.DataFrame([row3])
        df3 = pd.concat([df3, df3_1], ignore_index=True, axis=0)

    sleep(2)


# 드라이버 종료
driver.quit()

print('팀 기록 작업 완료')

# 각 분야별 데이터프레임을 dfs 딕셔너리에 매칭하여 저장
dfs['팀 기록'] = df3


# KBO 용어 스크래핑
word_url = "https://www.koreabaseball.com/Record/Team/Defense/Basic.aspx"

driver = webdriver.Chrome()
driver.get(word_url)
sleep(1.5)

# 기록용어 이미지 클릭
driver.find_element(By.XPATH,"//img[@alt='기록용어']").click()
sleep(1.5)

soup = BeautifulSoup(driver.page_source, 'html.parser')

word_cat = ['카테고리']
word_term = ['용어']

for dl in soup.select('div#words div.list dl'):
    category = dl.select_one('dt').text.strip()
    for dd in dl.select('dd'):
        term = dd.text.strip()
        word_cat.append(category)
        word_term.append(term)

word = pd.DataFrame(list(zip(word_cat, word_term)))


# 드라이버 종료
driver.quit()

print('용어정리 작업 완료')

# 각 분야별 데이터프레임을 dfs 딕셔너리에 매칭하여 저장
dfs['용어정리'] = word


# 엑셀 파일 생성
writer = pd.ExcelWriter('KBO 팀기록.xlsx', engine='xlsxwriter')

# 각 분야별 시트 생성 후 데이터 엑셀에 저장
for sheet_name, df in dfs.items():
    df.to_excel(writer, sheet_name=sheet_name, header=False, index=False)

writer.close()

print("엑셀 파일로 저장 완료!")



