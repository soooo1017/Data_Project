'''
import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')


# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

# 3. 사용할 변수 설정
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner' ]

# 'ERA_pitcher', 'OOB_runner', 'E_defense', 'RBI_hitter', 'CS%_defense', 'RISP_hitter', 'AVG_pitcher', 'CS_runner', 'PB_defense'

y_target = '승률'

# 4. 학습 데이터 준비 (2005~2023년)
train_list = []
for year in range(2005, 2024):  # 2005년부터 2023년까지 학습 데이터 생성
    avg_data = calculate_3yr_avg(Final_df, year, features)
    actual_winrate = Final_df[Final_df['연도'] == year][['팀명_라벨링', '승률']]
    merged_data = avg_data.merge(actual_winrate, on='팀명_라벨링', how='left')
    merged_data['연도'] = year
    train_list.append(merged_data)
train_df = pd.concat(train_list, ignore_index=True)

X_train = train_df[features]
y_train = train_df[y_target]

# 5. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)


# 6. 평가 (2024년 데이터를 기반으로 한 테스트)
y_2024_pred = model.predict(calculate_3yr_avg(Final_df, 2024, features)[features])
y_2024_true = Final_df[Final_df['연도'] == 2024]['승률'].values


# 7. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2024_pred

# 8. 예측 순위 계산
y_2024_pred_df = Final_df[Final_df['연도'] == 2024].copy()
y_2024_pred_df = y_2024_pred_df.sort_values(by='예측_승률', ascending=False)
y_2024_pred_df['예측_순위'] = range(1, len(y_2024_pred_df) + 1)

# 9. 모델 평가
mae = mean_absolute_error(y_train, model.predict(X_train))
mse = mean_squared_error(y_train, model.predict(X_train))
r2 = r2_score(y_train, model.predict(X_train))

# 10. 결과 출력
print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 11. 예측값 출력
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률', '승률', '예측_순위', '순위']])
'''

import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

# 3. 사용할 변수 설정
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner']
y_target = '승률'

# 4. 학습 데이터 준비 (2005~2023년)
train_list = []
for year in range(2005, 2024):
    avg_data = calculate_3yr_avg(Final_df, year, features)
    actual_winrate = Final_df[Final_df['연도'] == year][['팀명_라벨링', '승률']]
    merged_data = avg_data.merge(actual_winrate, on='팀명_라벨링', how='left')
    merged_data['연도'] = year
    train_list.append(merged_data)
train_df = pd.concat(train_list, ignore_index=True)
X_train = train_df[features]
y_train = train_df[y_target]

# 5. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)
import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v1.xlsx')


# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

# 3. 사용할 변수 설정
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner' ]

# 'ERA_pitcher', 'OOB_runner', 'E_defense', 'RBI_hitter', 'CS%_defense', 'RISP_hitter', 'AVG_pitcher', 'CS_runner', 'PB_defense'

y_target = '승률'

# 4. 학습 데이터 준비 (2005~2023년)
train_list = []
for year in range(2005, 2024):  # 2005년부터 2023년까지 학습 데이터 생성
    avg_data = calculate_3yr_avg(Final_df, year, features)
    actual_winrate = Final_df[Final_df['연도'] == year][['팀명_라벨링', '승률']]
    merged_data = avg_data.merge(actual_winrate, on='팀명_라벨링', how='left')
    merged_data['연도'] = year
    train_list.append(merged_data)
train_df = pd.concat(train_list, ignore_index=True)

X_train = train_df[features]
y_train = train_df[y_target]

# 5. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)


# 6. 평가 (2024년 데이터를 기반으로 한 테스트)
y_2024_pred = model.predict(calculate_3yr_avg(Final_df, 2024, features)[features])
y_2024_true = Final_df[Final_df['연도'] == 2024]['승률'].values


# 7. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2024_pred

# 8. 모델 평가
mae = mean_absolute_error(y_train, model.predict(X_train))
mse = mean_squared_error(y_train, model.predict(X_train))
r2 = r2_score(y_train, model.predict(X_train))

# 9. 결과 출력
print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 10. 예측값 출력
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률', '승률', '순위']])

# 6. 평가 (2024년 데이터를 기반으로 한 테스트)
y_2024_pred = model.predict(calculate_3yr_avg(Final_df, 2024, features)[features])
y_2024_true = Final_df[Final_df['연도'] == 2024]['승률'].values

# 7. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2024_pred

# 8. 예측 순위 계산
y_2024_pred_df = Final_df[Final_df['연도'] == 2024].copy()
y_2024_pred_df = y_2024_pred_df.sort_values(by='예측_승률', ascending=False)
y_2024_pred_df['예측_순위'] = range(1, len(y_2024_pred_df) + 1)

# 9. 모델 평가
mae = mean_absolute_error(y_train, model.predict(X_train))
mse = mean_squared_error(y_train, model.predict(X_train))
r2 = r2_score(y_train, model.predict(X_train))

# 10. 결과 출력
print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 11. 예측값 출력 (팀명, 연도, 예측 승률, 실제 승률, 실제 순위, 예측 순위)
print(y_2024_pred_df[['팀명', '연도', '예측_승률', '승률', '순위', '예측_순위']])
