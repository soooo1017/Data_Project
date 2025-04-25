import pandas as pd

video_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/(2025-04-25_135732)ssglanders_video_data.csv')
comment_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/(2025-04-25_140202)ssglanders_video_comments.csv')
playlist_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/(2025-04-25_145525)ssglanders_playlist_metadata.csv')
video_playlist_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/(2025-04-25_145525)ssglanders_video_playlist_map.csv')

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

video_df['like_rate'] = video_df['like_count'] / video_df['view_count']
video_df['comment_rate'] = video_df['comment_count'] / video_df['view_count']

