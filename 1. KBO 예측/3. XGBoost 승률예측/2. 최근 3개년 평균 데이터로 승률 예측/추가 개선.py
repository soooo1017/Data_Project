import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data_v1.xlsx')


# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()


# 3. 주요 스탯 변화율 추가 함수
def calculate_feature_change_rate(df, year, features):
    prev_year_data = df[df['연도'] == year - 1][['팀명_라벨링'] + features].set_index('팀명_라벨링')
    current_year_data = df[df['연도'] == year][['팀명_라벨링'] + features].set_index('팀명_라벨링')

    # NaN 발생 방지 (팀이 새로 생겼거나 데이터가 없는 경우)
    change_rate = (current_year_data - prev_year_data) / prev_year_data
    change_rate = change_rate.reset_index().fillna(0)  # NaN 값 0으로 처리
    change_rate.columns = [f"{col}_변화율" if col != '팀명_라벨링' else col for col in change_rate.columns]

    return change_rate


# 4. 사용할 변수 설정
features = ['WHIP_pitcher', 'R_pitcher', 'BPC_pitcher', 'OPS_hitter', 'R_hitter',
            'AVG_hitter', 'FPCT_defense', 'SB_defense', 'SB_runner', 'SBA_runner']

change_features = ['OPS_hitter', 'R_hitter', 'WHIP_pitcher', 'ERA_pitcher']

y_target = '승률'

# 5. 학습 데이터 준비 (2005~2023년)
train_list = []
for year in range(2005, 2024):
    avg_data = calculate_3yr_avg(Final_df, year, features)
    actual_winrate = Final_df[Final_df['연도'] == year][['팀명_라벨링', '승률']]
    change_rate = calculate_feature_change_rate(Final_df, year, change_features)

    merged_data = avg_data.merge(actual_winrate, on='팀명_라벨링', how='left')
    merged_data = merged_data.merge(change_rate, on='팀명_라벨링', how='left')

    merged_data['연도'] = year
    train_list.append(merged_data)

train_df = pd.concat(train_list, ignore_index=True)

# 6. X, y 설정
X_train = train_df.drop(columns=['팀명_라벨링', '연도', y_target])
y_train = train_df[y_target]

# 7. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=120, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 8. 2024년 예측
X_test_2024 = calculate_3yr_avg(Final_df, 2024, features)
change_rate_2024 = calculate_feature_change_rate(Final_df, 2024, change_features)

X_test_2024 = X_test_2024.merge(change_rate_2024, on='팀명_라벨링', how='left')
X_test_2024 = X_test_2024.drop(columns=['팀명_라벨링'])

y_2024_pred = model.predict(X_test_2024)

# 9. 예측값 저장 및 정규화
Final_df.loc[Final_df['연도'] == 2024, '예측_승률'] = y_2024_pred
Final_df['예측_승률_정규화'] = (Final_df['예측_승률'] - Final_df['예측_승률'].min()) / (
            Final_df['예측_승률'].max() - Final_df['예측_승률'].min())

# 10. 예측 순위 계산
Final_df['예측_순위'] = Final_df[Final_df['연도'] == 2024]['예측_승률'].rank(ascending=False, method='min')

# 11. 모델 평가
mae = mean_absolute_error(y_train, model.predict(X_train))
mse = mean_squared_error(y_train, model.predict(X_train))
r2 = r2_score(y_train, model.predict(X_train))

print(f"📊 평균절대오차(MAE): {mae:.4f}")
print(f"📊 평균제곱오차(MSE): {mse:.4f}")
print(f"📊 결정계수(R²): {r2:.4f}")

# 12. 결과 출력
print(Final_df[Final_df['연도'] == 2024][['팀명', '연도', '예측_승률', '예측_승률_정규화', '예측_순위', '승률', '순위']])
