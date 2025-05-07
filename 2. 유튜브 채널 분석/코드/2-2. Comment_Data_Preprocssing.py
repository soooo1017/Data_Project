import pandas as pd
import re

video_final_df = pd.read_csv('../2. Data_Preprocessing/ssglanders_video_final.csv')
comment_df = pd.read_csv('../1. Data_Collection/(2025-05-07_021015)ssglanders_video_comments.csv')


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)



# comment_df 전처리
comment_final_df =  comment_df

# 'id' 컬럼 생성 (영상 인덱스 기반으로 id 생성)
comment_final_df['comment_label'] = ['comment_' + str(i+1) for i in comment_df.index]

comment_final_df['playlist_label'] = pd.merge(comment_df, video_final_df, on='video_id', how='left')['playlist_label']
comment_final_df['playlist'] = pd.merge(comment_df, video_final_df, on='video_id', how='left')['playlist_title']
comment_final_df['video_title'] = pd.merge(comment_df, video_final_df, on='video_id', how='left')['title']
comment_final_df['video_view_count'] = pd.merge(comment_df, video_final_df, on='video_id', how='left')['view_count']
comment_final_df['video_published_at'] = pd.merge(comment_df, video_final_df, on='video_id', how='left')['published_at_y']


# 'published_at' 컬럼을 datetime으로 변환
comment_final_df['video_published_at'] = pd.to_datetime(comment_final_df['video_published_at'])
comment_final_df['published_at'] = pd.to_datetime(comment_final_df['published_at'])


comment_final_df['comment_video_publish'] = comment_final_df['published_at'] - comment_final_df['video_published_at']


print(comment_final_df.head())

# 데이터 저장
comment_final_df.to_csv(f'../2. Data_Preprocessing/ssglanders_comment_final.csv', index=False, encoding='utf-8-sig')
