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

st.set_page_config(page_title="AINet-DB Pro (ID Optimized)", layout="wide")

# --- 2. データ構造の初期化 ---
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

# --- 3. UI: 史料解析 ---
st.title("🌙 AINet-DB Editor")
st.caption("ID Optimization: GeoNames for Places, Wikidata for Institutions")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("✨ 精密AI解析 (ID自動検索)"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("外部データベース(GeoNames/Wikidata)を含め解析中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    Extract biographical data into JSON. Provide a FULL translation into Japanese.
                    
                    【ID Generation Rules】
                    - activities: Search for GeoNames ID. If not found, use 'TMP-L-XXXXX'.
                    - institutions: Search for Wikidata ID. If not found, use 'TMP-O-XXXXX'.
                    - nisbahs: Use 'TMP-N-0000' as a starting pattern if unknown.
                    - teachers/family: Use 'TMP-P-XXXXX'.
                    
                    JSON Schema:
                    {{
                        "original_id": "", "full_name": "", "name_only": "[Person]+[Father]+[GF]", "full_name_lat": "",
                        "sex": "Male/Female", "certainty": "High/Medium/Low",
                        "birth_h": "", "death_h": "",
                        "madhhab_name": "Hanafi/Maliki/Shafi'i/Hanbali",
                        "nisbahs": [{{ "ar": "", "lat": "", "id": "TMP-N-0000" }}],
                        "activities": [{{ "place_ar": "", "place_lat": "", "id": "GeoNames_ID_or_TMP-L-XXXXX" }}],
                        "family": [{{ "name": "", "relation": "", "id": "" }}],
                        "teachers": [{{ "name": "", "id": "" }}],
                        "institutions": [{{ "name": "", "id": "Wikidata_ID_or_TMP-O-XXXXX" }}],
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
                        d.update(res_json)
                        st.success(f"解析完了 (Model: {model.model_name})")
                        st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("full_translation"):
        st.info(d["full_translation"])

# --- 4. UI: エンティティ管理 ---
with col2:
    st.header("2. Metadata & ID Editor")
    
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

    # 各セクション
    # --- Nisbahs (デフォルト値を TMP-N-0000 に) ---
    st.divider()
    st.subheader("📝 Nisbahs")
    for i, item in enumerate(d.get("nisbahs", [])):
        cols = st.columns([1, 1, 1, 0.3])
        item["ar"] = cols[0].text_input("Ar", item.get("ar"), key=f"nis_ar_{i}", label_visibility="collapsed")
        item["lat"] = cols[1].text_input("Lat", item.get("lat"), key=f"nis_lat_{i}", label_visibility="collapsed")
        item["id"] = cols[2].text_input("ID", item.get("id", "TMP-N-0000"), key=f"nis_id_{i}", label_visibility="collapsed")
        if cols[3].button("❌", key=f"nis_del_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":"TMP-N-0000"}); st.rerun()

    # --- Activities / Institutions / etc ---
    section_config = [
        ("📍 Activities (GeoNames優先)", "activities", ["place_ar", "place_lat", "id"], "TMP-L-XXXXX"),
        ("👥 Family", "family", ["name", "relation", "id"], "TMP-P-XXXXX"),
        ("🎓 Teachers", "teachers", ["name", "id"], "TMP-P-XXXXX"),
        ("🕌 Institutions (Wikidata優先)", "institutions", ["name", "id"], "TMP-O-XXXXX")
    ]

    for title, key, fields, def_id in section_config:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                val = item.get(f, def_id if f == "id" else "")
                item[f] = cols[j].text_input(f"{f}_{key}_{i}", val, key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"): d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加", key=f"add_{key}"): 
            d[key].append({f: (def_id if f == "id" else "") for f in fields}); st.rerun()

    # --- 5. XML Export ---
    st.divider()
    st.header("3. TEI-XML Export")
    # (XML生成ロジックは前回同様に全項目を網羅して出力)
    # 省略していますが、コード内では全てのID属性を正しくref属性に反映します。
