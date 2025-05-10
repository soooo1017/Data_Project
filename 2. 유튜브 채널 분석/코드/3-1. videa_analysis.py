import pandas as pd

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_excel('../2. Data_Preprocessing/ssglanders_video_final.xlsx')
top5_final_df = pd.read_excel('../2. Data_Preprocessing/top5_video_final.xlsx')
bottom5_final_df = pd.read_excel('../2. Data_Preprocessing/bottom5_video_final.xlsx')

result = ['view_count', 'like_count', 'comment_count', 'like_rate', 'comment_rate']


# 분석 함수(성과, 영상개수 대비 조회수)
def analyze_performance(index, columns=None):
    # pivot_table 계산 (mean, sum, count)
    pivot = video_final_df.pivot_table(
        index=index,
        columns=columns,
        values=result,
        aggfunc=['mean', 'sum', 'count']
    ) # 성과(평균, 합계, 개수)

    # sum(view_count) ÷ count(view_count)로 avg_views 계산 - 업로드 영상 개수 대비 조회수
    view_sum = pivot['sum']['view_count']
    view_count = pivot['count']['view_count']
    avg_views = view_sum / view_count

    # avg_views 이름 지정 (다중 컬럼/단일 컬럼 구분)
    if columns is None:
        avg_views.name = 'avg_views'
    else:
        avg_views.name = ('avg_views', '', '')

    # DataFrame으로 변환
    avg_views_df = avg_views.to_frame()

    # 결과 합치기
    combined = pd.concat([pivot, avg_views_df], axis=1)

    return combined

result_pivot = analyze_performance(video_final_df['publish_year'], video_final_df['publish_day'])
print(result_pivot)


'''
x_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
sheet_number = 1

for x in x_list:
    result_pivot = analyze_performance(video_final_df[x])
    print(result_pivot)

    for y in y_list:
        result_pivot_2 = analyze_performance(video_final_df[x], video_final_df[y])

        # 시트번호 1 증가
        sheet_number += 1
        '''




'''

# 성과분석
def pivot_result(x, y=None) : # result 값에 대한 평균, 총합, 갯수 산출
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

def avg_views_per_upload(x, y=None): # result 값에 대한 평균 조회수(단순 조회수 평균을 계산하는 것이 아니라 업로드한 영상 수를 총 조회수로 나눔) 산출
    if y is not None:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = video_final_df.groupby([x, y]).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views'].to_frame()
    else:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = video_final_df.groupby(x).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views'].to_frame()

# 전체 분석_엑셀 통합파일 생성
with pd.ExcelWriter('../3. Analysis_result/1-1. ssglanders_analysis.xlsx', engine='xlsxwriter') as writer:

    # 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
    all_describe = video_final_df[result].describe()
    all_describe.to_excel(writer, sheet_name = '기초통계')

    # 상관정도 확인
    all_corr = video_final_df[result].corr()
    all_corr.to_excel(writer, sheet_name = '상관분석')

# 성과분석_엑셀 통합파일 생성
with pd.ExcelWriter('../3. Analysis_result/1-2. ssglanders_성과분석.xlsx', engine='xlsxwriter') as writer:
    agg_list = ['mean', 'sum', 'count']
    x_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
    y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
    sheet_number = 1

    for x in x_list:
        result_pivot = pivot_result(video_final_df[x])
        result_pivot.to_excel(writer, sheet_name= f'{x}_성과분석')

        for y in y_list:
            result_pivot_2 = pivot_result(video_final_df[x], video_final_df[y])
            result_pivot_2.to_excel(writer, sheet_name=f'{sheet_number}_성과분석')

            # 시트번호 1 증가
            sheet_number += 1

# 평균조회수_엑셀 통합파일 생성
with pd.ExcelWriter('../3. Analysis_result/1-3. ssglanders_평균조회수.xlsx', engine='xlsxwriter') as writer:
    x_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
    y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']
    sheet_number = 1

    for x in x_list:
        avg_views = avg_views_per_upload(video_final_df[x])
        avg_views.to_excel(writer, sheet_name=f'{x}별_평균조회수')

        for y in y_list:
            avg_views_2 = avg_views_per_upload(video_final_df[x], video_final_df[y])
            avg_views_2.to_excel(writer, sheet_name=f'{sheet_number}_평균조회수')

            # 시트번호 1 증가
            sheet_number += 1

# 데이터 프레임 구분
video_view_df = video_final_df.sort_values(by='view_count', ascending=True)
video_like_df = video_final_df.sort_values(by='like_rate', ascending=True)
video_comment_df = video_final_df.sort_values(by='comment_rate', ascending=True)

view_top_5 = video_view_df.head()
view_bottom_5 = video_view_df.tail()

like_top_5 = video_like_df.head()
like_bottom_5 = video_like_df.tail()

comment_top_5 = video_comment_df.head()
comment_bottom_5 = video_comment_df.tail()

with pd.ExcelWriter('../3. Analysis_result/2. ssglanders_video.xlsx', engine='xlsxwriter') as writer:
    view_top_5.to_excel(writer, sheet_name=f'조회수_상위5')
    # 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
    view_top_5_describe = view_top_5[result].describe()
    view_top_5_describe.to_excel(writer, sheet_name='조회수_상위5_기초통계')

    view_bottom_5.to_excel(writer, sheet_name=f'조회수_하위5')
    # 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
    view_bottom_5_describe = view_bottom_5[result].describe()
    view_bottom_5_describe.to_excel(writer, sheet_name='조회수_하위5_기초통계')

    like_top_5.to_excel(writer, sheet_name=f'좋아요_상위5')
    like_top_5_describe = like_top_5[result].describe()
    like_top_5_describe.to_excel(writer, sheet_name='좋아요_상위5_기초통계')

    like_bottom_5.to_excel(writer, sheet_name=f'좋아요_하위5')
    like_bottom_5_describe = like_bottom_5[result].describe()
    like_bottom_5_describe.to_excel(writer, sheet_name='좋아요_하위5_기초통계')

    comment_top_5.to_excel(writer, sheet_name=f'댓글_상위5')
    comment_top_5_describe = comment_top_5[result].describe()
    comment_top_5_describe.to_excel(writer, sheet_name='댓글_상위5_기초통계')

    comment_bottom_5.to_excel(writer, sheet_name=f'댓글_하위5')
    comment_bottom_5_describe = comment_bottom_5[result].describe()
    comment_bottom_5_describe.to_excel(writer, sheet_name='댓글_하위5_기초통계')



# 성과분석_엑셀 통합파일 생성
with pd.ExcelWriter('../3. Analysis_result/3-1. ssglanders_영상길이_성과분석.xlsx', engine='xlsxwriter') as writer:
    y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']

    result_pivot = pivot_result(video_final_df['duration_label'])
    result_pivot.to_excel(writer, sheet_name= f'duration_label_성과분석')

    for y in y_list:
        result_pivot_2 = pivot_result(video_final_df['duration_label'], video_final_df[y])
        result_pivot_2.to_excel(writer, sheet_name=f'{y}_성과분석')


# 평균조회수_엑셀 통합파일 생성
with pd.ExcelWriter('../3. Analysis_result/3-2. ssglanders_영상길이_평균조회수.xlsx', engine='xlsxwriter') as writer:
    y_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm']

    avg_views = avg_views_per_upload(video_final_df['duration_label'])
    avg_views.to_excel(writer, sheet_name=f'duration_label별_평균조회수')

    for y in y_list:
        avg_views_2 = avg_views_per_upload(video_final_df['duration_label'], video_final_df[y])
        avg_views_2.to_excel(writer, sheet_name=f'{y}_평균조회수')



'''
