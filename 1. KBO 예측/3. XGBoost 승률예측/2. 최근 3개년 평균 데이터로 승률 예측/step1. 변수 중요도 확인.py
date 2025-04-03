import xgboost as xgb
import matplotlib.pyplot as plt
import pandas as pd

# 1. 데이터 불러오기
Final_df = pd.read_excel('/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. 최근 3년 평균 데이터 생성 함수
def calculate_3yr_avg(df, year, columns):
    past_data = df[(df['연도'] >= year - 3) & (df['연도'] < year)]
    return past_data.groupby('팀명_라벨링')[columns].mean().reset_index()

# 3. 사용할 변수 설정
features = ['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher',
            'OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter',
            'FPCT_defense', 'SB_defense', 'PB_defense', 'E_defense', 'CS%_defense',
            'SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']

y_target = '승률'

# 4. 학습 데이터 준비 (2005~2023년)
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

# 5. XGBoost 모델 학습
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
model.fit(X_train, y_train)

# 6. 변수 중요도 시각화
plt.figure(figsize=(10, 6))
xgb.plot_importance(model, importance_type="gain")  # 정보획득량 기준
plt.show()
