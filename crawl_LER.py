import os
import time
import requests
from bs4 import BeautifulSoup

# 저장 폴더 생성
os.makedirs('./LER_PDFs', exist_ok=True)

# LER 검색 페이지 URL
url = "https://lersearch.inl.gov/LERSearchResults.aspx"

# 페이지 요청 및 HTML 파싱
response = requests.get(url)
if response.status_code != 200:
    print(f"페이지 로드 실패: {response.status_code}")
    exit()

soup = BeautifulSoup(response.content, 'html.parser')

# PDF 다운로드 함수 정의
def download_pdf(pdf_url, file_name):
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            pdf_path = f'./LER_PDFs/{file_name}.pdf'
            with open(pdf_path, 'wb') as f:
                f.write(response.content)

            if os.path.getsize(pdf_path) > 0:
                print(f"{file_name}.pdf 다운로드 완료")
            else:
                print(f"{file_name}.pdf 다운로드 실패 (파일 크기 0바이트)")
                os.remove(pdf_path)  # 잘못된 파일 삭제
        else:
            print(f"{file_name}.pdf 다운로드 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"{file_name}.pdf 다운로드 중 오류 발생: {e}")

# PDF 링크와 LER 번호 추출
rows = soup.find_all('tr')

for row in rows:
    cells = row.find_all('td')
    if len(cells) > 1:
        ler_number = cells[0].text.strip()  # LER 번호 추출
        pdf_element = cells[1].find('a', href=True, title='PDF')

        if pdf_element:
            pdf_url = pdf_element['href']
            if not pdf_url.startswith('http'):
                pdf_url = f"https://lersearch.inl.gov/{pdf_url}"  # 상대 경로 처리

            # PDF 다운로드 실행
            download_pdf(pdf_url, ler_number)

    # 서버 부하를 줄이기 위해 요청 사이에 딜레이 추가
    time.sleep(1)

print("모든 PDF 다운로드 완료")
