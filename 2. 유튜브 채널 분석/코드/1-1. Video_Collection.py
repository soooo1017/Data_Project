import time

import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime

# 2. API 키 입력 (YouTube API v3에서 받은 키)
api_key = 'AIzaSyBqklA_4k7nyCUzvBB72Jg0V14DOMUcW2U' # 개인 구글 API key

# 3. API 연결 설정
youtube = build('youtube', 'v3', developerKey=api_key)

'''
# 사용자 이름(@ssglanders) 기반으로 채널 검색
request = youtube.search().list(
    q='ssglanders',        # 검색어
    type='channel',        # 채널만 찾기
    part='snippet',
    maxResults=1
)
response = request.execute()

# 채널 ID 추출
channel_id = response['items'][0]['snippet']['channelId'] 
'''

channel_id = 'UCt8iRtgjVqm5rJHNl1TUojg'
# 확인 print("SSG 랜더스 채널 ID:", channel_id)


# 5. 채널에서 업로드된 영상 재생목록 ID 가져오기
channel_response = youtube.channels().list(
    part='contentDetails',
    id=channel_id
).execute()

uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# 6. 전체 영상 리스트 수집
video_ids = []
next_page_token = None

while True:
    playlist_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    for item in playlist_response['items']:
        video_ids.append({
            'video_id': item['snippet']['resourceId']['videoId'],
            'title': item['snippet']['title'],
            'published_at': item['snippet']['publishedAt']
        })

    '''
    if len(video_ids) >= 10:
        break  # 10개까지만 수집

    if len(video_ids) >= 10 or not playlist_response.get('nextPageToken'):
        break
    '''

    next_page_token = playlist_response.get('nextPageToken')
    if not next_page_token:
        break

# 8. 영상 상세 정보 수집
all_video_data = []

for video in video_ids:
    vid = video['video_id']
    try:
        video_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=vid
        ).execute()

        if not video_response['items']:
            continue  # 삭제된 영상 등 예외 처리

        item = video_response['items'][0]

        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        details = item.get('contentDetails', {})

        all_video_data.append({
            'video_id': vid, # 영상 아이디
            'title': video['title'], # 영상 제목
            'published_at': video['published_at'], # 영상 게시일
            'view_count': stats.get('viewCount', 0), # 조회수
            'like_count': stats.get('likeCount', 0), # 좋아요 수
            'comment_count': stats.get('commentCount', 0), # 댓글 수
            'duration': details.get('duration'), # 영상 길이
            'description': snippet.get('description'), # 영상 설명
            'tags': ', '.join(snippet.get('tags', [])),  # 리스트 -> 문자열 # 영상 태그
            'category_id': snippet.get('categoryId'), # 영상 카테고리
            'dimension': details.get('dimension'), # 영상 2D/3D
            'definition': details.get('definition') # 영상
        })

        time.sleep(0.1)  # 너무 빠른 호출 방지 (API 한도 보호용)

    except Exception as e:
        print(f"Error for video {vid}: {e}")


# 9. 데이터프레임으로 정리 후 CSV 저장
now = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # 날짜+시간을 파일명으로 쓸 수 있게 형식화
df = pd.DataFrame(all_video_data)

df.to_csv(f'../1. Data_Collection/({now})ssglanders_video_data.csv',
          index=False, encoding='utf-8-sig')

print(f"{len(df)}개의 영상 데이터를 파일에 저장했어요!")