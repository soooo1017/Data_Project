import xgboost as xgb
import matplotlib.pyplot as plt
import pandas as pd

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. Feature & Target 설정
X = ['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher',
     'OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter',
     'FPCT_defense', 'SB_defense', 'PB_defense', 'E_defense', 'CS%_defense',
     'SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']  # 예측 변수
Y = ['예측_승률']  # 목표 변수

# 3. 훈련 데이터와 테스트 데이터 분리 (2024년 이전 데이터로 훈련)
X_train = Final_df[Final_df['연도'] < 2024][X]
y_train = Final_df[Final_df['연도'] < 2024][Y]

# 4. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
model.fit(X_train, y_train)

# 5. 변수 중요도 시각화
plt.figure(figsize=(10, 6))
xgb.plot_importance(model, importance_type="gain")  # 정보획득량 기준
plt.show()
