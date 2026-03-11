import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. 法学派マスター ---
MADHHAB_MASTER = {
    "Hanafi": "Q160851", "حنفي": "Q160851",
    "Maliki": "Q48221", "مالكي": "Q48221",
    "Shafii": "Q82245", "شافعي": "Q82245",
    "Hanbali": "Q191314", "حنبلي": "Q191314"
}

# --- 3. セッション初期化 ---
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

# --- 4. UI ---
st.title("🌙 AINet-DB Editor Pro (High-Performance Extraction)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("AIが史料を徹底解析中..."):
                try:
                    # モデルは安定版の1.5-flashを使用（2.5は環境により不安定なため）
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # プロンプトの強化：出力形式を厳密に指定
                    prompt = f"""
                    You are a professional historian of Islamic bio-bibliographical traditions. 
                    Analyze the following Arabic text and extract data into a valid JSON object.

                    【Output Schema】
                    {{
                        "original_id": "Number found between ### and #",
                        "full_name": "Full Arabic name including nisbahs",
                        "name_only": "Name without nisbahs",
                        "full_name_lat": "IJMES Latin transcription",
                        "sex": "Male or Female",
                        "certainty": "High, Medium, or Low",
                        "madhhab": {{"ar": "Arabic name", "lat": "Latin name", "id": "Wikidata ID if available"}},
                        "nisbahs": [ {{"ar": "", "lat": "", "id": ""}} ],
                        "activities": [ {{"place_ar": "", "place_lat": "", "id": "TMP-L-xxxx"}} ],
                        "family": [ {{"name": "", "relation": "", "id": "TMP-P-xxxx"}} ],
                        "teachers": [ {{"name": "", "id": "TMP-P-xxxx"}} ],
                        "institutions": [ {{"name": "", "id": "TMP-O-xxxx"}} ],
                        "japanese_translation": "Brief Japanese summary"
                    }}

                    【Extraction Rules】
                    - ID Prefix: Person=TMP-P-, Place=TMP-L-, Institution=TMP-O-
                    - If Madhhab is Maliki, ID is Q48221. Shafii is Q82245. Hanafi is Q160851. Hanbali is Q191314.

                    Text to analyze:
                    {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # JSON抽出のロジックを強化
                    json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                    if json_match:
                        res_json = json.loads(json_match.group())
                        d.update(res_json)
                        st.success("解析成功！項目を更新しました。")
                        st.rerun()
                    else:
                        st.error("AIの応答からJSONが見つかりませんでした。")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語要約")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性管理 (Labels with @ as per TEI notation)
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Lat)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    s_opts = ["Male", "Female", "Unknown"]
    d["sex"] = c3.selectbox("@sex", s_opts, index=s_opts.index(d.get("sex", "Male")) if d.get("sex") in s_opts else 2)
    c_opts = ["High", "Medium", "Low"]
    d["certainty"] = c4.selectbox("@cert", c_opts, index=c_opts.index(d.get("certainty", "High")) if d.get("certainty") in c_opts else 0)

    # --- ⚖️ Madhhab ---
    st.markdown("### ⚖️ Madhhab")
    m_cols = st.columns([1, 1, 1])
    m_data = d.get("madhhab", {"ar":"","lat":"","id":""})
    m_data["ar"] = m_cols[0].text_input("Ar", m_data.get("ar",""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Lat", m_data.get("lat",""), key="m_lat")
    m_data["id"] = m_cols[2].text_input("@ref (WD ID)", m_data.get("id",""), key="m_id")

    # --- 📝 Nisbahs ---
    st.markdown("### 📝 Nisbahs")
    for i, n in enumerate(d.get("nisbahs", [])):
        nc = st.columns([2, 2, 1.2, 0.4])
        n["ar"] = nc[0].text_input(f"Ar_{i}", n.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        n["lat"] = nc[1].text_input(f"Lat_{i}", n.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        n["id"] = nc[2].text_input(f"@ref_{i}", n.get("id",""), key=f"nid_{i}", label_visibility="collapsed")
        if nc[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # --- 📍 Activities ---
    st.markdown("### 📍 Activities")
    for i, a in enumerate(d.get("activities", [])):
        ac = st.columns([2, 2, 1.2, 0.4])
        a["place_ar"] = ac[0].text_input(f"AAr_{i}", a.get("place_ar",""), key=f"aar_{i}", label_visibility="collapsed")
        a["place_lat"] = ac[1].text_input(f"ALat_{i}", a.get("place_lat",""), key=f"alat_{i}", label_visibility="collapsed")
        a["id"] = ac[2].text_input(f"@ref_{i}", a.get("id", "TMP-L-"), key=f"aid_{i}", label_visibility="collapsed")
        if ac[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ 活動拠点追加"): d["activities"].append({"place_ar":"","place_lat":"","id":"TMP-L-"}); st.rerun()

    # --- 👥 Family ---
    st.markdown("### 👥 Family")
    for i, f in enumerate(d.get("family", [])):
        fc = st.columns([2, 1, 1.2, 0.4])
        f["name"] = fc[0].text_input(f"FN_{i}", f.get("name",""), key=f"fn_{i}", label_visibility="collapsed")
        f["relation"] = fc[1].text_input(f"Rel_{i}", f.get("relation",""), key=f"frel_{i}", label_visibility="collapsed")
        f["id"] = fc[2].text_input(f"@ref_{i}", f.get("id", "TMP-P-"), key=f"fid_{i}", label_visibility="collapsed")
        if fc[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ 家族追加"): d["family"].append({"name":"","relation":"","id":"TMP-P-"}); st.rerun()

    # --- 🎓 Teachers ---
    st.divider()
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        tc = st.columns([3, 2, 0.5])
        t["name"] = tc[0].text_input(f"TName {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = tc[1].text_input(f"@ref {i}", t.get("id", "TMP-P-"), key=f"tid_{i}")
        if tc[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()

    # --- 🕌 Institutions ---
    st.divider()
    st.subheader("🕌 Institutions")
    for i, inst in enumerate(d.get("institutions", [])):
        ic = st.columns([3, 2, 0.5])
        inst["name"] = ic[0].text_input(f"IName {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = ic[1].text_input(f"@ref {i}", inst.get("id", "TMP-O-"), key=f"iid_{i}")
        if ic[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
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
    st.download_button("📥 TEI XMLダウンロード", data=xml_str, file_name=f"{d['aind_id']}.xml")
