import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. データ構造の完全定義（全ての抽出項目を網羅） ---
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

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Editor (Ultimate Recovery)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=500)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新の安定版モデルへ接続中..."):
                try:
                    # 2026年3月現在、最も互換性が高いモデルIDを指定
                    # models/ プレフィックスを付け、末尾にバージョンを固定
                    model = genai.GenerativeModel('models/gemini-1.5-flash-002')
                    
                    prompt = f"""
                    Extract ALL biographical information from the text into JSON. 
                    Be meticulous. If a field is empty, return [].
                    
                    【Required JSON Structure】
                    {{
                        "original_id": "Number between ### and #",
                        "full_name": "Full Arabic name",
                        "name_only": "Name only (ism)",
                        "full_name_lat": "IJMES Latin transcription",
                        "sex": "Male/Female/Unknown",
                        "certainty": "High/Medium/Low",
                        "madhhab": {{"ar": "", "lat": "", "id": "WD ID"}},
                        "nisbahs": [ {{"ar": "", "lat": "", "id": ""}} ],
                        "activities": [ {{"place_ar": "", "place_lat": "", "id": "TMP-L-xxxx"}} ],
                        "family": [ {{"name": "", "relation": "", "id": "TMP-P-xxxx"}} ],
                        "teachers": [ {{"name": "", "id": "TMP-P-xxxx"}} ],
                        "institutions": [ {{"name": "", "id": "TMP-O-xxxx"}} ],
                        "japanese_translation": "Concise summary in Japanese"
                    }}
                    
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    # JSON部分だけを正規表現で確実に抜き出す
                    json_str = re.search(r"\{.*\}", response.text, re.DOTALL).group()
                    d.update(json.loads(json_str))
                    st.success("解析完了！全ての項目を同期しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"接続エラー: {e}\n(モデルID 'models/gemini-1.5-pro-002' への変更も検討してください)")

    if d.get("japanese_translation"):
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性入力（先生こだわりの @ 表記）
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("@sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("@cert", ["High", "Medium", "Low"], index=0)

    # --- ⚖️ 法学派 / 📝 ニスバ / 📍 活動 / 👥 家族 / 🎓 師匠 / 🕌 施設 ---
    sections = [
        ("⚖️ Madhhab (affiliation)", "madhhab", ["ar", "lat", "id"]),
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
        ("👥 Family Relations", "family", ["name", "relation", "id"]),
        ("🎓 Teachers", "teachers", ["name", "id"]),
        ("🕌 Institutions", "institutions", ["name", "id"])
    ]

    for title, key, fields in sections:
        st.divider()
        st.subheader(title)
        
        if key == "madhhab":
            cols = st.columns(3)
            for j, f in enumerate(fields):
                label = f"@{f}" if f == "id" else f
                d[key][f] = cols[j].text_input(f"{label}_{key}", d[key].get(f,""), key=f"m_{f}")
            continue

        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                label = f"@{f}" if f == "id" else f
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
    <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">
        <desc xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
    </affiliation>
    <listRelation>
"""
    for f in d.get("family", []):
        xml_str += f'        <relation name="{f.get("relation")}" active="{f.get("id")}" passive="#{d["aind_id"]}"/>\n'
    for t in d.get("teachers", []):
        xml_str += f'        <relation name="teacher" active="{t.get("id")}" passive="#{d["aind_id"]}"/>\n'
    xml_str += "    </listRelation>\n"
    for inst in d.get("institutions", []):
        xml_str += f'    <affiliation type="institution" ref="#{inst.get("id")}">{inst.get("name")}</affiliation>\n'
    xml_str += "</person>"

    st.code(xml_str, language="xml")
