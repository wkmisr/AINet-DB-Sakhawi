import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 & モデル自動検知 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m]
        return genai.GenerativeModel(flash_models[0] if flash_models else models[0])
    except:
        return genai.GenerativeModel('models/gemini-1.5-flash')

def convert_h_to_g(h_year):
    try:
        h_clean = re.sub(r"\D", "", str(h_year))
        if not h_clean: return ""
        h = int(h_clean)
        return int(h * 0.97 + 622)
    except:
        return ""

st.set_page_config(page_title="AINet-DB Pro (Bilingual Translation)", layout="wide")

# --- 2. データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "birth_h": "", "birth_g": "", "death_h": "", "death_g": "",
        "madhhab": {"lat": "Unknown / Other", "id": ""}, 
        "nisbahs": [], "activities": [], "teachers": [], "institutions": [], "family": [], 
        "source_text": "", "translation_jp": "", "translation_en": ""
    }
d = st.session_state.data

# --- 3. UI: 史料解析エリア ---
st.title("🌙 AINet-DB Researcher Pro")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & Bilingual Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("🚀 精密解析（日英翻訳・外部ID）"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("日英翻訳とIDを探索中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    You are a professional historian of Islamic studies. Extract data into JSON.
                    
                    【IMPORTANT: Translation】
                    - translation_jp: Accurate academic Japanese translation.
                    - translation_en: Accurate academic English translation.
                    
                    【IMPORTANT: ID SEARCH】
                    - Search and provide REAL IDs.
                    - Places: GeoNames IDs. Institutions: Wikidata IDs.
                    
                    JSON Structure:
                    {{
                        "original_id": "", "full_name": "", "name_only": "", 
                        "birth_h": "", "death_h": "", "madhhab_name": "",
                        "nisbahs": [{{ "ar": "", "lat": "", "id": "TMP-N-0000" }}],
                        "activities": [{{ "place_ar": "", "place_lat": "", "id": "GeoNames_ID" }}],
                        "teachers": [{{ "name": "", "id": "TMP-P-XXXXX", "subject": "", "subject_id": "TMP-S-XXXXX" }}],
                        "institutions": [{{ "name": "", "id": "Wikidata_ID" }}],
                        "translation_jp": "", "translation_en": ""
                    }}
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                    if json_match:
                        res_json = json.loads(json_match.group())
                        res_json["birth_g"] = convert_h_to_g(res_json.get("birth_h", ""))
                        res_json["death_g"] = convert_h_to_g(res_json.get("death_h", ""))
                        d.update(res_json)
                        st.success("解析完了")
                        st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    # 翻訳結果の表示
    if d.get("translation_jp") or d.get("translation_en"):
        t_tab1, t_tab2 = st.tabs(["🇯🇵 日本語訳", "🇺🇸 English"])
        with t_tab1: st.info(d["translation_jp"])
        with t_tab2: st.info(d["translation_en"])

# --- 4. UI: エディタエリア ---
with col2:
    st.header("2. Metadata Editor")
    
    # 基本情報
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    d["full_name"] = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"] = st.text_input("persName (Ism/Father/GF)", d["name_only"])

    # 生没年
    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    d["birth_g"] = dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]))
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    d["death_g"] = dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]))

    # Madhhab 連携
    m_col1, m_col2 = st.columns([2, 1])
    selected_m = m_col1.selectbox("⚖️ Madhhab", options=list(MADHHAB_DATA.keys()), 
                                  index=list(MADHHAB_DATA.keys()).index(d["madhhab"]["lat"]) if d["madhhab"]["lat"] in MADHHAB_DATA else 4)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}
    m_col2.text_input("Wikidata ID", d["madhhab"]["id"], disabled=True)

    # Teachers & Subjects (Triple)
    st.divider()
    st.subheader("🎓 Teachers & Subjects")
    for i, item in enumerate(d.get("teachers", [])):
        r1 = st.columns([1, 1, 1, 1, 0.3])
        item["name"] = r1[0].text_input("師匠名", item.get("name"), key=f"t_n_{i}")
        item["id"] = r1[1].text_input("師匠ID", item.get("id", "TMP-P-XXXXX"), key=f"t_i_{i}")
        item["subject"] = r1[2].text_input("内容", item.get("subject", ""), key=f"t_s_{i}")
        item["subject_id"] = r1[3].text_input("内容ID", item.get("subject_id", "TMP-S-XXXXX"), key=f"t_si_{i}")
        if r1[4].button("❌", key=f"t_d_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ 師匠追加"): d["teachers"].append({"name":"","id":"TMP-P-XXXXX", "subject":"", "subject_id":"TMP-S-XXXXX"}); st.rerun()

    # その他項目
    sections = [("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"], "TMP-N-0000"),
                ("📍 Activities", "activities", ["place_ar", "place_lat", "id"], "TMP-L-XXXXX"),
                ("👥 Family", "family", ["name", "relation", "id"], "TMP-P-XXXXX"),
                ("🕌 Institutions", "institutions", ["name", "id"], "TMP-O-XXXXX")]

    for title, key, fields, def_id in sections:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                val = item.get(f, def_id if f=="id" else "")
                item[f] = cols[j].text_input(f"{f}_{key}_{i}", val, key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"): d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加", key=f"add_{key}"): d[key].append({f: (def_id if f=="id" else "") for f in fields}); st.rerun()

    # --- 5. XML Export ---
    st.divider()
    st.header("3. TEI-XML Export")
    
    def fr(rid): # format_ref
        if not rid: return ""
        if rid.startswith("TMP-"): return f"#{rid}"
        if rid.startswith("Q"): return f"wd:{rid}"
        if rid.isdigit(): return f"gn:{rid}"
        return rid

    xml_str = f"""<person xml:id="{d['aind_id']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <persName type="name_only" xml:lang="ar">{d['name_only']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab']['id']}">{d['madhhab']['lat']}</affiliation>
    <listRelation>\n"""
    for t in d.get("teachers", []):
        xml_str += f'        <relation name="teacher" active="{fr(t.get("id"))}" passive="#{d["aind_id"]}">\n'
        xml_str += f'            <desc ref="{fr(t.get("subject_id"))}">{t.get("subject")}</desc>\n'
        xml_str += f'        </relation>\n'
    xml_str += '    </listRelation>\n'
    # ... 中略（Nisbah, Activities 等も同様に fr() 関数を通して追加）...
    xml_str += f"    <note type='translation' xml:lang='ja'>{d['translation_jp']}</note>\n"
    xml_str += f"    <note type='translation' xml:lang='en'>{d['translation_en']}</note>\n"
    xml_str += "</person>"

    st.code(xml_str, language="xml")
