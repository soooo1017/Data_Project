import pandas as pd  # 데이터 처리 및 분석
import matplotlib.pyplot as plt  # 그래프를 그리기 위한 라이브러리
import re  # 정규 표현식 처리
from mecab import MeCab  # 한국어 형태소 분석
from collections import Counter  # 단어 빈도 수를 세는 도구
from wordcloud import WordCloud  # 워드클라우드를 만들기 위한 라이블러리
import os  # 폴더 생성, 경로 처리 등
from datetime import datetime  # 날짜 및 시간 처리
import numpy as np


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기

# 영상 데이터
all_final_df = pd.read_excel('../2. Data_Preprocessing/ssglanders_video_final.xlsx')
top5_final_df = pd.read_excel('../2. Data_Preprocessing/top5_video_final.xlsx')
bottom5_final_df = pd.read_excel('../2. Data_Preprocessing/bottom5_video_final.xlsx')

# 댓글 데이터
all_comment_df = pd.read_excel('../2. Data_Preprocessing/(ALL)_comment_data.xlsx')
top5_comment_df = pd.read_excel('../2. Data_Preprocessing/(TOP5)_comment_data.xlsx')
bottom5_comment_df = pd.read_excel('../2. Data_Preprocessing/(BOTTOM5)_comment_data.xlsx')

# 댓글 텍스트 데이터만 추출
all_text = all_comment_df['text'][all_comment_df['text'].notnull()].dropna() # 전체 댓글
top5_text = top5_comment_df['text'][top5_comment_df['text'].notnull()].dropna() # 상위5 댓글
bottom5_text = bottom5_comment_df['text'][bottom5_comment_df['text'].notnull()].dropna() # 하위5 댓글

all_text= all_text.astype(dtype='object')
top5_text= top5_text.astype(dtype='object')
bottom5_text= bottom5_text.astype(dtype='object')

text_df = {
    'all' : all_text,
    'top5' : top5_text,
    'bottom5' : bottom5_text
}

# 폴더 없는 경우 생성
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 기본 폴더 경로 생성
now = datetime.now().strftime('%Y-%m-%d_%H%M%S') # 날짜+시간을 파일명으로 쓸 수 있게 형식화
makedirs(f'../3. Analysis_result/{now} comment_result/text_length')
base_path = f'../3. Analysis_result/{now} comment_result/text_length'

# makedirs(f'{base_path}/video')

# 댓글에서 \n, \t, \\, \ 등을 제거하는 함수
def clean_special_chars(text):
    text = re.sub(r'\\n', ' ', text)  # \n을 공백으로 치환
    text = re.sub(r'\\t', ' ', text)  # \t을 공백으로 치환
    text = re.sub(r'\\\\', ' ', text)  # \\ (역슬래시)를 공백으로 치환
    return text

# 텍스트 길이 확인 함수 -> 길이 그래프도 확인 및 파일 저장
def analyze_text_length(deta, label, graph_file_path, stats_file_path) :
    text_num = [len(str(text)) if isinstance(text, str) else 0 for text in deta]

    plt.figure(figsize=(14,5))
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.hist(text_num, bins=80, range=[0,150], color = 'b', label = label)
    plt.legend()
    plt.title('댓글 길이 확인')
    plt.xlabel('텍스트 길이')
    plt.ylabel('해당 길이에 속하는 텍스트 개수')
    plt.savefig(f'{base_path}/{graph_file_path}')
    # plt.show()
    plt.close()  # ✅ 메모리 정리

    mean = np.mean(text_num)
    max = np.max(text_num)
    min = np.min(text_num)
    median = np.median(text_num)
    quartiles = np.percentile(text_num, [25, 50, 75])

    text_describe = pd.DataFrame({
        '구분' : ['mean', 'max', 'min', 'median', 'quartiles'],
        '통계값' : [mean, max, min, median, quartiles]
    })

    text_describe.to_excel(f'{base_path}/{stats_file_path}', index=False)

    return text_num

