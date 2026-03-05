import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定（Secretsから取得）
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが見つかりません。Secretsを確認してください。")
else:
    # APIの初期化
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. データの初期化（セッション状態）
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
                    # 【重要】モデル名の指定方法を最新の 'gemini-1.5-flash' に戻し、
                    # かつ安全な呼び出し方に変更しました
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    以下のテキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                    {{ "name": "姓名", "death_year": 数字のみ, "teachers": ["師匠1", "師匠2"], "family": ["親族1", "親族2"] }}
                    テキスト：{source_text}
                    """
                    # AIの応答を取得
                    response = model.generate_content(prompt)
                    
                    # 応答テキストのクリーニング
                    res_text = response.text.strip()
                    if "```json" in res_text:
                        res_text = res_text.split("```json")[1].split("```")[0]
                    elif "```" in res_text:
                        res_text = res_text.split("```")[1].split("```")[0]
                    
                    st.session_state.ai_data = json.loads(res_text)
                    st.success("抽出成功！")
                except Exception as e:
                    # エラーの詳細を表示
                    st.error(f"解析エラーが発生しました。設定を再確認してください: {e}")
        else:
            st.warning("テキストを入力してください。")

with col2:
    st.header("2. 構造化データ入力")
    d = st.session_state.ai_data
    
    # AIの結果を反映
    name = st.text_input("フルネーム", value=d.get("name", ""))
    
    # 没年の処理
    try:
        val = int(d.get("death_year", 850))
    except:
        val = 850
    death = st.number_input("没年 (Hijri)", value=val)
    
    st.subheader("🎓 抽出されたリスト")
    
    st.write("**師匠候補:**")
    t_list = d.get("teachers", [])
    st.info(", ".join(t_list) if t_list else "なし")
    
    st.write("**家族候補:**")
    f_list = d.get("family", [])
    st.info(", ".join(f_list) if f_list else "なし")
    
    st.divider()
    st.caption("AIによる抽出結果です。手動で内容を修正して、保存の準備をしてください。")
