import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. セッション状態の初期化（全項目を定義） ---
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
st.title("🌙 AINet-DB Editor (Gemini 2.0 Flash / TEI Pro)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=500)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新のGeminiモデルで全項目を抽出中..."):
                try:
                    # 404対策: 2026年現在の推奨モデル名 'models/gemini-2.0-flash' を使用
                    model = genai.GenerativeModel('models/gemini-2.0-flash')
                    
                    prompt = f"""
                    You are an expert historian. Analyze the Arabic text and extract data into JSON.
                    【JSON Schema】
                    {{
                        "original_id": "Number between ### and #",
                        "full_name": "Full Arabic name",
                        "name_only": "Name without nisbahs",
                        "full_name_lat": "IJMES Transcription",
                        "sex": "Male/Female/Unknown",
                        "certainty": "High/Medium/Low",
                        "madhhab": {{"ar": "", "lat": "", "id": "Wikidata ID"}},
                        "nisbahs": [ {{"ar": "", "lat": "", "id": ""}} ],
                        "activities": [ {{"place_ar": "", "place_lat": "", "id": "TMP-L-xxxx"}} ],
                        "family": [ {{"name": "", "relation": "", "id": "TMP-P-xxxx"}} ],
                        "teachers": [ {{"name": "", "id": "TMP-P-xxxx"}} ],
                        "institutions": [ {{"name": "", "id": "TMP-O-xxxx"}} ],
                        "japanese_translation": "Brief summary in Japanese"
                    }}
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    # JSON抽出の堅牢化
                    json_str = re.search(r"\{.*\}", response.text, re.DOTALL).group()
                    d.update(json.loads(json_str))
                    st.success("解析成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"接続エラー: {e}\nモデル名を 'models/gemini-1.5-flash-latest' 等に書き換えて試してください。")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語要約")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性にはTEIの流儀に基づき @ を表示
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("@sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("@cert", ["High", "Medium", "Low"], index=0)

    # --- ⚖️ 法学派 ---
    st.markdown("### ⚖️ 法学派 (affiliation)")
    m_cols = st.columns([1, 1, 1])
    d["madhhab"]["ar"] = m_cols[0].text_input("Ar", d["madhhab"].get("ar",""), key="m_ar")
    d["madhhab"]["lat"] = m_cols[1].text_input("Lat", d["madhhab"].get("lat",""), key="m_lat")
    d["madhhab"]["id"] = m_cols[2].text_input("@ref (WD ID)", d["madhhab"].get("id",""), key="m_id")

    # --- 📝 ニスバ / 📍 活動拠点 / 👥 家族 ---
    for title, key, f1, f2 in [("📝 ニスバ", "nisbahs", "ar", "lat"), 
                               ("📍 活動拠点", "activities", "place_ar", "place_lat"), 
                               ("👥 家族関係", "family", "name", "relation")]:
        st.markdown(f"### {title}")
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns([2, 2, 1.2, 0.4])
            item[f1] = cols[0].text_input(f"{f1}_{i}", item.get(f1,""), key=f"{key}1_{i}", label_visibility="collapsed")
            item[f2] = cols[1].text_input(f"{f2}_{i}", item.get(f2,""), key=f"{key}2_{i}", label_visibility="collapsed")
            item["id"] = cols[2].text_input(f"id_{i}", item.get("id",""), key=f"{key}id_{i}", label_visibility="collapsed")
            if cols[3].button("❌", key=f"{key}del_{i}"): d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加"): d[key].append({f1:"", f2:"", "id":""}); st.rerun()

    # --- 🎓 師匠 & 🕌 施設 ---
    st.divider()
    c_t, c_i = st.columns(2)
    with c_t:
        st.subheader("🎓 Teachers")
        for i, t in enumerate(d.get("teachers", [])):
            cols = st.columns([3, 2, 0.5])
            t["name"] = cols[0].text_input(f"TN_{i}", t.get("name",""), key=f"tn_{i}", label_visibility="collapsed")
            t["id"] = cols[1].text_input(f"TID_{i}", t.get("id","TMP-P-"), key=f"tid_{i}", label_visibility="collapsed")
            if cols[2].button("❌", key=f"td_{i}"): d["teachers"].pop(i); st.rerun()
        if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()

    with c_i:
        st.subheader("🕌 Institutions")
        for i, inst in enumerate(d.get("institutions", [])):
            cols = st.columns([3, 2, 0.5])
            inst["name"] = cols[0].text_input(f"IN_{i}", inst.get("name",""), key=f"in_{i}", label_visibility="collapsed")
            inst["id"] = cols[1].text_input(f"IID_{i}", inst.get("id","TMP-O-"), key=f"iid_{i}", label_visibility="collapsed")
            if cols[2].button("❌", key=f"id_{i}"): d["institutions"].pop(i); st.rerun()
        if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":"TMP-O-"}); st.rerun()

    # --- 3. XML Export ---
    st.divider()
    st.header("3. XML Export")
    
    xml_str = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <persName type="name_only" xml:lang="ar">{d['name_only']}</persName>
    <persName type="ijmes" xml:lang="lat">{d['full_name_lat']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">
        <desc xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
        <desc xml:lang="lat">{d['madhhab'].get('lat','')}</desc>
    </affiliation>
    <listRelation>
"""
    for f in d.get("family", []): xml_str += f'        <relation name="{f.get("relation")}" active="{f.get("id")}" passive="#{d["aind_id"]}"/>\n'
    for t in d.get("teachers", []): xml_str += f'        <relation name="teacher" active="{t.get("id")}" passive="#{d["aind_id"]}"/>\n'
    xml_str += "    </listRelation>\n"
    for inst in d.get("institutions", []): xml_str += f'    <affiliation type="institution" ref="#{inst.get("id")}">{inst.get("name")}</affiliation>\n'
    xml_str += "</person>"

    st.code(xml_str, language="xml")
    st.download_button("📥 TEI XML保存", data=xml_str, file_name=f"{d['aind_id']}.xml", mime="application/xml")
