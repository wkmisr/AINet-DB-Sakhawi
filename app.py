import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")

# --- CSS لتحسين القراءة ---
st.markdown("""
    <style>
    textarea {
        font-size: 22px !important;
        line-height: 2.0 !important;
        font-family: 'Amiri', serif;
    }
    .translation-box {
        font-size: 18px;
        line-height: 1.8;
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        color: #2c3e50;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. إدارة الحالة (Session State)
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "death_year": 850,
        "teachers": [], "family": [], "institutions": [], "source_text": "",
        "translation": ""
    }

col1, col2 = st.columns([1, 1.2])

# --- العمود الأول: التحليل ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Sakhawi text here", height=450)
    
    if st.button("✨ Extract, Translate & Generate Data"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("Analyzing text..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    Extract biographical data and return ONLY JSON.
                    Translate metadata (gender, relation) into English.
                    JSON structure:
                    {{
                      "original_id": "string",
                      "name": "Arabic name",
                      "death_year": number,
                      "teachers": [ {{"name": "name", "gender": "Male/Female"}} ],
                      "family": [ {{"name": "name", "gender": "Male/Female", "relation": "Child/Parent/Sibling/Spouse/Cousin/Other"}} ],
                      "institutions": [ {{"name": "name", "relation": "Founder/Instructor/Student/Other"}} ],
                      "japanese_translation": "全文の日本語訳"
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
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.data["translation"]:
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["translation"]}</div>', unsafe_allow_html=True)

# --- العمود الثاني: المحرر ---
with col2:
    st.header("2. Structural Data Editor")
    d = st.session_state.data
    
    c_id1, c_id2 = st.columns(2)
    d["aind_id"] = c_id1.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = c_id2.text_input("Original ID", value=d.get("original_id", ""))
    d["name"] = st.text_input("Person Name (Arabic)", value=d.get("name", ""))
    
    c_y1, c_y2 = st.columns(2)
    try:
        death_val = int(d.get("death_year", 850))
    except:
        death_val = 850
    d["death_year"] = c_y1.number_input("Death (Hijri)", value=death_val)
    c_y2.metric("AD Year", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # --- القوائم (Teachers, Family, Institutions) ---
    for section, label, key_prefix, fields in [
        ("teachers", "🎓 Teachers", "tn", ["name", "gender"]),
        ("family", "👪 Family", "fn", ["name", "gender", "relation"]),
        ("institutions", "🕌 Institutions", "in", ["name", "relation"])
    ]:
        st.subheader(label)
        items = d.get(section, [])
        for i, item in enumerate(items):
            cols = st.columns([3, 2, 2, 1] if len(fields)==3 else [4, 3, 1])
            item["name"] = cols[0].text_input(f"Name", value=item.get("name", ""), key=f"{key_prefix}n_{i}")
            if "gender" in fields:
                item["gender"] = cols[1].selectbox(f"Sex", ["Male", "Female"], index=0 if item.get("gender")=="Male" else 1, key=f"{key_prefix}g_{i}")
            if "relation" in fields:
                opts = ["Parent", "Child", "Sibling", "Spouse", "Cousin", "Other"] if section=="family" else ["Founder", "Instructor", "Student", "Other"]
                idx = opts.index(item["relation"]) if item.get("relation") in opts else 0
                item["relation"] = cols[-2].selectbox(f"Role", opts, index=idx, key=f"{key_prefix}r_{i}")
            if cols[-1].button("❌", key=f"{key_prefix}d_{i}"):
                items.pop(i); st.rerun()
        if st.button(f"＋ Add {section.capitalize()}"):
            new_item = {"name": "", "gender": "Male"} if section=="teachers" else {"name": "", "gender": "Male", "relation": "Other"} if section=="family" else {"name": "", "relation": "Student"}
            items.append(new_item); st.rerun()
        st.divider()
    
# Final XML Output (Focusing on Attributes/@)
    if st.checkbox("Show TEI XML Preview"):
        xml_output = f"""<person xml:id="{d['aind_id']}" source="#original_{d['original_id']}">
    <persName xml:lang="ar" type="full">{d['name']}</persName>
    <death calendar="hijri" when-custom="{d['death_year']}">{d['death_year']}</death>
    <listBibl>
        {" ".join([f'<person sex="{t["gender"]}" role="teacher" name="{t["name"]}"/>' for t in d["teachers"] if t["name"]])}
    </listBibl>
    <listRelation>
        {" ".join([f'<relation sex="{f["gender"]}" type="{f["relation"].lower()}" name="{f["name"]}"/>' for f in d["family"] if f["name"]])}
    </listRelation>
    <listOrg>
        {" ".join([f'<orgName ref="{ins["relation"].lower()}" name="{ins["name"]}"/>' for ins in d["institutions"] if ins["name"]])}
    </listOrg>
    <note type="description">
{d['source_text']}
    </note>
</person>"""
        st.code(xml_output, language="xml")
