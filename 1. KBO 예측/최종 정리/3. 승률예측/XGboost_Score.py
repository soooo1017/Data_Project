import pandas as pd
import xgboost as xgb
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 데이터 로드
final_data = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v3.xlsx')

# X와 Y로 분리
# 사용할 변수
features = ['R_hitter', 'WHIP_pitcher', 'OPS_hitter', 'ERA_pitcher', 'R_pitcher',
            'BPC_pitcher', 'AVG_hitter', 'RBI_hitter', 'CS_runner', 'E_defense' ]

X = final_data[features]
Y = final_data['승률']

# 3. 훈련 데이터
X_train = final_data[final_data['연도'] < 2024][features]
y_train = final_data[final_data['연도'] < 2024]['승률']

# 4. 테스트 데이터
X_test = final_data[final_data['연도'] == 2024][features]
y_test = final_data[final_data['연도'] == 2024]['승률']


# 5. XGBoost 모델 생성
xgb_model = xgb.XGBRegressor(objective='reg:squarederror')

# 6. 하이퍼파라미터 후보 설정
param_grid = {
    'n_estimators': [100, 130, 150],  # 트리 개수
    'learning_rate': [ 0.05, 0.1, 0.15, 0.2],  # 학습률
    'max_depth': [3, 5, 7]  # 트리 깊이
}

# 7. GridSearchCV 실행 (교차검증 5번 진행)
grid_search = GridSearchCV(xgb_model, param_grid, cv=5, scoring='r2', n_jobs=-1)
grid_search.fit(X_train, y_train)

# 9. 최적의 모델로 다시 학습
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)


# 예측하기
Y_pred = best_model.predict(X_test)
predictions = [value for value in Y_pred]


# 평가하기
rank_mae = mean_absolute_error(y_test, predictions)
rank_mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"📊 순위 예측 MAE (평균 오차): {rank_mae:.2f} 계단")
print(f"📊 순위 예측 MSE: {rank_mse:.2f}")
print(f"📊 R²: {r2:.4f}")

# 11. 예측값 출력
final_data.loc[final_data['연도'] == 2024, '예측_승률'] = predictions
print(final_data[final_data['연도'] == 2024][['팀명', '연도', '예측_승률', '승률']])