all_text = all_text.astype(str).apply(clean_special_chars)
top5_text = top5_text.astype(str).apply(clean_special_chars)
bottom5_text = bottom5_text.astype(str).apply(clean_special_chars)

# 영상 전체, 상위5, 하위5개 댓글 길이 파악
for name, data in text_df.items() :
    makedirs(f'{base_path}/{name}')
    text_count = analyze_text_length(data, f'{name}_댓글', f'{name}/1-1.{name}_text_num_graph.png', f'{name}/1-2.{name}_text_describe.xlsx')

print("영상 전체, 상위5, 하위5의 댓글 길이 분석 완료했습니다!")
'''
# 영상별 댓글 길이 그래프 생성
for id, group in all_comment_df.groupby('id') :
    group_text = group['text'][group['text'].notnull()].dropna()
    group_text = group_text.astype(dtype='object')
    makedirs(f'{base_path}/video/{id}')
    graph_file_path = f"video/{id}/1-1. comment_text_num_graph.png"
    stats_file_path = f"video/{id}/1-2. comment_text_describe.xlsx"

    analyze_text_length(group_text, f'{id}번 영상 댓글', graph_file_path, stats_file_path)

    print(f"{id}의 댓글 길이 분석 완료했습니다!")
'''
# 반복 문자 패턴 정리
def normalize_repeated_char(text):
    text = re.sub(r'(ㅋ)\1{1,}', r'\1', text)  # ㅋㅋㅋㅋ → ㅋ
    text = re.sub(r'(ㅎ)\1{1,}', r'\1', text)  # ㅎㅎㅎㅎ → ㅎ
    text = re.sub(r'(ㄷ)\1{1,}', r'\1', text)  # ㄷㄷㄷ → ㄷ
    text = re.sub(r'(ㅠ)\1{1,}', r'\1', text)  # ㅠㅠㅠ → ㅠ
    text = re.sub(r'(ㅜ)\1{1,}', r'\1', text)  # ㅜㅜ → ㅜ
    text = re.sub(r'(\n)\1{1,}', r'\1', text)
    text = re.sub(r'(\r\n)\1{1,}', r'\1', text)
    text = re.sub(r'(\n\r)\1{1,}', r'\1', text)
    text = re.sub(r'(\r)\1{1,}', r'\1', text)
    text = re.sub(r'(\n )\1{1,}', r'\1', text)
    text = re.sub(r'(\r\n )\1{1,}', r'\1', text)
    text = re.sub(r'(\n\r )\1{1,}', r'\1', text)
    text = re.sub(r'(\r )\1{1,}', r'\1', text)
    text = re.sub(r'( )\1{1,}', r'\1', text)
    # 숫자 제거
    text = re.sub(r'\d+', '', text)
    # 이모티콘, 특수문자 제거
    text = re.sub(r'[^\w\s]', '', text)
    return text


# 반복 문자 정리
all_text = all_text.apply(normalize_repeated_char)
top5_text = top5_text.apply(normalize_repeated_char)
bottom5_text = bottom5_text.apply(normalize_repeated_char)


# 불필요한 단어 리스트
custom_stopwords = []

# stopwords.txt 불러오기
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    file_stopwords = [line.strip() for line in f]

# 기존 custom_stopwords + 파일에서 불러온 stopwords 합치기
custom_stopwords.extend(file_stopwords)

# MeCab 형태소 분석기 객체 생성
mecab = MeCab()

makedirs(f'../3. Analysis_result/{now} comment_result/text_distribution')

