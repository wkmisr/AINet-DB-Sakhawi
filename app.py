import streamlit as st
import google.generativeai as genai
import json

# APIキーの設定
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("APIキーが設定されていません。Secretsを確認してください。")

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# セッション状態の初期化
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {"name": "", "death_year": 850, "category": [], "teachers": [], "family": []}

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. 原文テキスト")
    source_text = st.text_area("サハウィーのテキストを貼り付け", height=400)
    
    if st.button("✨ AIで項目を自動抽出する"):
        if source_text:
            with st.spinner("AIが解析中..."):
                model = genai.GenerativeModel('gemini-1.5-pro')
                prompt = f"""
                以下のテキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                {{ "name": "姓名", "death_year": 数字, "category": ["属性1"], "teachers": ["師匠1"], "family": ["親族1"] }}
                テキスト：{source_text}
                """
                response = model.generate_content(prompt)
                # JSON部分を抽出してパース（簡易版）
                try:
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.ai_data = json.loads(res_text)
                    st.success("抽出成功！")
                except:
                    st.error("AIの応答を解析できませんでした。")

with col2:
    st.header("2. 構造化データ入力")
    d = st.session_state.ai_data
    
    # AIの抽出結果をデフォルト値としてフォームを表示
    name = st.text_input("フルネーム", value=d.get("name", ""))
    death = st.number_input("没年 (Hijri)", value=int(d.get("death_year", 850)))
    
    st.subheader("🎓 抽出された師弟・家族")
    st.write(f"師匠候補: {', '.join(d.get('teachers', []))}")
    st.write(f"家族候補: {', '.join(d.get('family', []))}")
    
    st.divider()
    if st.button("🚀 GitHubへ保存 (XML生成)", type="primary"):
        st.info("次のステップで、この内容をXML化してGitHubへ送る機能を実装します！")
