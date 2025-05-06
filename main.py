# Filename: simple_qa_streamlit.py

import os
import datetime
import random
from dotenv import load_dotenv
import openai
import streamlit as st
import time
import pandas as pd
import altair as alt
from streamlit_lottie import st_lottie
import requests
import json

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# 設置頁面狀態管理
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "問答系統"

# Lottie動畫加載函數
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def init_environment():
    load_dotenv(override=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai.api_key

def init_llm(openai_key, model_name="gpt-3.5-turbo", temperature=0.7):
    return ChatOpenAI(model_name=model_name, openai_api_key=openai_key, temperature=temperature)

def save_output(question, answer, output_path="./output"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_path, f"qa_result_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("[Question]\n" + question + "\n\n")
        f.write("[Answer]\n" + answer + "\n")
    return filename

def rate_answer(score):
    st.session_state.last_rating = score
    st.toast(f"謝謝您的評分：{score} 星！", icon="🌟")

def main():
    # 設置頁面配置和主題
    st.set_page_config(
        page_title="🤖 法規問答系統",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/your-repo',
            'Report a bug': "https://github.com/yourusername/your-repo/issues",
            'About': "# 法規知識問答系統 v1.0\n 這是一個基於 GPT 的法規問答助手"
        }
    )

    # 設置頁面主題
    
    st.markdown("""
<style>
/* 字體大小與顏色 */
.big-font {
    font-size: 28px !important;
    font-weight: bold;
    color: #000000;
}
.medium-font {
    font-size: 22px !important;
    font-weight: bold;
    color: #000000;
}

/* 按鈕樣式：大地色 + 白字 */
.stButton>button {
    background-color: #A47551;
    color: white;
    border-radius: 10px;
    border: none;
}
.stButton>button:hover {
    background-color: #8B5E3C;
    color: white;
}

/* 卡片樣式 */
.card {
    background-color: #F8F1EB;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
    color: #000000;
}

/* Tabs 樣式 */
div.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #D6C2B0;
    border-radius: 5px 5px 0 0;
}
div.stTabs [data-baseweb="tab"] {
    background-color: #EFE5DC;
    color: #000000;
    border-radius: 5px 5px 0px 0px;
    padding: 10px 20px;
    font-size: 18px;
}
div.stTabs [aria-selected="true"] {
    background-color: #A47551;
    color: white;
}

/* 背景色與文字顏色 */
body, .main {
    background-color: #F8F1EB;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)


    # 加載動畫
    robot_animation = load_lottieurl("https://lottie.host/94d35de1-af0e-46b4-8bc7-23860f97f363/0HBYeoiSU9.json")

    # 側邊欄設置
    with st.sidebar:
        if robot_animation:
            st_lottie(robot_animation, height=200, key="robot")
        else:
            st.image("https://www.svgrepo.com/show/306500/openai.svg", width=100)
        
        st.title("系統設置")
        model = st.selectbox(
            "選擇模型",
            ["gpt-3.5-turbo", "gpt-4"],
            index=0,
            key="model_selection"
        )
        
        st.divider()
        
        st.markdown("### 📊 使用統計")
        st.metric(label="總查詢次數", value=st.session_state.total_queries, delta=f"↑{len(st.session_state.query_history)}" if len(st.session_state.query_history) > 0 else None)
        
        # 添加一個簡單的圖表來顯示使用情況
        if len(st.session_state.query_history) > 0:
            # 創建虛擬數據用於演示
            dates = [datetime.datetime.now() - datetime.timedelta(days=x) for x in range(7)]
            dates.reverse()
            counts = [random.randint(3, 10) for _ in range(7)]
            counts[-1] = len(st.session_state.query_history)  # 今天的實際查詢次數
            
            df = pd.DataFrame({
                '日期': [d.strftime('%m/%d') for d in dates],
                '查詢次數': counts
            })
            
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('日期', sort=None),
                y='查詢次數',
                color=alt.condition(
                    alt.datum.日期 == df['日期'].iloc[-1],
                    alt.value('#4CAF50'),
                    alt.value('#A9A9A9')
                )
            ).properties(height=200)
            
            st.altair_chart(chart, use_container_width=True)
        
        st.divider()
        st.markdown("### 🔄 系統操作")
        if st.button("清空歷史記錄", use_container_width=True):
            st.session_state.query_history = []
            st.experimental_rerun()

    # 頁面標籤
    tabs = st.tabs(["📝 問答系統", "📚 歷史紀錄", "ℹ️ 使用說明"])
    
    with tabs[0]:
        st.markdown('<p class="big-font" style="color: white;">🤖 法規知識簡易問答系統</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
            <h4 style="color: black;">💡 使用說明</h4>
            <p style="color: black;">請輸入與車輛法規相關的問題，系統會使用 AI 為您解答。</p>
        </div>
        """, unsafe_allow_html=True)

        openai_key = init_environment()
        
        # 主要問答區塊
        st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)  # 增加上方間距
        query = st.text_area(
            "請輸入您的問題（繁體中文）:",
            placeholder="在此輸入您的問題...",
            height=150
        )
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)  # 增加下方間距

        # 查詢按鈕
        if st.button("🚀 開始查詢", use_container_width=True, key="search_btn"):
            if not query:
                st.error("❌ 請輸入問題內容！")
            else:
                # 增加查詢次數
                st.session_state.total_queries += 1
                
                # 添加進度條動畫
                progress_text = "正在思考中..."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)

                with st.spinner("🤔 正在整理回答..."):
                    # 實際使用模型和溫度參數
                    llm = init_llm(
                        openai_key, 
                        model_name=st.session_state.model_selection
                    )
                    response = llm.invoke([HumanMessage(content=query)])
                    
                # 清除進度條
                my_bar.empty()

                # 保存至歷史紀錄
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.query_history.append({
                    "timestamp": timestamp,
                    "query": query,
                    "response": response.content,
                    "model": st.session_state.model_selection
                })

                # 顯示回答結果
                st.success("✅ 回答完成！")
                
                # 使用卡片式設計顯示結果
                st.markdown("""
                <div class="card">
                    <h3 style='color: #1f77b4;'>🔹 問題</h3>
                    <p style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>{}</p>
                    <h3 style='color: #1f77b4; margin-top: 20px;'>🔸 回答</h3>
                    <p style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>{}</p>
                </div>
                """.format(query, response.content), unsafe_allow_html=True)

                # 評分系統
                st.markdown("### 📊 您對這個回答的評分")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.button("⭐", on_click=rate_answer, args=(1,), key="star1")
                with col2:
                    st.button("⭐⭐", on_click=rate_answer, args=(2,), key="star2")
                with col3:
                    st.button("⭐⭐⭐", on_click=rate_answer, args=(3,), key="star3")
                with col4:
                    st.button("⭐⭐⭐⭐", on_click=rate_answer, args=(4,), key="star4")
                with col5:
                    st.button("⭐⭐⭐⭐⭐", on_click=rate_answer, args=(5,), key="star5")
                
                # 儲存並提供下載
                filename = save_output(query, response.content)
                with st.expander("💾 下載結果"):
                    st.download_button(
                        "📥 下載完整回答內容",
                        data=open(filename, "r", encoding="utf-8").read(),
                        file_name=os.path.basename(filename),
                        mime="text/plain",
                        use_container_width=True
                    )
    
    # 歷史紀錄頁面
    with tabs[1]:
        st.markdown('<p class="big-font" style="color: white;">📚 歷史查詢紀錄</p>', unsafe_allow_html=True)
        
        if not st.session_state.query_history:
            st.info("目前尚無查詢記錄，請在問答系統中提出問題。")
        else:
            for i, item in enumerate(reversed(st.session_state.query_history)):
                with st.expander(f"**{item['timestamp']}** - {item['query'][:30]}...", expanded=(i==0)):
                    st.markdown(f"""
                    <div class='card'>
                        <p><strong>時間：</strong> {item['timestamp']}</p>
                        <p><strong>使用模型：</strong> {item['model']}</p>
                        <p><strong>問題：</strong></p>
                        <p style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>{item['query']}</p>
                        <p><strong>回答：</strong></p>
                        <p style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>{item['response']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # 使用說明頁面
    with tabs[2]:
        st.markdown('<p class="big-font" style="color: white;">ℹ️ 使用說明</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class='card'>
                <h3>🔍 如何使用</h3>
                <ol>
                    <li>在輸入框中輸入您的問題</li>
                    <li>點擊「開始查詢」按鈕</li>
                    <li>系統會使用AI處理您的問題並給出回答</li>
                    <li>您可以下載回答或提供評分</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='card'>
                <h3>⚙️ 系統功能</h3>
                <ul>
                    <li>法規知識查詢：提供交通法規相關資訊</li>
                    <li>模型選擇：可選擇不同的AI模型</li>
                    <li>歷史記錄：查看過去的問答歷史</li>
                    <li>評分系統：對回答提供評分反饋</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card'>
            <h3>📋 問題範例</h3>
            <table>
                <tr>
                    <th>問題類型</th>
                    <th>範例問題</th>
                </tr>
                <tr>
                    <td>交通違規</td>
                    <td>酒後開車會受到什麼處罰？超速會被罰多少錢？闖紅燈的處罰規定是什麼？</td>
                </tr>
                <tr>
                    <td>駕照相關</td>
                    <td>考駕照需要哪些條件？駕照被吊銷後如何恢復？駕照扣分制度如何運作？</td>
                </tr>
                <tr>
                    <td>車輛管理</td>
                    <td>車輛年檢的規定是什麼？車輛報廢的標準是什麼？如何辦理車輛過戶？</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # 頁尾資訊
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>© 2024 法規知識問答系統 | 使用 OpenAI GPT 技術提供服務</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
