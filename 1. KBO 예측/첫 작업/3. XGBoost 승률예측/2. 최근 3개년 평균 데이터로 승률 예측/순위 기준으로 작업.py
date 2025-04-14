import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v1.xlsx')

# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

# 3. 사용할 변수 설정
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner' ]
target = '순위'  # 순위 예측

# 4. 학습 데이터 준비 (2005~2023년)
train_list = []
for year in range(2005, 2024):  # 2005~2023년 데이터를 학습에 사용
    avg_data = calculate_3yr_avg(Final_df, year, features)
    actual_rank = Final_df[Final_df['연도'] == year][['팀명_라벨링', '순위']]
    merged_data = avg_data.merge(actual_rank, on='팀명_라벨링', how='left')
    merged_data['연도'] = year
    train_list.append(merged_data)

train_df = pd.concat(train_list, ignore_index=True)

# 5. XGBoost 회귀 모델 학습을 위한 데이터 준비
X_train = train_df[features]
y_train = train_df[target]  # 순위를 그대로 학습

# 6. XGBoost 회귀 모델 학습
model = xgb.XGBRegressor(n_estimators=120, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 7. 2024년 순위 예측
X_test = calculate_3yr_avg(Final_df, 2024, features)[features]
y_2024_pred = model.predict(X_test)  # 예측값이 실수형태로 나옴

# 8. 예측값 정수 변환 (반올림 후 1~10 범위 조정)
y_2024_pred = [max(1, min(10, round(rank))) for rank in y_2024_pred]

# 9. 실제 순위 데이터와 비교
y_2024_true = Final_df[Final_df['연도'] == 2024]['순위'].values

# 10. 평가 지표 출력
rank_mae = mean_absolute_error(y_2024_true, y_2024_pred)
rank_mse = mean_squared_error(y_2024_true, y_2024_pred)
r2 = r2_score(y_2024_true, y_2024_pred)

print(f"📊 순위 예측 MAE (평균 오차): {rank_mae:.2f} 계단")
print(f"📊 순위 예측 MSE: {rank_mse:.2f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 11. 예측값 출력
Final_df.loc[Final_df['연도'] == 2024, '예측_순위'] = y_2024_pred
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_순위', '순위']])
