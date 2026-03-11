import streamlit as st
import google.generativeai as genai
import json

# --- 1. API・基本設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# カスタムCSS
st.markdown("""
    <style>
    .stTextInput input { padding: 4px 8px !important; }
    .ar-font { font-family: 'Amiri', serif; font-size: 1.3rem !important; direction: rtl; }
    .section-header { background-color: #e8f0fe; padding: 5px 10px; border-radius: 5px; margin-top: 20px; font-weight: bold; border-left: 5px solid #1a73e8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. セッション状態の初期化 ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "nisbahs": [], "activities": [],
        "death_year": 850, "teachers": [], "family": [], "institutions": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- 3. UIレイアウト ---
st.title("🌙 AINet-DB Researcher Editor (AIND 2026)")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source Text & AI Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=480)
    
    if st.button("✨ AI解析実行 (最新モデル)"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("最新世代のGeminiで解析中..."):
                try:
                    # 【重要】リストにあった現役モデル 'gemini-2.0-flash' を使用
                    # これで 404 エラーを回避します。
                    model = genai.GenerativeModel('models/gemini-2.0-flash')
                    
                    prompt = f"""以下のテキストから人物情報を抽出し、JSON形式で返してください。
                    - ID体系: 全てのIDは AIND- で始めてください。
                    - 翻字: IJMESスタイル。
                    - 分離: 'teachers'（個人名）と 'institutions'（施設名）を厳密に区別。
                    - 属性: 'sex' (Male/Female), 'certainty' (High/Medium/Low)。
                    - 日本語訳を 'japanese_translation' に含めてください。
                    テキスト: {source_input}"""
                    
                    response = model.generate_content(prompt)
                    
                    # JSONクレンジング
                    res_text = response.text.strip()
                    if "```" in res_text:
                        res_text = res_text.split("```")[1].replace("json", "").strip()
                    
                    res_json = json.loads(res_text)
                    d.update(res_json)
                    d["translation"] = res_json.get("japanese_translation", "")
                    st.success("解析が完了しました（Gemini 2.0 Flashを使用）")
                    st.rerun()
                except Exception as e:
                    if "429" in str(e):
                        st.error("【制限エラー】APIキーがまだ無料枠扱いです。")
                        st.info("解決策: 課金設定したプロジェクトで『新しいAPIキー』を再発行してください。")
                    else:
                        st.error(f"解析エラー: {e}")

    if d.get("translation"):
        st.subheader("🇯🇵 日本語訳")
        st.info(d["translation"])

with col2:
    st.header("2. Entity Management")
    
    # ID & 性別・確信度
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    d["aind_id"] = c1.text_input("Person ID", d["aind_id"])
    d["original_id"] = c2.text_input("Source ID", d["original_id"])
    d["sex"] = c3.selectbox("性別", ["Male", "Female", "Unknown"], index=0 if d["sex"]=="Male" else 1)
    d["certainty"] = c4.selectbox("確信度", ["High", "Medium", "Low"], 
                                  index=["High", "Medium", "Low"].index(d.get("certainty", "High")))
    
    f_ar, f_lat = st.columns(2)
    d["full_name"] = f_ar.text_input("氏名 (Arabic)", d["full_name"])
    d["full_name_lat"] = f_lat.text_input("氏名 (Latin IJMES)", d["full_name_lat"])

    # ニスバ
    st.markdown('<div class="section-header">📝 Nisbahs</div>', unsafe_allow_html=True)
    for i, nis in enumerate(d.get("nisbahs", [])):
        cols = st.columns([2, 2, 1.2, 0.4])
        nis["ar"] = cols[0].text_input(f"Ar_{i}", nis.get("ar",""), key=f"nar_{i}", label_visibility="collapsed")
        nis["lat"] = cols[1].text_input(f"Lat_{i}", nis.get("lat",""), key=f"nlat_{i}", label_visibility="collapsed")
        nis["id"] = cols[2].text_input(f"ID_{i}", nis.get("id",""), key=f"nid_{i}", label_visibility="collapsed")
        if cols[3].button("❌", key=f"ndel_{i}"): d["nisbahs"].pop(i); st.rerun()
    if st.button("＋ ニスバ追加"): d["nisbahs"].append({"ar":"","lat":"","id":""}); st.rerun()

    # 師匠
    st.markdown('<div class="section-header">🎓 Teachers (AIND-P-xxx)</div>', unsafe_allow_html=True)
    for i, t in enumerate(d.get("teachers", [])):
        cols = st.columns([3, 2, 0.5])
        t["name"] = cols[0].text_input(f"氏名 {i}", t.get("name",""), key=f"tn_{i}")
        t["id"] = cols[1].text_input(f"ID {i}", t.get("id",""), key=f"tid_{i}")
        if cols[2].button("❌", key=f"tdel_{i}"): d["teachers"].pop(i); st.rerun()
    if st.button("＋ 師匠追加"): d["teachers"].append({"name":"","id":""}); st.rerun()

    # 施設
    st.markdown('<div class="section-header">🕌 Institutions (AIND-O-xxx)</div>', unsafe_allow_html=True)
    for i, inst in enumerate(d.get("institutions", [])):
        cols = st.columns([3, 2, 0.5])
        inst["name"] = cols[0].text_input(f"施設名 {i}", inst.get("name",""), key=f"in_{i}")
        inst["id"] = cols[1].text_input(f"施設ID {i}", inst.get("id",""), key=f"iid_{i}")
        if cols[2].button("❌", key=f"idel_{i}"): d["institutions"].pop(i); st.rerun()
    if st.button("＋ 施設追加"): d["institutions"].append({"name":"","id":""}); st.rerun()

    # XML プレビュー
    st.divider()
    if st.checkbox("Show TEI XML Preview"):
        xml_output = f"""<person xml:id="{d['aind_id']}" sex="{d['sex']}" cert="{d['certainty']}">
  <persName xml:lang="ar">{d['full_name']}</persName>
  <persName xml:lang="lat">{d['full_name_lat']}</persName>
</person>"""
        st.code(xml_output, language="xml")
