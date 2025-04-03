import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. 선택한 변수만 사용
X_selected = ['RBI_hitter', 'WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'OPS_hitter',
              'CS_runner', 'CS%_defense', 'BPC_pitcher', 'E_defense', 'SB_runner']
Y = ['예측_승률']

# 3. 훈련 데이터와 테스트 데이터 분리 (2024년 제외)
X_train = Final_df[Final_df['연도'] < 2024][X_selected]
y_train = Final_df[Final_df['연도'] < 2024][Y]

# 4. 2024년 데이터로 X_test 생성 (2025년 예측)
X_test = Final_df[Final_df['연도'] == 2024][X_selected]

# 5. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
model.fit(X_train, y_train)

# 6. 2025년 예측
y_2025_pred = model.predict(X_test)

# 7. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2025_pred

# 8. 모델 평가
mae = mean_absolute_error(y_train, model.predict(X_train))
mse = mean_squared_error(y_train, model.predict(X_train))
r2 = r2_score(y_train, model.predict(X_train))

# 9. 결과 출력
print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 10. 예측값 출력
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률']])
