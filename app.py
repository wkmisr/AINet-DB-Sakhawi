import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. セッション状態（全項目） ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "madhhab": {"ar": "", "lat": "", "id": ""}, 
        "nisbahs": [], "activities": [], "teachers": [], "institutions": [], "family": [], 
        "source_text": "", "japanese_translation": ""
    }

d = st.session_state.data

# --- 3. UI ---
st.title("🌙 AINet-DB Editor (Full TEI & Extraction)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=500)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新モデル（2.0-flash-exp）で解析中..."):
                try:
                    # エラーメッセージに従い、2026年時点で確実に動作する最新名称に修正
                    # もしこれでも404が出る場合は 'models/gemini-1.5-flash-latest' に書き換えてください
                    model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
                    
                    prompt = f"""
                    You are a professional historian. Extract biographical data into JSON.
                    【Fields to Extract】
                    - original_id: Number between ### and #
                    - full_name, name_only, full_name_lat
                    - sex (Male/Female), certainty (High/Medium/Low)
                    - madhhab: {{ar, lat, id: Hanafi=Q160851, Maliki=Q48221, Shafii=Q82245, Hanbali=Q191314}}
                    - nisbahs: [{{ar, lat, id}}]
                    - activities: [{{place_ar, place_lat, id: TMP-L-xxxx}}]
                    - family: [{{name, relation, id: TMP-P-xxxx}}]
                    - teachers: [{{name, id: TMP-P-xxxx}}]
                    - institutions: [{{name, id: TMP-O-xxxx}}]
                    - japanese_translation: concise summary
                    
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    json_str = re.search(r"\{.*\}", response.text, re.DOTALL).group()
                    d.update(json.loads(json_str))
                    st.success("解析完了！全項目を更新しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"接続エラー: {e}")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語要約")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性ラベル（@付与）
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("@sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("@cert", ["High", "Medium", "Low"], index=0)

    # --- 各セクション ---
    st.markdown("### ⚖️ Madhhab")
    m_cols = st.columns(3)
    d["madhhab"]["ar"] = m_cols[0].text_input("Ar", d["madhhab"].get("ar",""), key="m_ar")
    d["madhhab"]["lat"] = m_cols[1].text_input("Lat", d["madhhab"].get("lat",""), key="m_lat")
    d["madhhab"]["id"] = m_cols[2].text_input("@ref", d["madhhab"].get("id",""), key="m_id")

    # 抽出漏れを指摘された全項目
    sections = [
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
        ("👥 Family", "family", ["name", "relation", "id"]),
        ("🎓 Teachers", "teachers", ["name", "id"]),
        ("🕌 Institutions", "institutions", ["name", "id"])
    ]

    for title, key, fields in sections:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                label = f"@{f}" if f in ["id", "ref"] else f
                item[f] = cols[j].text_input(f"{label}_{key}_{i}", item.get(f,""), key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"):
                d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加", key=f"add_{key}"):
            d[key].append({f: "" for f in fields}); st.rerun()

    # --- 3. XML Export ---
    st.divider()
    st.header("3. XML Export")
    
    xml_str = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <persName type="name_only" xml:lang="ar">{d['name_only']}</persName>
    <persName type="ijmes" xml:lang="lat">{d['full_name_lat']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">
        <desc xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
    </affiliation>
    <listRelation>
"""
    for f in d.get("family", []): xml_str += f'        <relation name="{f.get("relation")}" active="{f.get("id")}" passive="#{d["aind_id"]}"/>\n'
    for t in d.get("teachers", []): xml_str += f'        <relation name="teacher" active="{t.get("id")}" passive="#{d["aind_id"]}"/>\n'
    xml_str += "    </listRelation>\n"
    for inst in d.get("institutions", []): xml_str += f'    <affiliation type="institution" ref="#{inst.get("id")}">{inst.get("name")}</affiliation>\n'
    xml_str += "</person>"

    st.code(xml_str, language="xml")
    st.download_button("📥 XML保存", data=xml_str, file_name=f"{d['aind_id']}.xml", mime="application/xml")
