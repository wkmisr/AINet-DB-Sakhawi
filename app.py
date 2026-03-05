import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。Secretsを確認してください。")
else:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. データの初期化
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {"name": "", "death_year": 850, "teachers": [], "family": []}

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. 原文テキスト")
    source_text = st.text_area("サハウィーのテキストを貼り付け", height=400)
    
    if st.button("✨ AIで項目を自動抽出する"):
        if source_text:
            with st.spinner("AIが解析中..."):
                try:
                    # 【ここが最大の修正ポイント】
                    # 名前を 'gemini-1.5-flash-latest' にすることで、古いAPIバージョンへの誤誘導を防ぎます
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    
                    prompt = f"""
                    以下のアラビア語テキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。余計な説明は一切不要です。
                    {{ "name": "姓名", "death_year": 数字のみ, "teachers": ["師匠1", "師匠2"], "family": ["親族1", "親族2"] }}
                    テキスト：{source_text}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # 応答からJSONを抽出
                    res_text = response.text.strip()
                    if "```json" in res_text:
                        res_text = res_text.split("```json")[1].split("```")[0]
                    elif "```" in res_text:
                        res_text = res_text.split("```")[1].split("```")[0]
                    
                    st.session_state.ai_data = json.loads(res_text)
                    st.success("抽出に成功しました！")
                except Exception as e:
                    # エラーの詳細を画面に出す
                    st.error(f"解析エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

with col2:
    st.header("2. 構造化データ入力")
    d = st.session_state.ai_data
    
    name = st.text_input("フルネーム", value=d.get("name", ""))
    
    try:
        val = int(d.get("death_year", 850))
    except:
        val = 850
    death = st.number_input("没年 (Hijri)", value=val)
    
    st.subheader("🎓 抽出されたリスト")
    st.write("**師匠候補:**")
    st.info(", ".join(d.get("teachers", [])) if d.get("teachers") else "なし")
    
    st.write("**家族候補:**")
    st.info(", ".join(d.get("family", [])) if d.get("family") else "なし")
    
    st.divider()
    st.caption("AI抽出後、手動で修正してください。")
