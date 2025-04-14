import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
import pandas as pd

# 1. 데이터 준비 (Feature & Target)
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')
X =['ERA_pitcher', 'R_pitcher', 'OPS_hitter', 'RISP_hitter', 'AVG_hitter', 'SB_defense', 'E_defense', 'SB_runner', 'SBA_runner']  # 예측에 사용할 주요 지표
Y = ['예측_승률']  # 예측 대상




# 2. 훈련 데이터와 테스트 데이터 분리 (2023년 이전까지의 데이터로 학습 후 2023년 데이터로 2024년 승률 예측)
# 2-1. 학습 데이터(X_train, y_train) 준비 (2023, 2024년 제외)
X_train = Final_df[Final_df['연도'] < 2023][X]
y_train = Final_df[Final_df['연도'] < 2023][Y]

# 2-2. 2023년 데이터로 X_test 생성 (2024년을 예측할 데이터)
X_test = Final_df[Final_df['연도'] == 2023][X]
y_test = Final_df[Final_df['연도'] == 2024]['승률']

# 3. XGBoost 모델 생성 및 훈련
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.3, max_depth=5)
model.fit(X_train, y_train)

y_2024_pred = model.predict(X_test)  # 2023년 데이터로 예측한 2024년 예측 승률


# 6. 평가 (2023년 데이터로 예측한 2024년 승률과 2024년 실제 승률에 대한 모델 평가)
# 6-1. 평가 지표 계산
mae = mean_absolute_error(y_test, y_2024_pred)
mse = mean_squared_error(y_test, y_2024_pred)
r2 = r2_score(y_test, y_2024_pred)

# 6-2. 결과 출력
print(f"📊 평균절대오차(MAE): {mae:.4f}" )  # 평균절대오차 : 예측값과 실제값의 차이의 절댓값 평균 / 값이 작을수록 모델이 예측을 잘한 것!
print(f"📊 평균제곱오차(MSE): {mse:.4f}")   # 평균제곱오차 : 예측값과 실제값 차이를 제곱한 뒤 평균을 낸 값 / 이상치(극단적인 값)에 민감함!
print(f"📊 결정계수(R²): {r2:.4f}")     # 결정계수 : 모델이 데이터를 얼마나 잘 설명하는지 나타내는 지표 / 1에 가까울수록 예측이 잘 맞음! (보통 0.7 이상이면 괜찮은 모델!)
