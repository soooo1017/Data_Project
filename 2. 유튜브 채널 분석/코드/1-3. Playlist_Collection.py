import pandas as pd
import time
from googleapiclient.discovery import build
from datetime import datetime

# API 설정
api_key = 'AIzaSyBqklA_4k7nyCUzvBB72Jg0V14DOMUcW2U'
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCt8iRtgjVqm5rJHNl1TUojg'

# 기존 영상 메타데이터 불러오기
video_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/(2025-04-25_135732)ssglanders_video_data.csv')
existing_video_ids = set(video_df['video_id'])

# 1. 재생목록 메타데이터 수집
playlist_id_to_title = {}
playlist_meta = []
next_page_token = None

while True:
    playlists_response = youtube.playlists().list(
        part='snippet,contentDetails',
        channelId=channel_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    for item in playlists_response['items']:
        pid = item['id']
        snippet = item['snippet']
        content = item['contentDetails']

        playlist_id_to_title[pid] = snippet['title']

        playlist_meta.append({
            'playlist_id': pid,
            'playlist_title': snippet['title'],
            'published_at': snippet['publishedAt'],
            'item_count': content['itemCount'],
            'video_ids': []  # 일단 비워두고 나중에 채움
        })

    next_page_token = playlists_response.get('nextPageToken')
    if not next_page_token:
        break

# 2. 재생목록별 영상 ID 수집
video_playlist_map = []

for playlist in playlist_meta:
    pid = playlist['playlist_id']
    title = playlist['playlist_title']
    next_page_token = None

    while True:
        items_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=pid,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in items_response['items']:
            vid = item['snippet']['resourceId']['videoId']
            if vid in existing_video_ids:  # 기존 영상 데이터에 포함된 것만
                playlist['video_ids'].append(vid)
                video_playlist_map.append({
                    'video_id': vid,
                    'playlist_id': pid,
                    'playlist_title': title
                })

        next_page_token = items_response.get('nextPageToken')
        if not next_page_token:
            break
    time.sleep(0.1)

# 3. 저장
now = datetime.now().strftime('%Y-%m-%d_%H%M%S')

# playlist_metadata 저장
playlist_meta_df = pd.DataFrame(playlist_meta)
playlist_meta_df['video_ids'] = playlist_meta_df['video_ids'].apply(lambda x: ', '.join(x))
playlist_meta_df.to_csv(f'/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/({now})ssglanders_playlist_metadata.csv',
                        index=False, encoding='utf-8-sig')

# video-playlist 매핑 저장
video_playlist_df = pd.DataFrame(video_playlist_map)
video_playlist_df.to_csv(f'/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/({now})ssglanders_video_playlist_map.csv',
                         index=False, encoding='utf-8-sig')

print("재생목록 메타데이터와 영상-재생목록 매핑 정보를 저장했어요!")
