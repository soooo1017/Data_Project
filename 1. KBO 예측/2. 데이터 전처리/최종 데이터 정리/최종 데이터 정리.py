import pandas as pd

pd.set_option('display.max_columns', None)

# 1. 데이터 불러오기
KBO_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/(2차) 데이터 전처리 및 상관계수 결과/전처리_v4(연도 2001 삭제).xlsx', sheet_name = '데이터취합')

# 1-1. BPC_pitcher 변수 생성 (세이브 + 홀드)
# 가중치 : 세이브와 홀드의 상관계수로 계산함 ( 계산 = 세이브(or 홀드) 가중치 / (세이브 가중치 + 홀드 가중치) )
# 세이브 가중치 : 0.697076763 / 홀드 가중치 : 0.302923237
KBO_df['BPC_pitcher'] = KBO_df['SV_pitcher']*0.697076763 + KBO_df['HLD_pitcher']*0.302923237

# 2. 선정된 지표만 남기기
# 2-1. 선정된 지표 리스트
team_variable = ['연도', '순위', '팀명', '승률', '팀명_라벨링']
defense_variable = ['FPCT_defense', 'SB_defense', 'PB_defense', 'E_defense', 'CS%_defense']
runner_variable = ['SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']
hitter_variable = ['OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter']
pitcher_variable = ['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher']

# 2-2. 선정된 지표 새로운 df 생성
selected_columns = team_variable + pitcher_variable + hitter_variable + defense_variable + runner_variable
Final_df = KBO_df[selected_columns]


# 3. '예측_순위' 변수 생성

# 3-1. 데이터 정렬 (기준 : '팀명_라벨링' > '연도')
Final_df = Final_df.sort_values(by=['팀명_라벨링', '연도'])

# 3-2. 같은 팀에 대해 '순위' 값을 이전 연도의 '예측_순위'값으로!! : GROUP BY ('팀명_라벨링'별로!) / SHIFT(데이터를 행이나 열 이동!) 활용
# Final_df['예측_순위'] = Final_df.groupby('팀명_라벨링')['순위'].shift(-1, fill_value = 0).astype(int) # 단순히 '예측_순위' 컬럼 추가하면 맨 뒤에 위치함!!
Final_df.insert(2, '예측_순위', Final_df.groupby('팀명_라벨링')['순위'].shift(-1, fill_value = 0).astype(int)) # '예측_순위'가 '순위' 뒤로 오도록!!

# 3-2. 데이터 재정렬 (기준 : '연도' > '순위')
Final_df = Final_df.sort_values(by=['연도', '순위'])

# 엑셀 저장
Final_df.to_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx', index=False)


# print(Final_df.head())