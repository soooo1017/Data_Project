import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 데이터 불러오기
KBO_df = pd.read_excel('전처리_v2.xlsx', sheet_name='데이터취합')

# '팀_순위'와의 상관계수 계산 및 정렬(낮은 값부터!!)
KBO_corr = KBO_df.corr(numeric_only=True)['팀_순위'].sort_values(ascending = True)

# 상관계수 Series를 DataFrame으로 변환
KBO_corr_df = KBO_corr.reset_index()
KBO_corr_df.columns = ['변수', '상관계수']  # Rename columns

KBO_corr_df.to_excel('/Users/SOO/Desktop/데분 포트폴리오/1. KBO 예측/2. 데이터 전처리/팀순위_상관계수.xlsx', sheet_name='상관계수', index=False)


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