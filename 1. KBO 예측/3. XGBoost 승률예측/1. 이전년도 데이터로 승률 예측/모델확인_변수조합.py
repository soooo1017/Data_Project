import xgboost as xgb
import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.metrics import r2_score, mean_absolute_error

# 1. 데이터 로드
Final_df = pd.read_excel(
    '/Users/SOO/Desktop/데분 포트폴리오/Data_Project/1. KBO 예측/2. 데이터 전처리/최종 데이터 정리/Final_KBO_Data.xlsx')

# 2. 초기 변수 설정
base_features = ['WHIP_pitcher', 'ERA_pitcher', 'R_pitcher', 'AVG_pitcher', 'BPC_pitcher',
                 'OPS_hitter', 'RISP_hitter', 'R_hitter', 'RBI_hitter', 'AVG_hitter',
                 'FPCT_defense', 'SB_defense', 'E_defense', 'PB_defense', 'CS%_defense',
                 'SB_runner', 'SBA_runner', 'OOB_runner', 'CS_runner']

# 3. 결과 저장을 위한 리스트 초기화
results_list = []

# 4. 단계적 변수 추가 알고리즘 (최대 5개 변수 조합으로 제한)
max_features = 19  # 전체 테스트 시 19로 변경 (주의: 조합 수 급격히 증가)
total_combos = sum([len(list(combinations(base_features, i))) for i in range(1, max_features + 1)])  # 전체 조합 수 계산
progress = 0  # 진행 상황 추적

print(f"🚀 총 {total_combos}개의 변수 조합을 테스트합니다!")

for step in range(10, max_features + 1):
    combos = list(combinations(base_features, step))  # 해당 단계의 모든 조합 리스트화
    print(f"\n🔹 {step}개 변수 조합 테스트 시작 (총 {len(combos)}개)")

    for idx, combo in enumerate(combos):
        progress += 1  # 진행 카운트 증가
        print(f"▶ 진행률: {progress}/{total_combos} ({(progress / total_combos) * 100:.2f}%)")

        # 데이터 분할
        X_train = Final_df[Final_df['연도'] < 2023][list(combo)]
        y_train = Final_df[Final_df['연도'] < 2023]['예측_승률']
        X_test = Final_df[Final_df['연도'] == 2023][list(combo)]
        y_test = Final_df[Final_df['연도'] == 2024]['승률']

        # 모델 훈련
        model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=7)
        model.fit(X_train, y_train)

        # 성능 평가
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        # 결과 저장
        results_list.append({
            '변수_조합': '+'.join(combo),
            '변수_수': step,
            'R²': r2,
            'MAE': mae
        })

        # 현재 조합의 성능 출력
        print(f"   📊 R²: {r2:.4f} | MAE: {mae:.4f}")

# 5. 결과를 DataFrame으로 변환
results_df = pd.DataFrame(results_list)

# 6. 성능 기준 정렬 및 상위 조합 출력
results_df = results_df.sort_values('R²', ascending=False)

# 7. 엑셀 파일로 저장
results_df.to_excel('모든_변수조합_결과_all.xlsx', index=False)

print("\n✅ 모든 테스트 완료! 결과가 '모든_변수조합_결과_all_V2.xlsx' 파일로 저장되었습니다.")
