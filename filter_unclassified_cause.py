import pandas as pd

# 데이터 불러오기
data = pd.read_csv('combined_LER_reports.csv')

# 'Unclassified' 원인 제거
filtered_data = data[data['Cause Labels'].apply(lambda labels: 'Unclassified' not in eval(labels))]

# 필터링된 데이터 저장
filtered_filename = "filtered_LER_reports.csv"
filtered_data.to_csv(filtered_filename, index=False)

print(f"필터링된 데이터가 {filtered_filename}에 저장되었습니다.")
