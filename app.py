import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 & 利用可能モデルの自動取得 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    """APIから現在利用可能なモデルを自動取得して404を回避"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m]
        if flash_models:
            return genai.GenerativeModel(flash_models[0])
        return genai.GenerativeModel(models[0])
    except:
        return genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="AINet-DB Editor Pro", layout="wide")

# --- 2. 法学派データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

# --- 3. データ構造の初期化 ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "madhhab": {"lat": "Hanafi (ハナフィー派)", "id": "Q160851"}, # 初期値
        "nisbahs": [], "activities": [], "teachers": [], "institutions": [], "family": [], 
        "source_text": "", "japanese_translation": ""
    }
d = st.session_state.data

# --- 4. UI ---
st.title("🌙 AINet-DB Editor (Madhhab Select Edition)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=500)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("AI解析中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    Extract biographical data into JSON. Missing fields = [].
                    Madhhab should be one of: Hanafi, Maliki, Shafi'i, Hanbali.
                    {{
                        "original_id": "Number between ### and #",
                        "full_name": "Arabic full name",
                        "name_only": "Ism only",
                        "full_name_lat": "IJMES transcription",
                        "sex": "Male/Female",
                        "certainty": "High/Medium/Low",
                        "madhhab_name": "Hanafi/Maliki/Shafi'i/Hanbali",
                        "nisbahs": [ {{"ar": "", "lat": "", "id": ""}} ],
                        "activities": [ {{"place_ar": "", "place_lat": "", "id": "TMP-L-xxxx"}} ],
                        "family": [ {{"name": "", "relation": "", "id": "TMP-P-xxxx"}} ],
                        "teachers": [ {{"name": "", "id": "TMP-P-xxxx"}} ],
                        "institutions": [ {{"name": "", "id": "TMP-O-xxxx"}} ],
                        "japanese_translation": "Summary"
                    }}
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    res_json = json.loads(re.search(r"\{.*\}", response.text, re.DOTALL).group())
                    
                    # 法学派のマッピング処理
                    m_name = res_json.get("madhhab_name", "Unknown / Other")
                    for k in MADHHAB_DATA.keys():
                        if m_name in k:
                            d["madhhab"]["lat"] = k
                            d["madhhab"]["id"] = MADHHAB_DATA[k]
                    
                    d.update(res_json)
                    st.success(f"解析完了！ (Model: {model.model_name})")
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")

with col2:
    st.header("2. Entity Management")
    
    # 基本情報 (@付きラベル)
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("@sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("@cert", ["High", "Medium", "Low"], index=0)

    # --- 法学派セクション (スクロール選択) ---
    st.divider()
    st.subheader("⚖️ Madhhab (affiliation)")
    selected_m = st.selectbox("法学派を選択", options=list(MADHHAB_DATA.keys()), index=list(MADHHAB_DATA.keys()).index(d["madhhab"]["lat"]) if d["madhhab"]["lat"] in MADHHAB_DATA else 4)
    d["madhhab"]["lat"] = selected_m
    d["madhhab"]["id"] = MADHHAB_DATA[selected_m]
    st.text_input("@ref (Auto-filled)", d["madhhab"]["id"], disabled=True)

    # --- その他エンティティ管理 ---
    sections = [
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
        ("👥 Family", "family", ["name", "relation", "id"]),
        ("🎓 Teachers", "teachers", ["name", "id"]),
        ("🕌 Institutions", "institutions", ["name", "id"])
    ]

    for title, key, fields in sections:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                label = f"@{f}" if f == "id" else f
                item[f] = cols[j].text_input(f"{label}_{key}_{i}", item.get(f,""), key=f"{key}_{f}_{i}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{i}"):
                d[key].pop(i); st.rerun()
        if st.button(f"＋ {title}追加", key=f"add_{key}"):
            d[key].append({f: "" for f in fields}); st.rerun()

    # --- XML Export ---
    st.divider()
    st.header("3. XML Export")
    xml_output = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab']['id']}"/>
</person>"""
    st.code(xml_output, language="xml")
