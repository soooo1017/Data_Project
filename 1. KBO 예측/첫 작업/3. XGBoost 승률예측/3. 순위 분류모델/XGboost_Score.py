import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 데이터 로드
final_data = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v3.xlsx')

# X와 Y로 분리
# 사용할 변수
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner' ]

X = final_data[features]
Y = final_data['승률']

# 3. 훈련 데이터
X_train = final_data[final_data['연도'] < 2024][features]
y_train = final_data[final_data['연도'] < 2024]['승률']

# 4. 테스트 데이터
X_test = final_data[final_data['연도'] == 2024][features]
y_test = final_data[final_data['연도'] == 2024]['승률']


# 학습 데이터로 모델 학습시키기
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 예측하기
Y_pred = model.predict(X_test)
predictions = [value for value in Y_pred]


# 평가하기
rank_mae = mean_absolute_error(y_test, predictions)
rank_mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"📊 순위 예측 MAE (평균 오차): {rank_mae:.2f} 계단")
print(f"📊 순위 예측 MSE: {rank_mse:.2f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 11. 예측값 출력
final_data.loc[final_data['연도'] == 2024, '예측_승률'] = predictions
print(final_data[final_data['연도'] == 2024][['팀명', '연도', '예측_승률', '승률']])
