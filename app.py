import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB TEI Editor", layout="wide")

# --- CSS (UIの調整) ---
st.markdown("""
    <style>
    textarea { font-size: 22px !important; line-height: 2.0 !important; font-family: 'Amiri', serif; }
    .translation-box { font-size: 18px; line-height: 1.8; background-color: #f8f9fa; padding: 25px; border-left: 5px solid #007bff; border-radius: 10px; margin-bottom: 25px; color: #2c3e50; }
    .stSelectbox label, .stTextInput label, .stNumberInput label { font-weight: bold; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted TEI Editor")

CERT_OPTIONS = ["High", "Medium", "Low", "Unknown"]

# 2. セッション状態の初期化
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D00001", "original_id": "", 
        "full_name": "", "name_cert": "High",
        "lineage": ["", "", ""], 
        "nisbahs": [], "madhhab": "",
        "activities": [],
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
            with st.spinner("Analyzing..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    Analyze the Arabic text and return ONLY JSON.
                    Guidelines:
                    - full_name: Complete name with all nisbahs.
                    - lineage: List from person to ancestors (e.g. ["ism", "father", "grandfather"]).
                    - nisbahs: List of nisbahs.
                    - activities: Regions of activity.
                    - japanese_translation: Fluent Japanese translation.
                    
                    JSON Format:
                    {{
                      "original_id": "string",
                      "full_name": "Arabic full name", "name_cert": "High/Medium/Low",
                      "lineage": ["person", "father", "grandfather"],
                      "nisbahs": ["nis1"], "madhhab": "School", "activities": ["City1"],
                      "death_year": 850, "death_cert": "High",
                      "teachers": [ {{"name": "name", "gender": "Male", "cert": "High"}} ],
                      "family": [ {{"name": "name", "gender": "Male", "relation": "Parent", "cert": "High"}} ],
                      "institutions": [ {{"name": "name", "relation": "Student", "cert": "High"}} ],
                      "japanese_translation": "Japanese"
                    }}
                    Text: {source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    st.session_state.data.update(new_data)
                    st.session_state.data["translation"] = new_data.get("japanese_translation", "")
                    st.success("Analysis complete")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.data["translation"]:
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["translation"]}</div>', unsafe_allow_html=True)

# --- 右カラム：TEI Data Editor ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # ID系
    c_id_1, c_id_2 = st.columns(2)
    d["aind_id"] = c_id_1.text_input("AIND ID (@xml:id)", value=d.get("aind_id", ""))
    d["original_id"] = c_id_2.text_input("Original ID (@source)", value=d.get("original_id", ""))
    
    # 名前
    c_full, c_ncert = st.columns([3, 1])
    d["full_name"] = c_full.text_input("Full Name (Complete)", value=d.get("full_name", ""))
    d["name_cert"] = c_ncert.selectbox("Name Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("name_cert", "High")), key="ncert")
    
    # 系譜
    st.subheader("🧬 Lineage (本人-父-祖父...)")
    for i, name in enumerate(d.get("lineage", [])):
        label = "Person (本人)" if i == 0 else "Father (父)" if i == 1 else "Grandfather (祖父)" if i == 2 else f"Ancestor {i}"
        c = st.columns([5, 1])
        d["lineage"][i] = c[0].text_input(label, value=name, key=f"lin_{i}")
        if c[1].button("❌", key=f"lind_{i}"): d["lineage"].pop(i); st.rerun()
    if st.button("＋ Add Ancestor"): d["lineage"].append(""); st.rerun()

    st.divider()

    # 属性 (Nisbah, Madhhab, Activities)
    st.subheader("📝 Attributes")
    d["madhhab"] = st.text_input("Madhhab", value=d.get("madhhab", ""))
    for i, nis in enumerate(d.get("nisbahs", [])):
        c = st.columns([5, 1])
        d["nisbahs"][i] = c[0].text_input(f"Nisbah {i+1}", value=nis, key=f"nis_{i}")
        if c[1].button("❌", key=f"nisd_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"): d["nisbahs"].append(""); st.rerun()

    for i, area in enumerate(d.get("activities", [])):
        c = st.columns([5, 1])
        d["activities"][i] = c[0].text_input(f"Activity Area {i+1}", value=area, key=f"act_{i}")
        if c[1].button("❌", key=f"actd_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ Add Activity Area"): d["activities"].append(""); st.rerun()

    st.divider()

    # 没年
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    try: death_val = int(d.get("death_year", 850))
    except: death_val = 850
    d["death_year"] = c_death.number_input("Death (Hijri)", value=death_val)
    d["death_cert"] = c_dcert.selectbox("Death Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("death_cert", "High")), key="dcert")
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # 師匠 / Teachers
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        c = st.columns([3, 1.5, 1.5, 0.5])
        t["name"] = c[0].text_input("Teacher Name", value=t.get("name", ""), key=f"tn_{i}")
        t["gender"] = c[1].selectbox("Sex", ["Male", "Female"], index=0 if t.get("gender")=="Male" else 1, key=f"tg_{i}")
        t["cert"] = c[2].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(t.get("cert", "High")), key=f"tc_{i}")
        if c[3].button("❌", key=f"td_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name": "", "gender": "Male", "cert": "High"}); st.rerun()

    # 家族 / Family
    st.subheader("👪 Family")
    rel_f = ["Parent", "Child", "Sibling", "Spouse", "Cousin", "Other"]
    for i, f in enumerate(d.get("family", [])):
        c = st.columns([2.5, 1.5, 1.5, 1.5, 0.5])
        f["name"] = c[0].text_input("Family Member", value=f.get("name", ""), key=f"fn_{i}")
        f["gender"] = c[1].selectbox("Sex", ["Male", "Female"], index=0 if f.get("gender")=="Male" else 1, key=f"fg_{i}")
        f["relation"] = c[2].selectbox("Relation", rel_f, index=rel_f.index(f.get("relation", "Other")) if f.get("relation") in rel_f else 5, key=f"fr_{i}")
        f["cert"] = c[3].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(f.get("cert", "High")), key=f"fc_{i}")
        if c[4].button("❌", key=f"fd_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ Add Family"): d["family"].append({"name": "", "gender": "Male", "relation": "Other", "cert": "High"}); st.rerun()

    # 施設 / Institutions
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
        lin_tags = ""
        for i, name in enumerate(d["lineage"]):
            if name:
                role = "ism" if i == 0 else "parent" if i == 1 else "grandparent" if i == 2 else "ancestor"
                lin_tags += f'\n        <name @type="{role}">{name}</name>'
        struct_name = f'\n    <persName @type="structured">{lin_tags}\n    </persName>' if lin_tags else ""
        nis_tags = "".join([f'\n    <name @type="nisbah">{n}</name>' for n in d.get("nisbahs", []) if n])
        madh_tag = f'\n    <affiliation @type="madhhab">{d["madhhab"]}</affiliation>' if d.get("madhhab") else ""
        act_tags = "".join([f'\n    <residence><region>{a}</region></residence>' for a in d.get("activities", []) if a])

        xml_output = f"""<person @xml:id="{d['aind_id']}" @source="#original_{d['original_id']}" @cert="{d['name_cert'].lower()}">
    <persName @xml:lang="ar" @type="full">{d['full_name']}</persName>{struct_name}{nis_tags}{madh_tag}
    <death @calendar="hijri" @when-custom="{d['death_year']}" @cert="{d['death_cert'].lower()}">{d['death_year']}</death>{act_tags}
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
