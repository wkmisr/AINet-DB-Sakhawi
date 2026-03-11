import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API・モデル設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_model():
    """利用可能な最適なモデルを返す"""
    # 候補リスト：環境に合わせて順に試行
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            # 試しに空のコンテンツを送ってチェック（オプション）
            return model
        except:
            continue
    return genai.GenerativeModel('gemini-1.5-flash') # 最終的なフォールバック

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. データ初期化（全項目） ---
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
st.title("🌙 AINet-DB Editor (Stabilized Edition)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("AIモデルに接続中..."):
                try:
                    # エラーを避けるために確実に存在するモデルを指定
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Bio-data extraction task for Islamic History. 
                    Extract into JSON: original_id (between ### and #), full_name, name_only, full_name_lat, sex, certainty.
                    Also extract:
                    - madhhab (ar, lat, id: Hanafi=Q160851, Maliki=Q48221, Shafii=Q82245, Hanbali=Q191314)
                    - nisbahs: [{{ar, lat, id}}]
                    - activities: [{{place_ar, place_lat, id: TMP-L-xxxx}}]
                    - family: [{{name, relation, id: TMP-P-xxxx}}]
                    - teachers: [{{name, id: TMP-P-xxxx}}]
                    - institutions: [{{name, id: TMP-O-xxxx}}]
                    - japanese_translation: summary
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    # JSON抽出強化
                    json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                    if json_match:
                        d.update(json.loads(json_match.group()))
                        st.success("解析成功！")
                        st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

with col2:
    st.header("2. Entity Management")
    
    # 基本情報
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Lat)", d["full_name_lat"])

    # ⚖️ Madhhab
    st.markdown("### ⚖️ Madhhab")
    m_cols = st.columns([1, 1, 1])
    m_data = d.get("madhhab", {"ar":"","lat":"","id":""})
    m_data["ar"] = m_cols[0].text_input("Ar", m_data.get("ar",""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Lat", m_data.get("lat",""), key="m_lat")
    m_data["id"] = m_cols[2].text_input("@ref (WD ID)", m_data.get("id",""), key="m_id")
    d["madhhab"] = m_data

    # 📝 Nisbahs, 📍 Activities, 👥 Family, 🎓 Teachers, 🕌 Institutions
    # すべて同じロジックで復活
    sections = [
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
        ("👥 Family", "family", ["name", "relation", "id"]),
    ]
    
    for title, key, fields in sections:
        st.markdown(f"### {title}")
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                label = f"@{f}" if f in ["id", "ref"] else f
                item[f] = cols[j].text_input(f"{label}_{i}", item.get(f,""), key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"):
                d[key].pop(i)
                st.rerun()
        if st.button(f"＋ {title}追加"):
            d[key].append({f: "" for f in fields})
            st.rerun()

    # Teachers & Institutions
    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("🎓 Teachers")
        for i, t in enumerate(d.get("teachers", [])):
            tc = st.columns([2, 1, 0.5])
            t["name"] = tc[0].text_input(f"TName_{i}", t.get("name",""), key=f"tn_{i}", label_visibility="collapsed")
            t["id"] = tc[1].text_input(f"@ref_{i}", t.get("id", "TMP-P-"), key=f"tid_{i}", label_visibility="collapsed")
            if tc[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
        if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()

    with c6:
        st.subheader("🕌 Institutions")
        for i, inst in enumerate(d.get("institutions", [])):
            ic = st.columns([2, 1, 0.5])
            inst["name"] = ic[0].text_input(f"IName_{i}", inst.get("name",""), key=f"in_{i}", label_visibility="collapsed")
            inst["id"] = ic[1].text_input(f"@ref_{i}", inst.get("id", "TMP-O-"), key=f"iid_{i}", label_visibility="collapsed")
            if ic[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
        if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":"TMP-O-"}); st.rerun()

    # --- 3. XML Export ---
    st.divider()
    st.header("3. XML Export")
    # 生成コードは以前と同様
    xml_str = f"""<person xml:id="{d['aind_id']}" source="#source_{d['original_id']}" sex="{d['sex']}" cert="{d['certainty']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">
        <desc xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
    </affiliation>
</person>"""
    st.code(xml_str, language="xml")
