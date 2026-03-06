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
        "lineage": ["", "", ""], # 初期状態で 本人, 父, 祖父 の3枠
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
            with st.spinner("Analyzing and translating..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    Analyze the Arabic text and return ONLY JSON.
                    - full_name: Complete name with all nisbahs.
                    - lineage: A list of names starting from the person, then father, then grandfather, etc. (as many as traceable).
                    - nisbahs: List of nisbahs.
                    - activities: Cities or regions of activity.
                    
                    JSON Format:
                    {{
                      "original_id": "string",
                      "full_name": "Arabic full name", "name_cert": "High/Medium/Low",
                      "lineage": ["person", "father", "grandfather", "great-grandfather"],
                      "nisbahs": ["nis1", "nis2"],
                      "madhhab": "School",
                      "activities": ["City1"],
                      "death_year": number, "death_cert": "High/Medium/Low",
                      "teachers": [ {{"name": "name", "gender": "Male", "cert": "High"}} ],
                      "family": [ {{"name": "name", "gender": "Male", "relation": "Parent", "cert": "High"}} ],
                      "institutions": [ {{"name": "name", "relation": "Student", "cert": "High"}} ],
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

# --- 右カラム：TEI Data Editor ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # ID系
    c_id_1, c_id_2 = st.columns(2)
    d["aind_id"] = c_id_1.text_input("AIND ID (@xml:id)", value=d.get("aind_id", ""))
    d["original_id"] = c_id_2.text_input("Original ID (@source)", value=d.get("original_id", ""))
    
    # フルネーム
    c_full, c_ncert = st.columns([3, 1])
    d["full_name"] = c_full.text_input("Full Name (Complete with Nisbahs)", value=d.get("full_name", ""))
    d["name_cert"] = c_ncert.selectbox("Name Cert (@cert)", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("name_cert", "High")), key="ncert")
    
    # 系譜 (Lineage)
    st.subheader("🧬 Lineage (本人-父-祖父...)")
    for i, name in enumerate(d.get("lineage", [])):
        label = "Person (本人)" if i == 0 else "Father (父)" if i == 1 else "Grandfather (祖父)" if i == 2 else f"Ancestor {i} (祖先)"
        c = st.columns([5, 1])
        d["lineage"][i] = c[0].text_input(label, value=name, key=f"lin_{i}")
        if c[1].button("❌", key=f"lind_{i}"):
            d["lineage"].pop(i); st.rerun()
    if st.button("＋ Add Ancestor"):
        d["lineage"].append(""); st.rerun()

    st.divider()

    # Nisbah & Madhhab
    st.subheader("📝 Attributes")
    d["madhhab"] = st.text_input("Madhhab (School of Law)", value=d.get("madhhab", ""))
    for i, nis in enumerate(d.get("nisbahs", [])):
        c = st.columns([5, 1])
        d["nisbahs"][i] = c[0].text_input(f"Nisbah {i+1}", value=nis, key=f"nis_{i}")
        if c[1].button("❌", key=f"nisd_{i}"):
            d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ Add Nisbah"):
        d["nisbahs"].append(""); st.rerun()

    # Activity Areas
    st.subheader("📍 Activity Areas")
    for i, area in enumerate(d.get("activities", [])):
        c = st.columns([5, 1])
        d["activities"][i] = c[0].text_input(f"Area {i+1}", value=area, key=f"act_{i}")
        if c[1].button("❌", key=f"actd_{i}"):
            d["activities"].pop(i); st.rerun()
    if st.button("＋ Add Activity Area"):
        d["activities"].append(""); st.rerun()

    st.divider()

    # 没年
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    try: death_val = int(d.get("death_year", 850))
    except: death_val = 850
    d["death_year"] = c_death.number_input("Death (Hijri @when-custom)", value=death_val)
    d["death_cert"] = c_dcert.selectbox("Death Cert (@cert)", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("death_cert", "High")), key="dcert")
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    # Teachers, Family, Institutions
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        c = st.columns([3, 1.5, 1.5, 0.5])
        t["name"] = c[0].text_input("Teacher Name", value=t.get("name", ""), key=f"tn_{i}")
        t["gender"] = c[1].selectbox("Sex (@sex)", ["Male", "Female"], index=0 if t.get("gender")=="Male" else 1, key=f"tg_{i}")
        t["cert"] = c[2].selectbox("Cert (@cert)", CERT_OPTIONS, index=CERT_OPTIONS.index(t.get("cert", "High")), key=f"tc_{i}")
        if c[3].button("❌", key=f"td_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Add Teacher"): d["teachers"].append({"name": "", "gender": "Male", "cert": "High"}); st.rerun()

    st.divider()
    
    # --- 最終的な TEI XML 出力 ---
    if st.checkbox("Show Final TEI XML Preview"):
        # 系譜タグの動的生成
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
    <desc @xml:lang="ar">
{d['source_text']}
    </desc>
    <desc @xml:lang="ja">
{d.get('translation', '')}
    </desc>
</person>"""
        st.code(xml_output, language="xml")
