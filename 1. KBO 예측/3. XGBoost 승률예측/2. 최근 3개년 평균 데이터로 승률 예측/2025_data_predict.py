import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd

# 1. 데이터 준비
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v1.xlsx')

# 2. 최근 3년 평균 데이터 생성 (팀이 존재하는 연도만 포함)
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

features = ['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher',
            'OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter',
            'FPCT_defense', 'SB_defense', 'PB_defense', 'E_defense', 'CS%_defense',
            'SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']

y_target = '승률'  # 예측할 값

# 3. 학습 데이터 준비
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

# 4. 2025년 예측 데이터 준비
X_test = calculate_3yr_avg(Final_df, 2025, features)

# 5. XGBoost 모델 학습 및 예측
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=7)
model.fit(X_train, y_train)
y_2025_pred = model.predict(X_test[features])

# 6. 평가 (2024년 데이터를 기반으로 한 테스트)
y_2024_pred = model.predict(calculate_3yr_avg(Final_df, 2024, features)[features])
y_2024_true = Final_df[Final_df['연도'] == 2024]['승률'].values

mae = mean_absolute_error(y_2024_true, y_2024_pred)
mse = mean_squared_error(y_2024_true, y_2024_pred)
r2 = r2_score(y_2024_true, y_2024_pred)

print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 7. 2025년 예측 결과 저장
X_test['예측_승률'] = y_2025_pred
print(X_test[['팀명_라벨링', '예측_승률']])
