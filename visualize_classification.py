import pandas as pd
import matplotlib.pyplot as plt
import os

# results 폴더 생성
os.makedirs('./results', exist_ok=True)

# 데이터 불러오기
data = pd.read_csv('./combined_LER_reports.csv')

# Cause와 Incident 각각의 라벨 리스트 추출
data['Cause Labels'] = data['Cause Labels'].apply(eval)
data['Incident Labels'] = data['Incident Labels'].apply(eval)

# 각 라벨별 분류와 Unclassified 분류
def classify_data(label_column):
    classified = data[data[label_column].str.len() > 0]
    unclassified = data[data[label_column].str.len() == 0]
    return classified, unclassified

cause_classified, cause_unclassified = classify_data('Cause Labels')
incident_classified, incident_unclassified = classify_data('Incident Labels')

# 각 클래스별 개수 계산
def get_class_counts(classified_data, label_column):
    all_labels = sum(classified_data[label_column], [])
    return pd.Series(all_labels).value_counts()

cause_counts = get_class_counts(cause_classified, 'Cause Labels')
incident_counts = get_class_counts(incident_classified, 'Incident Labels')

# 미분류 데이터 포함한 비율 계산 및 파이차트 생성
def plot_pie_with_unclassified(counts, unclassified_count, title, filename):
    unclassified_series = pd.Series({'Unclassified': unclassified_count})
    counts_with_unclassified = pd.concat([counts, unclassified_series])

    counts_with_unclassified_percentage = counts_with_unclassified / counts_with_unclassified.sum() * 100

    plt.figure(figsize=(8, 8))
    plt.pie(
        counts_with_unclassified_percentage,
        labels=counts_with_unclassified_percentage.index,
        autopct='%1.1f%%',
        startangle=140
    )
    plt.title(title)
    plt.savefig(filename)
    plt.close()

# Cause 파이차트 저장
plot_pie_with_unclassified(
    cause_counts,
    len(cause_unclassified),
    'Cause Labels Distribution (Including Unclassified)',
    './results/cause_class_distribution.png'
)

# Incident 파이차트 저장
plot_pie_with_unclassified(
    incident_counts,
    len(incident_unclassified),
    'Incident Labels Distribution (Including Unclassified)',
    './results/incident_class_distribution.png'
)

print("Cause와 Incident 분류 파이차트가 성공적으로 저장되었습니다.")
