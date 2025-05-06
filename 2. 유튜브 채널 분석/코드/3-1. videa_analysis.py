import pandas as pd
from datetime import datetime
from scipy.stats import chi2_contingency

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_csv('../2. Data_Preprocessing/ssglanders_video_final.csv')
result = ['view_count', 'like_count', 'comment_count', 'like_rate', 'comment_rate']

# 성과분석
def pivot_result(x, y=None) :
   if y is not None:
       return video_final_df.pivot_table(
           index=x, columns=y,
           values=result,
           aggfunc=['mean', 'sum', 'count']
       )

   else:
       return video_final_df.pivot_table(
           index=x,
           values=result,
           aggfunc=['mean', 'sum', 'count']
       )

def avg_views_per_upload(x, y=None):
    if y is not None:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = video_final_df.groupby([x, y]).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views']
    else:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = video_final_df.groupby(x).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views']

# publish_time : object에서 datetime 형식 변경
video_final_df['publish_time'] = video_final_df['publish_time'].apply(
    lambda x: datetime.strptime(x, '%H:%M:%S').time()
)

# 업로드 시간 라벨링 함수 만들기
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
video_final_df['publish_time_label'] = video_final_df['publish_time'].apply(label_publish_time)


# 업로드 시간 라벨링 함수 만들기
def am_pm_publish_time(time_obj):
    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= time_obj < datetime.strptime('12:00:00', '%H:%M:%S').time():
        return '오전'
    else:
        return '오후'

# DataFrame에 적용
video_final_df['publish_am_pm'] = video_final_df['publish_time'].apply(am_pm_publish_time)

def duration(duration_seconds) :
    if duration_seconds <= 60 :
        return '1분 이하'
    elif (duration_seconds > 60) and (duration_seconds <= 180) :
        return '1분 초과 3분 이하'
    elif (duration_seconds > 180) and (duration_seconds <= 300) :
        return '3분 초과 5분 이하'
    elif (duration_seconds > 300) and (duration_seconds <= 600) :
        return '5분 초과 10분 이하'
    elif duration_seconds > 600 :
        return '10분 초과'

video_final_df['duration_label'] = video_final_df['duration_seconds'].apply(duration)

# 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
# print(video_final_df[result].describe())

# 상관정도 확인
# print(video_final_df[result].corr())

# print(video_final_df['duration_seconds'].describe())

# print(pd.crosstab(video_final_df['playlist_label'], video_final_df['view_count'], margins=False))


agg_list = ['mean', 'sum', 'count']
x_list = ['playlist_label', 'publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
agg_results = {}

for x in x_list:
    result_pivot = pivot_result(video_final_df[x])
    avg_views = avg_views_per_upload(video_final_df[x])
    agg_results[(x,)] = (result_pivot, avg_views)

    for y in y_list:
        result_pivot_2 = pivot_result(video_final_df[x], video_final_df[y])
        avg_views_2 = avg_views_per_upload(video_final_df[x], video_final_df[y])
        agg_results[(x, y)] = (result_pivot_2, avg_views_2)

# print(agg_results[('publish_year', 'publish_am_pm')])

video_like_df = video_final_df.sort_values(by='like_rate', ascending=True)
video_comment_df = video_final_df.sort_values(by='comment_rate', ascending=True)

like_top_5 = video_like_df.groupby('duration_label').head()
like_bottom_5 = video_like_df.tail()

comment_top_5 = video_comment_df.head()
comment_bottom_5 = video_comment_df.tail()

# duration_like_df = video_like_df..sort_values(by='like_rate', ascending=True)

