import pandas as pd

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/2. Data_Preprocessing/ssglanders_video_final.csv')

# 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
# print(video_final_df[['view_count','like_count', 'comment_count', 'duration_seconds', 'like_rate', 'comment_rate']].describe())

# 상관정도 확인
# print(video_final_df[['view_count', 'like_count', 'comment_count', 'like_rate', 'comment_rate', 'duration_seconds']].corr())

print(video_final_df['duration_seconds'].describe())


