import os
import tkinter as tk
from tkinter import filedialog
from google import genai

client = genai.Client(api_key="AIzaSyBsXISq1dX85XwLbA9ZgRfKro9nIiak7VA")

def read_project_files(project_path): # 특정 확장자만 받는다든가의 변경 가능
    project_data = {}
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    project_data[file_path] = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return project_data

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

def select_project_folder():
    root = tk.Tk()
    root.withdraw()  # GUI 창 숨기기
    project_path = filedialog.askdirectory(title="프로젝트 폴더 선택")
    return project_path

if __name__ == "__main__":
    project_path = select_project_folder()
    if project_path:
        project_data = read_project_files(project_path)
        analysis = analyze_project(project_data)
        print("\n=== 프로젝트 분석 결과 ===\n")
        print(analysis)
    else:
        print("폴더를 선택하지 않았습니다.")