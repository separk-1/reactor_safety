import os
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer

# LOCA 관련 키워드 분류 (초기 설정)
loca_keywords = {
    'coolant': 'cause', 'leakage': 'cause', 'pressure': 'cause', 'temperature': 'cause',
    'shutdown': 'effect', 'emergency': 'effect', 'reactor': 'effect', 'core': 'effect', 'failure': 'effect',
    'safety': 'countermeasure', 'containment': 'countermeasure', 'LOCA': 'countermeasure'
}

# 카테고리별 색상 설정
category_colors = {
    'cause': 'lightcoral',        # 원인 - 빨간색 계열
    'effect': 'lightblue',        # 결과 - 파란색 계열
    'countermeasure': 'lightgreen', # 조치 - 초록색 계열
    'other': 'lightgray'          # 새로 추가된 키워드는 회색
}

# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        text += doc[page_num].get_text()
    return text

# 모든 PDF 텍스트 추출
def extract_all_text_from_pdfs(folder_path):
    all_text = []
    pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.pdf')]
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        all_text.append(text)
    return all_text

# TF-IDF 분석을 통해 새로운 키워드 추출 (n-gram 적용)
def extract_additional_keywords(documents, max_features=20, ngram_range=(1, 3)):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=max_features, ngram_range=ngram_range)
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    return feature_names

# 키워드를 LOCA 카테고리로 분류
def categorize_keywords(extracted_keywords, loca_keywords, top_n=10):
    keyword_counts = Counter(extracted_keywords)
    # 상위 top_n개의 키워드만 표시
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(top_n)]
    for keyword in top_keywords:
        if keyword not in loca_keywords:
            loca_keywords[keyword] = 'other'
    return loca_keywords

# 키워드 공동 발생 계산
def calculate_cooccurrence(sentences, keywords):
    cooccurrence_counts = Counter()
    
    for sentence in sentences:
        words = sentence.lower().split()
        sentence_keywords = [kw for kw in keywords if kw in words]
        if len(sentence_keywords) > 1:
            for pair in itertools.combinations(sentence_keywords, 2):
                cooccurrence_counts[pair] += 1
                
    return cooccurrence_counts

# 지식 그래프 시각화 (원인 -> 결과 -> 조치 화살표 추가)
def visualize_cooccurrence_graph(cooccurrence_counts, loca_keywords):
    G = nx.DiGraph()  # 유향 그래프 생성
    
    for (kw1, kw2), weight in cooccurrence_counts.items():
        G.add_edge(kw1, kw2, weight=weight)

    # 노드 간의 간격을 조정 (k 값 높이기)
    pos = nx.spring_layout(G, k=1.0, iterations=50)
    
    # 엣지의 두께를 더 부드럽게 조정
    edges = G.edges(data=True)
    weights = [G[u][v]['weight'] / 20.0 for u, v in G.edges()]  # 가중치의 크기를 반으로 줄임
    
    # 노드 크기 설정
    node_sizes = [300 + 300 * G.degree(n) for n in G.nodes()]  # 노드의 크기를 노드의 연결도에 따라 줄임
    
    # 노드 색상 설정 (카테고리에 따른 색상 지정, 새로 추가된 키워드는 회색)
    node_colors = [category_colors[loca_keywords.get(node, 'other')] for node in G.nodes()]
    
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color="gray", node_size=node_sizes, font_size=10, width=weights, arrows=True, arrowstyle='-|>', arrowsize=20)
    plt.show()

# Main script
folder_path = './data/'  # PDF 파일들이 있는 폴더 경로
documents = extract_all_text_from_pdfs(folder_path)

# LOCA 관련 문장만 추출
loca_related_sentences = []
for doc in documents:
    loca_related_sentences.extend([sentence.strip() for sentence in doc.split('.') if any(kw in sentence.lower() for kw in loca_keywords)])

# TF-IDF를 통해 추가 키워드 추출
extracted_keywords = extract_additional_keywords(documents, max_features=50, ngram_range=(1, 3))

# LOCA 카테고리에 맞게 키워드 분류 추가 (상위 top_n개만 표시, 나머지는 제외)
loca_keywords = categorize_keywords(extracted_keywords, loca_keywords, top_n=10)

# 키워드 공동 발생 분석
cooccurrence_counts = calculate_cooccurrence(loca_related_sentences, loca_keywords.keys())

# 지식 그래프 시각화
if cooccurrence_counts:
    print(f"number of co-occurrences: {len(cooccurrence_counts)}")
    visualize_cooccurrence_graph(cooccurrence_counts, loca_keywords)
else:
    print("No significant co-occurrences found.")
