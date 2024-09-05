import os
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

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

# TF-IDF 분석
def perform_tfidf_analysis(documents):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    dense = tfidf_matrix.todense()
    scores = dense.sum(axis=0).tolist()[0]  # 모든 문서의 단어 중요도를 합산
    return feature_names, scores

# 숫자나 불필요한 기호 제거
def remove_numerical_and_symbols(feature_names):
    return [re.sub(r'\d+', '', word) for word in feature_names if not re.search(r'\d+', word)]

# 워드클라우드 생성
def generate_wordcloud_from_tfidf(feature_names, scores):
    word_freq = dict(zip(feature_names, scores))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# Main script
folder_path = './data/'  # PDF 파일들이 있는 폴더 경로
documents = extract_all_text_from_pdfs(folder_path)

# TF-IDF 분석 수행
feature_names, scores = perform_tfidf_analysis(documents)

# 숫자나 기호가 포함된 단어 제거
cleaned_feature_names = remove_numerical_and_symbols(feature_names)

# 워드클라우드 시각화
generate_wordcloud_from_tfidf(cleaned_feature_names, scores)
