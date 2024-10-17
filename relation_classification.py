import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# 데이터 불러오기
data = pd.read_csv('./combined_LER_reports.csv')

# Cause와 Incident 라벨을 리스트 형태로 변환
data['Cause Labels'] = data['Cause Labels'].apply(eval)
data['Incident Labels'] = data['Incident Labels'].apply(eval)

# 그래프 생성 (Cause가 'Unclassified'인 경우 제외)
G = nx.DiGraph()

for _, row in data.iterrows():
    causes = [cause for cause in row['Cause Labels'] if cause != 'Unclassified']
    incidents = row['Incident Labels']  # Incident의 'Unclassified'는 남겨둠

    # 원인과 사건이 동시에 나타나는 경우에만 엣지 추가
    if causes and incidents:
        for cause in causes:
            for incident in incidents:
                if not G.has_edge(cause, incident):
                    G.add_edge(cause, incident, cases=[], abstracts=[])
                G[cause][incident]['cases'].append(row['LER Number'])
                G[cause][incident]['abstracts'].append(row['Title/Abstract'])

# 노드 색상 설정 (원인은 파스텔 블루, 사건은 파스텔 핑크)
node_colors = []
for node in G.nodes:
    if any(node in causes for causes in data['Cause Labels'] if node != 'Unclassified'):
        node_colors.append('#A7C7E7')  # 파스텔 블루 (원인)
    else:
        node_colors.append('#F4A7B9')  # 파스텔 핑크 (사건)

# 노드 위치 설정
pos = nx.spring_layout(G, seed=42)

# 엣지 추출 및 화살표 설정
annotations = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]

    annotations.append(
        dict(
            ax=x0, ay=y0, axref='x', ayref='y',
            x=x1, y=y1, xref='x', yref='y',
            showarrow=True,
            arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor='gray'
        )
    )

# 노드 위치 및 툴팁 생성
node_x, node_y, node_text = [], [], []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

    # 노드와 관련된 사건 수와 정보 추출
    connected_cases = []
    connected_abstracts = []

    # 노드가 원인인 경우
    if node in G:
        for neighbor in G[node]:
            connected_cases.extend(G[node][neighbor]['cases'])
            connected_abstracts.extend(G[node][neighbor]['abstracts'])

    # 노드가 사건인 경우 (역방향 탐색)
    if node in nx.reverse(G):
        for neighbor in nx.reverse(G)[node]:
            connected_cases.extend(G[neighbor][node]['cases'])
            connected_abstracts.extend(G[neighbor][node]['abstracts'])

    # 상위 5개 사건만 표시
    k = 5
    connected_cases_k = connected_cases[:k]
    connected_abstracts_k = connected_abstracts[:k]

    # 툴팁 텍스트 생성
    text = f"<b>{node}</b><br>Number of Cases: {len(connected_cases)}<br>"
    for i, (case, abstract) in enumerate(zip(connected_cases_k, connected_abstracts_k)):
        text += f"LER: {int(case)}<br>Abstract: {abstract}<br>"

    node_text.append(text)

# 노드 그래프 생성 (드래그 가능하게 설정)
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    textposition='top center',
    marker=dict(
        size=15,
        color=node_colors,
        line=dict(width=2, color='black')
    ),
    text=list(G.nodes),
    hovertext=node_text,
    hoverinfo='text'
)

# 레이아웃 설정 및 그래프 생성
fig = go.Figure(
    data=[node_trace],
    layout=go.Layout(
        title='Interactive Cause and Incident Network',
        titlefont=dict(size=16),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        annotations=annotations,
        dragmode='pan'  # 드래그 모드 활성화
    )
)

# 그래프 출력
fig.show()
