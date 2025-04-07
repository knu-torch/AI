import os
import tkinter as tk
import zipfile
from tkinter import filedialog
from google import genai

client = genai.Client(api_key="AIzaSyCpFzXsjw_NP_sSEGpKpsxmVlgVk33KNW4")

def read_project_files(zip_path): # 특정 확장자만 받는다든가의 변경 가능
    extracted_code = {}
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            if not file_name.endswith('/'):
                with zip_ref.open(file_name) as file:
                    try:
                        extracted_code[file_name] = file.read()
                    except Exception as e:
                        print(f"파일 읽기 오류 ({file_name}): {e}")
    print(extracted_code)
    return extracted_code

def analyze_project(project_data): # 프롬프트 생각하기 체크박스같은 입력에 따라 프롬프트 변경해야됨
    prompt = """
    다음 프로젝트의 내용을 분석해 주세요:
    {project_data}

    프로젝트의 개요, 주요 기능, 아키텍처, 핵심 코드 및 개선점을 정리해 주세요.
    """.format(project_data=str(project_data)[:50000])  # Gemini 입력 제한 고려

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def select_zip_file():
    root = tk.Tk()
    root.withdraw()  # GUI 창 숨기기
    zip_file_path = filedialog.askopenfilename(
        title="ZIP 파일 선택",
        filetypes=[("ZIP Files", "*.zip")]  # ZIP 파일만 선택할 수 있도록 필터 설정
    )
    return zip_file_path

if __name__ == "__main__":
    project_path = select_zip_file()
    if project_path:
        project_data = read_project_files(project_path)
        analysis = analyze_project(project_data)
        print("\n=== 프로젝트 분석 결과 ===\n")
        print(analysis)
    else:
        print("폴더를 선택하지 않았습니다.")