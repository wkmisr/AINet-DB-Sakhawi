import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 & モデル自動検知 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    """利用可能なモデルを自動取得"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m]
        return genai.GenerativeModel(flash_models[0] if flash_models else models[0])
    except:
        return genai.GenerativeModel('models/gemini-1.5-flash')

def convert_h_to_g(h_year):
    """ヒジュラ暦から西暦への換算ロジック"""
    try:
        # 数字以外の文字（"c." や "?" など）が含まれる場合を除去
        h_clean = re.sub(r"\D", "", str(h_year))
        if not h_clean: return ""
        h = int(h_clean)
        return int(h * 0.97 + 622)
    except:
        return ""

st.set_page_config(page_title="AINet-DB Researcher Pro", layout="wide")

# --- 2. 法学派データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

# --- 3. セッション状態の初期化 ---
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

# --- 4. UI: 史料解析エリア ---
st.title("🌙 AINet-DB Researcher Pro")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("✨ 全項目・精密AI解析 & 全訳"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("AI解析中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    You are a historian. Extract biographical data into JSON. Provide a FULL translation into Japanese.
                    
                    【Rules】
                    1. Return VALID JSON ONLY.
                    2. name_only: MUST be [Person's name] + [Father's name] + [Grandfather's name] in Arabic.
                    3. Extract Hijri years for birth_h and death_h.
                    4. full_translation: Translate the entire source into academic Japanese.

                    【JSON Schema】
                    {{
                        "original_id": "", "full_name": "", "name_only": "", "full_name_lat": "",
                        "sex": "Male/Female", "certainty": "High/Medium/Low",
                        "birth_h": "", "death_h": "",
                        "madhhab_name": "Hanafi/Maliki/Shafi'i/Hanbali",
                        "nisbahs": [{{ "ar": "", "lat": "", "id": "" }}],
                        "activities": [{{ "place_ar": "", "place_lat": "", "id": "" }}],
                        "family": [{{ "name": "", "relation": "", "id": "" }}],
                        "teachers": [{{ "name": "", "id": "" }}],
                        "institutions": [{{ "name": "", "id": "" }}],
                        "full_translation": ""
                    }}
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    
                    # --- JSON抽出の堅牢化 ---
                    raw_text = response.text
                    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                    
                    if json_match:
                        res_json = json.loads(json_match.group())
                        
                        # 西暦への自動計算
                        res_json["birth_g"] = convert_h_to_g(res_json.get("birth_h", ""))
                        res_json["death_g"] = convert_h_to_g(res_json.get("death_h", ""))
                        
                        # 法学派マッピング
                        m_name = res_json.get("madhhab_name", "")
                        res_json["madhhab"] = {"lat": "Unknown / Other", "id": ""}
                        for k, v in MADHHAB_DATA.items():
                            if m_name and m_name.lower() in k.lower():
                                res_json["madhhab"] = {"lat": k, "id": v}
                        
                        d.update(res_json)
                        st.success(f"解析成功！ (Model: {model.model_name})")
                        st.rerun()
                    else:
                        st.error("AIの回答からJSONデータが見つかりませんでした。もう一度お試しください。")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("full_translation"):
        st.subheader("🇯🇵 史料全訳")
        st.info(d["full_translation"])

# --- 5. UI: エンティティ管理エリア ---
with col2:
    st.header("2. TEI Metadata Editor")
    
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"] = st.text_input("persName (Name/Father/Grandfather)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin/IJMES)", d["full_name_lat"])

    st.markdown("### 📅 Dates (Birth & Death)")
    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    d["birth_g"] = dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]))
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    d["death_g"] = dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]))

    st.markdown("### ⚖️ Madhhab")
    selected_m = st.selectbox("法学派を選択", options=list(MADHHAB_DATA.keys()), 
                              index=list(MADHHAB_DATA.keys()).index(d["madhhab"]["lat"]) if d["madhhab"]["lat"] in MADHHAB_DATA else 4)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}

    for title, key, fields in [("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]), 
                               ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
                               ("👥 Family", "family", ["name", "relation", "id"]),
                               ("🎓 Teachers", "teachers", ["name", "id"]),
                               ("🕌 Institutions", "institutions", ["name", "id"])]:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                item[f] = cols[j].text_input(f"{f}_{key}_{i}", item.get(f,""), key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"): d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加", key=f"add_{key}"): d[key].append({f: "" for f in fields}); st.rerun()

    # --- 6. XML Export (TEI準拠) ---
    st.divider()
    st.header("3. TEI-XML Export")
    
    xml_str = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <persName type="name_only" xml:lang="ar">{d['name_only']}</persName>
    <persName type="ijmes" xml:lang="lat">{d['full_name_lat']}</persName>
    <birth when-custom="{d['birth_h']}" datingMethod="#islamic" when="{d['birth_g']}"/>
    <death when-custom="{d['death_h']}" datingMethod="#islamic" when="{d['death_g']}"/>
    <affiliation type="madhhab" ref="wd:{d['madhhab']['id']}">{d['madhhab']['lat']}</affiliation>
    <listRelation>
"""
    for f in d.get("family", []): xml_str += f'        <relation name="{f.get("relation")}" active="{f.get("id")}" passive="#{d["aind_id"]}"/>\n'
    for t in d.get("teachers", []): xml_str += f'        <relation name="teacher" active="{t.get("id")}" passive="#{d["aind_id"]}"/>\n'
    xml_str += "    </listRelation>\n"
    for a in d.get("activities", []): xml_str += f'    <residence ref="#{a.get("id")}">{a.get("place_lat")}</residence>\n'
    for i in d.get("institutions", []): xml_str += f'    <affiliation type="institution" ref="#{i.get("id")}">{i.get("name")}</affiliation>\n'
    xml_str += f"    <note type='translation' xml:lang='ja'>{d['full_translation']}</note>\n"
    xml_str += f"    <desc type='original_source' xml:lang='ar'>{d['source_text']}</desc>\n"
    xml_str += "</person>"

    st.code(xml_str, language="xml")
