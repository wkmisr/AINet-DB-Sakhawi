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
        "madhhab": {"ar": "", "lat": "", "id": ""},
        "nisbahs": [], "activities": [],
        "teachers": [], "institutions": [], "family": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 精密AI解析実行"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("法学派・師匠・施設を抽出中..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.0-flash')
                    
                    # より詳細で厳格なプロンプト
                    prompt = f"""
                    以下の伝記史料から情報を抽出し、必ず指定のJSON形式で返してください。
                    
                    【ルール】
                    1. 翻字: IJMESスタイル (例: al-Maqdisī)。
                    2. ID命名規則:
                       - 人物 (Teachers/Family): AIND-P-xxxx
                       - 施設 (Institutions): AIND-O-xxxx
                       - 法学派 (Madhhab): AIND-M-xxxx
                    3. 項目:
                       - full_name, full_name_lat
                       - sex (Male/Female), certainty (High/Medium/Low)
                       - madhhab: {{"ar": "...", "lat": "...", "id": "..."}}
                       - teachers: [{{"name": "...", "id": "..."}}]
                       - institutions: [{{"name": "...", "id": "..."}}]
                       - japanese_translation: 日本語訳
                    
                    テキスト:
                    {source_input}
                    """
                    
                    response = model.generate_content(prompt)
                    res_text = response.text.strip()
                    if "```" in res_text:
                        res_text = res_text.split("```")[1].replace("json", "").strip()
                    
                    res_json = json.loads(res_text)
                    d.update(res_json)
                    st.success("解析成功！項目を更新しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("translation"):
        st.subheader("🇯🇵 日本語訳")
        st.info(d.get("japanese_translation", d.get("translation", "")))

with col2:
    st.header("2. Entity Management")
    
    # ID / 性別 / 確信度
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    d["aind_id"] = c1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c2.text_input("Source ID", d["original_id"])
    d["sex"] = c3.selectbox("Sex", ["Male", "Female", "Unknown"], 
                            index=["Male", "Female", "Unknown"].index(d.get("sex", "Male")))
    d["certainty"] = c4.selectbox("Certainty", ["High", "Medium", "Low"], 
                                  index=["High", "Medium", "Low"].index(d.get("certainty", "High")))

    # 名前
    f_ar, f_lat = st.columns(2)
    d["full_name"] = f_ar.text_input("氏名 (Arabic)", d["full_name"])
    d["full_name_lat"] = f_lat.text_input("氏名 (IJMES)", d["full_name_lat"])

    # 法学派 (Madhhab) - 新設
    st.markdown("### ⚖️ 法学派 (Madhhab)")
    m_cols = st.columns([2, 2, 1.2])
    m_data = d.get("madhhab", {"ar": "", "lat": "", "id": ""})
    m_data["ar"] = m_cols[0].text_input("Madhhab (Ar)", m_data.get("ar", ""), key="m_ar")
    m_data["lat"] = m_cols[1].text_input("Madhhab (Lat)", m_data.get("lat", ""), key="m_lat")
    m_data["id"] = m_cols[2].text_input("Madhhab ID", m_data.get("id", ""), key="m_id", placeholder="AIND-M-...")
    d["madhhab"] = m_data

    # 師匠と施設
    st.markdown("---")
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

    # XML プレビュー
    st.divider()
    if st.checkbox("Show Final TEI XML Preview"):
        xml_output = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}">
  <persName xml:lang="ar">{d['full_name']}</persName>
  <persName xml:lang="lat">{d['full_name_lat']}</persName>
  <trait type="madhhab" ref="{d['madhhab'].get('id','')}">
    <desc>{d['madhhab'].get('lat','')}</desc>
  </trait>
</person>"""
        st.code(xml_output, language="xml")
