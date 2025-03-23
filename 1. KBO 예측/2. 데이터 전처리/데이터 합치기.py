import pandas as pd

pd.set_option('display.max_columns', None)

team_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/팀기록.xlsx')
hitter_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/타자기록.xlsx')
pitcher_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/투수기록.xlsx')
defense_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/수비기록.xlsx')
runner_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/주루기록.xlsx')
word_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/DATA/용어정리.xlsx')

# 용어 데이터 처리 (분류 : '타자, 투수, 수비, 주루'로 표현 / 용어와 해설 별도로 분류)
word_df.columns = ['분류', '용어해설']
word_df['분류'] = word_df['분류'].str.replace(' 기록', '', regex=False)

split_result = word_df['용어해설'].str.split(r'\s*:\s*', n=1, expand=True)
word_df['용어'] = split_result[0]
word_df['해설'] = split_result[1]

word_df = word_df.drop(columns='용어해설')

# 불필요한 컬럼 삭제 및 컬럼명 변경(각 분야별 순위 구분할 수 있도록함)
team_df = team_df.drop(columns=['게임차', '최근10경기', '연속', '홈', '방문'])
team_df = team_df.rename(columns={'순위':'팀_순위'})
hitter_df = hitter_df.rename(columns={'순위':'타자_순위'})
pitcher_df = pitcher_df.rename(columns={'순위':'투수_순위'})
defense_df = defense_df.rename(columns={'순위':'수비_순위'})
runner_df = runner_df.rename(columns={'순위':'주루_순위'})

# 데이터프레임 merge시 기준 열 생성(고유값 : 연도_팀명)
team_df['연도_팀명'] = team_df['연도'].astype(str) + '_' + team_df['팀명']
hitter_df['연도_팀명'] = hitter_df['연도'].astype(str) + '_' + hitter_df['팀명']
pitcher_df['연도_팀명'] = pitcher_df['연도'].astype(str) + '_' + pitcher_df['팀명']
defense_df['연도_팀명'] = defense_df['연도'].astype(str) + '_' + defense_df['팀명']
runner_df['연도_팀명'] = runner_df['연도'].astype(str) + '_' + runner_df['팀명']

# 불필요한 컬럼 삭제
hitter_df = hitter_df.drop(columns=['연도', '팀명', 'G'])
pitcher_df = pitcher_df.drop(columns=['연도', '팀명', 'G'])
defense_df = defense_df.drop(columns=['연도', '팀명', 'G'])
runner_df = runner_df.drop(columns=['연도', '팀명', 'G'])

# 데이터 하나씩 추가 merge
KBO_h_df = pd.merge(team_df, hitter_df, on='연도_팀명', how='left', suffixes=('_team', '_hitter'))
KBO_hp_df = pd.merge(KBO_h_df, pitcher_df, on='연도_팀명', how='left', suffixes=('', '_pitcher'))
KBO_hpd_df = pd.merge(KBO_hp_df, defense_df, on='연도_팀명', how='left', suffixes=('', '_defense'))
KBO_all_df = pd.merge(KBO_hpd_df, runner_df, on='연도_팀명', how='left', suffixes=('', '_runner'))

# 최종 데이터의 불필요한 컬럼 삭제
KBO_all_df = KBO_all_df.drop(columns='연도_팀명')

'''
KBO_all_df.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/전처리_v2.xlsx', sheet_name='데이터취합', index=False)
word_df.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/전처리_v2.xlsx', sheet_name='용어정리', index=False)
'''

# 데이터와 용어 2개 시트로 엑셀 저장
# create a excel writer object
with pd.ExcelWriter("/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/전처리_v2.xlsx") as writer:
    # use to_excel function and specify the sheet_name and without index
    KBO_all_df.to_excel(writer, sheet_name="데이터취합", index=False)
    word_df.to_excel(writer, sheet_name="용어정리", index=False)