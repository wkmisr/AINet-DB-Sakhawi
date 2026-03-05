import streamlit as st
import google.generativeai as genai
import json

# APIキーをSecretsから直接取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが見つかりません。StreamlitのSecretsに 'GEMINI_API_KEY' が設定されているか確認してください。")
else:
    genai.configure(api_key=api_key)

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
                try:
                    # モデル名を flash に変更（より速く、エラーが出にくいです）
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    以下のテキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                    {{ "name": "姓名", "death_year": 数字, "category": ["属性1"], "teachers": ["師匠1"], "family": ["親族1"] }}
                    テキスト：{source_text}
                    """
                    response = model.generate_content(prompt)
                    
                    # AIの応答から余計な文字を削除
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.ai_data = json.loads(res_text)
                    st.success("抽出成功！")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("テキストを入力してください。")

with col2:
    st.header("2. 構造化データ入力")
    d = st.session_state.ai_data
    
    name = st.text_input("フルネーム", value=d.get("name", ""))
    death = st.number_input("没年 (Hijri)", value=int(d.get("death_year", 850)))
    
    st.subheader("🎓 抽出された師弟・家族")
    st.write(f"師匠候補: {', '.join(d.get('teachers', []))}")
    st.write(f"家族候補: {', '.join(d.get('family', []))}")
    
    st.divider()
    st.info("AIがうまく動かない場合は、APIキーが正しくSecretsに保存されているか再確認してください。")
