import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_excel('../2. Data_Preprocessing/ssglanders_video_final.xlsx')
top5_final_df = pd.read_excel('../2. Data_Preprocessing/top5_video_final.xlsx')
bottom5_final_df = pd.read_excel('../2. Data_Preprocessing/bottom5_video_final.xlsx')

# 각 지표별 상위,하위 영상 데이터 구분
like_rank_df = video_final_df.sort_values(by='like_rate', ascending=True)
comment_rank_df = video_final_df.sort_values(by='comment_rate', ascending=True)


# 좋아요 비율 기준 상위5, 하위5
like_top_5 = like_rank_df.head()
like_bottom_5 = like_rank_df.tail()

# 댓극 비율 기준 상위5, 하위5
comment_top_5 = comment_rank_df.head()
comment_bottom_5 = comment_rank_df.tail()


result = ['view_count', 'like_count', 'comment_count', 'like_rate', 'comment_rate']
df = {
    'all' : video_final_df,
    'top5' : top5_final_df,
    'bottom5' : bottom5_final_df,
    'like_top5' :  like_top_5,
    'like_bottom5' : like_bottom_5,
    'comment_top5' :  comment_top_5,
    'comment_bottom5' : comment_bottom_5,
}
index_list = ['publish_year', 'publish_day', 'publish_time_label', 'publish_am_pm', 'duration_label']
pivot_final_result = {}

# 폴더 없는 경우 생성
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 성과분석
def pivot_result(final_df, z, x, y=None) : # result 값에 대한 평균, 총합, 갯수 산출
    # result 값에 대한 평균, 총합, 갯수 산출
    return final_df.pivot_table(
        index=x, columns=y,
        values=z,
        aggfunc=['mean', 'sum', 'count']
    )

# 업로드 당 평균 조회수
def avg_views_per_upload(final_df, x, y=None) :
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

    return avg_views


now = datetime.now().strftime('%Y-%m-%d_%H%M%S') # 날짜+시간을 파일명으로 쓸 수 있게 형식화

makedirs(f'../3. Analysis_result/{now} total_result')

# all, top5, bottom별 / 전체 분석, 각 지표별 분석 결과 파일 생성 / 표측-표두별로 시트 생성
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

        # 히트맵 생성 및 저장
        plt.rc("font", family="AppleGothic")  # 한글 폰트 설정
        plt.figure(figsize=(10, 8))  # 그래프 크기 조정
        hm = sns.heatmap(all_corr, annot=True, fmt=".2f", cmap="coolwarm")
        plt.title(f"({name}) 상관계수 히트맵", fontsize=16)
        plt.show()
        hm.get_figure().savefig(f"../3. Analysis_result/{now} total_result/{name}/({name}) 상관계수_히트맵.png")
        plt.close()


        if name in ['like_top5', 'like_bottom5', 'comment_top5', 'comment_bottom5'] : # 좋아요 비율, 댓글 비율 기준 상위5, 하위5인 경우 데이터도 엑셀로 저장
            data.to_excel(writer, sheet_name = f'{name}_data')

    # 성과분석_엑셀 통합파일 생성
    for z in result:
        with pd.ExcelWriter(f'../3. Analysis_result/{now} total_result/{name}/1-2. {name} ssglanders_{z}_analysis.xlsx', engine='xlsxwriter') as writer:
            for index in index_list:
                pivot_result(data, z, data[f'{index}']).to_excel(writer, sheet_name=f'{index}_성과분석')
                avg_views_per_upload(data, data[f'{index}']).to_excel(writer, sheet_name=f'{index}_평균조회수')
                if index == 'publish_day':
                    for column in ['publish_time_label', 'publish_am_pm', 'duration_label']:
                        pivot_result(data, z, data[f'{index}'], data[f'{column}']).to_excel(writer, sheet_name=f'day_{column}_성과분석')
                        avg_views_per_upload(data, data[f'{index}'], data[f'{column}']).to_excel(writer, sheet_name=f'day_{column}_평균조회수')
                if index == 'publish_time_label':
                    pivot_result(data, z, data[f'{index}'], data['duration_label']).to_excel(writer, sheet_name=f'time_duration_성과분석')
                    avg_views_per_upload(data, data[f'{index}'], data['duration_label']).to_excel(writer, sheet_name=f'time_duration_평균조회수')
                if index == 'publish_am_pm':
                    pivot_result(data, z, data[f'{index}'], data['duration_label']).to_excel(writer,
                                                                                             sheet_name=f'am_pm_duration_성과분석')
                    avg_views_per_upload(data, data[f'{index}'], data['duration_label']).to_excel(writer,
                                                                                                  sheet_name=f'am_pm_duration_평균조회수')
