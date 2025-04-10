import os
import tkinter as tk
import zipfile
from tkinter import filedialog
from google import genai
from little_project.model.enums import summary_options

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
    return extracted_code

def generate_prompt(options: list[summary_options.SummaryOption], code_text: str):
    prompt = []

    if summary_options.SummaryOption.Project in options:
        prompt.append(
            "이 프로젝트의 핵심 기능과 목적을 한 줄로 요약해줘"
            "사용된 라이브러리 종류와 버전 정보를 알려줘."
            "주요 라이브러리와 역할을 포함해줘. (예: 웹 프레임워크, 데이터베이스, 머신러닝 등)"
            "디펜던시 트리에서 Depth 2까지 포함해줘."
            "배포 관련 정보를 분석하여 정리해줘."
            "git action, 서비스 파일, Dockerfile 등의 자동화 빌드 및 배포 정보 포함"
            "설정 파일(config, env 파일) 샘플 및 형식 제공"
            "한국어로 작성해줘."
            "## title, ## libs, ## deploy_info, ## another 영역으로 순서대로 나눠서 작성해줘."
            "무조건 ## title로 시작하고 그 앞에는 아무 내용도 나오지 않게 출력해줘"
            "libs 섹션에서 각 라이브러리의 역할을 설명하는 테이블 형식으로 제공해줘."
        )

    if summary_options.SummaryOption.Package in options:
        prompt.append(
            "1 프로젝트의 각 패키지 역할을 분석하여 최대 2줄로 요약해줘."
            "1-1 각 패키지가 담당하는 기능을 명확하게 작성해줘." 
            "2 프로젝트 내부에서 사용되는 패키지들의 의존성을 정리해줘."
            "2-1 외부 라이브러리는 제외하고, 내부 패키지 간의 관계만 다뤄줘." 
            "2-2 의존성을 트리 구조 또는 표 형태로 표현해줘."
            "3 한국어로 작성해줘."
            "4 마크다운 형식으로 작성해줘."
            "5 ## title, ## libs, ## deploy_info, ## another 영역으로 순서대로 나눠서 작성해줘."
        )
    prompt.extend(code_text)
    return prompt

def analyze_project(project_data): # 프롬프트 생각하기 체크박스같은 입력에 따라 프롬프트 변경해야됨
    prompt = """
    다음 프로젝트의 내용을 분석해 주세요:
    {project_data}
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

def parse_markdown_sections(text: str) -> dict:
    sections = {"title": "", "libs": "", "deploy_info": "", "another": ""}
    current_section = "Nope"
    buffer = []
    print(text)
    for line in text.splitlines():
        if "## title" in line.lower():
            current_section = "title"
        elif "## libs" in line.lower():
            sections[current_section] = "\n".join(buffer).strip()
            buffer = []
            current_section = "libs"
        elif "## deploy_info" in line.lower():
            sections[current_section] = "\n".join(buffer).strip()
            buffer = []
            current_section = "deploy_info"
        elif '## another' in line.lower():
            sections[current_section] = "\n".join(buffer).strip()
            buffer = []
            current_section = "another"
        elif current_section == "Nope":
            continue
        else:
            buffer.append(line)

    sections[current_section] = "\n".join(buffer).strip()
    print(sections)
    return {
        "title": sections["title"],
        "libs": sections["libs"],
        "deploy_info": sections["deploy_info"],
        "another": sections["another"]
    }

if __name__ == "__main__":
    project_path = select_zip_file()
    if project_path:
        project_data = read_project_files(project_path)
        generated_prompt = generate_prompt([summary_options.SummaryOption.Project], project_data)
        analysis = analyze_project(generated_prompt)
        parsed = parse_markdown_sections(analysis)
        print("\n=== 프로젝트 분석 결과 ===\n")
    else:
        print("폴더를 선택하지 않았습니다.")