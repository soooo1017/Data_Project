import time
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)


# YouTube API 키 설정
api_key = 'AIzaSyBqklA_4k7nyCUzvBB72Jg0V14DOMUcW2U' # 개인 구글 API key
youtube = build('youtube', 'v3', developerKey=api_key)

# 영상 데이터 CSV 파일 불러오기
video_df = pd.read_excel(f'../2. Data_Preprocessing/ssglanders_video_final.xlsx')
top5_df = pd.read_excel(f'../2. Data_Preprocessing/top5_video_final.xlsx')
bottom5_df = pd.read_excel(f'../2. Data_Preprocessing/bottom5_video_final.xlsx')

# video_id 리스트로 추출
all_ids = video_df['video_id'].tolist()
top_5_ids = top5_df['video_id'].tolist()
bottom_5_ids = bottom5_df['video_id'].tolist()


print(f"✅ 총 {len(all_ids)}개 영상의 댓글 수집을 시작합니다!")
print()
print("Top5 영상 ID 목록:", top_5_ids)
print("Bottom5 영상 ID 목록:", bottom_5_ids)
print()


# 전체 댓글 데이터 저장 리스트
all_comments = []
top5_comments = []
bottom5_comments = []

# 댓글 데이터 수집
def comment_collection(id_data, comments_list):
    for video_id in id_data:
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
                    comments_list.append({
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

comment_collection(all_ids, all_comments)
comment_collection(top_5_ids, top5_comments)
comment_collection(bottom_5_ids, bottom5_comments)

# 데이터프레임으로 저장
now = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # 날짜+시간을 파일명으로 쓸 수 있게 형식화

all_comments_df = pd.DataFrame(all_comments)
top5_comments_df = pd.DataFrame(top5_comments)
bottom5_comments_df = pd.DataFrame(bottom5_comments)

output_path_all = f'../1. Data_Collection/({now})ssglanders_comments.xlsx'
output_path_1 = f'../1. Data_Collection/({now})ssglanders_top5_comments.xlsx'
output_path_2 = f'../1. Data_Collection/({now})ssglanders_bottom5_comments.xlsx'

def save_excel(data, path, sheet) :
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name=sheet, index=False)

        workbook = writer.book
        worksheet = writer.sheets[sheet]

        # 3. id 관련 열의 인덱스 확인 (0-based → A=0, B=1, ...)
        id_columns = ['video_id', 'comment_id']
        for col in id_columns:
            if col in data.columns:
                col_idx = data.columns.get_loc(col)
                col_letter = chr(ord('A') + col_idx)
                # 열 서식을 텍스트로 지정
                worksheet.set_column(f'{col_letter}:{col_letter}', None, workbook.add_format({'num_format': '@'}))

save_excel(all_comments_df, output_path_all, 'ssglanders_comments')
print(f"top5 {len(all_comments_df)}개의 댓글 데이터를 Excel 파일로 저장했어요!")


save_excel(top5_comments_df, output_path_1, 'top5_comments')
print(f"top5 {len(top5_comments_df)}개의 댓글 데이터를 Excel 파일로 저장했어요!")

save_excel(bottom5_comments_df, output_path_2, 'bottom5_comments')
print(f"bottom5 {len(bottom5_comments_df)}개의 댓글데이터를 Excel 파일로 저장했어요!")
