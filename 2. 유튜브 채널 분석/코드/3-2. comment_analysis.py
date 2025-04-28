import pandas as pd

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/2. Data_Preprocessing/ssglanders_video_final.csv')
comment_final_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/2. Data_Preprocessing/ssglanders_comment_final.csv')

# 각 컬럼별 기초통계
print(comment_final_df.describe())
