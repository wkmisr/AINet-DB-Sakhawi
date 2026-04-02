import streamlit as st
import google.generativeai as genai
import json
import re
import uuid

# --- 1. API設定 & モデル自動検知 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    try:
        # 1. 利用可能なモデルをリストアップ
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. 'flash' が含まれるモデルを優先的に探す
        flash_models = [m for m in models if 'flash' in m]
        
        if flash_models:
            # 見つかった中から最新（リストの後ろの方）を返す
            return genai.GenerativeModel(flash_models[-1])
        elif models:
            # flashがなければ最初のモデルを返す
            return genai.GenerativeModel(models)
            
    except Exception as e:
        # 万が一リスト取得に失敗した場合の最終手段
        # 'models/' プレフィックスを外した名前を試す
        return genai.GenerativeModel('gemini-1.5-flash')

def convert_h_to_g(h_year):
    try:
        h_clean = re.sub(r"\D", "", str(h_year))
        if not h_clean: return ""
        h = int(h_clean)
        return int(h * 0.97 + 622)
    except:
        return ""

st.set_page_config(page_title="AINet-DB Pro (Bilingual Translation)", layout="wide")

# --- 2. データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

if 'data_v14' not in st.session_state:
    st.session_state.data_v14 = {
        "aind_id": "AIND-D0000", "original_id": "", 
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "birth_h": "", "birth_g": "", "death_h": "", "death_g": "",
        "madhhab": {"lat": "Unknown / Other", "id": ""}, 
        "nisbahs": [], 
        "activities": [], 
        "teachers": [], 
        "students": [], 
        "institutions": [], "family": [], 
        "source_text": "", "translation_jp": "", "translation_en": ""
    }
d = st.session_state.data_v14

