import streamlit as st
import google.generativeai as genai
import json
import re

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. セッション状態の管理
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "",
        "original_id": "",
        "name": "",
        "death_year": 850,
        "teachers": [],
        "family": []
    }

col1, col2 = st.columns([1, 1.2])

# --- 左カラム：AI解析 ---
with col1:
    st.header("1. 原文解析")
    source_text = st.text_area("サハウィーのテキストを貼り付け", height=400)
    
    if st.button("✨ AIで項目を自動抽出"):
        if source_text:
            with st.spinner("AI解析中..."):
                try:
                    # 利用可能なモデルを自動取得して実行
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    
                    model = genai.GenerativeModel(selected_model)
                    
                    # プロンプトの強化：ID抽出の指示を追加
                    prompt = f"""
                    以下のアラビア語テキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                    特に「###$数字$# $」という形式があれば、その数字をoriginal_idとして抽出してください。
                    {{ 
                      "original_id": "数字", 
                      "name": "姓名", 
                      "death_year": 数字のみ, 
                      "teachers": ["師匠1", "師匠2"], 
                      "family": ["親族1", "親族2"] 
                    }}
                    テキスト：{source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    
                    # データをセッションに保存（aind_idは空のまま保持）
                    extracted_data = json.loads(res_text)
                    st.session_state.data.update(extracted_data)
                    st.success(f"抽出成功！ (使用モデル: {selected_model})")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# --- 右カラム：データ編集 ---
with col2:
    st.header("2. データ編集・確定")
    d = st.session_state.data
    
    # ID関連の入力
    cid1, cid2 = st.columns(2)
    with cid1:
        st.session_state.data["aind_id"] = st.text_input("AIND ID", value=d.get("aind_id", ""))
    with cid2:
        st.session_state.data["original_id"] = st.text_input("Original ID (###$ID$#)", value=d.get("original_id", ""))

    # 基本情報
    st.session_state.data["name"] = st.text_input("フルネーム", value=d.get("name", ""))
    
    c1, c2 = st.columns(2)
    with c1:
        try:
            val = int(d.get("death_year", 850))
        except:
            val = 850
        st.session_state.data["death_year"] = st.number_input("没年 (Hijri)", value=val)
    with c2:
        ad_year = int(st.session_state.data["death_year"] * 0.97 + 622)
        st.metric("西暦 (目安)", f"約 {ad_year} 年")

    st.divider()

    # 師匠リストの編集
    st.subheader("🎓 師匠 (Teachers)")
    updated_teachers = []
    for i, t in enumerate(d.get("teachers", [])):
        col_t, col_del = st.columns([4, 1])
        with col_t:
            edited_t = st.text_input(f"師匠 {i+1}", value=t, key=f"t_{i}")
            updated_teachers.append(edited_t)
        with col_del:
            if st.button("❌", key=f"del_t_{i}"):
                d["teachers"].pop(i)
                st.rerun()
    
    if st.button("＋ 師匠を追加"):
        d["teachers"].append("")
        st.rerun()
    st.session_state.data["teachers"] = updated_teachers

    st.divider()

    # 家族リストの編集
    st.subheader("👪 家族 (Family)")
    updated_family = []
    for i, f in enumerate(d.get("family", [])):
        col_f, col_del_f = st.columns([4, 1])
        with col_f:
            edited_f = st.text_input(f"家族 {i+1}", value=f, key=f"f_{i}")
            updated_family.append(edited_f)
        with col_del_f:
            if st.button("❌", key=f"del_f_{i}"):
                d["family"].pop(i)
                st.rerun()
    
    if st.button("＋ 家族を追加"):
        d["family"].append("")
        st.rerun()
    st.session_state.data["family"] = updated_family

    st.divider()
    
    # 最終出力プレビュー
    if st.checkbox("XMLプレビューを表示"):
        xml_output = f"""<person id="{st.session_state.data['aind_id']}" original_id="{st.session_state.data['original_id']}">
    <name>{st.session_state.data['name']}</name>
    <death>{st.session_state.data['death_year']}</death>
    <teachers>
        {" ".join([f'<teacher>{t}</teacher>' for t in st.session_state.data['teachers'] if t])}
    </teachers>
    <family>
        {" ".join([f'<member>{f}</member>' for f in st.session_state.data['family'] if f])}
    </family>
</person>"""
        st.code(xml_output, language="xml")
