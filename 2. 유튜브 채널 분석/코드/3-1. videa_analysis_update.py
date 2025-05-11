import pandas as pd
from datetime import datetime
import os


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_excel('../2. Data_Preprocessing/ssglanders_video_final.xlsx')
top5_final_df = pd.read_excel('../2. Data_Preprocessing/top5_video_final.xlsx')
bottom5_final_df = pd.read_excel('../2. Data_Preprocessing/bottom5_video_final.xlsx')

result = ['view_count', 'like_count', 'comment_count', 'like_rate', 'comment_rate']
df = {
    'all' : video_final_df,
    'top5' : top5_final_df,
    'bottom5' : bottom5_final_df
}
index_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm', 'duration_label']
pivot_final_result = {}

# 폴더 없는 경우 생성
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 단순 성과분석
def pivot_result(final_df, x, y=None) : # result 값에 대한 평균, 총합, 갯수 산출
   if y is not None:
       return final_df.pivot_table(
           index=x, columns=y,
           values=result,
           aggfunc=['mean', 'sum', 'count']
       )

   else:
       return final_df.pivot_table(
           index=x,
           values=result,
           aggfunc=['mean', 'sum', 'count']
       )

# 성과분석 + 업로드 당 평균 조회수
def pivot_result_update(final_df, x, y=None) :
    for z in result:
        # result 값에 대한 평균, 총합, 갯수 산출
        pivot_1 = final_df.pivot_table(
           index=x, columns=y,
           values=z,
           aggfunc=['mean', 'sum', 'count']
        )

    pivot_2 = final_df.pivot_table(
        index=x,
        columns=y,
        values='view_count',
        aggfunc=['sum', 'count']
    )

    # 업로드당 평균 조회수 계산 = sum / count
    view_sum = pivot_2['sum']
    view_count = pivot_2['count']
    avg_views = view_sum / view_count

    # ✅ pivot_1과 똑같은 nlevels로 맞춰주기
    nlevels = pivot_1.columns.nlevels


    if isinstance(avg_views.columns, pd.MultiIndex):

        # 첫 번째 레벨을 'avg_views'로 설정하고, 나머지 레벨은 그대로 유지
        avg_views.columns = pd.MultiIndex.from_product([
            ['avg_views'] * avg_views.shape[1],  # 첫 번째 레벨은 'avg_views'로 채우기
            *[[''] * (nlevels - 2)],  # 두 번째 레벨은 그대로 가져옴
            y.repeat(avg_views.shape[1])  # 세 번째 레벨도 그대로 가져옴
        ])[:avg_views.shape[1]]  # avg_views의 열 개수에 맞게 자르기

        '''
        # 예: pivot_1이 3-level이면 ('avg_views', '', '') 형태로 맞춰줌
        avg_views.columns = pd.MultiIndex.from_product(
            [['avg_views'], *[[''] * (nlevels - 1)]]
        )[:avg_views.shape[1]]  # column 수 맞춰 자르기
        '''

    else:
        avg_views.columns = pd.MultiIndex.from_tuples([
            tuple(['avg_views'] + [''] * (nlevels - 1)) for _ in avg_views.columns
        ])

    final_pivot = pd.concat([pivot_1, avg_views], axis=1)

    return final_pivot



now = datetime.now().strftime('%Y-%m-%d_%H%M%S') # 날짜+시간을 파일명으로 쓸 수 있게 형식화

makedirs(f'../3. Analysis_result/{now} total_result')

