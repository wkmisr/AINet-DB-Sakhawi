import streamlit as st
import google.generativeai as genai
import json

# --- 1. 基本設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB Researcher Editor", layout="wide")

# セッション状態の初期化
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "TMP-P-00001", "original_id": "", 
        "full_name": "", "full_name_lat": "",
        "lineage": [], "nisbahs": [], "activities": [],
        "death_year": 850, "teachers": [], "family": [], "institutions": [],
        "source_text": "", "translation": ""
    }

d = st.session_state.data

# --- 2. レイアウト ---
st.title("🌙 AINet-DB Researcher Editor")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source Text")
    source_input = st.text_area("Biographical Source (Arabic)", value=d.get("source_text", ""), height=400)
    
    # --- ここが重要：インデントを col1 の中に合わせる ---
    if st.button("✨ AI Analysis (Ar/Lat/Struct)"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("Analyzing..."):
                try:
                    # モデル名の修正 (models/ を外す)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Extract data into JSON: {source_input}" # 簡略化
                    response = model.generate_content(prompt)
                    # JSON抽出ロジック（中略）
                    st.success("Complete")
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

with col2:
    st.header("2. Entity Management")
    
    # 基本情報の入力（インデントは col2 の中に一段下げる）
    d["aind_id"] = st.text_input("Person ID", d.get("aind_id", ""))
    
    # 🧬 Lineage 
    st.subheader("🧬 Lineage")
    for i, lin in enumerate(d.get("lineage", [])):
        c = st.columns([2, 2, 1, 0.5])
        lin["ar"] = c[0].text_input(f"Ar_{i}", lin.get("ar", ""), key=f"lar_{i}")
        lin["lat"] = c[1].text_input(f"Lat_{i}", lin.get("lat", ""), key=f"llat_{i}")
        lin["id"] = c[2].text_input(f"ID_{i}", lin.get("id", ""), key=f"lid_{i}")
        if c[3].button("❌", key=f"ldel_{i}"):
            d["lineage"].pop(i)
            st.rerun()

    if st.button("＋ Add Lineage"):
        d["lineage"].append({"ar":"","lat":"","id":""})
        st.rerun()

    # 🕌 Institutions (TMP-O-xxx)
    st.subheader("🕌 Institutions")
    for i, inst in enumerate(d.get("institutions", [])):
        c = st.columns([3, 2, 0.5])
        inst["name"] = c[0].text_input(f"Inst Name {i}", inst.get("name", ""), key=f"in_{i}")
        inst["id"] = c[1].text_input(f"Inst ID {i}", inst.get("id", ""), key=f"iid_{i}", placeholder="TMP-O-xxx")
        if c[2].button("❌", key=f"idel_{i}"):
            d["institutions"].pop(i)
            st.rerun()
            
    if st.button("＋ Add Institution"):
        d["institutions"].append({"name":"","id":""})
        st.rerun()
