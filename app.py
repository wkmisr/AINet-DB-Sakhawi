import streamlit as st
import google.generativeai as genai
import json
import requests
import base64
from datetime import datetime

# 1. APIキー・トークンの設定
api_key = st.secrets.get("GEMINI_API_KEY")
github_token = st.secrets.get("GITHUB_TOKEN")
repo_name = "あなたのユーザー名/レポジトリ名"  # ←ここを書き換えてください

if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB TEI Editor", layout="wide")

# --- CSS (可読性とUI) ---
st.markdown("""
    <style>
    textarea { font-size: 22px !important; line-height: 2.0 !important; font-family: 'Amiri', serif; }
    .translation-box { font-size: 18px; line-height: 1.8; background-color: #f8f9fa; padding: 25px; border-left: 5px solid #007bff; border-radius: 10px; margin-bottom: 25px; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted TEI Editor")

# 2. セッション状態の初期化
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "name_cert": "High",
        "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [], 
        "source_text": "", "translation": ""
    }

col1, col2 = st.columns([1, 1.3])

# --- 左カラム：解析 ---
with col1:
    st.header("1. Source Analysis")
    source_text = st.text_area("Paste Arabic text here", height=450)
    if st.button("✨ AI Analysis"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("Analyzing..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Extract biographical data into JSON. Translate metadata (gender, relation) into English. Estimate 'cert' (High, Medium, Low). Text: {source_text}"
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.data.update(json.loads(res_text))
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.data.get("japanese_translation"):
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["japanese_translation"]}</div>', unsafe_allow_html=True)

# --- 右カラム：編集と送信 ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # 基本情報入力（前回同様）
    d["aind_id"] = st.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = st.text_input("Original ID", value=d.get("original_id", ""))
    d["name"] = st.text_input("Name (Arabic)", value=d.get("name", ""))
    
    # --- (Teachers, Family, Institutions の編集ループは前回と同じため省略) ---
    # ※ 実際の実装では前回のループ処理をここに入れてください

    st.divider()
    
    # XML生成
    xml_output = f"""<person xml:id="{d['aind_id']}" source="#original_{d['original_id']}" cert="{d.get('name_cert','high').lower()}">
    <persName xml:lang="ar">{d['name']}</persName>
    <death calendar="hijri" when-custom="{d['death_year']}">{d['death_year']}</death>
    <note type="description">{d['source_text']}</note>
</person>"""

    st.code(xml_output, language="xml")

    # --- GitHub送信セクション ---
    st.subheader("🚀 GitHub Deployment")
    file_path = st.text_input("File Path (e.g., data/person_001.xml)", value=f"data/{d['aind_id'] or 'temp'}.xml")
    commit_message = st.text_input("Commit Message", value=f"Add data for {d['name']}")

    if st.button("⬆️ Send to GitHub"):
        if not github_token:
            st.error("GitHub Token is missing in Secrets!")
        else:
            # GitHub APIを使ってファイルを送信
            url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
            headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
            
            # 既存ファイルがあるか確認（更新用）
            res = requests.get(url, headers=headers)
            sha = res.json().get("sha") if res.status_code == 200 else None
            
            payload = {
                "message": commit_message,
                "content": base64.b64encode(xml_output.encode()).decode(),
                "sha": sha
            }
            
            put_res = requests.put(url, headers=headers, json=payload)
            if put_res.status_code in [200, 201]:
                st.success(f"Successfully sent to GitHub: {file_path}")
            else:
                st.error(f"GitHub Error: {put_res.json().get('message')}")
