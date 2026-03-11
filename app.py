import streamlit as st
import google.generativeai as genai
import json

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. 法学派マスター (Auto-ID用) ---
MADHHAB_MASTER = {
    "Hanafi": "Q160851", "حنفي": "Q160851",
    "Maliki": "Q48221", "مالكي": "Q48221",
    "Shafii": "Q82245", "شافعي": "Q82245",
    "Hanbali": "Q191314", "حنبلي": "Q191314"
}

def get_madhhab_id(name):
    if not name: return ""
    for key, val in MADHHAB_MASTER.items():
        if key.lower() in name.lower(): return val
    return ""

# --- 3. セッション状態の初期化 ---
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

# --- 4. UIレイアウト ---
st.title("🌙 AINet-DB Editor Pro (Full TEI Edition)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新のGeminiで全項目を抽出中..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    prompt = f"""
                    Extract biographical data into JSON.
                    【Rules】
                    1. original_id: Extract the number between ### and #.
                    2. Names: full_name, name_only.
                    3. IDs: Person: TMP-P-xxxx, Inst: TMP-O-xxxx, Location: TMP-L-xxxx.
                    4. Madhhab: Hanafi, Maliki, Shafi'i, or Hanbali.
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().strip("```json").strip()
                    res_json = json.loads(res_text)
                    
                    # 法学派IDの自動補完
                    m = res_json.get("madhhab", {})
                    if not m.get("id"):
                        m["id"] = get_madhhab_id(m.get("lat", "")) or get_madhhab_id(m.get("ar", ""))
                    res_json["madhhab"] = m
                    
                    d.update(res_json)
                    st.success("解析成功！")
                    st.rerun()
                except Exception as e: st.error(f"解析エラー: {e}")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語訳")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 基本情報（属性には @ を付与）
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id (Person ID)", d["aind_id"])
    d["original_id"] = c2.text_input("@source (Source ID)", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin IJMES)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    s_opts = ["Male", "Female", "Unknown"]
    d["sex"] = c3.selectbox("@sex", s_opts, index=s_opts.index(d.get("sex", "Male")) if d.get("sex") in s_opts else 2)
    c_opts = ["High", "Medium", "Low"]
    d["certainty"] = c4.selectbox("@cert", c_opts, index=c_opts.index(d.get("certainty", "High")) if d.get("certainty") in c_opts else 0)

    # --- ⚖️ 法学派 ---
    st.markdown("### ⚖️ 法学派 (affiliation)")
    m_cols = st.columns([1, 1, 1])
    m_data = d.get("madhhab", {"ar": "", "lat": "", "id": ""})
    m_data["ar"] = m_cols[0].text_input("Ar Name", m_data.get("ar", ""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Lat Name", m_data.get("lat", ""), key="m_lat")
    m_data["id"] = m_cols[2].text_input("@ref (WD ID)", m_data.get("id", ""), key="m_id")
    d["madhhab"] = m_data

    # --- 📝 ニスバ ---
    st.markdown("### 📝 ニスバ (Nisbahs)")
    for i, nis in enumerate(d.get("nisbahs", [])):
        n_cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = n_cols[0].text_input(f"Ar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = n_cols[1].text_input(f"Lat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = n_cols[2].text_input(f"@ref_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed", placeholder="WD ID")
        if n_cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # --- 📍 活動拠点 ---
    st.markdown("### 📍 活動拠点 (Activities)")
    for i, act in enumerate(d.get("activities", [])):
        a_cols = st.columns([2, 2, 1.2, 0.4])
        act["place_ar"] = a_cols[0].text_input(f"AAr_{i}", act.get("place_ar",""), key=f"aar_{i}", label_visibility="collapsed")
        act["place_lat"] = a_cols[1].text_input(f"ALat_{i}", act.get("place_lat",""), key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = a_cols[2].text_input(f"@ref_{i}", act.get("id", "TMP-L-"), key=f"aid_{i}", label_visibility="collapsed")
        if a_cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ 活動拠点追加"): d["activities"].append({"place_ar":"","place_lat":"","id":"TMP-L-"}); st.rerun()

    # --- 👥 家族関係 ---
    st.markdown("### 👥 家族関係 (Family)")
    for i, f in enumerate(d.get("family", [])):
        f_cols = st.columns([2, 1, 1.2, 0.4])
        f["name"] = f_cols[0].text_input(f"FName_{i}", f.get("name",""), key=f"fname_{i}", label_visibility="collapsed")
        f["relation"] = f_cols[1].text_input(f"Rel_{i}", f.get("relation",""), key=f"frel_{i}", label_visibility="collapsed")
        f["id"] = f_cols[2].text_input(f"@ref_{i}", f.get("id", "TMP-P-"), key=f"fid_{i}", label_visibility="collapsed")
        if f_cols[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ 家族追加"): d["family"].append({"name":"","relation":"","id":"TMP-P-"}); st.rerun()

    # --- 🎓 Teachers ---
    st.divider()
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        t_cols = st.columns([3, 2, 0.5])
        t["name"] = t_cols[0].text_input(f"Teacher Name {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = t_cols[1].text_input(f"@ref {i}", t.get("id", "TMP-P-"), key=f"tid_{i}")
        if t_cols[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()

    # --- 🕌 Institutions ---
    st.divider()
    st.subheader("🕌 Institutions")
    for i, inst in enumerate(d.get("institutions", [])):
        i_cols = st.columns([3, 2, 0.5])
        inst["name"] = i_cols[0].text_input(f"Inst Name {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = i_cols[1].text_input(f"@ref {i}", inst.get("id", "TMP-O-"), key=f"iid_{i}")
        if i_cols[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":"TMP-O-"}); st.rerun()

    # --- 3. XML Export ---
    st.divider()
    st.header("3. XML Export")
    
    xml_str = f"""<person @xml:id="{d['aind_id']}" @sex="{d['sex']}" @cert="{d['certainty']}" @source="#source_{d['original_id']}">
    <persName @type="full" @xml:lang="ar">{d['full_name']}</persName>
    <persName @type="name_only" @xml:lang="ar">{d['name_only']}</persName>
    <persName @type="ijmes" @xml:lang="lat">{d['full_name_lat']}</persName>
    <affiliation @type="madhhab" @ref="wd:{d['madhhab'].get('id','')}">
        <desc @xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
        <desc @xml:lang="lat">{d['madhhab'].get('lat','')}</desc>
    </affiliation>
    <listRelation>
"""
    for f in d.get("family", []): xml_str += f'        <relation @name="{f.get("relation")}" @active="{f.get("id")}" @passive="#{d["aind_id"]}"/>\n'
    for t in d.get("teachers", []): xml_str += f'        <relation @name="teacher" @active="{t.get("id")}" @passive="#{d["aind_id"]}"/>\n'
    xml_str += "    </listRelation>\n"
    for inst in d.get("institutions", []): xml_str += f'    <affiliation @type="institution" @ref="#{inst.get("id")}">{inst.get("name")}</affiliation>\n'
    xml_str += "</person>"

    st.code(xml_str, language="xml")
    st.download_button("📥 TEI XMLダウンロード", data=xml_str, file_name=f"{d['aind_id']}.xml")
