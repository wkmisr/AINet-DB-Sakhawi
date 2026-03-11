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
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "madhhab": {"ar": "", "lat": ""}, 
        "nisbahs": [], 
        "activities": [], 
        "teachers": [], 
        "institutions": [], 
        "family": [], 
        "source_text": "", "japanese_translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・最新AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新のGeminiで全項目を抽出中..."):
                try:
                    # 2026年3月最新モデル
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    prompt = f"""
                    Extract biographical data into JSON.
                    【Rules】
                    1. original_id: Extract the number between ### and # (e.g. 491647926297).
                    2. Names: full_name (with nisbahs), name_only (without nisbahs).
                    3. IDs (Temporary Prefixes):
                       - Person (Family/Teachers): TMP-P-xxxx
                       - Institution: TMP-O-xxxx
                       - Location/Activity: TMP-L-xxxx
                    4. Madhhab (Separate from Nisbahs):
                       - If Maliki, set id 'Q48221'. If Shafii, set id 'Q82245'.
                    5. Fields: full_name, name_only, full_name_lat, sex, certainty, madhhab(ar, lat, id), 
                       nisbahs(ar, lat, id), activities(place_ar, place_lat, id), 
                       family(name, relation, id), teachers(name, id), institutions(name, id), 
                       japanese_translation.
                    Text: {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    res_text = response.text.strip()
                    if "```" in res_text:
                        res_text = res_text.split("```")[1].replace("json", "").strip()
                    
                    res_json = json.loads(res_text)
                    d.update(res_json)
                    st.success("解析成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("japanese_translation"):
        st.subheader("🇯🇵 日本語訳")
        st.info(d["japanese_translation"])

with col2:
    st.header("2. Entity Management")
    
    # --- ID / Names ---
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c2.text_input("Source ID (###...#)", d["original_id"])
    
    d["full_name"] = st.text_input("氏名 (Full Arabic with Nisbahs)", d["full_name"])
    d["name_only"] = st.text_input("氏名 (Name Only / Without Nisbahs)", d["name_only"])
    d["full_name_lat"] = st.text_input("氏名 (IJMES Latin)", d["full_name_lat"])

    c3, c4 = st.columns(2)
    d["sex"] = c3.selectbox("Sex", ["Male", "Female", "Unknown"], index=["Male", "Female", "Unknown"].index(d.get("sex", "Male")))
    d["certainty"] = c4.selectbox("Certainty", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(d.get("certainty", "High")))

    # --- ⚖️ 法学派 (IDなし表示) ---
    st.markdown("### ⚖️ 法学派 (Madhhab)")
    m_cols = st.columns([1, 1])
    m_data = d.get("madhhab", {"ar": "", "lat": ""})
    m_data["ar"] = m_cols[0].text_input("Madhhab (Ar)", m_data.get("ar", ""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Madhhab (Lat)", m_data.get("lat", ""), key="m_lat")
    d["madhhab"] = m_data

    # --- 📝 ニスバ ---
    st.markdown("### 📝 ニスバ (Nisbahs)")
    for i, nis in enumerate(d.get("nisbahs", [])):
        n_cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = n_cols[0].text_input(f"N-Ar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = n_cols[1].text_input(f"N-Lat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = n_cols[2].text_input(f"N-ID_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed", placeholder="WD ID")
        if n_cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # --- 📍 活動拠点 (TMP-L) ---
    st.markdown("### 📍 活動拠点 (Activities)")
    for i, act in enumerate(d.get("activities", [])):
        a_cols = st.columns([2, 2, 1.2, 0.4])
        act["place_ar"] = a_cols[0].text_input(f"A-Ar_{i}", act.get("place_ar",""), key=f"aar_{i}", label_visibility="collapsed")
        act["place_lat"] = a_cols[1].text_input(f"A-Lat_{i}", act.get("place_lat",""), key=f"alat_{i}", label_visibility="collapsed")
        act["id"] = a_cols[2].text_input(f"A-ID_{i}", act.get("id", "TMP-L-"), key=f"aid_{i}", label_visibility="collapsed")
        if a_cols[3].button("❌", key=f"adel_{i}"): d["activities"].pop(i); st.rerun()
    if st.button("＋ 活動拠点追加"): d["activities"].append({"place_ar":"","place_lat":"","id":"TMP-L-"}); st.rerun()

    # --- 👥 家族関係 (TMP-P) ---
    st.markdown("### 👥 家族関係 (Family)")
    for i, f in enumerate(d.get("family", [])):
        f_cols = st.columns([2, 1, 1.2, 0.4])
        f["name"] = f_cols[0].text_input(f"F-Name_{i}", f.get("name",""), key=f"fname_{i}", label_visibility="collapsed")
        f["relation"] = f_cols[1].text_input(f"Rel_{i}", f.get("relation",""), key=f"frel_{i}", label_visibility="collapsed")
        f["id"] = f_cols[2].text_input(f"F-ID_{i}", f.get("id", "TMP-P-"), key=f"fid_{i}", label_visibility="collapsed")
        if f_cols[3].button("❌", key=f"fdel_{i}"): d["family"].pop(i); st.rerun()
    if st.button("＋ 家族追加"): d["family"].append({"name":"","relation":"","id":"TMP-P-"}); st.rerun()

    # --- 🎓 Teachers (TMP-P) / 1カラム表示 ---
    st.divider()
    st.subheader("🎓 Teachers")
    for i, t in enumerate(d.get("teachers", [])):
        t_cols = st.columns([3, 2, 0.5])
        t["name"] = t_cols[0].text_input(f"Teacher Name {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = t_cols[1].text_input(f"Teacher ID {i}", t.get("id", "TMP-P-"), key=f"tid_{i}")
        if t_cols[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ Teacher追加"): d["teachers"].append({"name":"","id":"TMP-P-"}); st.rerun()

    # --- 🕌 Institutions (TMP-O) / 1カラム表示 ---
    st.divider()
    st.subheader("🕌 Institutions")
    for i, inst in enumerate(d.get("institutions", [])):
        i_cols = st.columns([3, 2, 0.5])
        inst["name"] = i_cols[0].text_input(f"Inst Name {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = i_cols[1].text_input(f"Inst ID {i}", inst.get("id", "TMP-O-"), key=f"iid_{i}")
        if i_cols[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":"TMP-O-"}); st.rerun()
