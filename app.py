import streamlit as st
import google.generativeai as genai
import json

# --- 1. API・基本設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# --- 2. セッション状態の初期化 ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "madhhab": {"ar": "", "lat": ""}, 
        "nisbahs": [], 
        "activities": [], 
        "teachers": [], 
        "institutions": [], 
        "family": [], 
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor (2026.03 Edition)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・最新AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新のGemini 2.5で全項目を抽出中..."):
                try:
                    # 2026年3月現在、新規ユーザーが確実に使用できる最新モデル
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    prompt = f"""
                    Extract biographical data into JSON.
                    【Rules】
                    1. Transliteration: IJMES style (e.g., al-Baghdādī).
                    2. IDs: AIND-P-xxxx (Person), AIND-O-xxxx (Institution), gn:xxxx (Place).
                    3. Required JSON Fields:
                       - full_name, full_name_lat
                       - sex, certainty
                       - madhhab: {{"ar": "", "lat": ""}}
                       - nisbahs: [{{"ar": "", "lat": "", "id": ""}}]
                       - activities: [{{"place_ar": "", "place_lat": "", "id": ""}}]
                       - family: [{{"name": "", "relation": "", "id": ""}}]
                       - teachers: [{{"name": "", "id": ""}}]
                       - institutions: [{{"name": "", "id": ""}}]
                       - japanese_translation: (Detailed summary in Japanese)
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    res_text = response.text.strip()
                    if "```" in res_text:
                        res_text = res_text.split("```")[1].replace("json", "").strip()
                    
                    res_json = json.loads(res_text)
                    d.update(res_json)
                    st.success("解析成功！全項目を更新しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語訳")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # 基本情報
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    d["aind_id"] = c1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c2.text_input("Source ID", d["original_id"])
    d["sex"] = c3.selectbox("Sex", ["Male", "Female", "Unknown"], index=["Male", "Female", "Unknown"].index(d.get("sex", "Male")))
    d["certainty"] = c4.selectbox("Certainty", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(d.get("certainty", "High")))

    f_ar, f_lat = st.columns(2)
    d["full_name"] = f_ar.text_input("氏名 (Arabic)", d["full_name"])
    d["full_name_lat"] = f_lat.text_input("氏名 (IJMES)", d["full_name_lat"])

    # --- 法学派 (Madhhab) ---
    st.markdown("### ⚖️ 法学派 (Madhhab)")
    m_cols = st.columns([1, 1])
    m_data = d.get("madhhab", {"ar": "", "lat": ""})
    m_data["ar"] = m_cols[0].text_input("Madhhab (Ar)", m_data.get("ar", ""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Madhhab (Lat)", m_data.get("lat", ""), key="m_lat")
    d["madhhab"] = m_data

    # --- ニスバ ---
    st.markdown("### 📝 ニスバ (Nisbahs)")
    for i, nis in enumerate(d.get("nisbahs", [])):
        n_cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = n_cols[0].text_input(f"N-Ar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = n_cols[1].text_input(f"N-Lat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = n_cols[2].text_input(f"N-ID_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed")
        if n_cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # --- 活動拠点 ---
    st.markdown("### 📍 活動拠点 (Activities)")
    for i, act in enumerate(d.get("activities", [])):
        a_cols = st.columns([2, 2, 1.2, 0.4])
        act["place_ar"] = a_cols[0].text_input(f"A-Ar_{i}", act.get("place_ar",""), key=f"aar_{i}", label_visibility="collapsed")
        act["place_lat"] = a_cols[1].text_input(f"A-Lat_{i}", act.get("place_lat",""), key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = a_cols[2].text_input(f"A-ID_{i}", act.get("id",""), key=f"aid_{i}", label_visibility="collapsed")
        if a_cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ 活動拠点追加"): d["activities"].append({"place_ar":"","place_lat":"","id":""}); st.rerun()

    # --- 家族関係 ---
    st.markdown("### 👥 家族関係 (Family)")
    for i, f in enumerate(d.get("family", [])):
        f_cols = st.columns([2, 1, 1.2, 0.4])
        f["name"] = f_cols[0].text_input(f"F-Name_{i}", f.get("name",""), key=f"fname_{i}", label_visibility="collapsed")
        f["relation"] = f_cols[1].text_input(f"Rel_{i}", f.get("relation",""), key=f"frel_{i}", label_visibility="collapsed")
        f["id"] = f_cols[2].text_input(f"F-ID_{i}", f.get("id",""), key=f"fid_{i}", label_visibility="collapsed")
        if f_cols[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ 家族追加"): d["family"].append({"name":"","relation":"","id":""}); st.rerun()

    # --- 師匠・施設 ---
    st.divider()
    t_col, i_col = st.columns(2)
    with t_col:
        st.subheader("🎓 Teachers")
        for i, t in enumerate(d.get("teachers", [])):
            t["name"] = st.text_input(f"T-Name {i}", t.get("name",""), key=f"tn_{i}")
            t["id"] = st.text_input(f"T-ID {i}", t.get("id",""), key=f"tid_{i}")
        if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":""}); st.rerun()
    with i_col:
        st.subheader("🕌 Institutions")
        for i, inst in enumerate(d.get("institutions", [])):
            inst["name"] = st.text_input(f"I-Name {i}", inst.get("name",""), key=f"in_{i}")
            inst["id"] = st.text_input(f"I-ID {i}", inst.get("id",""), key=f"iid_{i}")
        if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":""}); st.rerun()
