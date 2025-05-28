import pandas as pd

# 공통 경로 지정
base_path = '/Users/SOO/Desktop/데분 포트폴리오/SS_Project/2. 국내 부동산 현황분석/국토교통부_부동산 실거래가(수진 수집 완)/'
apt_file = '아파트(매매)/아파트(매매)_실거래가_'
apt_rent_file = '아파트(전월세)/아파트(전월세)_실거래가_'
multi_file = '연립다세대(매매)/연립다세대(매매)_실거래가_'
multi_rent_file = '연립다세대(전월세)/연립다세대(전월세)_실거래가_'

# 파일 이름 리스트
filenames = [
    '24년 1월.csv',
    '24년 2월.csv',
    '24년 3월.csv',
    '24년 4월.csv',
    '24년 5월.csv',
    '24년 6월.csv',
    '24년 7월.csv',
    '24년 8월.csv',
    '24년 9월.csv',
    '24년 10월.csv',
    '24년 11월.csv',
    '24년 12월.csv',
    '25년 1월.csv',
    '25년 2월.csv',
    '25년 3월.csv',
    '25년 4월.csv',
]

# 데이터프레임 리스트로 불러오기
apt_data_list = [pd.read_csv(base_path + apt_file + fname, encoding='cp949', skiprows=15) for fname in filenames]
apt_rent_data_list = [pd.read_csv(base_path + apt_rent_file + fname, encoding='cp949', dtype={19 : str, 11 : str}, skiprows=15) for fname in filenames]
multi_data_list = [pd.read_csv(base_path + multi_file + fname, encoding='cp949', skiprows=15) for fname in filenames]
multi_rent_data_list = [pd.read_csv(base_path + multi_rent_file + fname, encoding='cp949', skiprows=15) for fname in filenames]

apt_data = pd.DataFrame()

file_final_list = []
file_names = {
    '아파트(매매)_데이터' : apt_data_list,
    '아파트(전월세)_데이터' : apt_rent_data_list,
    '연립다세대(매매)_데이터' : multi_data_list,
    '연립다세대(전월세)_데이터' : multi_rent_data_list
}
'''
for data in apt_rent_data_list:
    print(data.info())
    print()

'''

for name, db in file_names.items():
    property_data = pd.DataFrame()
    for data in db :
        property_data = pd.concat([property_data, data])
    property_data.to_csv(f'/Users/SOO/Desktop/데분 포트폴리오/SS_Project/2. 국내 부동산 현황분석/국토교통부_부동산 실거래가(수진 수집 완)/취합/(최종) {name}.csv', encoding='euc-kr', index = False)
    print(f'{name} 파일을 저장 완료하였습니다!')

