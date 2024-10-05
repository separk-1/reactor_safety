import os
import fitz  # PyMuPDF
import spacy
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        text += doc[page_num].get_text()
    return text

# 문장에서 주어와 목적어 추출
def extract_subjects_objects(sentences, nlp):
    subjects_objects = []
    for sentence in sentences:
        doc = nlp(sentence)
        for token in doc:
            if token.dep_ == 'nsubj':  # 주어(nsubj)
                subjects_objects.append(token.text)
            elif token.dep_ == 'dobj':  # 목적어(dobj)
                subjects_objects.append(token.text)
    return subjects_objects

# 문장 단위로 텍스트 나누기
def split_text_into_sentences(text, nlp):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

# 불용어 제거
def remove_stopwords(words, nlp):
    filtered_words = []
    for word in words:
        if not nlp.vocab[word].is_stop:  # spaCy의 기본 불용어 필터
            filtered_words.append(word)
    return filtered_words

# 워드클라우드 생성
def generate_wordcloud(word_freq):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# Main script
nlp = spacy.load("en_core_web_sm")  # spaCy 언어 모델 로드

folder_path = './data/'  # PDF 파일들이 있는 폴더 경로
pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.pdf')]

all_text = ""
# 모든 PDF 파일에서 텍스트 추출 및 결합
for pdf_file in pdf_files:
    all_text += extract_text_from_pdf(pdf_file)

# 텍스트를 문장 단위로 나누기
sentences = split_text_into_sentences(all_text, nlp)

# 문장에서 주어와 목적어 추출
subjects_objects = extract_subjects_objects(sentences, nlp)

# 불용어 제거
filtered_subjects_objects = remove_stopwords(subjects_objects, nlp)

# 주어와 목적어의 빈도를 계산
word_freq = Counter(filtered_subjects_objects)

# 워드클라우드 시각화
generate_wordcloud(word_freq)