# --- 3. UI: 史料解析エリア ---
st.title("🌙 AINet-DB Researcher Pro")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("1. Source & Bilingual Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)
    
    if st.button("🚀 精密解析（日英翻訳・外部ID）"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("日英翻訳とIDを探索中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    You are a professional historian of Islamic studies. Extract data into JSON.
                    
                    【IMPORTANT: Translation】
                    - translation_jp: Accurate academic Japanese translation.
                    - translation_en: Accurate academic English translation.
                    
                    【IMPORTANT: ID SEARCH】
                    - Search and provide REAL IDs. Places: GeoNames. Institutions: Wikidata.
                    
                    JSON Structure:
                    {{
                        "original_id": "", "full_name": "", "name_only": "", 
                        "birth_h": "", "death_h": "", "madhhab_name": "",
                        "nisbahs": [{{ "ar": "", "lat": "", "id": "TMP-L-00000" }}],
                        "activities": [{{ "place_ar": "", "place_lat": "", "type": "study/buried/reside/visit", "id": "GeoNames_ID" }}],
                        "teachers": [{{ "name": "", "id": "TMP-P-00000", "subject": "", "subject_id": "TMP-S-00000" }}],
                        "students": [{{ "name": "", "id": "TMP-P-00000", "subject": "", "subject_id": "TMP-S-00000" }}],
                        "institutions": [{{ "name": "", "id": "Wikidata_ID" }}],
                        "translation_jp": "", "translation_en": ""
                    }}
                    Text: {source_input}
                    """
                    response = model.generate_content(prompt)
                    json_match_obj = re.search(r"\{.*\}", response.text, re.DOTALL)
                    
                    if json_match_obj:
                        res_json = json.loads(json_match_obj.group())
                        
                        # リスト更新と重複防止、UI用ID付与
                        list_keys = ["teachers", "students", "activities", "nisbahs", "family", "institutions"]
                        for k in list_keys:
                            if k in res_json:
                                for item in res_json[k]:
                                    item["ui_id"] = str(uuid.uuid4())
                                d[k] = res_json[k]
                        
                        # その他のフィールド更新
                        for field in ["original_id", "full_name", "name_only", "birth_h", "death_h", "translation_jp", "translation_en"]:
                            if field in res_json:
                                d[field] = res_json[field]
                        
                        d["birth_g"] = convert_h_to_g(d["birth_h"])
                        d["death_g"] = convert_h_to_g(d["death_h"])
                        
                        st.success("解析完了")
                        st.rerun()
                except Exception as e:
                    st.error(f"解析エラー: {e}")

    if d.get("translation_jp") or d.get("translation_en"):
        t_tab1, t_tab2 = st.tabs(["🇯🇵 日本語訳", "🇺🇸 English"])
        with t_tab1: st.info(d["translation_jp"])
        with t_tab2: st.info(d["translation_en"])

# --- 4. UI: エディタエリア ---
with col2:
    st.header("2. Metadata Editor")
    
    c1, c2 = st.columns(2)
    d["aind_id"] = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])
    d["full_name"] = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"] = st.text_input("persName (Ism/Father/GF)", d["name_only"])

    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    d["birth_g"] = dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]))
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    d["death_g"] = dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]))

    m_col1, m_col2 = st.columns(2)
    selected_m = m_col1.selectbox("⚖️ Madhhab", options=list(MADHHAB_DATA.keys()), 
                                  index=list(MADHHAB_DATA.keys()).index(d["madhhab"]["lat"]) if d["madhhab"]["lat"] in MADHHAB_DATA else 4)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}
    m_col2.text_input("Wikidata ID", d["madhhab"]["id"], disabled=True)

    # Teachers
    st.divider()
    st.subheader("🎓 Teachers & Subjects")
    for i, item in enumerate(d.get("teachers", [])):
        if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]
        
        # 5列作成
        r = st.columns([1, 1, 1, 1, 0.3])
        
        # 各カラム〜 を指定して入力欄を作る
        item["name"] = r.text_input("n", item.get("name"), key=f"t_n_{uid}", label_visibility="collapsed")
        item["id"] = r.text_input("i", item.get("id"), key=f"t_i_{uid}", label_visibility="collapsed")
        item["subject"] = r.text_input("s", item.get("subject"), key=f"t_s_{uid}", label_visibility="collapsed")
        item["subject_id"] = r.text_input("si", item.get("subject_id"), key=f"t_si_{uid}", label_visibility="collapsed")
        
        if r.button("❌", key=f"t_del_{uid}"):
            d["teachers"].pop(i)
            st.rerun()

    # Students
    st.divider()
    st.subheader("🧑‍🎓 Students & Subjects")
    for i, item in enumerate(d.get("students", [])):
        if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]
        
        # 5列作成
        r = st.columns([1, 1, 1, 1, 0.3])
        
        # 同様に〜 を指定
        item["name"] = r.text_input("n", item.get("name"), key=f"s_n_{uid}", label_visibility="collapsed")
        item["id"] = r.text_input("i", item.get("id"), key=f"s_i_{uid}", label_visibility="collapsed")
        item["subject"] = r.text_input("s", item.get("subject"), key=f"s_s_{uid}", label_visibility="collapsed")
        item["subject_id"] = r.text_input("si", item.get("subject_id"), key=f"s_si_{uid}", label_visibility="collapsed")
        
        if r.button("❌", key=f"s_del_{uid}"):
            d["students"].pop(i)
            st.rerun()

    # NISBAHS, ACTIVITIES, FAMILY, INSTITUTIONS
    sections = [
        ("📝 Nisbahs", "nisbahs", ["ar", "lat", "id"], "TMP-L-00000"),
        ("📍 Activities", "activities", ["place_ar", "place_lat", "type", "id"], "TMP-L-00000"),
        ("👥 Family", "family", ["name", "relation", "id"], "TMP-P-00000"),
        ("🕌 Institutions", "institutions", ["name", "id"], "TMP-O-00000")
    ]
    for title, key, fields, def_id in sections:
        st.divider()
        st.subheader(title)
        for i, item in enumerate(d.get(key, [])):
            if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
            uid = item["ui_id"]
            cols = st.columns(len(fields) + 1)
            for j, f in enumerate(fields):
                val = item.get(f, def_id if f=="id" else "")
                item[f] = cols[j].text_input(f, val, key=f"{key}_{f}_{uid}", label_visibility="collapsed")
            if cols[-1].button("❌", key=f"{key}_del_{uid}"):
                d[key].pop(i); st.rerun()
        if st.button(f"＋ add {title}", key=f"add_{key}"):
            d[key].append({"ui_id": str(uuid.uuid4()), **{f: (def_id if f=="id" else "") for f in fields}}); st.rerun()

# --- 5. XML Export ---
st.divider()
st.header("3. TEI-XML Export")

def fr(rid):
    if not rid: return ""
    rid = str(rid).strip()
    if rid.startswith("TMP-"): return f"#{rid}"
    if rid.startswith("Q"): return f"wd:{rid}"
    if "GeoNames_" in rid: return f"gn:{rid.replace('GeoNames_', '')}"
    if rid.isdigit(): return f"gn:{rid}"
    return rid

xml_str = f'<person @xml:id="{d["aind_id"]}" @source="#source_{d["original_id"]}">\n'
xml_str += f'    <persName @type="full" @xml:lang="ar">{d["full_name"]}</persName>\n'
xml_str += f'    <persName @type="name_only" @xml:lang="ar">{d["name_only"]}</persName>\n'
for n in d.get("nisbahs", []):
    if n.get("ar"): xml_str += f'    <persName @type="nisbah" @xml:lang="ar" @ref="{fr(n.get("id"))}">{n.get("ar")}</persName>\n'
xml_str += f'    <affiliation @type="madhhab" @ref="wd:{d["madhhab"]["id"]}">{d["madhhab"]["lat"]}</affiliation>\n'
xml_str += '    <listRelation>\n'
for t in d.get("teachers", []):
    xml_str += f'        <relation @name="teacher" @active="{fr(t.get("id"))}" @passive="#{d["aind_id"]}">\n'
    if t.get("subject"): xml_str += f'            <desc @ref="{fr(t.get("subject_id"))}">{t.get("subject")}</desc>\n'
    xml_str += '        </relation>\n'
for s in d.get("students", []):
    xml_str += f'        <relation @name="student" @active="#{d["aind_id"]}" @passive="{fr(s.get("id"))}">\n'
    if s.get("subject"): xml_str += f'            <desc @ref="{fr(s.get("subject_id"))}">{s.get("subject")}</desc>\n'
    xml_str += '        </relation>\n'
for f in d.get("family", []):
    xml_str += f'        <relation @name="family" @active="{fr(f.get("id"))}" @passive="#{d["aind_id"]}" @subtype="{f.get("relation")}">{f.get("name")}</relation>\n'
xml_str += '    </listRelation>\n'
for a in d.get("activities", []):
    if a.get("place_ar"): xml_str += f'    <residence @subtype="{a.get("type")}" @ref="{fr(a.get("id"))}">{a.get("place_ar")}</residence>\n'
for i in d.get("institutions", []):
    if i.get("name"): xml_str += f'    <affiliation @type="institution" @ref="{fr(i.get("id"))}">{i.get("name")}</affiliation>\n'
xml_str += f"    <note @type='translation' @xml:lang='ja'>{d['translation_jp']}</note>\n"
xml_str += f"    <note @type='translation' @xml:lang='en'>{d['translation_en']}</note>\n"
xml_str += "</person>"

st.code(xml_str, language="xml")
