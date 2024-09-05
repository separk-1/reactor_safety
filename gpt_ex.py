from openai import OpenAI


# OpenAI API 키 설정
api_key = "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" 

client = OpenAI(api_key=api_key)

client = OpenAI()

# GPT를 사용한 인과 관계 추출
def extract_causal_relations_with_gpt(sentence):
    response = client.chat.completions.create(# 정확한 메서드 이름 사용
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts cause, effect, and countermeasure from sentences."},
            {"role": "user", "content": f"Analyze the following sentence and identify the cause, effect, and countermeasure: {sentence}"}
        ],
        max_tokens=100,
        temperature=0.7)
    return response.choices[0].message.content.strip()

# 문서에서 인과 관계 추출
def extract_relations_from_documents(documents):
    causal_relations = []
    for sentence in documents:
        result = extract_causal_relations_with_gpt(sentence)
        causal_relations.append(result)
    return causal_relations

# 예시 문장
example_sentence = "The reactor coolant system pressure increased due to a leakage in the coolant line, causing a shutdown of the reactor and activation of emergency cooling measures."

# GPT로 인과 관계 추출
causal_relation = extract_causal_relations_with_gpt(example_sentence)
print(causal_relation)
