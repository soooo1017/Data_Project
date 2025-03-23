import pandas as pd

KBO_word_df = pd.read_excel("/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/전처리_v2.xlsx", sheet_name='용어정리')
KBO_corr_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수.xlsx')

KBO_corr_df['용어'] = KBO_corr_df['변수']

KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_runner', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_hitter', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_pitcher', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_defense', '', regex=False)


# 상관계수 데이터와 용어 데이터 합치기
merge_df = pd.merge(KBO_corr_df, KBO_word_df, left_on='변수', right_on='용어', how='left')
merge_df = merge_df.drop(columns=['용어_y', '해설'])
merge_df = merge_df.rename(columns={'용어_x':'용어'})



# 데이터 값에 따라 분류 값이 누락된 경우 지정해서 입력
merge_df.loc[merge_df['변수'].str.endswith('_runner'), '분류'] = '주루'
merge_df.loc[merge_df['변수'].str.endswith('_pitcher'), '분류'] = '투수'

merge_df.loc[merge_df['변수'].str.startswith('주루_'), '분류'] = '주루'
merge_df.loc[merge_df['변수'].str.startswith('타자_'), '분류'] = '타자'
merge_df.loc[merge_df['변수'].str.startswith('투수_'), '분류'] = '투수'
merge_df.loc[merge_df['변수'].str.startswith('수비_'), '분류'] = '수비'

merge_df.loc[~merge_df['분류'].isin(['주루', '타자', '투수', '수비']), '분류'] = '전체'


KBO_word_df['용어_분류'] = KBO_word_df['용어'] + KBO_word_df['분류']
merge_df['용어_분류'] = merge_df['용어'] + merge_df['분류']


merge_df1 = pd.merge(merge_df, KBO_word_df, on='용어_분류', how='left')
merge_df1 = merge_df1.drop(columns=['용어_분류', '분류_y', '용어_y'])
merge_df1 = merge_df1.rename(columns={'용어_x':'용어', '분류_x' : '분류'})

merge_df1["해설"] = merge_df1["해설"].fillna(merge_df1["변수"])


# merge_df1.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수_2.xlsx', index=False)

# merge_df2 : 각 지표들의 긍정,부정 효과 변수 추
merge_df2 = merge_df1

# 긍정적인 지표 리스트
positive_metrics = [
    "WPCT", "W", "SV", "QS", "SHO", "RBI", "HLD", "CG", "MH", "HR", "3B", "2B", "TB", "SB",
    "SO_pitcher", "PKO_runner", "AB", "AVG", "OBP", "SLG", "OPS", "RISP", "PH-BA", "AVG_pitcher"
]

# 부정적인 지표 리스트
negative_metrics = [
    "L", "E", "PB", "BK", "WP", "BSV", "OOB", "ERA", "WHIP", "BB_pitcher", "H_pitcher",
    "HR_pitcher", "3B_pitcher", "2B_pitcher", "SF_pitcher", "IBB_pitcher", "HBP_pitcher",
    "R_pitcher", "TBF", "CS", "CS%", "PKO"
]

# '지표구분' 컬럼 생성
merge_df2["지표구분"] = merge_df2["변수"].apply(
    lambda x: "긍정" if x in positive_metrics else "부정" if x in negative_metrics else "기타"
)

merge_df2.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수_3(지표구분추가).xlsx', index=False)
