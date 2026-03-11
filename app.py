import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Editor Pro", layout="wide")

# --- 2. データ構造の完全定義 ---
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
st.title("🌙 AINet-DB Editor (Total Recovery Edition)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=500)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("AI接続を試行中..."):
                try:
                    # 404エラー対策：モデル名を極限までシンプルにする、または最新の 'gemini-1.5-flash' を使用
                    # models/ を付けないのが 2026年版の定石です
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Professional Task: Extract biographical data into JSON.
                    Text: {source_input}

                    JSON Schema (Strict):
                    {{
                        "original_id": "Number between ### and #",
                        "full_name": "Full Arabic name",
                        "name_only": "Name without nisbahs",
                        "full_name_lat": "IJMES Latin",
                        "sex": "Male/Female",
                        "certainty": "High/Medium/Low",
                        "madhhab": {{"ar": "", "lat": "", "id": "WD ID"}},
                        "nisbahs": [ {{"ar": "", "lat": "", "id": ""}} ],
                        "activities": [ {{"place_ar": "", "place_lat": "", "id": "TMP-L-xxxx"}} ],
                        "family": [ {{"name": "", "relation": "", "id": "TMP-P-xxxx"}} ],
                        "teachers": [ {{"name": "", "id": "TMP-P-xxxx"}} ],
                        "institutions": [ {{"name": "", "id": "TMP-O-xxxx"}} ],
                        "japanese_translation": "Summary"
                    }}
                    """
                    
                    response = model.generate_content(prompt)
                    # JSONの切り出しを強化
                    json_content = re.search(r"\{.*\}", response.text, re.DOTALL).group()
                    d.update(json.loads(json_content))
                    st.success("解析完了！全データを同期しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"接続エラー: {e}")

    if d.get("japanese_translation"):
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 属性入力 (@付き)
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    
    # 基本情報
    d["full_name"] = st.text_input("persName (Full)", d["full_name"])
    d["name_only"] = st.text_input("persName (Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("persName (Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("@sex", ["Male", "Female", "Unknown"], index=0)
    d["certainty"] = c4.selectbox("@cert", ["High", "Medium", "Low"], index=0)

    # 全項目の管理 UI
    sections = [
        ("⚖️ Madhhab", "madhhab", ["ar", "lat", "id"]),
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"]),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "id"]),
        ("👥 Family", "family", ["name", "relation", "id"]),
        ("🎓 Teachers", "teachers", ["name", "id"]),
        ("🕌 Institutions", "institutions", ["name", "id"])
    ]

    for title, key, fields in sections:
        st.divider()
        st.subheader(title)
        
        if key == "madhhab":
            cols = st.columns(3)
            for j, f in enumerate(fields):
                label = f"@{f}" if f == "id" else f
                d[key][f] = cols[j].text_input(f"{label}_{key}", d[key].get(f,""), key=f"m_{f}")
            continue

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
    xml_str = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}" source="#source_{d['original_id']}">
    <persName type="full" xml:lang="ar">{d['full_name']}</persName>
    <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">
        <desc xml:lang="ar">{d['madhhab'].get('ar','')}</desc>
    </affiliation>
</person>"""
    st.code(xml_str, language="xml")
