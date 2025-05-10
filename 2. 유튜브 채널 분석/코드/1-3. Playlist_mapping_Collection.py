import pandas as pd
import time
from googleapiclient.discovery import build
from datetime import datetime

# API 설정
api_key = 'AIzaSyB1sFEqp2Vf2WjdFas1avlv30a38wskJ_M'
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCt8iRtgjVqm5rJHNl1TUojg'

# 1. 재생목록별 영상 ID 수집 (필터링 없이 전부 수집)
video_playlist_map = []

next_page_token = None
while True:
    playlists_response = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    for item in playlists_response['items']:
        pid = item['id']
        title = item['snippet']['title']

        playlist_next_page = None
        while True:
            items_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=pid,
                maxResults=50,
                pageToken=playlist_next_page
            ).execute()

            for video_item in items_response['items']:
                vid = video_item['snippet']['resourceId']['videoId']
                video_playlist_map.append({
                    'video_id': vid,
                    'playlist_id': pid,
                    'playlist_title': title
                })

            playlist_next_page = items_response.get('nextPageToken')
            if not playlist_next_page:
                break
        time.sleep(0.1)

# 2. DataFrame으로 정리
video_playlist_df = pd.DataFrame(video_playlist_map)

# 3. ExcelWriter로 xlsx 저장 (id 열을 텍스트로 지정)
now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
output_path = f'../1. Data_Collection/({now})ssglanders_video_playlist_map.xlsx'

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    video_playlist_df.to_excel(writer, sheet_name='Playlist_map_Data', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Playlist_map_Data']

    # id 관련 열의 인덱스 확인 → 텍스트 서식 지정
    id_columns = ['video_id', 'playlist_id']
    for col in id_columns:
        if col in video_playlist_df.columns:
            col_idx = video_playlist_df.columns.get_loc(col)
            col_letter = chr(ord('A') + col_idx)
            worksheet.set_column(f'{col_letter}:{col_letter}', None, workbook.add_format({'num_format': '@'}))

print(f"{len(video_playlist_df)}개의 영상-재생목록 매핑 정보를 Excel 파일로 저장했어요!")
