import time
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd


# YouTube API 키 설정
api_key = 'AIzaSyBqklA_4k7nyCUzvBB72Jg0V14DOMUcW2U' # 개인 구글 API key
youtube = build('youtube', 'v3', developerKey=api_key)

# 영상 데이터 CSV 파일 불러오기
video_df = pd.read_csv('../2. Data_Preprocessing/ssglanders_video_final.csv')

# 조회수 컬럼을 숫자로 변환
video_df['view_count'] = pd.to_numeric(video_df['view_count'], errors='coerce')

# 결측치 제거
video_df = video_df.dropna(subset=['view_count'])

# 조회수 높은 5개 + 낮은 5개 영상 추출
top_5 = video_df.sort_values(by='view_count', ascending=False).head(5)
bottom_5 = video_df.sort_values(by='view_count', ascending=True).head(5)

# video_id 리스트로 추출
target_videos = pd.concat([top_5, bottom_5])
video_ids = target_videos['video_id'].tolist()
top_5_ids = top_5['video_id'].tolist()
bottom_5_ids = bottom_5['video_id'].tolist()

print("댓글 수집할 영상 ID 목록:", video_ids)
print("Top5 영상 ID 목록:", top_5_ids)
print("Bottom5 영상 ID 목록:", bottom_5_ids)


# 전체 댓글 데이터 저장 리스트
all_comments = []

for video_id in video_ids:
    print(f"📺 {video_id} 댓글 수집 중...")

    next_page_token = None
    while True:
        try:
            comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,  # 한 번에 100개까지 가능
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()

            for item in comment_response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                all_comments.append({
                    'video_id': video_id,
                    'comment_id': item['id'],
                    'author': comment.get('authorDisplayName'),
                    'text': comment.get('textDisplay'),
                    'like_count': comment.get('likeCount'),
                    'published_at': comment.get('publishedAt')
                })

            next_page_token = comment_response.get('nextPageToken')
            if not next_page_token:
                break

            time.sleep(0.1)  # 너무 빠른 호출 방지

        except Exception as e:
            print(f"❌ {video_id} 댓글 수집 중 오류 발생: {e}")
            break

# 데이터프레임으로 저장
now = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # 날짜+시간을 파일명으로 쓸 수 있게 형식화

df_comments = pd.DataFrame(all_comments)

# video_id '-'로 시작하면 앞에 ' 붙이기
df_comments['video_id'] = df_comments['video_id'].apply(
    lambda x: f"'{x}" if str(x).startswith('-') else x
)

# video_id '-'로 시작하면 앞에 ' 붙이기
df_comments['comment_id'] = df_comments['comment_id'].apply(
    lambda x: f"'{x}" if str(x).startswith('-') else x
)


df_comments.to_csv(f'../1. Data_Collection/({now})ssglanders_video_comments.csv',
                   index=False, encoding='utf-8-sig')

print(f"✅ 총 {len(df_comments)}개의 댓글을 저장했어요!")
