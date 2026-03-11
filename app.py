import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 & モデル自動検知 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    """利用可能な最新モデルを動的に取得"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Flash系を優先（速度と精度のバランス）
        flash_models = [m for m in models if 'flash' in m]
        return genai.GenerativeModel(flash_models[0] if flash_models else models[0])
    except:
        return genai.GenerativeModel('models/gemini-1.5-flash')

def convert_h_to_g(h_year):
    """ヒジュラ暦から西暦への換算"""
    try:
        h_clean = re.sub(r"\D", "", str(h_year))
        if not h_clean: return ""
        h = int(h_clean)
        return int(h * 0.97 + 622)
    except:
        return ""

st.set_page_config(page_title="AINet-DB Pro", layout="wide")

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
        "source_text": "", "full_translation": ""
    }
d = st.session_state.data

# --- 3. UI: 史料解析エリア ---
st.title("🌙 AINet-DB Researcher Pro")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & Deep Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("🚀 精密解析・全訳を実行"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("思考ステップに沿って精密解析中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    Extract biographical data into JSON. Provide a FULL translation.
                    
                    【Rules: Teachers & Subjects】
                    - In 'teachers', extract NOT ONLY the master's name but also the 'subject' (text name or discipline) if mentioned.
                    - e.g., "A learned Fiqh from B" -> teacher: B, subject: Fiqh.
                    - name_only: MUST extract [Ism] + [Father] + [Grandfather] in Arabic.
                    
                    JSON Structure:
                    {{
                        "original_id": "", "full_name": "", "name_only": "", "full_name_lat": "",
                        "sex": "Male/Female", "birth_h": "", "death_h": "",
                        "madhhab_name": "",
                        "nisbahs": [{{ "ar": "", "lat": "", "id": "TMP-N-0000" }}],
                        "activities": [{{ "place_ar": "", "place_lat": "", "id": "TMP-L-XXXXX" }}],
                        "teachers": [{{ "name": "", "id": "TMP-P-XXXXX", "subject": "" }}],
                        "institutions": [{{ "name": "", "id": "TMP-O-XXXXX" }}],
                        "full_translation": ""
                    }}
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                    if json_match:
                        res_json = json.loads(json_match.group())
                        res_json["birth_g"] = convert_h_to_g(res_json.get("birth_h", ""))
                        res_json["death_g"] = convert_h_to_g(res_json.get("death_h", ""))
                        m_name = res_json.get("madhhab_name", "")
                        res_json["madhhab"] = {"lat": "Unknown / Other", "id": ""}
                        for k, v in MADHHAB_DATA.items():
                            if m_name and m_name.lower() in k.lower():
                                res_json["madhhab"] = {"lat": k, "id": v}
                        d.update(res_json)
                        st.success("解析成功")
                        st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("full_translation"):
        st.subheader("🇯🇵 史料全訳")
        st.info(d["full_translation"])

# --- 4. UI: エディタエリア ---
with col2:
    st.header("2. Metadata Editor")
    
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"] = st.text_input("persName (Ism/Father/GF)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin/IJMES)", d["full_name_lat"])

    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    d["birth_g"] = dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]))
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    d["death_g"] = dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]))

    selected_m = st.selectbox("⚖️ Madhhab", options=list(MADHHAB_DATA.keys()), 
                              index=list(MADHHAB_DATA.keys()).index(d["madhhab"]["lat"]) if d["madhhab"]["lat"] in MADHHAB_DATA else 4)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}

    # リスト項目管理
    sections_config = [
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"], "TMP-N-0000"),
        ("📍 Activities (GeoNames)", "activities", ["place_ar", "place_lat", "id"], "TMP-L-00000"),
        ("👥 Family", "family", ["name", "relation", "id"], "TMP-P-00000"),
        ("🎓 Teachers", "teachers", ["name", "id"], "TMP-P-00000"),
        ("🕌 Institutions (Wikidata)", "institutions", ["name", "id"], "TMP-O-00000")
    ]

    for title, key, fields, def_id in sections_config:
        # --- 師匠・学習内容の入力欄 ---
    st.divider()
    st.subheader("🎓 Teachers & Subjects (Triple)")
    for i, item in enumerate(d.get("teachers", [])):
        cols = st.columns([1, 1, 1.5, 0.3])
        item["name"] = cols[0].text_input("師匠名", item.get("name"), key=f"t_name_{i}", label_visibility="collapsed")
        item["id"] = cols[1].text_input("師匠ID", item.get("id", "TMP-P-XXXXX"), key=f"t_id_{i}", label_visibility="collapsed")
        # ここに「学習内容」の列を追加
        item["subject"] = cols[2].text_input("学習内容", item.get("subject", ""), key=f"t_sub_{i}", placeholder="科目名やテキスト名", label_visibility="collapsed")
        if cols[3].button("❌", key=f"t_del_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ 師匠追加"): d["teachers"].append({"name":"","id":"TMP-P-XXXXX", "subject":""}); st.rerun()

    # --- 5. XML Export (TEI 完全版) ---
    st.divider()
    st.header("3. TEI-XML Export")
    
    def format_ref(raw_id):
        if not raw_id: return ""
        if raw_id.startswith("TMP-"): return f"#{raw_id}"
        if raw_id.startswith("Q"): return f"wd:{raw_id}"
        if raw_id.isdigit(): return f"gn:{raw_id}"
        return raw_id

    xml_str = f"""<person @xml:id="{d['aind_id']}" @sex="{d['sex']}" @cert="{d['certainty']}" @source="#source_{d['original_id']}">
    <persName @type="full" @xml:lang="ar">{d['full_name']}</persName>
    <persName @type="name_only" @xml:lang="ar">{d['name_only']}</persName>
    <persName @type="ijmes" @xml:lang="lat">{d['full_name_lat']}</persName>\n"""
    for n in d.get("nisbahs", []):
        xml_str += f'    <persName @type="nisba" @xml:lang="ar" @ref="{format_ref(n.get("id"))}">{n.get("ar")}</persName>\n'
    xml_str += f"""    <birth @when-custom="{d['birth_h']}" @datingMethod="#islamic" when="{d['birth_g']}"/>
    <death @when-custom="{d['death_h']}" @datingMethod="#islamic" @when="{d['death_g']}"/>
    <affiliation @type="madhhab" @ref="wd:{d['madhhab']['id']}">{d['madhhab']['lat']}</affiliation>
    <listRelation>\n"""
    for f in d.get("family", []):
        xml_str += f'        <relation @name="{f.get("relation")}" @active="{format_ref(f.get("id"))}" @passive="#{d["aind_id"]}"/>\n'
    xml_str += '    <listRelation>\n'
    for t in d.get("teachers", []):
        subj = t.get("subject", "")
        # 学習内容がある場合は <desc> でトリプルとして記述
        if subj:
            xml_str += f'        <relation @name="teacher" @active="{format_ref(t.get("id"))}" @passive="#{d["aind_id"]}">\n'
            xml_str += f'            <desc>Subject: {subj}</desc>\n'
            xml_str += f'        </relation>\n'
        else:
            xml_str += f'        <relation @name="teacher" @active="{format_ref(t.get("id"))}" @passive="#{d["aind_id"]}"/>\n'
    xml_str += '    </listRelation>\n'
    for a in d.get("activities", []):
        xml_str += f'    <residence @ref="{format_ref(a.get("id"))}">{a.get("place_lat")}</residence>\n'
    for i in d.get("institutions", []):
        xml_str += f'    <affiliation @type="institution" @ref="{format_ref(i.get("id"))}">{i.get("name")}</affiliation>\n'
    xml_str += f"    <note @type='translation' @xml:lang='ja'>{d['full_translation']}</note>\n"
    xml_str += f"    <desc @type='original_source' @xml:lang='ar'>{d['source_text']}</desc>\n"
    xml_str += "</person>"

    st.code(xml_str, language="xml")
    st.download_button("📥 XMLダウンロード", data=xml_str, file_name=f"{d['aind_id']}.xml", mime="application/xml")
