import pandas as pd

import matplotlib.pyplot as plt

import re
from mecab import MeCab
from collections import Counter

from wordcloud import WordCloud


# 모든 컬럼 확인가능하도록 설정
pd.set_option('display.max_columns', None)

# 데이터 가져오기
video_final_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/2. Data_Preprocessing/ssglanders_video_final.csv')
comment_final_df = pd.read_csv('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/2. 유튜브 채널 분석/2. Data_Preprocessing/ssglanders_comment_final.csv')
comment_text = comment_final_df['text'][comment_final_df['text'].notnull()].dropna() # 전체 댓글

# 조회수 상위 5개
top5_videos = video_final_df.sort_values(by='view_count', ascending=False).head(5)['title'] # 영상
top5_comments = comment_final_df[comment_final_df['video_title'].isin(top5_videos)]['text'].dropna() # 영상 댓글

# 조회수 하위 5개
bottom5_videos = video_final_df.sort_values(by='view_count', ascending=True).head(5)['title'] # 영상
bottom5_comments = comment_final_df[comment_final_df['video_title'].isin(bottom5_videos)]['text'].dropna() # 영상 댓글


# 1. 텍스트 길이 확인 함수 -> 길이 그래프도 확인 및 파일 저장
def text_count(deta, label, save_path) :
    text_num = [len(text) for text in deta]

    plt.figure(figsize=(14,5))
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.hist(text_num, bins=80, range=[0,200], color = 'b', label = label)
    plt.legend()
    plt.title('댓글 길이 확인')
    plt.xlabel('텍스트 길이')
    plt.ylabel('해당 길이에 속하는 텍스트 개수')
    plt.savefig(save_path)
    # plt.show()

    return text_num

comment_text_num = text_count(comment_text, '전체 댓글', '../3. Analysis_result/4. comment_text_num_graph/4-1. Comment_text_num_graph.png')
top5_text_num = text_count(top5_comments, 'Top5 영상 댓글', '../3. Analysis_result/4. comment_text_num_graph/4-2. Top5_text_num_graph.png')
bottom5_text_num = text_count(bottom5_comments, 'Bottom5 영상 댓글', '../3. Analysis_result/4. comment_text_num_graph/4-3. Bottom5_text_num_graph.png')

# 영상별로 그룹
video_num = 4
video_match = {}
for video_title, group in comment_final_df.groupby('video_title'):
    group_text = group['text'].dropna()
    save_path = f"../3. Analysis_result/4. comment_text_num_graph/4-{video_num}. video_text_num_graph.png"

    text_count(group_text, f'{video_num}번 영상 댓글', save_path)

    video_match[video_num] = video_title
    video_num += 1

# print(pd.Series(comment_text_num).describe())

# 조사 등 불필요한 품사 및 단어 제거

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
comment_text = comment_text.apply(normalize_repeated_char)
top5_comments = top5_comments.apply(normalize_repeated_char)
bottom5_comments = bottom5_comments.apply(normalize_repeated_char)
text_dict = {
    'all': comment_text,
    'top5': top5_comments,
    'bottom5': bottom5_comments
}

video_num = 1
for video_title, group in comment_final_df.groupby('video_title'):
    group_text = group['text'].dropna().apply(normalize_repeated_char)
    text_dict[f'video_{video_num}'] = group_text
    video_num += 1



# 불필요한 단어 리스트
custom_stopwords = []

# stopwords.txt 불러오기
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    file_stopwords = [line.strip() for line in f]

# 기존 custom_stopwords + 파일에서 불러온 stopwords 합치기
custom_stopwords.extend(file_stopwords)

# MeCab 형태소 분석기 객체 생성
mecab = MeCab()

# 불용어 제거 및 품사 태깅
file_num = 0
for type in text_dict.keys() :
    prepro_words = []
    for comment in text_dict[type] :
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

    # print(word_df)
    word_df.to_csv(f'../3. Analysis_result/5. comment_word_df/5-{file_num}. {type}_comment_text.csv', index=False, encoding='utf-8-sig')

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
    plt.savefig(f'../3. Analysis_result/6. wordcloud_graph/6-{type}. wordcloud_graph.png')
    # plt.show()

    file_num += 1



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