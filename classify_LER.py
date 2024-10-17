import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 로드
file_path = "./data/LERSearchResults_210101_231231.csv"

# 데이터 전처리: 필요한 컬럼 추출 및 NaN 제거
data_cleaned = pd.read_csv(file_path, skiprows=4)  # 4번째 행부터 데이터 시작
data_filtered = data_cleaned[['LER Number', 'Plant Name', 'Event Date', 'Report Date', 'Title/Abstract']].dropna(subset=['Title/Abstract'])

# Cause와 Incident 키워드 정의
cause_keywords = {
    'Design or Maintenance Issues': ['faulty', 'design', 'inadequate', 'aging', 'maintenance'],
    'Human Factors and Errors': ['operator', 'miscommunication', 'error', 'training'],
    'Systemic or Policy Failures': ['conflicting', 'regulations', 'inspection'],
    'External Factors': ['natural disasters', 'environmental', 'flood', 'weather']
}

incident_keywords = {
    'Equipment and Mechanical Failures': ['pump', 'valve', 'failure'],
    'Electrical and Power Issues': ['power', 'generator', 'outage'],
    'Operational Incidents': ['reactor trip', 'shutdown', 'manual actuation'],
    'Environmental and Containment Issues': ['leakage', 'containment', 'isolation']
}

# 멀티라벨 할당 함수
def assign_labels(text):
    cause_labels = [label for label, keywords in cause_keywords.items() if any(kw in text.lower() for kw in keywords)]
    incident_labels = [label for label, keywords in incident_keywords.items() if any(kw in text.lower() for kw in keywords)]
    return cause_labels, incident_labels

# 멀티라벨 할당
data_filtered['Cause Labels'], data_filtered['Incident Labels'] = zip(*data_filtered['Title/Abstract'].apply(assign_labels))

# 미분류된 보고서에 'Unclassified' 라벨 추가
data_filtered['Cause Labels'] = data_filtered['Cause Labels'].apply(lambda x: ['Unclassified'] if not x else x)
data_filtered['Incident Labels'] = data_filtered['Incident Labels'].apply(lambda x: ['Unclassified'] if not x else x)

# 모든 데이터를 새로운 CSV로 저장
combined_filename = "combined_LER_reports.csv"
data_filtered.to_csv(combined_filename, index=False)
print(f"{combined_filename}에 모든 데이터가 저장되었습니다.")
