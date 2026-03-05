import streamlit as st
import google.generativeai as genai
import json

# APIキーをSecretsから取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが見つかりません。Secretsの設定を確認してください。")
else:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# セッション状態（AI抽出結果の保存用）
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
                    # モデル名をフルパス形式に変更して確実に呼び出す
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    prompt = f"""
                    以下のアラビア語テキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                    {{ "name": "姓名", "death_year": 数字のみ, "teachers": ["師匠1", "師匠2"], "family": ["親族1", "親族2"] }}
                    テキスト：{source_text}
                    """
                    response = model.generate_content(prompt)
                    
                    # JSON部分を抽出
                    raw_res = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.ai_data = json.loads(raw_res)
                    st.success("抽出成功！")
                except Exception as e:
                    st.error(f"解析エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

with col2:
    st.header("2. 構造化データ入力")
    d = st.session_state.ai_data
    
    # AIの結果をフォームの初期値に設定
    name = st.text_input("フルネーム (Name)", value=d.get("name", ""))
    death = st.number_input("没年 (Death Year - Hijri)", value=int(d.get("death_year", 850)))
    
    st.subheader("🎓 抽出されたリスト")
    st.write("**師匠候補:**")
    st.info(", ".join(d.get("teachers", [])) if d.get("teachers") else "なし")
    
    st.write("**家族候補:**")
    st.info(", ".join(d.get("family", [])) if d.get("family") else "なし")
    
    st.divider()
    st.caption("※AIの抽出は100%ではありません。必要に応じて手動で修正してください。")
