import pandas as pd
import time
from googleapiclient.discovery import build
from datetime import datetime

# API 설정
api_key = 'AIzaSyBqklA_4k7nyCUzvBB72Jg0V14DOMUcW2U'
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCt8iRtgjVqm5rJHNl1TUojg'

# 기존 영상 메타데이터 불러오기
video_df = pd.read_excel('../1. Data_Collection/(2025-05-09_025608)ssglanders_video_data.csv')

'''
video data 가져올 때, 'video_id' 값을 텍스트로 처리함

# existing_video_ids = set(video_df['video_id'])
existing_video_ids = set(
    video_df.loc[~video_df['video_id'].astype(str).str.startswith("'"), 'video_id']
)
'''

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

# playlist_metadata 저장
playlist_meta_df = pd.DataFrame(playlist_meta)
playlist_meta_df['video_ids'] = playlist_meta_df['video_ids'].apply(lambda x: ', '.join(x))

'''
playlist_meta_df.to_csv(f'../1. Data_Collection/({now})ssglanders_playlist_metadata.csv',
                        index=False, encoding='utf-8-sig')
                        '''

# video-playlist 매핑 저장
video_playlist_df = pd.DataFrame(video_playlist_map)


# 2. ExcelWriter 사용해서 xlsx로 저장
now = datetime.now().strftime('%Y-%m-%d_%H%M%S') # 날짜+시간을 파일명으로 쓸 수 있게 형식화
output_path = f'../1. Data_Collection/({now})ssglanders_video_playlist_map.xlsx'

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    video_playlist_df.to_excel(writer, sheet_name='Playlist_map_Data', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Playlist_map_Data']

    # 3. id 관련 열의 인덱스 확인 (0-based → A=0, B=1, ...)
    id_columns = ['video_id', 'category_id']
    for col in id_columns:
        if col in video_playlist_df.columns:
            col_idx = video_playlist_df.columns.get_loc(col)
            col_letter = chr(ord('A') + col_idx)
            # 열 서식을 텍스트로 지정
            worksheet.set_column(f'{col_letter}:{col_letter}', None, workbook.add_format({'num_format': '@'}))

print(f"{len(video_playlist_df)}개의 재생목록 메타데이터와 영상-재생목록 매핑 정보를 Excel 파일로 저장했어요!")


'''
video_playlist_df.to_csv(f'../1. Data_Collection/({now})ssglanders_video_playlist_map.csv',
                         index=False, encoding='utf-8-sig')

print("재생목록 메타데이터와 영상-재생목록 매핑 정보를 저장했어요!")

'''
