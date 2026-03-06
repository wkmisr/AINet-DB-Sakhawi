import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB TEI Editor", layout="wide")

# --- CSS (可読性とUIの調整) ---
st.markdown("""
    <style>
    textarea { font-size: 22px !important; line-height: 2.0 !important; font-family: 'Amiri', serif; }
    .translation-box { font-size: 18px; line-height: 1.8; background-color: #f8f9fa; padding: 25px; border-left: 5px solid #007bff; border-radius: 10px; margin-bottom: 25px; color: #2c3e50; }
    .stSelectbox label, .stTextInput label, .stNumberInput label { font-weight: bold; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted TEI Editor")

# 確信度の選択肢
CERT_OPTIONS = ["High", "Medium", "Low", "Unknown"]

# 2. セッション状態の初期化
# aind_id の初期値を AIND-S00001 に設定
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-S00001", "original_id": "", "name": "", "name_cert": "High",
        "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [], 
        "source_text": "", "translation": ""
    }

col1, col2 = st.columns([1, 1.3])

# --- 左カラム：ソース解析と翻訳 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Arabic biographical text here", height=450)
    
    if st.button("✨ AI Analysis (Data + Translation)"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("Analyzing and translating..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    Analyze the Arabic text and return ONLY JSON.
                    JSON Format:
                    {{
                      "original_id": "string",
                      "name": "Arabic full name", "name_cert": "High/Medium/Low",
                      "death_year": number, "death_cert": "High/Medium/Low",
                      "teachers": [ {{"name": "name", "gender": "Male/Female", "cert": "High/Medium/Low"}} ],
                      "family": [ {{"name": "name", "gender": "Male/Female", "relation": "Parent/Child/Sibling/Spouse/Cousin/Other", "cert": "High/Medium/Low"}} ],
                      "institutions": [ {{"name": "name", "relation": "Founder/Instructor/Student/Other", "cert": "High/Medium/Low"}} ],
                      "japanese_translation": "Fluent Japanese translation"
                    }}
                    Text: {source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    
                    if not isinstance(new_data.get("death_year"), (int, float)):
                        new_data["death_year"] = 850
                    
                    st.session_state.data.update(new_data)
                    st.session_state.data["translation"] = new_data.get("japanese_translation", "")
                    st.success(f"Analysis complete")
                except Exception as e:
                    st.error(f"Analysis Error: {e}")

    if st.session_state.data["translation"]:
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["translation"]}</div>', unsafe_allow_html=True)

# --- 右カラム：TEI 構造化データ編集 ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # ID & 姓名
    c_id_1, c_id_2 = st.columns(2)
    d["aind_id"] = c_id_1.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = c_id_2.text_input("Original ID", value=d.get("original_id", ""))
    
    c_name, c_ncert = st.columns([3, 1])
    d["name"] = c_name.text_input("Full Name (Arabic)", value=d.get("name", ""))
    d["name_cert"] = c_ncert.selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("name_cert", "High")), key="ncert")
    
    # 没年
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    try: death_val = int(d.get("death_year", 850))
    except: death_val = 850
    d["death_year"] = c_death.number_input("Death (Hijri AH)", value=death_val)
    d["death_cert"] = c_dcert.selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("death_cert", "High")), key="dcert")
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # --- 各種リストの入力UI ---
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        c = st.columns([3, 1.5, 1.5, 0.5])
        t["name"] = c[0].text_input("Teacher Name", value=t.get("name", ""), key=f"tn_{i}")
        t["gender"] = c[1].selectbox("Sex", ["Male", "Female"], index=0 if t.get("gender")=="Male" else 1, key=f"tg_{i}")
        t["cert"] = c[2].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(t.get("cert", "High")), key=f"tc_{i}")
        if c[3].button("❌", key=f"td_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name": "", "gender": "Male", "cert": "High"}); st.rerun()

    st.subheader("👪 Family")
    rel_f = ["Parent", "Child", "Sibling", "Spouse", "Cousin", "Other"]
    for i, f in enumerate(d.get("family", [])):
        c = st.columns([2.5, 1.5, 1.5, 1.5, 0.5])
        f["name"] = c[0].text_input("Family Name", value=f.get("name", ""), key=f"fn_{i}")
        f["gender"] = c[1].selectbox("Sex", ["Male", "Female"], index=0 if f.get("gender")=="Male" else 1, key=f"fg_{i}")
        f["relation"] = c[2].selectbox("Relation", rel_f, index=rel_f.index(f.get("relation", "Other")) if f.get("relation") in rel_f else 5, key=f"fr_{i}")
        f["cert"] = c[3].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(f.get("cert", "High")), key=f"fc_{i}")
        if c[4].button("❌", key=f"fd_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family"): d["family"].append({"name": "", "gender": "Male", "relation": "Other", "cert": "High"}); st.rerun()

    st.subheader("🕌 Institutions")
    rel_i = ["Founder", "Instructor", "Student", "Other"]
    for i, inst in enumerate(d.get("institutions", [])):
        c = st.columns([3, 2, 2, 0.5])
        inst["name"] = c[0].text_input("Inst Name", value=inst.get("name", ""), key=f"in_{i}")
        inst["relation"] = c[1].selectbox("Role", rel_i, index=rel_i.index(inst.get("relation", "Other")) if inst.get("relation") in rel_i else 3, key=f"ir_{i}")
        inst["cert"] = c[2].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(inst.get("cert", "High")), key=f"ic_{i}")
        if c[3].button("❌", key=f"id_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ Add Institution"): d["institutions"].append({"name": "", "relation": "Student", "cert": "High"}); st.rerun()

    st.divider()
    
    # --- 最終的な TEI XML 出力 ---
    if st.checkbox("Show Final TEI XML Preview"):
        xml_output = f"""<person @xml:id="{d['aind_id']}" @source="#original_{d['original_id']}" @cert="{d['name_cert'].lower()}">
    <persName @xml:lang="ar" @type="full">{d['name']}</persName>
    <death @calendar="hijri" @when-custom="{d['death_year']}" @cert="{d['death_cert'].lower()}">{d['death_year']}</death>
    <listBibl @type="teachers">
        {" ".join([f'<person @sex="{t["gender"][0]}" @role="teacher" @cert="{t.get("cert", "High").lower()}"><persName>{t["name"]}</persName></person>' for t in d["teachers"] if t["name"]])}
    </listBibl>
    <listRelation @type="family">
        {" ".join([f'<relation @active="#this" @passive="{f["name"]}" @name="{f.get("relation", "Other").lower()}" @sex="{f["gender"][0]}" @cert="{f.get("cert", "High").lower()}"/>' for f in d["family"] if f["name"]])}
    </listRelation>
    <listOrg @type="institutions">
        {" ".join([f'<orgName @role="{ins.get("relation", "Other").lower()}" @cert="{ins.get("cert", "High").lower()}">{ins["name"]}</orgName>' for ins in d["institutions"] if ins["name"]])}
    </listOrg>
    <desc @xml:lang="ar">
{d['source_text']}
    </desc>
    <desc @xml:lang="ja">
{d.get('translation', '')}
    </desc>
</person>"""
        st.code(xml_output, language="xml")
