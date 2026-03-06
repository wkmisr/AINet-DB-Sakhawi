import streamlit as st
import google.generativeai as genai
import json

# APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Pro Editor v2", layout="wide")

# UIデザインの調整
st.markdown("""
    <style>
    .stTextInput input { padding: 5px !important; }
    .label-hint { font-size: 0.8rem; color: #666; margin-bottom: -5px; }
    .ar-font { font-family: 'Amiri', serif; font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化と不足キーの補完
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "TMP-P-00001", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "lineage": [{"ar": "", "lat": "", "id": ""}, {"ar": "", "lat": "", "id": ""}, {"ar": "", "lat": "", "id": ""}],
        "nisbahs": [], "madhhab": "",
        "activities": [], "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- KeyError対策: 既存セッションに新しいキーがない場合に補完 ---
for key in ["full_name_lat", "death_cert", "translation", "source_text"]:
    if key not in d: d[key] = ""

col1, col2 = st.columns([1, 1.5])

# --- 左カラム：ソースとAI解析 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Arabic Text", value=d.get("source_text", ""), height=400)
    
    if st.button("✨ AI Analysis (Ar/Lat/Struct)"):
        if source_text:
            d["source_text"] = source_text
            with st.spinner("Analyzing..."):
                try:
                    # モデル選択 (2.5 flash が利用可能なら優先)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""Analyze the text and return JSON. 
                    Transliterate names using IJMES style (e.g., Ibrāhīm, al-Bā'ūnī).
                    Include Japanese translation.
                    JSON: {{
                      "full_name": "Ar", "full_name_lat": "Lat",
                      "lineage": [ {{"ar": "Ar", "lat": "Lat"}} ],
                      "nisbahs": [ {{"ar": "Ar", "lat": "Lat"}} ],
                      "activities": [ {{"ar": "Ar", "lat": "Lat"}} ],
                      "death_year": 850, "japanese_translation": "..."
                    }}
                    Text: {source_text}"""
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    d.update(new_data)
                    d["translation"] = new_data.get("japanese_translation", "")
                    st.success("Analysis Complete")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if d.get("translation"):
        st.subheader("🇯🇵 Translation")
        st.info(d["translation"])

# --- 右カラム：プロフェッショナル・エディタ ---
with col2:
    st.header("2. TEI Entity Editor")
    
    # 基本IDとフルネーム
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("Person TMP-ID", d.get("aind_id", "TMP-P-00001"))
    d["original_id"] = c2.text_input("Original ID (Source)", d.get("original_id", ""))
    
    f1, f2 = st.columns(2)
    d["full_name"] = f1.text_input("Full Name (Arabic)", d.get("full_name", ""))
    d["full_name_lat"] = f2.text_input("Full Name (Latin IJMES)", d.get("full_name_lat", ""))

    st.divider()

    # 🧬 系譜 (Lineage)
    st.subheader("🧬 Lineage (Structured Nasab)")
    st.markdown('<p class="label-hint">Arabic | Latin (IJMES) | TMP-ID</p>', unsafe_allow_html=True)
    for i, lin in enumerate(d["lineage"]):
        cols = st.columns([2, 2, 1.2, 0.4])
        lin["ar"] = cols[0].text_input(f"Ar {i}", lin.get("ar", ""), key=f"lar_{i}", label_visibility="collapsed")
        lin["lat"] = cols[1].text_input(f"Lat {i}", lin.get("lat", ""), key=f"llat_{i}", label_visibility="collapsed")
        lin["id"] = cols[2].text_input(f"ID {i}", lin.get("id", ""), key=f"lid_{i}", label_visibility="collapsed", placeholder="TMP-P-...")
        if cols[3].button("❌", key=f"ldel_{i}"): d["lineage"].pop(i); st.rerun()
    if st.button("＋ Add Ancestor"): d["lineage"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    st.divider()

    # 📝 属性 (Nisbah & Activities)
    st.subheader("📝 Attributes & Places")
    
    # Nisbah
    st.write("**Nisbahs** (Ar | Lat | ID)")
    for i, nis in enumerate(d.get("nisbahs", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = cols[0].text_input(f"N-Ar {i}", nis.get("ar", ""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = cols[1].text_input(f"N-Lat {i}", nis.get("lat", ""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = cols[2].text_input(f"N-ID {i}", nis.get("id", ""), key=f"nid_{i}", label_visibility="collapsed", placeholder="TMP-L-...")
        if cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"): d["nisbahs"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    # Activities / Places
    st.write("**Places / Activities** (Ar | Lat | GeoNames ID)")
    for i, act in enumerate(d.get("activities", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        act["ar"] = cols[0].text_input(f"A-Ar {i}", act.get("ar", ""), key=f"aar_{i}", label_visibility="collapsed")
        act["lat"] = cols[1].text_input(f"A-Lat {i}", act.get("lat", ""), key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = cols[2].text_input(f"A-ID {i}", act.get("id", ""), key=f"aid_{i}", label_visibility="collapsed", placeholder="gn:xxxx")
        if cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ Add Place"): d["activities"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    st.divider()

    # 没年
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    d["death_year"] = c_death.number_input("Death (Hijri)", value=int(d.get("death_year", 850)))
    d["death_cert"] = c_dcert.selectbox("Death Cert", ["High", "Medium", "Low"], index=0)
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # 🎓 Teachers
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        c = st.columns([3, 1, 1.5, 0.5])
        t["name"] = c[0].text_input("Name", t.get("name", ""), key=f"tn_{i}")
        t["id"] = c[1].text_input("ID", t.get("id", ""), key=f"tid_{i}", placeholder="TMP-P-...")
        t["cert"] = c[2].selectbox("Cert", ["High", "Medium", "Low"], key=f"tc_{i}")
        if c[3].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name": "", "id": "", "cert": "High"}); st.rerun()

    # 👪 Family
    st.subheader("👪 Family")
    for i, f in enumerate(d.get("family", [])):
        c = st.columns([2, 1.5, 1.5, 0.5])
        f["name"] = c[0].text_input("Name", f.get("name", ""), key=f"fn_{i}")
        f["relation"] = c[1].text_input("Relation", f.get("relation", ""), key=f"fr_{i}")
        f["id"] = c[2].text_input("TMP-ID", f.get("id", ""), key=f"fid_{i}", placeholder="TMP-P-xxxxx-f1")
        if c[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family"): d["family"].append({"name": "", "relation": "", "id": ""}); st.rerun()

    # 🕌 Institutions
    st.subheader("🕌 Institutions")
    for i, inst in enumerate(d.get("institutions", [])):
        c = st.columns([3, 2, 0.5])
        inst["name"] = c[0].text_input("Institution", inst.get("name", ""), key=f"in_{i}")
        inst["id"] = c[1].text_input("GeoNames/Ref ID", inst.get("id", ""), key=f"iid_{i}")
        if c[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ Add Institution"): d["institutions"].append({"name": "", "id": ""}); st.rerun()

    st.divider()
    
    # --- XML出力ロジック ---
    if st.checkbox("Show Professional TEI XML"):
        # (多言語対応のXML生成コード)
        st.code("<person xml:id='...'> ... </person>", language="xml")
