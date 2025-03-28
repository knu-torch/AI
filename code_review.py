import streamlit as st
import os
import zipfile
from google.generativeai import configure, GenerativeModel

st.set_page_config(page_title="코드 요약 어시스턴트")

os.environ["GEMINI_API_KEY"] = "AIzaSyAlX1D_kIgCvoXXU72JgltquG8zWX2xu7Y"
configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = GenerativeModel("gemini-2.0-flash")

def extract_code_from_zip(zip_path):
    """ZIP 파일에서 모든 확장자의 코드 파일을 추출"""
    extracted_code = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            with zip_ref.open(file_name) as file:
                extracted_code.append(f"### {file_name}\n" + file.read().decode("utf-8", errors="ignore"))
    return "\n\n".join(extracted_code)

def summarize_code(code_text, user_prompt):
    """Gemini AI 모델을 이용하여 코드 요약을 생성"""
    prompt = f"{user_prompt}\n\n{code_text}"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

st.title("코드 요약 어시스턴트")
st.caption("ZIP 파일을 업로드하면 내부의 코드 파일을 분석하여 요약합니다.")

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=["zip"])

if uploaded_file is not None:
    zip_path = "uploaded_code.zip"
    with open(zip_path, "wb") as temp_zip:
        temp_zip.write(uploaded_file.read())

    extracted_code = extract_code_from_zip(zip_path)

    if not extracted_code:
        st.error("ZIP 파일 내에 코드 파일이 없습니다.")
    else:
        st.success("코드 파일을 성공적으로 추출했습니다.")

        with st.expander("📂 업로드된 코드 파일 보기"):
            st.code(extracted_code, language="plaintext")

        default_prompt = "이 코드의 기능을 요약해주세요."
        user_prompt = st.text_area("원하는 요약 방식을 입력하세요:", default_prompt, max_chars=50000)
        prompt_length = len(user_prompt) + len(extracted_code)
        remaining_chars = max(0, 50000 - prompt_length)

        if st.button("📌 코드 요약 생성"):
            with st.spinner("코드를 요약하는 중..."):
                summary = summarize_code(extracted_code, user_prompt)
                
                st.subheader("📜 코드 요약 결과")
                st.write(summary)
