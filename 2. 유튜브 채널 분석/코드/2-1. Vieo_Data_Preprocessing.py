import pandas as pd
import re


video_df = pd.read_csv('../1. Data_Collection/(2025-04-28_141831)ssglanders_video_data.csv')
playlist_df = pd.read_csv('../1. Data_Collection/(2025-04-28_142352)ssglanders_playlist_metadata.csv')
video_playlist_df = pd.read_csv('../1. Data_Collection/(2025-04-28_142352)ssglanders_video_playlist_map.csv')

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# video_df 전처리

# 'id' 컬럼 생성 (영상 인덱스 기반으로 id 생성)
video_df['id'] = ['video_' + str(i+1) for i in video_df.index]

# 변수 생성
video_df['like_rate'] = video_df['like_count'] / video_df['view_count'] # 좋아요율
video_df['comment_rate'] = video_df['comment_count'] / video_df['view_count'] # 댓글률

# 'published_at' 컬럼을 datetime으로 변환
video_df['published_at'] = pd.to_datetime(video_df['published_at'])

video_df['publish_year'] = video_df['published_at'].dt.year
video_df['publish_date'] = video_df['published_at'].dt.date
video_df['publish_time'] = video_df['published_at'].dt.time
video_df['publish_day'] = video_df['published_at'].dt.day_of_week # 0 : 월요일 ~ 6 : 일요일

# 정규 표현식을 사용하여 시간, 분, 초를 추출하는 함수
def parse_duration(duration):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours, minutes, seconds

# 각 행에 대해 parse_duration 함수 적용
video_df['duration_seconds'] = video_df['duration'].apply(lambda x: sum(i * j for i, j in zip([3600, 60, 1], parse_duration(x))))




# playlist_df 전처리
playlist_final_df = playlist_df

# 'id' 컬럼 생성 (영상 인덱스 기반으로 id 생성)
playlist_final_df['playlist_label'] = ['playlist_' + str(i+1) for i in playlist_df.index]


# video_playlist_df 전처리
video_playlist_final_df = video_playlist_df

# playlist_df['playlist_label'] 매칭하기
video_playlist_final_df['playlist_label'] = pd.merge(video_playlist_df, playlist_df, on='playlist_id', how='left')['playlist_label']


# video_final_df 생성
video_final_df = pd.merge(video_df, video_playlist_df, on='video_id', how='left')
video_final_df = video_final_df[video_final_df['publish_year'] >= 2020]


# 데이터 저장
playlist_final_df.to_csv(f'../2. Data_Preprocessing/ssglanders_playlist_final.csv', index=False, encoding='utf-8-sig')
video_final_df.to_csv(f'../2. Data_Preprocessing/ssglanders_video_final.csv', index=False, encoding='utf-8-sig')
video_playlist_final_df.to_csv(f'../2. Data_Preprocessing/ssglanders_video_playlist_final.csv', index=False, encoding='utf-8-sig')
