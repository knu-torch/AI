import os
import tkinter as tk
import zipfile
from tkinter import filedialog
from google import genai
from little_project.model.enums import summary_options
from pydantic import BaseModel
import json

client = genai.Client(api_key="AIzaSyCpFzXsjw_NP_sSEGpKpsxmVlgVk33KNW4")

#프로젝트 파일 받아서 그안의 모든 파일들을 재귀적으로 읽고 그 내용을 전부 파일이름 : 파일 내용 문자열 이렇게 해서 딕셔너리에 넣고 리턴
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

#옵션에 맞는 프롬프트를 선택해서 리턴(지금은 project 옵션밖에 안됨!!)
def generate_prompt(options: list[summary_options.SummaryOption], code_text: str):
    prompt = []

    if summary_options.SummaryOption.Project in options:
        prompt.append(
            "이 schema를 따라줘 : {'title': str, 'libs': str, 'deploy_info': str, 'another': str}"
            "이 json 요소들의 내용들은 다음과 같아"
            "title: 이 프로젝트의 핵심 기능과 목적을 한 줄로 요약해줘"
            "libs: 사용된 라이브러리 종류와 버전 정보를 알려주고 주요 라이브러리와 역할을 포함해줘. (예: 웹 프레임워크, 데이터베이스, 머신러닝 등) 그리고 디펜던시 트리에서 Depth 2까지 포함해줘."
            "deploy_info: 배포 관련 정보를 분석하여 정리해줘, git action, 서비스 파일, Dockerfile 등의 자동화 빌드 및 배포 정보 포함 되어야 하고 설정 파일(config, env 파일) 샘플 및 형식 제공해줘"
            "another: 앞에서 들어가지 않은 내용들을 넣어줘"
            "title은 한 줄로 쓰고 나머지는 길게 설명해줘"
            "한국어로 작성해줘."
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

#임시 json 형태
class recipe(BaseModel):
    title: str
    libs: str
    deploy_info: str
    another: str

#generate_prompt 함수에서 만든 프롬프트와 read_project_files에서 만든 딕셔너리를 합쳐서 llm에 넣음, return 값은 recipe class에 있는 형태의 딕셔너리의 문자열로 나오게 된다
def analyze_project(project_data):
    prompt = """
    다음 프로젝트의 내용을 분석해 주세요:
    {project_data}
    """.format(project_data=str(project_data)[:50000])  # Gemini 입력 제한 고려

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config= {
            'response_mime_type': 'application/json',
            'response_schema': recipe,
        },
    )
    return response.text

# llm 결과로 나온 딕셔너리 형태의 문자열을 딕셔너리로 파싱
def parse_text(data):
    parsed_dict = json.loads(data)
    return parsed_dict

#zip파일만 선택하게 하는 함수
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
        generated_prompt = generate_prompt([summary_options.SummaryOption.Project], project_data)
        analysis = analyze_project(generated_prompt)
        parsed_text = parse_text(analysis)
        print("\n=== 프로젝트 분석 결과 ===\n")
        print(parsed_text['title'])
        print(parsed_text['libs'])
        print(parsed_text['deploy_info'])
        print(parsed_text['another'])
    else:
        print("폴더를 선택하지 않았습니다.")