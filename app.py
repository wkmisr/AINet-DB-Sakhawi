import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")

# --- CSSによる可読性向上 ---
st.markdown("""
    <style>
    /* テキストエリアの文字サイズと行間を調整 */
    textarea {
        font-size: 20px !important;
        line-height: 1.8 !important;
        font-family: 'Amiri', serif; /* アラビア語に適したフォント */
    }
    /* 日本語訳の表示スタイル */
    .translation-box {
        font-size: 18px; /* 約13.5pt相当 */
        line-height: 1.6;
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        color: #1f1f1f;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. セッション状態の管理
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "death_year": 850,
        "teachers": [], "family": [], "institutions": [], "source_text": "",
        "translation": ""
    }

col1, col2 = st.columns([1, 1.2])

# --- 左カラム：AI解析 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Sakhawi text here", height=400)
    
    if st.button("✨ Extract, Translate & Japanese Translation"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("AI analyzing and translating..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    Extract biographical data and return ONLY JSON.
                    Also, provide a fluent Japanese translation of the entire text.
                    
                    JSON structure:
                    {{
                      "original_id": "string",
                      "name": "Arabic name",
                      "death_year": number,
                      "teachers": [ {{"name": "name", "gender": "Male/Female"}} ],
                      "family": [ {{"name": "name", "gender": "Male/Female", "relation": "Child/Parent/etc"}} ],
                      "institutions": [ {{"name": "name", "relation": "Founder/Instructor/Student/Other"}} ],
                      "japanese_translation": "全文の日本語訳"
                    }}
                    Text: {source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    
                    # データの型チェック
                    if not isinstance(new_data.get("death_year"), (int, float)):
                        new_data["death_year"] = 850
                    
                    st.session_state.data.update(new_data)
                    st.session_state.data["translation"] = new_data.get("japanese_translation", "")
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # 日本語訳の表示セクション
    if st.session_state.data["translation"]:
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["translation"]}</div>', unsafe_allow_html=True)

# --- 右カラム：データ編集 ---
with col2:
    st.header("2. Structural Data Editor")
    d = st.session_state.data
    
    # IDs & Basic Info
    c_id1, c_id2 = st.columns(2)
    d["aind_id"] = c_id1.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = c_id2.text_input("Original ID", value=d.get("original_id", ""))
    d["name"] = st.text_input("Person Name (Arabic)", value=d.get("name", ""))
    
    c_y1, c_y2 = st.columns(2)
    try:
        raw_death = d.get("death_year", 850)
        death_val = int(raw_death) if raw_death else 850
    except (ValueError, TypeError):
        death_val = 850

    d["death_year"] = c_y1.number_input("Death (Hijri)", value=death_val)
    c_y2.metric("AD Year", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # --- 各セクション（Teachers, Family, Institutions） ---
    # （前回のコードと同様のため省略しますが、フルセットのコードに組み込まれています）
    # ... (前回の編集用ループ処理) ...
    # ※ 便宜上、ここには以前と同じループ処理が動くように記述してください
    
    # --- Teachers ---
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        cols = st.columns([3, 2, 1])
        t["name"] = cols[0].text_input(f"Teacher Name {i}", value=t.get("name", ""), key=f"tn_{i}")
        t["gender"] = cols[1].selectbox(f"Gender {i}", ["Male", "Female"], index=0 if t.get("gender")=="Male" else 1, key=f"tg_{i}")
        if cols[2].button("❌", key=f"tdel_{i}"):
            d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"):
        d["teachers"].append({"name": "", "gender": "Male"}); st.rerun()

    # --- Family ---
    st.subheader("👪 Family")
    rel_f = ["Parent", "Child", "Sibling", "Spouse", "Cousin", "Other"]
    for i, f in enumerate(d.get("family", [])):
        cols = st.columns([3, 2, 2, 1])
        f["name"] = cols[0].text_input(f"Member Name {i}", value=f.get("name", ""), key=f"fn_{i}")
        f["gender"] = cols[1].selectbox(f"Gender {i}", ["Male", "Female"], index=0 if f.get("gender")=="Male" else 1, key=f"fg_{i}")
        idx = rel_f.index(f["relation"]) if f.get("relation") in rel_f else 5
        f["relation"] = cols[2].selectbox(f"Relation {i}", rel_f, index=idx, key=f"fr_{i}")
        if cols[3].button("❌", key=f"fdel_{i}"):
            d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family"):
        d["family"].append({"name": "", "gender": "Male", "relation": "Other"}); st.rerun()

    # --- Institutions ---
    st.subheader("🕌 Institutions")
    rel_i = ["Founder", "Instructor", "Student", "Other"]
    for i, inst in enumerate(d.get("institutions", [])):
        cols = st.columns([3, 3, 1])
        inst["name"] = cols[0].text_input(f"Inst Name {i}", value=inst.get("name", ""), key=f"in_{i}")
        idx = rel_i.index(inst["relation"]) if inst.get("relation") in rel_i else 3
        inst["relation"] = cols[1].selectbox(f"Role {i}", rel_i, index=idx, key=f"ir_{i}")
        if cols[2].button("❌", key=f"idel_{i}"):
            d["institutions"].pop(i); st.rerun()
    if st.button("＋ Add Institution"):
        d["institutions"].append({"name": "", "relation": "Student"}); st.rerun()

    st.divider()
    
    if st.checkbox("Final XML Preview"):
        xml_output = f"""<person xml:id="{d['aind_id']}" source="#original_{d['original_id']}">
    <persName xml:lang="ar">{d['name']}</persName>
    <death calendar="hijri" when-custom="{d['death_year']}">{d['death_year']}</death>
    <listBibl type="teachers">
        {" ".join([f'<person sex="{t["gender"]}" role="teacher">{t["name"]}</person>' for t in d["teachers"] if t["name"]])}
    </listBibl>
    <listRelation type="family">
        {" ".join([f'<relation sex="{f["gender"]}" name="{f["relation"].lower()}">{f["name"]}</relation>' for f in d["family"] if f["name"]])}
    </listRelation>
    <listOrg type="institutions">
        {" ".join([f'<orgName role="{ins["relation"].lower()}">{ins["name"]}</orgName>' for ins in d["institutions"] if ins["name"]])}
    </listOrg>
    <note type="description">
{d['source_text']}
    </note>
</person>"""
        st.code(xml_output, language="xml")
