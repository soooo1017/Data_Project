import pandas as pd

# 모든 컬럼 확인가능하도록 함
pd.set_option('display.max_columns', None)

# 데이터 불러오기
team_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/팀기록.xlsx')
hitter_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/타자기록.xlsx')
pitcher_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/투수기록.xlsx')
defense_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/수비기록.xlsx')
runner_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/주루기록.xlsx')
word_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/DATA/용어정리.xlsx')

# 용어 데이터 처리 (분류 : '타자, 투수, 수비, 주루'로 표현 / 용어와 해설 별도로 분류)
word_df.columns = ['분류', '용어해설']
word_df['분류'] = word_df['분류'].str.replace(' 기록', '', regex=False)

split_result = word_df['용어해설'].str.split(r'\s*:\s*', n=1, expand=True)
word_df['용어'] = split_result[0]
word_df['해설'] = split_result[1]

word_df = word_df.drop(columns='용어해설')

# 전체 데이터프레임 > 불필요 컬럼 삭제
team_df = team_df.drop(columns=['경기', '패', '무', '게임차', '최근10경기', '연속', '홈', '방문'])

# 불필요 컬럼 삭제 1. 타자, 투수, 수비, 주루 데이터프레임에서 '순위' 컬럼 삭제
for df in [hitter_df, pitcher_df, defense_df, runner_df]:
    df.drop(columns='순위', inplace=True)



# 데이터프레임 merge시 기준 열 생성(고유값 : 연도_팀명)
team_df['연도_팀명'] = team_df['연도'].astype(str) + '_' + team_df['팀명']
hitter_df['연도_팀명'] = hitter_df['연도'].astype(str) + '_' + hitter_df['팀명']
pitcher_df['연도_팀명'] = pitcher_df['연도'].astype(str) + '_' + pitcher_df['팀명']
defense_df['연도_팀명'] = defense_df['연도'].astype(str) + '_' + defense_df['팀명']
runner_df['연도_팀명'] = runner_df['연도'].astype(str) + '_' + runner_df['팀명']


# 불필요 컬럼 삭제 2. 타자, 투수, 수비, 주루 데이터프레임에서 '연도, 팀명, G' 컬럼 삭제
for df in [hitter_df, pitcher_df, defense_df, runner_df]:
    df.drop(columns=['연도', '팀명', 'G'], inplace=True)


# 불필요 컬럼 삭제 3. 투수 데이터에서 '승(W)', '패(L)', '승률(WPCT)' 컬럼 삭제
pitcher_df = pitcher_df.drop(columns=['W', 'L', 'WPCT'])

# 데이터 열제목 수정 : 기존 열제목에 '_hitter, _pitcher, _defense, _runner' 추가
hitter_df.columns = [col + '_hitter' for col in hitter_df.columns]
pitcher_df.columns = [col + '_pitcher' for col in pitcher_df.columns]
defense_df.columns = [col + '_defense' for col in defense_df.columns]
runner_df.columns = [col + '_runner' for col in runner_df.columns]

# '연도_팀명' 열제목 수정
hitter_df = hitter_df.rename(columns={'연도_팀명_hitter':'연도_팀명'})
pitcher_df = pitcher_df.rename(columns={'연도_팀명_pitcher':'연도_팀명'})
defense_df = defense_df.rename(columns={'연도_팀명_defense':'연도_팀명'})
runner_df = runner_df.rename(columns={'연도_팀명_runner':'연도_팀명'})

# 데이터 하나씩 추가 merge
KBO_h_df = pd.merge(team_df, hitter_df, on='연도_팀명', how='left', suffixes=('_team', '_hitter'))
KBO_hp_df = pd.merge(KBO_h_df, pitcher_df, on='연도_팀명', how='left', suffixes=('', '_pitcher'))
KBO_hpd_df = pd.merge(KBO_hp_df, defense_df, on='연도_팀명', how='left', suffixes=('', '_defense'))
KBO_all_df = pd.merge(KBO_hpd_df, runner_df, on='연도_팀명', how='left', suffixes=('', '_runner'))

# 최종 데이터의 불필요한 컬럼 삭제
KBO_all_df = KBO_all_df.drop(columns='연도_팀명')

# 팀명 라벨링 작업
'''
0. KT
1. 두산
2. 삼성
3. 키움 - 넥센 - 우리 - 현대
4. 한화
5. SSG - SK
6. KIA
7. LG
8. 롯데
9. NC '''

team_label = {'KT':0, '두산':1, '삼성':2,
              '키움':3, '넥센':3, '우리':3, '현대':3,
              '한화':4,
              'SSG':5, 'SK':5,
              'KIA':6, 'LG':7, '롯데':8, 'NC':9}


# 매핑 함수 정의
def label_team(team):
    return team_label.get(team, -1)  # 매칭되지 않는 경우 -1 반환

# 새로운 열 생성
KBO_all_df['팀명_라벨링'] = KBO_all_df['팀명'].apply(label_team)

KBO_all_df = KBO_all_df[KBO_all_df.연도 != 2001]


# 데이터와 용어 2개 시트로 엑셀 저장
# create a excel writer object
with pd.ExcelWriter("/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/(2차) 데이터 전처리 및 상관계수 결과/전처리_v5.xlsx") as writer:
    # use to_excel function and specify the sheet_name and without index
    KBO_all_df.to_excel(writer, sheet_name="데이터취합", index=False)
    word_df.to_excel(writer, sheet_name="용어정리", index=False)
