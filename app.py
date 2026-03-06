import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB TEI Editor", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    textarea { font-size: 22px !important; line-height: 2.0 !important; font-family: 'Amiri', serif; }
    .translation-box { font-size: 18px; line-height: 1.8; background-color: #f8f9fa; padding: 25px; border-left: 5px solid #007bff; border-radius: 10px; margin-bottom: 25px; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted TEI Editor")

CERT_OPTIONS = ["High", "Medium", "Low", "Unknown"]

if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "name_cert": "High",
        "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [], 
        "source_text": "", "translation": ""
    }

col1, col2 = st.columns([1, 1.3])

# --- 左カラム：ソース解析と翻訳 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Arabic biographical text here", height=450)
    
    if st.button("✨ AI Analysis (Data + Translation)"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("Analyzing..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"Analyze text and return ONLY JSON based on previous structure. Text: {source_text}"
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    
                    st.session_state.data.update(new_data)
                    st.session_state.data["translation"] = new_data.get("japanese_translation", "")
                    st.success("Analysis complete")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 右カラム：TEI 構造化データ編集 ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # ID系
    c_id_1, c_id_2 = st.columns(2)
    d["aind_id"] = c_id_1.text_input("AIND ID (@xml:id)", value=d.get("aind_id", ""))
    d["original_id"] = c_id_2.text_input("Original ID (@source)", value=d.get("original_id", ""))
    
    # 名前系
    c_name, c_ncert = st.columns([3, 1])
    d["name"] = c_name.text_input("Full Name (@xml:lang='ar')", value=d.get("name", ""))
    d["name_cert"] = c_ncert.selectbox("Cert (@cert)", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("name_cert", "High")), key="ncert")
    
    # 没年系
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    try: death_val = int(d.get("death_year", 850))
    except: death_val = 850
    d["death_year"] = c_death.number_input("Death (Hijri @when-custom)", value=death_val)
    d["death_cert"] = c_dcert.selectbox("Cert (@cert)", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("death_cert", "High")), key="dcert")
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # Teachers, Family, Institutions の入力UI（中略：ロジックは保持）
    # ... (既存のループ処理) ...

    # --- XML出力 (ご要望の @ 属性表記 & <desc> タグ) ---
    if st.checkbox("Show Final TEI XML Preview"):
        # 属性名の前に @ を付加したカスタム出力
        xml_output = f"""<person @xml:id="{d['aind_id']}" @source="#original_{d['original_id']}" @cert="{d['name_cert'].lower()}">
    <persName @xml:lang="ar" @type="full">{d['name']}</persName>
    <death @calendar="hijri" @when-custom="{d['death_year']}" @cert="{d['death_cert'].lower()}">{d['death_year']}</death>
    <listBibl @type="teachers">
        {" ".join([f'<person @sex="{t["gender"][0]}" @role="teacher" @cert="{t.get("cert", "High").lower()}"><persName>{t["name"]}</persName></person>' for t in d["teachers"] if t["name"]])}
    </listBibl>
    <listRelation @type="family">
        {" ".join([f'<relation @active="#this" @passive="{f["name"]}" @name="{f.get("relation", "Other").lower()}" @sex="{f["gender"][0]}" @cert="{f.get("cert", "High").lower()}"/>' for f in d["family"] if f["name"]])}
    </listRelation>
    <listOrg @type="institutions">
        {" ".join([f'<orgName @role="{ins.get("relation", "Other").lower()}" @cert="{ins.get("cert", "High").lower()}">{ins["name"]}</orgName>' for ins in d["institutions"] if ins["name"]])}
    </listOrg>
    <desc>
{d['source_text']}
    </desc>
</person>"""
        st.code(xml_output, language="xml")
