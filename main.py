# Filename: simple_qa_streamlit.py

import os
import datetime
from dotenv import load_dotenv
import openai
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

def init_environment():
    load_dotenv(override=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai.api_key

def init_llm(openai_key):
    return ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_key)

def save_output(question, answer, output_path="./output"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_path, f"qa_result_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("[Question]\n" + question + "\n\n")
        f.write("[Answer]\n" + answer + "\n")
    return filename

def main():
    st.set_page_config(page_title="🤖 法規問答系統", layout="wide")
    st.title("🤖 法規知識簡易問答系統")
    st.markdown("請輸入與車輛法規相關的問題，系統會使用 GPT 回答。")

    openai_key = init_environment()
    llm = init_llm(openai_key)

    query = st.text_area("請輸入您的問題（繁體中文）:", "酒後開車罰多少錢？", height=100)

    if st.button("🚀 查詢"):
        with st.spinner("正在查詢中..."):
            response = llm.invoke([HumanMessage(content=query)])
            st.success("✅ 回答完成！")
            st.subheader("🔹 回答內容")
            st.write(response.content)

            filename = save_output(query, response.content)
            st.download_button("💾 下載結果檔案", data=open(filename, "r", encoding="utf-8").read(), file_name=os.path.basename(filename))

if __name__ == "__main__":
    main()