# 불용어 제거 및 품사 태깅
for type in text_df.keys() :
    prepro_words = []
    for comment in text_df[type] :
        for word, tag in mecab.pos(comment) :
            # VV: 동사 / VA: 형용사 / NN* : 명사
            if tag.startswith(('VV', 'VA', 'NN')) or tag == 'SL':
                if tag == 'SL':
                    word = word.upper()
                if word not in custom_stopwords:
                    prepro_words.append(word)

    # 한자리 단어 제외
    prepro_words = [word for word in prepro_words if len(word) > 1]

    # 오타 교정 사전
    normalize_dict = {
        '김광민': '김강민', '강민': '김강민', '강민아': '김강민', '강민형': '김강민', '김강만': '김강민', '재미있': '재미', '귀엽': '귀여워',
        '성현': '김성현', '성현아': '김성현', '지훈': '최지훈', '성한': '박성한', '유박': '박성한', '귀여': '귀여워', '귀여우': '귀여워',
        '귀여운': '귀여워', '귀여울': '귀여워', '귀여움': '귀여워', '귀여워': '귀여워', '귀여워서': '귀여워', '귀요미': '귀여워',
        '그리우': '그리워', '그리운': '그리워', '그립': '그리워', '기다렸': '기다려', '기다리': '기다려', '기다린': '기다려',
        '날려라': '날려', '날리': '날려', '날릴': '날려', '넘겼': '넘어가', '넘기': '넘어가', '넘어간': '넘어가', '넘어갔': '넘어가',
        '넘어갔었': '넘어가', '넘어오': '넘어가', '때려서': '때려', '때려요': '때려', '때렸': '때려', '때리': '때려', '때린': '때려',
        '때릴': '때려', '라이온': '라이온즈', '멋있': '멋져요', '멋져': '멋져요', '멋지': '멋져요', '멋진': '멋져요', '미쳤': '미쳤다',
        '미친': '미쳤다', '미터': '미쳤다', '미팅': '미쳤다', '박성': '박성한', '보여': '보인다', '보여요': '보인다', '보유': '보인다',
        '보이': '보인다', '보임': '보인다', '부담': '부담감', '재미나': '재미', '재밌': '재미', '지환': '박지환', '진용': '서진용', '최재훈': '최지훈'
    }

    # 교정 적용
    prepro_words = [normalize_dict.get(word, word) for word in prepro_words]

    # 전처리된 텍스트 출력
    prepro_text = ' '.join(prepro_words)  # 전처리된 단어 합치기

    # 단어 빈도 계산
    word_counts = Counter(prepro_words)

    # Counter → DataFrame
    word_df = pd.DataFrame(word_counts.items(), columns=['word', 'count'])

    # count 기준으로 내림차순 정렬
    word_df = word_df.sort_values(by='count', ascending=False)

    makedirs(f'../3. Analysis_result/{now} comment_result/text_distribution/{type}')

    # print(word_df)
    word_df.to_csv(f'../3. Analysis_result/{now} comment_result/text_distribution/{type}/1-1. {type}_comment_text.csv', index=False, encoding='utf-8-sig')

    wc = word_df.set_index('word').to_dict()['count']

    wordCloud = WordCloud(
        font_path='AppleGothic',  # 폰트 지정
        width=400,  # 워드 클라우드의 너비 지정
        height=400,  # 워드 클라우드의 높이 지정
        max_font_size=100,  # 가장 빈도수가 높은 단어의 폰트 사이즈 지정
        background_color='white',  # 배경색 지정
        max_words=80  # 단어 표시 개수 제한
    ).generate_from_frequencies(wc)  # 워드 클라우드 빈도수 지정

    plt.figure()
    plt.imshow(wordCloud)
    plt.axis('off')
    plt.title(f'{type}_wordcloud')
    plt.savefig(f'../3. Analysis_result/{now} comment_result/text_distribution/{type}/1-2. {type}_wordcloud_graph.png')
    # plt.show()
    plt.close()

    print(f'{type} 작업 완료!')


