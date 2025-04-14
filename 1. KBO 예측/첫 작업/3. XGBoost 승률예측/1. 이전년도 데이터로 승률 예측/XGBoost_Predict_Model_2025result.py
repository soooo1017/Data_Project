import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
import pandas as pd

# 1. 데이터 준비 (Feature & Target)
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')
X =['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher',
    'OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter',
    'FPCT_defense', 'SB_defense', 'PB_defense', 'E_defense', 'CS%_defense',
    'SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']  # 예측에 사용할 주요 지표
Y = ['예측_승률']  # 예측 대상

# 2. 훈련 데이터와 테스트 데이터 분리 (2023년 이전까지의 데이터로 학습 후 2023년 데이터로 2024년 승률 예측)
# 2-1. 학습 데이터(X_train, y_train) 준비 (2023, 2024년 제외)
X_train = Final_df[Final_df['연도'] < 2024][X]
y_train = Final_df[Final_df['연도'] < 2024][Y]

# 2-2. 2023년 데이터로 X_test 생성 (2024년을 예측할 데이터)
X_test = Final_df[Final_df['연도'] == 2024][X]

# 3. XGBoost 모델 생성 및 훈련
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=9)
model.fit(X_train, y_train)

# 4. 2025년 예측
y_2025_pred = model.predict(X_test)

# 5. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2025_pred

print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률']])
