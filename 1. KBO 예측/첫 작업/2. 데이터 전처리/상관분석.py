import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 데이터 불러오기
KBO_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/(2차) 데이터 전처리 및 상관계수 결과/전처리_v3(지표 구분 추가).xlsx', sheet_name='데이터취합')
KBO_word_df = pd.read_excel("/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/(2차) 데이터 전처리 및 상관계수 결과/전처리_v2(팀명 라벨링 완료).xlsx", sheet_name='용어정리')

# '승률'와의 상관계수 계산 및 정렬(낮은 값부터!!)
KBO_corr = KBO_df.corr(numeric_only=True)['승률'].sort_values(ascending = True)

# 상관계수 Series를 DataFrame으로 변환
KBO_corr_df = KBO_corr.reset_index()
KBO_corr_df.columns = ['변수', '상관계수']  # Rename columns


# 상관계수 데이터프레임에 '용어' 컬럼 추가 > KBO 야구 표준 용어 필요. '변수' 컬럼은 (타자, 투수, 수비, 주루) 구분을 위해 변경되어있음
KBO_corr_df['용어'] = KBO_corr_df['변수']

KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_runner', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_hitter', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_pitcher', '', regex=False)
KBO_corr_df['용어'] = KBO_corr_df['용어'].str.replace('_defense', '', regex=False)


# 상관계수 데이터와 용어 데이터 합치기 (상관계수에서도 용어에 대한 설명과 분류를 보기 위함)
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

# 용어 설명 추가 데이터프레임 생성 : merge_df1
KBO_word_df['용어_분류'] = KBO_word_df['용어'] + KBO_word_df['분류']
merge_df['용어_분류'] = merge_df['용어'] + merge_df['분류']


merge_df1 = pd.merge(merge_df, KBO_word_df, on='용어_분류', how='left')
merge_df1 = merge_df1.drop(columns=['용어_분류', '분류_y', '용어_y'])
merge_df1 = merge_df1.rename(columns={'용어_x':'용어', '분류_x' : '분류'})

merge_df1["해설"] = merge_df1["해설"].fillna(merge_df1["변수"])


# merge_df2 : 각 지표들의 긍정,부정 효과 변수 추가
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


# 엑셀 저장
# merge_df2.to_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/상관계수/승률상관계수_v1.xlsx', index=False)



# (타자, 투수, 수비, 주루) 분류 작업
# 상관계수 절대값 처리
merge_df2['상관계수_절대값'] = merge_df2['상관계수'].abs()
merge_df2['구분'] = merge_df2['분류']

# 상위 5위 선별 함수 정의
def get_top5(x):
    # 상관계수_절대값을 기준으로 정렬하여 상위 5개 행을 반환
    return x.sort_values('상관계수_절대값', ascending=False).head(10)

type_top5 = merge_df2.groupby('분류').apply(get_top5, include_groups=False)

values_to_drop = ['팀명_라벨링', '연도']
type_top5 = type_top5[~type_top5['변수'].isin(values_to_drop)]

# print(type_top5)

# 엑셀 저장
type_top5.to_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/상관계수/분류별_상위10지표(상관계수절대값기준)_v1.xlsx', index=True)



'''
# 한글 폰트 설정 (AppleGothic 사용)
plt.rc("font", family="AppleGothic")  # 한글 폰트 설정

# 히트맵 생성
plt.figure(figsize=(10, 8))  # 그래프 크기 조정
sns.heatmap(KBO_df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm")

# 그래프 제목 추가
plt.title("KBO 팀 데이터 상관계수 히트맵", fontsize=16)

# 그래프 출력
plt.show()
'''