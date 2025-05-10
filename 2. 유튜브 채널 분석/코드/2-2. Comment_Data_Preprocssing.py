import pandas as pd

video_final_df = pd.read_excel('../2. Data_Preprocessing/ssglanders_video_final.xlsx')
all_comment_df = pd.read_excel('../1. Data_Collection/(2025-05-09_232332)ssglanders_comments.xlsx')
top5_comment_df = pd.read_excel('../1. Data_Collection/(2025-05-09_225205)ssglanders_top5_comments.xlsx')
bottom5_comment_df = pd.read_excel('../1. Data_Collection/(2025-05-09_225205)ssglanders_bottom5_comments.xlsx')


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)


# comment_df 전처리
all_final_df =  all_comment_df.copy()
top5_final_df =  top5_comment_df.copy()
bottom5_final_df =  bottom5_comment_df.copy()

# 최종으로 남기고 싶은 데이터 리스트
column_list = ['video_id', 'comment_id', 'author', 'text', 'like_count_comment', 'published_at_comment',
               'comment_label', 'id', 'title', 'published_at_video', 'view_count', 'comment_video_publish']

# 'id' 컬럼 생성 (영상 인덱스 기반으로 id 생성)
def data_preprocssing(data) :
    data['comment_label'] = ['comment_' + str(i+1) for i in data.index]
    # print(pd.merge(data, video_final_df, on='video_id', how='left').head())
    merge_df = pd.merge(data, video_final_df, on='video_id', how='left', suffixes=('_comment', '_video'))

    # 'published_at' 컬럼을 datetime으로 변환
    merge_df['published_at_video'] = pd.to_datetime(merge_df['published_at_video'], format='%Y년 %m월 %d일 %H시 %M분 %S.%f초')
    merge_df['published_at_comment'] = pd.to_datetime(merge_df['published_at_comment']).dt.tz_localize(None)

    # 영상 업로드 후 댓글 달리기까지 걸린 시간
    merge_df['comment_video_publish'] = merge_df['published_at_comment'] - merge_df['published_at_video']

    # 최종 column_list만 추출
    final_df = merge_df[column_list]

    # data를 최종 DataFrame으로 덮어쓰기 → 만약 함수 밖에서 사용하려면 return
    return final_df

def save_file(data, name) :
    output_path = f'../2. Data_Preprocessing/({name})_comment_data.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name=name, index=False)

        workbook = writer.book
        worksheet = writer.sheets[name]

        # 3. id 관련 열의 인덱스 확인 (0-based → A=0, B=1, ...)
        id_columns = ['video_id', 'comment_id']
        for col in id_columns:
            if col in data.columns:
                col_idx = data.columns.get_loc(col)
                col_letter = chr(ord('A') + col_idx)
                # 열 서식을 텍스트로 지정
                worksheet.set_column(f'{col_letter}:{col_letter}', None, workbook.add_format({'num_format': '@'}))

    print(f"{name}의 {len(data)}개의 데이터를 Excel 파일로 저장했어요!")

all_final_df = data_preprocssing(all_final_df)
top5_final_df = data_preprocssing(top5_final_df)
bottom5_final_df = data_preprocssing(bottom5_final_df)

save_file(all_final_df, 'ALL')
save_file(top5_final_df, 'TOP5')
save_file(bottom5_final_df, 'BOTTOM5')

