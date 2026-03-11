import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. システムリセット (db_v12) ---
if 'db_v12' not in st.session_state:
    st.session_state.clear()
    st.session_state.db_v12 = {
        "aind_id": "AIND-D00000", "original_id": "", 
        "full_name": "", "name_only": "", "full_name_lat": "",
        "birth_h": "", "birth_g": "", "death_h": "", "death_g": "",
        "activities": [{"ar": "", "type": "reside", "id": ""}], 
        "teachers": [{"name": "", "id": "", "subject": "", "subject_id": ""}], 
        "students": [{"name": "", "id": "", "subject": "", "subject_id": ""}], 
        "source_text": "", "translation_jp": "", "translation_en": ""
    }
    st.rerun()

d = st.session_state.db_v12

# --- 2. API & Model Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Pro v12", layout="wide")

# --- 3. UI: Main Header ---
st.title("🌙 AINet-DB Researcher Pro v12")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("🚀 精密解析"):
        with st.spinner("詳細データを解析中..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                # エラー回避のため、プロンプト内のJSON構造に二重括弧 {{ }} を使用
                prompt = f"""Extract biographical data into JSON.
                - activities: include 'type' (study, buried, visit, reside).
                - students: list with name, id, subject, subject_id.
                - names: separate full_name, name_only, and latin (full_name_lat).
                
                Expected JSON Structure:
                {{
                    "full_name":"", "name_only":"", "full_name_lat":"",
                    "birth_h":"", "death_h":"",
                    "activities":[{"ar":"", "type":"", "id":""}],
                    "students":[{"name":"","id":"","subject":"","subject_id":""}],
                    "translation_jp":"", "translation_en":""
                }}
                
                Text: {source_input}"""
                
                response = model.generate_content(prompt)
                json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    d.update(parsed_data)
                    d["source_text"] = source_input
                    st.rerun()
            except Exception as e:
                st.error(f"解析エラー: {e}")

    if d.get("translation_jp"):
        st.subheader("Bilingual Translation")
        st.info(f"【日】{d['translation_jp']}")
        st.info(f"【英】{d['translation_en']}")

with col2:
    st.header("2. Metadata Editor")
    
    # --- Basic Info (詳細版) ---
    st.subheader("👤 Basic Information")
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("Person ID (XML:ID)", d["aind_id"], key="v12_id")
    d["original_id"] = c2.text_input("Original Source ID", d["original_id"], key="v12_oid")
    
    d["full_name"] = st.text_input("Full Name (Arabic)", d["full_name"], key="v12_fn")
    d["name_only"] = st.text_input("Name Only (Arabic)", d["name_only"], key="v12_no")
    d["full_name_lat"] = st.text_input("Latin Name (Transliteration)", d["full_name_lat"], key="v12_lat")

    c3, c4, c5, c6 = st.columns(4)
    d["birth_h"] = c3.text_input("Birth (H)", d["birth_h"], key="v12_bh")
    d["birth_g"] = c4.text_input("Birth (G)", d["birth_g"], key="v12_bg")
    d["death_h"] = c5.text_input("Death (H)", d["death_h"], key="v12_dh")
    d["death_g"] = c6.text_input("Death (G)", d["death_g"], key="v12_dg")

    st.divider()

    # --- 📍 Activities (タイプ欄あり) ---
    st.subheader("📍 Activities (活動拠点)")
    for i, item in enumerate(d["activities"]):
        r = st.columns([1.2, 1, 1, 0.3])
        item["ar"] = r[0].text_input("地名", item.get("ar", ""), key=f"v12_a_ar_{i}")
        item["type"] = r[1].text_input("タイプ", item.get("type", ""), key=f"v12_a_tp_{i}")
        item["id"] = r[2].text_input("ID", item.get("id", ""), key=f"v12_a_id_{i}")
        if r[3].button("❌", key=f"v12_a_del_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ Activity追加"): d["activities"].append({"ar":"","type":"","id":""}); st.rerun()

    st.divider()

    # --- 🎓 Teachers ---
    st.subheader("🎓 Teachers (師匠)")
    for i, item in enumerate(d["teachers"]):
        r = st.columns([1, 1, 1, 1, 0.3])
        item["name"] = r[0].text_input("師匠名", item.get("name", ""), key=f"v12_t_n_{i}")
        item["id"] = r[1].text_input("師ID", item.get("id", ""), key=f"v12_t_i_{i}")
        item["subject"] = r[2].text_input("内容", item.get("subject", ""), key=f"v12_t_s_{i}")
        item["subject_id"] = r[3].text_input("内容ID", item.get("subject_id", ""), key=f"v12_t_si_{i}")
        if r[4].button("❌", key=f"v12_t_del_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ 師匠追加"): d["teachers"].append({"name":"","id":"","subject":"","subject_id":""}); st.rerun()

    st.divider()

    # --- 🧑‍🎓 Students ---
    st.subheader("🧑‍🎓 Students (弟子)")
    for i, item in enumerate(d["students"]):
        r = st.columns([1, 1, 1, 1, 0.3])
        item["name"] = r[0].text_input("弟子名", item.get("name", ""), key=f"v12_s_n_{i}")
        item["id"] = r[1].text_input("弟子ID", item.get("id", ""), key=f"v12_s_i_{i}")
        item["subject"] = r[2].text_input("内容", item.get("subject", ""), key=f"v12_s_s_{i}")
        item["subject_id"] = r[3].text_input("内容ID", item.get("subject_id", ""), key=f"v12_s_si_{i}")
        if r[4].button("❌", key=f"v12_s_del_{i}"): d["students"].pop(i); st.rerun()
    if st.button("＋ 弟子追加"): d["students"].append({"name":"","id":"","subject":"","subject_id":""}); st.rerun()

    # --- 5. XML Export ---
    st.divider()
    st.header("3. TEI-XML Export")
    
    xml = f'<person xml:id="{d["aind_id"]}" source="#{d["original_id"]}">\n'
    xml += f'  <persName type="full" xml:lang="ar">{d["full_name"]}</persName>\n'
    xml += f'  <persName type="name_only" xml:lang="ar">{d["name_only"]}</persName>\n'
    xml += f'  <persName type="lat">{d["full_name_lat"]}</persName>\n'
    xml += f'  <birth when-custom="{d["birth_h"]}" when="{d["birth_g"]}"/>\n'
    xml += f'  <death when-custom="{d["death_h"]}" when="{d["death_g"]}"/>\n'
    
    for a in d["activities"]:
        xml += f'  <residence subtype="{a.get("type")}" ref="#{a.get("id")}">{a.get("ar")}</residence>\n'
    
    xml += '  <listRelation>\n'
    for s in d["students"]:
        xml += f'    <relation name="student" active="#{d["aind_id"]}" passive="#{s.get("id")}">\n'
        if s.get("subject"): xml += f'      <desc ref="#{s.get("subject_id")}">{s.get("subject")}</desc>\n'
        xml += '    </relation>\n'
    xml += '  </listRelation>\n</person>'
    
    st.code(xml, language="xml")
