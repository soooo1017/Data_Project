import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. 사용할 변수 선택 (최적 변수 10개)
selected_features = ['RBI_hitter', 'WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'OPS_hitter',
                     'CS_runner', 'CS%_defense', 'BPC_pitcher', 'E_defense', 'SB_runner']

# 3. 훈련 데이터 (2024년 이전 데이터)
X_train = Final_df[Final_df['연도'] < 2024][selected_features]
y_train = Final_df[Final_df['연도'] < 2024]['예측_승률']

# 4. 테스트 데이터 (2024년 데이터로 2025년 예측)
X_test = Final_df[Final_df['연도'] == 2024][selected_features]

# 5. XGBoost 모델 생성
xgb_model = xgb.XGBRegressor(objective='reg:squarederror')

# 6. 하이퍼파라미터 후보 설정
param_grid = {
    'n_estimators': [100, 130, 150],  # 트리 개수
    'learning_rate': [ 0.05, 0.1, 0.15, 0.2],  # 학습률
    'max_depth': [3, 5, 7]  # 트리 깊이
}

# 7. GridSearchCV 실행 (교차검증 5번 진행)
grid_search = GridSearchCV(xgb_model, param_grid, cv=10, scoring='r2', n_jobs=-1)
grid_search.fit(X_train, y_train)

# 8. 최적의 하이퍼파라미터 출력
print("최적의 하이퍼파라미터:", grid_search.best_params_)
print("최적 모델 성능 (R²):", grid_search.best_score_)

# 9. 최적의 모델로 다시 학습
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# 10. 2025년 승률 예측
y_2025_pred = best_model.predict(X_test)

# 11. 예측값 저장
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2025_pred

# 12. 모델 성능 평가 (이전 데이터로 평가)
y_train_pred = best_model.predict(X_train)

mae = mean_absolute_error(y_train, y_train_pred)
mse = mean_squared_error(y_train, y_train_pred)
r2 = r2_score(y_train, y_train_pred)

print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 13. 2025년 예측 승률 출력
print("\n📌 2025년 예측 승률")
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률', '승률']])