'''
    prepro_words = []
    for comment in comment_text:
        for word, tag in mecab.pos(comment):
            # VV: 동사 / VA: 형용사 / NN* : 명사
            if tag.startswith(('VV', 'VA', 'NN')) or tag == 'SL':
                if tag == 'SL':
                    word = word.upper()
                if word not in custom_stopwords:
                    prepro_words.append(word)

# 한자리 단어 제외
prepro_words = [word for word in prepro_words if len(word) > 1]


# 오타 교정 사전
normalize_dict = {
    '김광민': '김강민',
    '강민': '김강민',
    '강민아' : '김강민',
    '강민형' : '김강민',
    '김강만' : '김강민',
    '재미있' : '재미',
    '귀엽' : '귀여워',
    '성현' : '김성현',
    '성현아' : '김성현',
    '지훈' : '최지훈',
    '성한' : '박성한',
    '유박' : '박성한',
    '귀여' : '귀여워',
    '귀여우' : '귀여워',
    '귀여운' : '귀여워',
    '귀여울' : '귀여워',
    '귀여움' : '귀여워',
    '귀여워' : '귀여워',
    '귀여워서' : '귀여워',
    '귀요미' : '귀여워',
    '그리우' : '그리워',
    '그리운' : '그리워',
    '그립' : '그리워',
    '기다렸' : '기다려',
    '기다리' : '기다려',
    '기다린' : '기다려',
    '날려라' : '날려',
    '날리' : '날려',
    '날릴' : '날려',
    '넘겼' : '넘어가',
    '넘기' : '넘어가',
    '넘어간' : '넘어가',
    '넘어갔' : '넘어가',
    '넘어갔었' : '넘어가',
    '넘어오' : '넘어가',
    '때려서' : '때려',
    '때려요' : '때려',
    '때렸' : '때려',
    '때리' : '때려',
    '때린' : '때려',
    '때릴' : '때려',
    '라이온' : '라이온즈',
    '멋있' : '멋져요',
    '멋져' : '멋져요',
    '멋지' : '멋져요',
    '멋진' : '멋져요',
    '미쳤' : '미쳤다',
    '미친' : '미쳤다',
    '미터' : '미쳤다',
    '미팅' : '미쳤다',
    '박성' : '박성한',
    '보여' : '보인다',
    '보여요' : '보인다',
    '보유' : '보인다',
    '보이' : '보인다',
    '보임' : '보인다',
    '부담' : '부담감',
    '재미나' : '재미',
    '재밌' : '재미',
    '지환' : '박지환',
    '진용' : '서진용',
    '최재훈' : '최지훈'
}

# 교정 적용
prepro_words = [normalize_dict.get(word, word) for word in prepro_words]


# 전처리된 텍스트 출력
prepro_text = ' '.join(prepro_words) # 전처리된 단어 합치기
# print(prepro_words)


# 단어 빈도 계산
word_counts = Counter(prepro_words)

# Counter → DataFrame
word_df = pd.DataFrame(word_counts.items(), columns=['word', 'count'])

# count 기준으로 내림차순 정렬
word_df = word_df.sort_values(by='count', ascending=False)

# print(word_df)
word_df.to_csv(f'../3. Analysis_result/4. ssglanders_comment_text.csv', index=False, encoding='utf-8-sig')

wc = word_df.set_index('word').to_dict()['count']

wordCloud = WordCloud(
    font_path='AppleGothic', # 폰트 지정
    width = 400, # 워드 클라우드의 너비 지정
    height = 400, # 워드 클라우드의 높이 지정
    max_font_size=100, # 가장 빈도수가 높은 단어의 폰트 사이즈 지정
    background_color='white', # 배경색 지정
    max_words=80 # 단어 표시 개수 제한
).generate_from_frequencies(wc) # 워드 클라우드 빈도수 지정

plt.figure()
plt.imshow(wordCloud)
plt.axis('off')
plt.show()
'''

'''
# 상위 100개 단어 추출
top_500 = word_df.head(500)

top_500.to_csv('../3. Analysis_result/4-1. top_500_words.csv', index=False, encoding='utf-8-sig')

'''