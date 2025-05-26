import pandas as pd
import re
from datetime import datetime

video_df = pd.read_excel('../1. Data_Collection/(2025-05-09_165521)ssglanders_video_data.xlsx')

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)


# 'id' 컬럼 생성 (영상 인덱스 기반으로 id 생성)
video_df['id'] = ['video_' + str(i+1) for i in video_df.index]

# 변수 생성
video_df['like_rate'] = video_df.apply(
    lambda row: row['like_count'] / row['view_count'] if row['view_count'] > 0 else 0, axis=1
) # 좋아요율

video_df['comment_rate'] = video_df.apply(
    lambda row: row['comment_count'] / row['view_count'] if row['view_count'] > 0 else 0, axis=1
) # 댓글률

# 'published_at' 컬럼을 datetime으로 변환
video_df['published_at'] = pd.to_datetime(video_df['published_at'])

video_df['publish_year'] = video_df['published_at'].dt.year # 업로드 연도
video_df['publish_date'] = video_df['published_at'].dt.date # 업로드 월일
video_df['publish_time'] = video_df['published_at'].dt.time # 업로드 시간
video_df['publish_day'] = video_df['published_at'].dt.day_of_week # 0 : 월요일 ~ 6 : 일요일

# 정규 표현식을 사용하여 시간, 분, 초를 추출하는 함수
def parse_duration(duration):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours, minutes, seconds

# 각 행에 대한 '영상 길이' 데이터를 parse_duration 함수를 적용해서 초 단위로 산출
video_df['duration_seconds'] = video_df['duration'].apply(lambda x: sum(i * j for i, j in zip([3600, 60, 1], parse_duration(x))))


# 업로드 시간 라벨링 함수
def label_publish_time(time_obj):
    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('06:00:00', '%H:%M:%S').time():
        return '심야'
    elif datetime.strptime('06:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('09:00:00', '%H:%M:%S').time():
        return '아침 이른시간'
    elif datetime.strptime('09:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('12:00:00', '%H:%M:%S').time():
        return '아침'
    elif datetime.strptime('12:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('15:00:00', '%H:%M:%S').time():
        return '점심'
    elif datetime.strptime('15:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('18:00:00', '%H:%M:%S').time():
        return '오후'
    elif datetime.strptime('18:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('21:00:00', '%H:%M:%S').time():
        return '저녁'
    else:
        return '밤'

# DataFrame에 적용
video_df['publish_time_label'] = video_df['publish_time'].apply(label_publish_time)


# 업로드 시간 라벨링 함수
def am_pm_publish_time(time_obj):
    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('12:00:00', '%H:%M:%S').time():
        return '오전'
    else:
        return '오후'

# DataFrame에 적용
video_df['publish_am_pm'] = video_df['publish_time'].apply(am_pm_publish_time)


# 영상 길이 라벨링 함수
def duration(duration_seconds) :
    if duration_seconds <= 60 :
        return '1분 이하'
    elif (duration_seconds > 60) and (duration_seconds <= 180) :
        return '1분 초과 3분 이하'
    elif (duration_seconds > 180) and (duration_seconds <= 300) :
        return '3분 초과 5분 이하'
    elif (duration_seconds > 300) and (duration_seconds <= 600) :
        return '5분 초과 10분 이하'
    elif (duration_seconds > 600) and (duration_seconds <= 900) :
        return '10분 초과 15분 이하'
    elif (duration_seconds > 900) and (duration_seconds <= 1800) :
        return '15분 초과 30분 이하'
    elif (duration_seconds > 1800) and (duration_seconds <= 3600) :
        return '30분 초과 1시간 이하'
    elif duration_seconds > 3600 :
        return '1시간 초과'

video_df['duration_label'] = video_df['duration_seconds'].apply(duration)


# 최근 5개년(2020년 이후)에 대한 영상만 추출
# (복사본으로 데이터프레임을 분리하기 위해 .copy()를 실행해야 뒤의 코드를 실행했을 때 확인하는 경고 문구가 뜨지 않음)
video_final_df = video_df[(video_df['publish_year'] >= 2020) & (pd.to_datetime(video_df['publish_date']) <= datetime(2025, 5, 8))].copy()

# 엑셀은 datetime에 대한 적용을 하지 못해 제거하지 않으면 오류 발생함. (따라서, datetime인 'published_at' 컬럼 형식 제거)
video_final_df['published_at'] = video_final_df['published_at'].dt.strftime("%Y년 %m월 %d일 %H시 %M분 %S.%f초")

# 조회수 상위5개, 하위5개 추출해서 별도 파일로 저장하기
# 결측치 제거
video_final_df = video_final_df.dropna(subset=['view_count'])

# 조회수 높은 5개 + 낮은 5개 영상 추출
top_5 = video_final_df.sort_values(by='view_count', ascending=False).head(5)
bottom_5 = video_final_df.sort_values(by='view_count', ascending=True).head(5)

# 엑셀 파일 저장
top_5.to_excel(f'../2. Data_Preprocessing/top5_video_final.xlsx', sheet_name='top5_final_Data', index=False)
bottom_5.to_excel(f'../2. Data_Preprocessing/bottom5_video_final.xlsx', sheet_name='bottom5_final_Data', index=False)
video_final_df.to_excel(f'../2. Data_Preprocessing/ssglanders_video_final.xlsx', sheet_name='Video_final_Data', index=False)
