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
        "madhhab": {"ar": "", "lat": "", "id": ""}, 
        "nisbahs": [], 
        "activities": [], 
        "teachers": [], 
        "institutions": [], 
        "family": [], 
        "source_text": "", "japanese_translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor (XML Export Ready)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ 全項目・精密AI解析"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新のGeminiで全項目を抽出中..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    prompt = f"""
                    Extract biographical data into JSON.
                    【Rules】
                    1. original_id: Extract the number between ### and #.
                    2. Names: full_name (with nisbahs), name_only (without nisbahs).
                    3. IDs: Person: TMP-P-xxxx, Inst: TMP-O-xxxx, Place: TMP-L-xxxx.
                    4. Madhhab IDs: Hanafi: Q160851, Maliki: Q48221, Shafi'i: Q82245, Hanbali: Q191314.
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip()
                    if "```" in res_text:
                        res_text = res_text.split("```")[1].replace("json", "").strip()
                    d.update(json.loads(res_text))
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
    d["original_id"] = c2.text_input("Source ID", d["original_id"])
    d["full_name"] = st.text_input("氏名 (Full)", d["full_name"])
    d["name_only"] = st.text_input("氏名 (Name Only)", d["name_only"])
    d["full_name_lat"] = st.text_input("氏名 (Latin)", d["full_name_lat"])

    sex_options = ["Male", "Female", "Unknown"]
    d["sex"] = st.selectbox("Sex", sex_options, index=sex_options.index(d.get("sex", "Male")) if d.get("sex") in sex_options else 2)
    
    # 各セクション（中略：前回の入力フォームを維持）
    # ... (法学派、ニスバ、拠点、家族、師匠、施設のコードをここに保持) ...
    # ※ 簡略化のため、末尾のXML出力部分に焦点を当てます

    st.markdown("---")
    st.header("3. XML Export")

    # XML組み立てロジック
    xml_str = f"""<person xml:id="{d['aind_id']}" source="#source_{d['original_id']}" sex="{d['sex']}">
  <persName xml:lang="ar" type="full">{d['full_name']}</persName>
  <persName xml:lang="ar" type="name_only">{d['name_only']}</persName>
  <persName xml:lang="lat" type="ijmes">{d['full_name_lat']}</persName>
  <affiliation type="madhhab" ref="wd:{d['madhhab'].get('id','')}">{d['madhhab'].get('lat','')}</affiliation>
  <listRelation>
"""
    for t in d.get("teachers", []):
        xml_str += f'    <relation name="teacher" active="{t.get("id")}" passive="#{d["aind_id"]}"/>\n'
    for f in d.get("family", []):
        xml_str += f'    <relation name="{f.get("relation")}" active="{f.get("id")}" passive="#{d["aind_id"]}"/>\n'
    
    xml_str += "  </listRelation>\n</person>"

    st.code(xml_str, language="xml")
    
    st.download_button(
        label="📥 XMLファイルをダウンロード",
        data=xml_str,
        file_name=f"{d['aind_id']}.xml",
        mime="application/xml"
    )
