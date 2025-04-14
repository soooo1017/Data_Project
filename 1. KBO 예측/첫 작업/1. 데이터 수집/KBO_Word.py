from bs4 import BeautifulSoup
from openpyxl import Workbook
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By

wb = Workbook()
ws = wb.active
ws.title = 'KBO용어'

url = "https://www.koreabaseball.com/Record/Team/Defense/Basic.aspx"

driver = webdriver.Chrome()
driver.get(url)
sleep(1.5)

# 기록용어 이미지 클릭
driver.find_element(By.XPATH,"//img[@alt='기록용어']").click()
sleep(1.5)

soup = BeautifulSoup(driver.page_source, 'html.parser')

for dl in soup.select('div#words div.list dl'):
    category = dl.select_one('dt').text.strip()
    for dd in dl.select('dd'):
        term = dd.text.strip()
        ws.append([category, term])

wb.save('용어정리.xlsx')
driver.quit()
