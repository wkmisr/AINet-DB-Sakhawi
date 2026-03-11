import streamlit as st
import google.generativeai as genai
import json

# --- 1. APIキーと基本設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# カスタムCSS
st.markdown("""
    <style>
    .stTextInput input { padding: 4px 8px !important; }
    .ar-font { font-family: 'Amiri', serif; font-size: 1.3rem !important; direction: rtl; }
    .section-header { background-color: #f0f2f6; padding: 5px 10px; border-radius: 5px; margin-top: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. セッション状態の初期化 ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "nisbahs": [], "activities": [],
        "death_year": 850, "teachers": [], "family": [], "institutions": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source Text & AI")
    source_input = st.text_area("Biographical Source (Arabic)", value=d["source_text"], height=450)
    
    if st.button("✨ AI Structuring (Ar/Lat)"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("Analyzing with Latest Gemini..."):
                try:
                    # モデル自動選択ロジック（404回避）
                    available_models = [m.name for m in genai.list_models()]
                    pref_models = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
                    model_name = next((m for m in pref_models if m in available_models), 'gemini-pro')
                    
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""Extract data into JSON. Rules:
                    1. Use IJMES transliteration (e.g. al-Maqdisī).
                    2. Distinguish between 'teachers' (persons) and 'institutions' (madrasas, etc.).
                    3. Determine 'sex' (Male/Female) and 'certainty' (High/Medium/Low).
                    4. Result must be ONLY JSON.
                    Text: {source_input}"""
                    
                    response = model.generate_content(prompt)
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    res_json = json.loads(clean_json)
                    
                    d.update(res_json)
                    d["translation"] = res_json.get("japanese_translation", "")
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

    if d.get("translation"):
        st.subheader("🇯🇵 Translation")
        st.info(d["translation"])

with col2:
    st.header("2. Entity Management")
    
    # (A) 基本情報 & 性別・確信度
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    d["aind_id"] = c1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c2.text_input("Source ID", d["original_id"])
    d["sex"] = c3.selectbox("Sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("Certainty", ["High", "Medium", "Low"], index=0)
    
    f_ar, f_lat = st.columns(2)
    d["full_name"] = f_ar.text_input("Full Name (Arabic)", d["full_name"])
    d["full_name_lat"] = f_lat.text_input("Full Name (Latin IJMES)", d["full_name_lat"])

    # (B) ニスバ
    st.markdown('<div class="section-header">📝 Nisbahs</div>', unsafe_allow_html=True)
    for i, nis in enumerate(d.get("nisbahs", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = cols[0].text_input(f"Nar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = cols[1].text_input(f"Nlat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = cols[2].text_input(f"Nid_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed", placeholder="gn:xxx")
        if cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # (C) 師匠
    st.markdown('<div class="section-header">🎓 Teachers (TMP-P-xxx)</div>', unsafe_allow_html=True)
    for i, t in enumerate(d.get("teachers", [])):
        cols = st.columns([3, 2, 0.5])
        t["name"] = cols[0].text_input(f"T-Name {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = cols[1].text_input(f"T-ID {i}", t.get("id",""), key=f"tid_{i}")
        if cols[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name":"","id":""}); st.rerun()

    # (D) 施設
    st.markdown('<div class="section-header">🕌 Institutions (TMP-O-xxx)</div>', unsafe_allow_html=True)
    for i, inst in enumerate(d.get("institutions", [])):
        cols = st.columns([3, 2, 0.5])
        inst["name"] = cols[0].text_input(f"I-Name {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = cols[1].text_input(f"I-ID {i}", inst.get("id",""), key=f"iid_{i}")
        if cols[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ Add Institution"): d["institutions"].append({"name":"","id":""}); st.rerun()

    # (E) 家族
    st.markdown('<div class="section-header">👪 Family</div>', unsafe_allow_html=True)
    for i, f in enumerate(d.get("family", [])):
        cols = st.columns([2, 1.5, 1.5, 0.5])
        f["name"] = cols[0].text_input(f"F-Name {i}", f.get("name",""), key=f"fn_{i}")
        f["relation"] = cols[1].text_input(f"Rel {i}", f.get("relation",""), key=f"fr_{i}")
        f["id"] = cols[2].text_input(f"F-ID {i}", f.get("id",""), key=f"fid_{i}")
        if cols[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family Member"): d["family"].append({"name":"","relation":"","id":""}); st.rerun()

    # --- XML Preview ---
    st.divider()
    if st.checkbox("Show Final TEI XML Preview"):
        xml_output = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}">
  <persName xml:lang="ar">{d['full_name']}</persName>
  <persName xml:lang="lat">{d['full_name_lat']}</persName>
</person>"""
        st.code(xml_output, language="xml")
