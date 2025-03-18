import pandas as pd

KBO_word_df = pd.read_excel("/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/전처리_v2.xlsx", sheet_name='용어정리')
KBO_corr_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수.xlsx')

# 상관계수 데이터와 용어 데이터 합치기
merge_df = pd.merge(KBO_corr_df, KBO_word_df, left_on='변수', right_on='용어', how='left')
merge_df = merge_df.drop(columns=['용어', '해설'])

# 데이터 값에 따라 분류 값이 누락된 경우 지정해서 입력
merge_df.loc[merge_df['변수'].str.endswith('_runner'), '분류'] = '주루'
merge_df.loc[merge_df['변수'].str.endswith('_pitcher'), '분류'] = '투수'

merge_df.loc[merge_df['변수'].str.startswith('주루_'), '분류'] = '주루'
merge_df.loc[merge_df['변수'].str.startswith('타자_'), '분류'] = '타자'
merge_df.loc[merge_df['변수'].str.startswith('투수_'), '분류'] = '투수'
merge_df.loc[merge_df['변수'].str.startswith('수비_'), '분류'] = '수비'

merge_df.loc[~merge_df['분류'].isin(['주루', '타자', '투수', '수비']), '분류'] = '전체'


merge_df.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수_1.xlsx', index=False)