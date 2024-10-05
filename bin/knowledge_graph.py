import os
import fitz  # PyMuPDF
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer

# PDF에서 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        text += doc[page_num].get_text()
    return text

# 폴더에서 모든 PDF 파일의 텍스트를 추출하는 함수
def extract_all_text_from_pdfs(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            all_text += extract_text_from_pdf(pdf_path)
    return all_text

# TF-IDF로 중요한 개념 필터링 함수
def filter_concepts_by_tfidf(text, top_n=5):  # 상위 5개 개념 필터링
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]

    # TF-IDF 점수가 높은 상위 top_n 개념만 선택
    top_indices = tfidf_scores.argsort()[-top_n:][::-1]
    top_concepts = [feature_names[i] for i in top_indices]
    
    return top_concepts

# 개념과 관계 추출 함수 (spacy 사용)
def extract_concepts_and_relationships(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    concepts = []
    relationships = []

    # 명사구(개념) 추출
    for chunk in doc.noun_chunks:
        concepts.append(chunk.text)

    # 동사구(관계) 추출 (중요한 동사만 필터링)
    important_verbs = ['cause', 'result', 'lead', 'affect', 'trigger']  # 중요한 동사들
    for token in doc:
        if token.pos_ == "VERB" and token.text in important_verbs:
            subj = [child for child in token.children if child.dep_ == 'nsubj']
            obj = [child for child in token.children if child.dep_ == 'dobj']
            if subj and obj:
                relationships.append((subj[0].text, token.text, obj[0].text))

    return concepts, relationships

# 불필요한 개념을 제거하는 필터링 리스트 추가
def remove_unnecessary_concepts(concepts):
    stop_concepts = ['that', 'which', 'capability', 'review', 'affect']  # 필요 없는 개념 예시
    return [concept for concept in concepts if concept not in stop_concepts]

# 지식 그래프 시각화 함수 (단일 색상 적용)
def visualize_knowledge_graph(concepts, relationships):
    G = nx.DiGraph()

    # 개념 추가
    for concept in concepts:
        G.add_node(concept)

    # 관계 추가
    for subj, verb, obj in relationships:
        G.add_edge(subj, obj, label=verb)

    # 그래프 시각화 (모든 노드를 lightblue 색상으로 설정)
    pos = nx.spring_layout(G, k=2)  # 노드 간의 간격을 넓히기 위해 k 값 조정
    plt.figure(figsize=(10, 10))  # 그래프 크기 조정
    nx.draw(G, pos, with_labels=True, node_size=300, node_color="lightblue", font_size=6, font_weight="bold")  # 단일 색상 적용
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    plt.show()


# 메인 실행 함수
folder_path = './data/'  # PDF 파일들이 있는 폴더 경로
documents_text = extract_all_text_from_pdfs(folder_path)

# TF-IDF를 사용해 상위 5개 중요한 개념 필터링
filtered_concepts = filter_concepts_by_tfidf(documents_text, top_n=5)

# 개념과 관계 추출
concepts, relationships = extract_concepts_and_relationships(documents_text)

# 불필요한 개념 제거
concepts = remove_unnecessary_concepts(concepts)

# 필터링된 개념만 사용
concepts = [concept for concept in concepts if concept in filtered_concepts]

# 지식 그래프 시각화
visualize_knowledge_graph(concepts, relationships)