# 전체 분석_엑셀 통합파일 생성
for name, data in df.items() :
    makedirs(f'../3. Analysis_result/{now} total_result/{name}')
    with pd.ExcelWriter(f'../3. Analysis_result/{now} total_result/{name}/1-1. {name} ssglanders_analysis.xlsx', engine='xlsxwriter') as writer:

        # 각 컬럼별 기초통계 (조회수, 좋아요 수, 댓글 수, 영상길이(초단위), 좋아요율, 댓글률)
        all_describe = data[result].describe()
        all_describe.to_excel(writer, sheet_name = '기초통계')

        # 상관정도 확인
        all_corr = data[result].corr()
        all_corr.to_excel(writer, sheet_name = '상관분석')

    if name == 'all':
        # 성과분석_엑셀 통합파일 생성
        with pd.ExcelWriter(f'../3. Analysis_result/{now} total_result/{name}/1-2. {name} ssglanders_성과분석.xlsx',
                            engine='xlsxwriter') as writer:
            for index in index_list:
                pivot_result_update(data, data[f'{index}']).to_excel(writer, sheet_name=f'{index}_성과분석')
                if index == 'publish_day':
                    for column in ['publish_time_label', 'publish_am_pm', 'duration_label']:
                        pivot_result_update(data, data[f'{index}'], data[f'{column}']).to_excel(writer,
                                                                                         sheet_name=f'day_{column}_성과분석')
                if index == 'publish_time_label':
                    pivot_result_update(data, data[f'{index}'], data['duration_label']).to_excel(writer,
                                                                                          sheet_name=f'time_duration_성과분석')
                if index == 'publish_am_pm':
                    pivot_result_update(data, data[f'{index}'], data['duration_label']).to_excel(writer,
                                                                                          sheet_name=f'am_pm_duration_성과분석')

    else :
        # 성과분석_엑셀 통합파일 생성
        with pd.ExcelWriter(f'../3. Analysis_result/{now} total_result/{name}/1-2. {name} ssglanders_성과분석.xlsx', engine='xlsxwriter') as writer:
            for index in index_list:
                pivot_result(data, data[f'{index}']).to_excel(writer, sheet_name= f'{index}_성과분석')
                if index == 'publish_day':
                    for column in ['publish_time_label', 'publish_am_pm', 'duration_label']:
                        pivot_result(data, data[f'{index}'], data[f'{column}']).to_excel(writer, sheet_name= f'day_{column}_성과분석')
                if index == 'publish_time_label':
                    pivot_result(data, data[f'{index}'], data['duration_label']).to_excel(writer, sheet_name= f'time_duration_성과분석')
                if index == 'publish_am_pm':
                    pivot_result(data, data[f'{index}'], data['duration_label']).to_excel(writer, sheet_name= f'am_pm_duration_성과분석')




'''
data_no = 1
for data in df :
    for index in index_list :
        pivot_final_result[f'{data_no}_{index}'] = pivot_result(data, data[f'{index}'])
        if index == 'publish_day' :
            for column in ['publish_time_label', 'publish_am_pm', 'duration_label'] :
                pivot_final_result[f'{data_no}_{index}_{column}'] = pivot_result(data, data[f'{index}'], data[f'{column}'])
        if index == 'publish_time_label' :
            pivot_final_result[f'{data_no}_{index}_{column}'] = pivot_result(data, data[f'{index}'], data['duration_label'])
        if index == 'publish_am_pm' :
            pivot_final_result[f'{data_no}_{index}_{column}'] = pivot_result(data, data[f'{index}'], data['duration_label'])
    data_no += 1

print(pivot_final_result)

'''

'''
def avg_views_per_upload(final_df, x, y=None): # result 값에 대한 평균 조회수(단순 조회수 평균을 계산하는 것이 아니라 업로드한 영상 수를 총 조회수로 나눔) 산출
    if y is not None:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = final_df.groupby([x, y]).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views'].to_frame()
    else:
        # groupby로 upload_count와 view_sum을 동시에 계산
        upload_data = final_df.groupby(x).agg(
            upload_count=('video_id', 'count'),
            view_sum=('view_count', 'sum')
        )
        # 평균 조회수 계산 (0으로 나누는 경우 처리)
        upload_data['avg_views'] = upload_data['view_sum'] / upload_data['upload_count']
        return upload_data['avg_views'].to_frame()
'''

'''
result_pivot = pivot_result(video_final_df, video_final_df['publish_year'])
result_pivot2 = pivot_result(video_final_df, video_final_df['publish_year'], video_final_df['publish_day'])
print(result_pivot)
print("-----------")
print(result_pivot2)
'''


# print(video_final_df.info())

'''
result_pivot = pivot_result(video_final_df['publish_year'])
result_pivot2 = pivot_result(video_final_df['publish_year'], video_final_df['publish_day'])
print(result_pivot)
print("-----------")
print(result_pivot2)
'''

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
