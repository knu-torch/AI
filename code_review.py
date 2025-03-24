import streamlit as st
import os
import zipfile
import threading
from concurrent.futures import ThreadPoolExecutor
from google.generativeai import configure, GenerativeModel

# ✅ set_page_config()를 가장 위에 배치
st.set_page_config(page_title="코드 요약 어시스턴트")

# Gemini API 키 설정 (보안상 환경 변수 사용 권장)
os.environ["GEMINI_API_KEY"] = "AIzaSyAlX1D_kIgCvoXXU72JgltquG8zWX2xu7Y"
configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = GenerativeModel("gemini-1.5-flash")

def extract_code_from_zip(zip_path, allowed_extensions):
    """ZIP 파일에서 특정 확장자의 코드 파일을 추출"""
    extracted_code = {}
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            if any(file_name.endswith(f".{ext}") for ext in allowed_extensions):
                with zip_ref.open(file_name) as file:
                    extracted_code[file_name] = file.read().decode("utf-8", errors="ignore")
    return extracted_code

def summarize_code(code_text, user_prompt):
    """Gemini AI 모델을 이용하여 코드 요약을 생성"""
    prompt = f"{user_prompt}\n\n{code_text}"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

def summarize_code_threaded(extracted_code, user_prompt):
    """멀티스레딩을 활용하여 코드 요약을 병렬 처리"""
    summaries = {}
    def process_file(file_name, content):
        summaries[file_name] = summarize_code(content, user_prompt)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, file_name, content): file_name for file_name, content in extracted_code.items()}
        for future in futures:
            future.result()
    return summaries

st.title("코드 요약 어시스턴트")
st.caption("ZIP 파일을 업로드하면 내부의 코드 파일을 분석하여 요약합니다.")

# ✅ 사용자 입력을 통한 확장자 지정
default_extensions = "py, js, java, cpp, go"
user_extensions = st.text_input("추출할 코드 파일 확장자를 입력하세요 (쉼표로 구분):", default_extensions)
allowed_extensions = [ext.strip() for ext in user_extensions.split(",") if ext.strip()]

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=["zip"])

if uploaded_file is not None:
    zip_path = "uploaded_code.zip"
    with open(zip_path, "wb") as temp_zip:
        temp_zip.write(uploaded_file.read())

    extracted_code = extract_code_from_zip(zip_path, allowed_extensions)

    if not extracted_code:
        st.error("ZIP 파일 내에 지원하는 코드 파일이 없습니다.")
    else:
        st.success(f"총 {len(extracted_code)}개의 코드 파일을 확인했습니다.")

        with st.expander("📂 업로드된 코드 파일 보기"):
            for file_name, content in extracted_code.items():
                st.subheader(f"📄 {file_name}")
                st.code(content, language=file_name.split(".")[-1])

        user_prompt = st.text_area(
            "원하는 요약 방식을 입력하세요:",
            "이 코드의 기능을 요약해주세요."
        )

        if st.button("📌 코드 요약 생성"):
            with st.spinner("코드를 요약하는 중..."):
                summaries = summarize_code_threaded(extracted_code, user_prompt)
                full_summary = "\n".join(f"### {file} 요약:\n{summary}\n" for file, summary in summaries.items())
                
                st.subheader("📜 코드 요약 결과")
                st.write(full_summary)
