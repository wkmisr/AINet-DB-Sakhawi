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
    .label-hint { font-size: 0.8rem; color: #666; margin-bottom: -15px; }
    .ar-input { font-family: 'Amiri', serif; font-size: 1.2rem !important; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

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

col1, col2 = st.columns([1, 1.5])

# --- 左カラム：ソースとAI解析 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Arabic Text", height=400)
    
    if st.button("✨ AI Analysis (Ar/Lat/Struct)"):
        with st.spinner("Gemini 2.5/1.5 is analyzing..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Analyze the Arabic text and return JSON. 
                - lineage: List ancestors [{{ "ar": "name", "lat": "IJMES transliteration" }}]
                - nisbahs: List nisbahs [{{ "ar": "name", "lat": "IJMES transliteration" }}]
                - activities: List places [{{ "ar": "name", "lat": "IJMES transliteration" }}]
                - transliteration: Use IJMES style (e.g., Ibrāhīm, al-Bā'ūnī).
                Text: {source_text}
                """
                # JSON抽出ロジック（実際にはここでAIが返したJSONをdに反映）
                # ... (AI呼び出しの詳細は維持)
                st.success("Analysis Complete (Pseudo-code for demo)")
            except Exception as e:
                st.error(f"Error: {e}")

# --- 右カラム：プロフェッショナル・エディタ ---
with col2:
    st.header("2. TEI Entity Editor")
    
    # 基本IDとフルネーム
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("Person TMP-ID", d["aind_id"])
    d["original_id"] = c2.text_input("Original ID (Source)", d["original_id"])
    
    f1, f2 = st.columns(2)
    d["full_name"] = f1.text_input("Full Name (Arabic)", d["full_name"])
    d["full_name_lat"] = f2.text_input("Full Name (Latin IJMES)", d["full_name_lat"])

    st.divider()

    # 🧬 系譜 (Lineage)
    st.subheader("🧬 Lineage (Structured Nasab)")
    st.markdown('<p class="label-hint">Arabic | Latin (IJMES) | TMP-ID</p>', unsafe_allow_html=True)
    for i, lin in enumerate(d["lineage"]):
        cols = st.columns([2, 2, 1.2, 0.4])
        lin["ar"] = cols[0].text_input(f"Ar {i}", lin["ar"], key=f"lar_{i}", label_visibility="collapsed")
        lin["lat"] = cols[1].text_input(f"Lat {i}", lin["lat"], key=f"llat_{i}", label_visibility="collapsed")
        lin["id"] = cols[2].text_input(f"ID {i}", lin["id"], key=f"lid_{i}", label_visibility="collapsed", placeholder="TMP-P-...")
        if cols[3].button("❌", key=f"ldel_{i}"): d["lineage"].pop(i); st.rerun()
    if st.button("＋ Add Ancestor"): d["lineage"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    st.divider()

    # 📝 属性 (Nisbah & Activities)
    st.subheader("📝 Attributes & Places")
    
    # Nisbah
    st.write("**Nisbahs** (Ar | Lat | ID)")
    for i, nis in enumerate(d.get("nisbahs", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = cols[0].text_input(f"N-Ar {i}", nis["ar"], key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = cols[1].text_input(f"N-Lat {i}", nis["lat"], key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = cols[2].text_input(f"N-ID {i}", nis["id"], key=f"nid_{i}", label_visibility="collapsed", placeholder="TMP-L-...")
        if cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"): d["nisbahs"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    # Activities / Places
    st.write("**Places / Activities** (Ar | Lat | GeoNames ID)")
    for i, act in enumerate(d.get("activities", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        act["ar"] = cols[0].text_input(f"A-Ar {i}", act["ar"], key=f"aar_{i}", label_visibility="collapsed")
        act["lat"] = cols[1].text_input(f"A-Lat {i}", act["lat"], key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = cols[2].text_input(f"A-ID {i}", act["id"], key=f"aid_{i}", label_visibility="collapsed", placeholder="gn:xxxx / TMP-L-...")
        if cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ Add Place"): d["activities"].append({"ar": "", "lat": "", "id": ""}); st.rerun()

    st.divider()

    # --- 師匠・家族・施設 (前回のUIを維持しつつID欄を追加) ---
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        c = st.columns([3, 1, 1, 1.5, 0.5])
        t["name"] = c[0].text_input("Name", t["name"], key=f"tn_{i}")
        t["gender"] = c[1].selectbox("Sex", ["M", "F"], key=f"tg_{i}")
        t["cert"] = c[2].selectbox("Cert", ["H", "M", "L"], key=f"tc_{i}")
        t["id"] = c[3].text_input("TMP-ID", t.get("id", ""), key=f"tid_{i}", placeholder="TMP-P-...")
        if c[4].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name": "", "gender": "M", "cert": "H", "id": ""}); st.rerun()

    # (Family, Institutions も同様の構造で配置)
    # ... 中略 ...

    # --- TEI XML Preview ---
    if st.checkbox("Show Multilingual TEI XML Preview"):
        st.code("", language="xml")
