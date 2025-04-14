import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 데이터 불러오기
KBO_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/최종 정리/취합_전처리 데이터.xlsx')

# '승률'와의 상관계수 계산 및 정렬(낮은 값부터!!)
KBO_corr = KBO_df.corr(numeric_only=True)['승률'].sort_values(ascending = True)

# 상관계수 Series를 DataFrame으로 변환
KBO_corr_df = KBO_corr.reset_index()
KBO_corr_df.columns = ['변수', '상관계수']  # Rename columns



# 데이터 값에 따라 분류 값이 누락된 경우 지정해서 입력
KBO_corr_df.loc[KBO_corr_df['변수'].str.endswith('_hitter'), '분류'] = '타자'
KBO_corr_df.loc[KBO_corr_df['변수'].str.endswith('defense'), '분류'] = '수비'
KBO_corr_df.loc[KBO_corr_df['변수'].str.endswith('_runner'), '분류'] = '주루'
KBO_corr_df.loc[KBO_corr_df['변수'].str.endswith('_pitcher'), '분류'] = '투수'

KBO_corr_df.loc[~KBO_corr_df['분류'].isin(['주루', '타자', '투수', '수비']), '분류'] = '전체'


# 엑셀 저장
KBO_corr_df.to_excel('승률상관계수.xlsx', index=False)


# (타자, 투수, 수비, 주루) 분류 작업
# 상관계수 절대값 처리
KBO_corr_df['상관계수_절대값'] = KBO_corr_df['상관계수'].abs()
KBO_corr_df['구분'] = KBO_corr_df['분류']

# 상위 10위 선별 함수 정의
def get_top10(x):
    # 상관계수_절대값을 기준으로 정렬하여 상위 5개 행을 반환
    return x.sort_values('상관계수_절대값', ascending=False).head(10)

type_top10 = KBO_corr_df.groupby('분류').apply(get_top10, include_groups=False)

values_to_drop = ['팀명_라벨링', '연도']
type_top10 = type_top10[~type_top10['변수'].isin(values_to_drop)]


# 엑셀 저장
type_top10.to_excel('분류별_상위10지표(상관계수절대값기준).xlsx', index=True)



# 한글 폰트 설정 (AppleGothic 사용)
plt.rc("font", family="AppleGothic")  # 한글 폰트 설정

# 히트맵 생성
plt.figure(figsize=(10, 8))  # 그래프 크기 조정
hm = sns.heatmap(KBO_df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm")

# 그래프 제목 추가
plt.title("KBO 팀 데이터 상관계수 히트맵", fontsize=16)

# 그래프 출력
plt.show()

# 히트맵 저장
hm.get_figure().savefig("상관계수_히트맵.png")

