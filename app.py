import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. セッション状態の初期化（全項目を網羅） ---
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
st.title("🌙 AINet-DB Editor (Gemini 3 Flash / TEI Standard)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("Gemini 3 Flashが全項目を解析中..."):
                try:
                    # 2026年現在の最新モデル名に修正
                    model = genai.GenerativeModel('gemini-3-flash')
                    
                    prompt = f"""
                    You are a specialist in Islamic prosopography. Extract biographical data into JSON.
                    【Fields to Extract】
                    - original_id (number between ### and #)
                    - full_name, name_only, full_name_lat
                    - sex (Male/Female), certainty (High/Medium/Low)
                    - madhhab (ar, lat, id: Hanafi=Q160851, Maliki=Q48221, Shafii=Q82245, Hanbali=Q191314)
                    - nisbahs (ar, lat, id)
                    - activities (place_ar, place_lat, id: TMP-L-xxxx)
                    - family (name, relation, id: TMP-P-xxxx)
                    - teachers (name, id: TMP-P-xxxx)
                    - institutions (name, id: TMP-O-xxxx)
                    - japanese_translation (summary)
                    
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    # JSON部分だけを確実に抽出するガード
                    json_str = re.search(r"\{.*\}", response.text, re.DOTALL).group()
                    res_json = json.loads(json_str)
                    
                    d.update(res_json)
                    st.success("解析成功！全項目を更新しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}。モデル名を 'gemini-2.0-flash' などに変更する必要があるかもしれません。")

    if d.get("japanese_translation"):
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性にはTEIの慣習に従い @ を付けて表示
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    s_opts = ["Male", "Female", "Unknown"]
    d["sex"] = c3.selectbox("@sex", s_opts, index=s_opts.index(d.get("sex", "Male")) if d.get("sex") in s_opts else 2)
    c_opts = ["High", "Medium", "Low"]
    d["certainty"] = c4.selectbox("@cert", c_opts, index=c_opts.index(d.get("certainty", "High")) if d.get("certainty") in c_opts else 0)

    # --- ⚖️ 法学派 ---
    st.markdown("### ⚖️ 法学派 (affiliation)")
    m_cols = st.columns([1, 1, 1])
    m_data = d.get("madhhab", {"ar":"","lat":"","id":""})
    m_data["ar"] = m_cols[0].text_input("Madhhab Ar", m_data.get("ar",""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Madhhab Lat", m_data.get("lat",""), key="m_lat")
    m_data["id"] = m_cols[2].text_input("@ref (WD ID)", m_data.get("id",""), key="m_id")

    # --- 📝 ニスバ ---
    st.markdown("### 📝 ニスバ (Nisbahs)")
    for i, n in enumerate(d.get("nisbahs", [])):
        nc = st.columns([2, 2, 1.2, 0.4])
        n["ar"] = nc[0].text_input(f"NAr_{i}", n.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        n["lat"] = nc[1].text_input(f"NLat_{i}", n.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        n["id"] = nc[2].text_input(f"@ref_{i}", n.get("id",""), key=f"nid_{i}", label_visibility="collapsed")
        if nc[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # --- 📍 活動拠点 ---
    st.markdown("### 📍 活動拠点 (Activities)")
    for i, a in enumerate(d.get("activities", [])):
        ac = st.columns([2, 2, 1.2, 0.4])
        a["place_ar"] = ac[0].text_input(f"AAr_{i}", a.get("place_ar",""), key=f"aar_{i}", label_visibility="collapsed")
        a["place_lat"] = ac[1].text_input(f"ALat_{i}", a.get("place_lat",""), key=f"alat_{i}", label_visibility="collapsed")
        a["id"] = ac[2].text_input(f"@ref_{i}", a.get("id", "TMP-L-"), key=f"aid_{i}", label_visibility="collapsed")
        if ac[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ 活動拠点追加"): d["activities"].append({"place_ar":"","place_lat":"","id":"TMP-L-"}); st.rerun()

    # --- 👥 家族関係 ---
    st.markdown("### 👥 家族関係 (Family)")
    for i, f in enumerate(d.get("family", [])):
        fc = st.columns([2, 1, 1.2, 0.4])
        f["name"] = fc[0].text_input(f"FN_{i}", f.get("name",""), key=f"fn_{i}", label_visibility="collapsed")
        f["relation"] = fc[1].text_input(f"Rel_{i}", f.get("relation",""), key=f"frel_{i}", label_visibility="collapsed")
        f["id"] = fc[2].text_input(f"@ref_{i}", f.get("id", "TMP-P-"), key=f"fid_{i}", label_visibility="collapsed")
        if fc[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ 家族追加"): d["family"].append({"name":"","relation":"","id":"TMP-P-"}); st.rerun()

    # --- 🎓 Teachers & 🕌 Institutions ---
    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("🎓 Teachers")
        for i, t in enumerate(d.get("teachers", [])):
            tc = st.columns([3, 1.5, 0.5])
            t["name"] = tc[0].text_input(f"TName_{i}", t.get("name",""), key=f"tn_{i}", label_visibility="collapsed")
            t["id"] = tc[1].text_input(f"@ref_{i}", t.get("id", "TMP-P-"), key=f"tid_{i}", label_visibility="collapsed")
            if tc[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
        if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()
    
    with c6:
        st.subheader("🕌 Institutions")
        for i, inst in enumerate(d.get("institutions", [])):
            ic = st.columns([3, 1.5, 0.5])
            inst["name"] = ic[0].text_input(f"IName_{i}", inst.get("name",""), key=f"in_{i}", label_visibility="collapsed")
            inst["id"] = ic[1].text_input(f"@ref_{i}", inst.get("id", "TMP-O-"), key=f"iid_{i}", label_visibility="collapsed")
            if ic[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
        if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":"TMP-O-"}); st.rerun()

    # --- 3. XML Export ---
    st.divider()
    st.header("3. XML Export")
    
    # TEI形式のXML生成（属性に@を付けるかどうかは、ファイル規格に従い標準的に出力）
    # ※ XMLファイル内で属性名に@を含めると不正なXMLになるため、標準的な記法で出力します。
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
    st.download_button("📥 XMLファイルを保存", data=xml_str, file_name=f"{d['aind_id']}.xml", mime="application/xml")
