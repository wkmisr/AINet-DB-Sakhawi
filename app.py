import streamlit as st
import google.generativeai as genai
import json

# --- 1. APIキーと基本設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# カスタムCSS（アラビア語フォントとコンパクトな入力欄）
st.markdown("""
    <style>
    .stTextInput input { padding: 4px 8px !important; }
    .ar-font { font-family: 'Amiri', serif; font-size: 1.3rem !important; direction: rtl; }
    .label-hint { font-size: 0.75rem; color: #888; margin-top: -10px; margin-bottom: 5px; }
    .section-header { background-color: #f0f2f6; padding: 5px 10px; border-radius: 5px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. セッション状態の初期化 ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "TMP-P-00001", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "lineage": [{"ar": "", "lat": "", "id": ""}],
        "nisbahs": [{"ar": "", "lat": "", "id": ""}],
        "activities": [{"ar": "", "lat": "", "id": ""}],
        "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# 不足しているキーの自動補完 (KeyError対策)
default_keys = {
    "full_name_lat": "", "death_cert": "High", "translation": "", 
    "source_text": "", "lineage": [], "nisbahs": [], "activities": []
}
for k, v in default_keys.items():
    if k not in d: d[k] = v

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source Text & AI")
    source_input = st.text_area("Biographical Source (Arabic)", value=d["source_text"], height=450)
    
    if st.button("✨ AI Structuring (Ar/Lat)"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("Analyzing..."):
                try:
                    # モデル名は安定していた gemini-1.5-flash または gemini-pro を使用
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""Extract data into JSON. 
                    Rules:
                    1. lineage: Array of {{ "ar": "...", "lat": "IJMES" }}
                    2. transliteration: Use IJMES style (e.g. al-Maqdisī).
                    3. Result must be ONLY JSON.
                    Text: {source_input}"""
                    response = model.generate_content(prompt)
                    # 余計なマークダウンを除去してパース
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    res_json = json.loads(clean_json)
                    d.update(res_json)
                    d["translation"] = res_json.get("japanese_translation", "")
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

    if d["translation"]:
        st.subheader("🇯🇵 Translation")
        st.info(d["translation"])

with col2:
    st.header("2. Entity Management")
    
    # (A) 基本ID
    c_id1, c_id2 = st.columns(2)
    d["aind_id"] = c_id1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c_id2.text_input("Source ID", d["original_id"])
    
    # (B) 名前
    f_ar, f_lat = st.columns(2)
    d["full_name"] = f_ar.text_input("Full Name (Arabic)", d["full_name"])
    d["full_name_lat"] = f_lat.text_input("Full Name (Latin IJMES)", d["full_name_lat"])

    # (C) 系譜
    st.markdown('<div class="section-header">🧬 Lineage (Nasab)</div>', unsafe_allow_html=True)
    for i, lin in enumerate(d["lineage"]):
        cols = st.columns([2, 2, 1.2, 0.4])
        lin["ar"] = cols[0].text_input(f"Ar_{i}", lin.get("ar",""), key=f"lar_{i}", label_visibility="collapsed")
        lin["lat"] = cols[1].text_input(f"Lat_{i}", lin.get("lat",""), key=f"llat_{i}", label_visibility="collapsed")
        lin["id"] = cols[2].text_input(f"ID_{i}", lin.get("id",""), key=f"lid_{i}", label_visibility="collapsed")
        if cols[3].button("❌", key=f"ldel_{i}"): d["lineage"].pop(i); st.rerun()
    if st.button("＋ Add Ancestor"): d["lineage"].append({"ar":"","lat":"","id":""}); st.rerun()

    # (D) ニスバ
    st.markdown('<div class="section-header">📝 Nisbahs</div>', unsafe_allow_html=True)
    for i, nis in enumerate(d["nisbahs"]):
        cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = cols[0].text_input(f"Nar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = cols[1].text_input(f"Nlat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = cols[2].text_input(f"Nid_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed")
        if cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # (E) 地名
    st.markdown('<div class="section-header">📍 Activities / Places</div>', unsafe_allow_html=True)
    for i, act in enumerate(d["activities"]):
        cols = st.columns([2, 2, 1.2, 0.4])
        act["ar"] = cols[0].text_input(f"Aar_{i}", act.get("ar",""), key=f"aar_{i}", label_visibility="collapsed")
        act["lat"] = cols[1].text_input(f"Alat_{i}", act.get("lat",""), key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = cols[2].text_input(f"Aid_{i}", act.get("id",""), key=f"aid_{i}", label_visibility="collapsed")
        if cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ Add Place"): d["activities"].append({"ar":"","lat":"","id":""}); st.rerun()

    # (F) 師匠・家族・施設
    st.markdown('<div class="section-header">🎓 Teachers</div>', unsafe_allow_html=True)
    for i, t in enumerate(d["teachers"]):
        cols = st.columns([3, 2, 0.5])
        t["name"] = cols[0].text_input(f"T-Name {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = cols[1].text_input(f"T-ID {i}", t.get("id",""), key=f"tid_{i}")
        if cols[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name":"","id":""}); st.rerun()

    st.markdown('<div class="section-header">👪 Family</div>', unsafe_allow_html=True)
    for i, f in enumerate(d["family"]):
        cols = st.columns([2, 1.5, 1.5, 0.5])
        f["name"] = cols[0].text_input(f"F-Name {i}", f.get("name",""), key=f"fn_{i}")
        f["relation"] = cols[1].text_input(f"Rel {i}", f.get("relation",""), key=f"fr_{i}")
        f["id"] = cols[2].text_input(f"F-ID {i}", f.get("id",""), key=f"fid_{i}")
        if cols[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family Member"): d["family"].append({"name":"","relation":"","id":""}); st.rerun()

    st.markdown('<div class="section-header">🕌 Institutions</div>', unsafe_allow_html=True)
    for i, inst in enumerate(d["institutions"]):
        cols = st.columns([3, 2, 0.5])
        inst["name"] = cols[0].text_input(f"I-Name {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = cols[1].text_input(f"I-ID {i}", inst.get("id",""), key=f"iid_{i}")
        if cols[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ Add Institution"): d["institutions"].append({"name":"","id":""}); st.rerun()

    # --- XML Preview ---
    st.divider()
    if st.checkbox("Show Final TEI XML Preview"):
        st.code(f'<person xml:id="{d["aind_id"]}">\n  <persName xml:lang="ar">{d["full_name"]}</persName>\n</person>', language="xml")
