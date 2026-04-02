import streamlit as st
import google.generativeai as genai
import json
import re
import uuid

# --- 1. ページ設定 ---
st.set_page_config(page_title="AINet-DB Pro (Bilingual Translation)", layout="wide")

# --- 2. API設定 & モデル自動検知 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m]
        if flash_models:
            return genai.GenerativeModel(flash_models[-1])
        elif models:
            return genai.GenerativeModel(models[0])
    except Exception:
        return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ユーティリティ関数 ---
def convert_h_to_g(h_year):
    try:
        h_clean = re.sub(r"\D", "", str(h_year))
        if not h_clean:
            return ""
        h = int(h_clean)
        return str(int(h * 0.97 + 622))
    except Exception:
        return ""

def fr(rid):
    if not rid:
        return ""
    rid = str(rid).strip()
    if rid.startswith("TMP-"):
        return f"#{rid}"
    if rid.startswith("Q"):
        return f"wd:{rid}"
    if "GeoNames_" in rid:
        return f"gn:{rid.replace('GeoNames_', '')}"
    if rid.isdigit():
        return f"gn:{rid}"
    return rid

# --- 4. データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

# --- 5. セッション状態の初期化 ---
if 'data_v14' not in st.session_state:
    st.session_state.data_v14 = {
        "aind_id": "AIND-D0000",
        "original_id": "",
        "full_name": "",
        "name_only": "",
        "full_name_lat": "",
        "sex": "Male",
        "certainty": "High",
        "birth_h": "",
        "birth_g": "",
        "death_h": "",
        "death_g": "",
        "madhhab": {"lat": "Unknown / Other", "id": ""},
        "nisbahs": [],
        "activities": [],
        "teachers": [],
        "students": [],
        "institutions": [],
        "family": [],
        "source_text": "",
        "translation_jp": "",
        "translation_en": ""
    }

d = st.session_state.data_v14

# ===================================================
# --- 6. メインUI ---
# ===================================================
st.title("🌙 AINet-DB Researcher Pro")

col1, col2 = st.columns([1, 1.5])

# ===================================================
# --- 左カラム: 史料解析 ---
# ===================================================
with col1:
    st.header("1. Source & Bilingual Analysis")

    source_input = st.text_area(
        "史料テキスト (Arabic)",
        value=d["source_text"],
        height=400
    )

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
    "original_id": "",
    "full_name": "",
    "name_only": "",
    "birth_h": "",
    "death_h": "",
    "madhhab_name": "",
    "nisbahs": [{{"ar": "", "lat": "", "id": "TMP-L-00000"}}],
    "activities": [{{"place_ar": "", "place_lat": "", "type": "study/buried/reside/visit", "id": "GeoNames_ID"}}],
    "teachers": [{{"name": "", "id": "TMP-P-00000", "subject": "", "subject_id": "TMP-S-00000"}}],
    "students": [{{"name": "", "id": "TMP-P-00000", "subject": "", "subject_id": "TMP-S-00000"}}],
    "institutions": [{{"name": "", "id": "Wikidata_ID"}}],
    "translation_jp": "",
    "translation_en": ""
}}
Text: {source_input}
"""
                    response = model.generate_content(prompt)
                    json_match_obj = re.search(r"\{.*\}", response.text, re.DOTALL)

                    if json_match_obj:
                        res_json = json.loads(json_match_obj.group())

                        # リスト更新（ui_id付与）
                        list_keys = ["teachers", "students", "activities", "nisbahs", "family", "institutions"]
                        for k in list_keys:
                            if k in res_json:
                                for item in res_json[k]:
                                    item["ui_id"] = str(uuid.uuid4())
                                d[k] = res_json[k]

                        # スカラーフィールド更新
                        for field in ["original_id", "full_name", "name_only", "birth_h", "death_h", "translation_jp", "translation_en"]:
                            if field in res_json:
                                d[field] = res_json[field]

                        d["birth_g"] = convert_h_to_g(d["birth_h"])
                        d["death_g"] = convert_h_to_g(d["death_h"])

                        st.success("解析完了")
                        st.rerun()
                    else:
                        st.error("JSONの抽出に失敗しました。")

                except Exception as e:
                    st.error(f"解析エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

    # 翻訳表示
    if d.get("translation_jp") or d.get("translation_en"):
        t_tab1, t_tab2 = st.tabs(["🇯🇵 日本語訳", "🇺🇸 English"])
        with t_tab1:
            st.info(d["translation_jp"])
        with t_tab2:
            st.info(d["translation_en"])


# ===================================================
# --- 右カラム: メタデータエディタ ---
# ===================================================
with col2:
    st.header("2. Metadata Editor")

    # --- 基本情報 ---
    c1, c2 = st.columns(2)
    d["aind_id"]     = c1.text_input("@xml:id", d["aind_id"])
    d["original_id"] = c2.text_input("@source", d["original_id"])

    d["full_name"]  = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"]  = st.text_input("persName (Ism/Father/GF)", d["name_only"])

    # --- 生没年 ---
    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]), disabled=True)
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]), disabled=True)

    # --- Madhhab ---
    m_col1, m_col2 = st.columns(2)
    madhhab_keys = list(MADHHAB_DATA.keys())
    current_madhhab = d["madhhab"]["lat"]
    default_index = madhhab_keys.index(current_madhhab) if current_madhhab in madhhab_keys else 4

    selected_m = m_col1.selectbox("⚖️ Madhhab", options=madhhab_keys, index=default_index)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}
    m_col2.text_input("Wikidata ID", value=d["madhhab"]["id"], disabled=True)

    # ===================================================
    # --- Teachers セクション ---
    # ===================================================
    st.divider()
    st.subheader("🎓 Teachers & Subjects")

    # ヘッダー行
    h = st.columns([1, 1, 1, 1, 0.3])
    h[0].caption("Name")
    h[1].caption("Person ID")
    h[2].caption("Subject")
    h[3].caption("Subject ID")
    h[4].caption("Del")

    for i, item in enumerate(d.get("teachers", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 1, 0.3])
        item["name"]       = r[0].text_input("name",    item.get("name", ""),       key=f"t_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r[1].text_input("id",      item.get("id", ""),         key=f"t_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r[2].text_input("subject", item.get("subject", ""),    key=f"t_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r[3].text_input("sid",     item.get("subject_id", ""), key=f"t_si_{uid}", label_visibility="collapsed")
        if r[4].button("❌", key=f"t_del_{uid}"):
            d["teachers"].pop(i)
            st.rerun()

    if st.button("＋ add teacher"):
        d["teachers"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "",
            "id": "TMP-P-00000",
            "subject": "",
            "subject_id": "TMP-S-00000"
        })
        st.rerun()

    # ===================================================
    # --- Students セクション ---
    # ===================================================
    st.divider()
    st.subheader("🧑‍🎓 Students & Subjects")

    # ヘッダー行
    h2 = st.columns([1, 1, 1, 1, 0.3])
    h2[0].caption("Name")
    h2[1].caption("Person ID")
    h2[2].caption("Subject")
    h2[3].caption("Subject ID")
    h2[4].caption("Del")

    for i, item in enumerate(d.get("students", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 1, 0.3])
        item["name"]       = r[0].text_input("name",    item.get("name", ""),       key=f"s_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r[1].text_input("id",      item.get("id", ""),         key=f"s_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r[2].text_input("subject", item.get("subject", ""),    key=f"s_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r[3].text_input("sid",     item.get("subject_id", ""), key=f"s_si_{uid}", label_visibility="collapsed")
        if r[4].button("❌", key=f"s_del_{uid}"):
            d["students"].pop(i)
            st.rerun()

    if st.button("＋ add student"):
        d["students"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "",
            "id": "TMP-P-00000",
            "subject": "",
            "subject_id": "TMP-S-00000"
        })
        st.rerun()

    # ===================================================
    # --- Nisbahs セクション ---
    # ===================================================
    st.divider()
    st.subheader("🏷️ Nisbahs")

    h3 = st.columns([1, 1, 1, 0.3])
    h3[0].caption("Arabic")
    h3[1].caption("Latinized")
    h3[2].caption("ID")
    h3[3].caption("Del")

    for i, item in enumerate(d.get("nisbahs", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 0.3])
        item["ar"]  = r[0].text_input("ar",  item.get("ar", ""),  key=f"n_a_{uid}", label_visibility="collapsed")
        item["lat"] = r[1].text_input("lat", item.get("lat", ""), key=f"n_l_{uid}", label_visibility="collapsed")
        item["id"]  = r[2].text_input("id",  item.get("id", ""),  key=f"n_i_{uid}", label_visibility="collapsed")
        if r[3].button("❌", key=f"n_del_{uid}"):
            d["nisbahs"].pop(i)
            st.rerun()

    if st.button("＋ add nisbah"):
        d["nisbahs"].append({
            "ui_id": str(uuid.uuid4()),
            "ar": "",
            "lat": "",
            "id": "TMP-L-00000"
        })
        st.rerun()

    # ===================================================
    # --- Activities セクション ---
    # ===================================================
    st.divider()
    st.subheader("📍 Activities / Places")

    h4 = st.columns([1, 1, 1, 1, 0.3])
    h4[0].caption("Place (Arabic)")
    h4[1].caption("Place (Latin)")
    h4[2].caption("Type")
    h4[3].caption("GeoNames ID")
    h4[4].caption("Del")

    activity_types = ["study", "buried", "reside", "visit", "born", "died", "other"]

    for i, item in enumerate(d.get("activities", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 1, 0.3])
        item["place_ar"]  = r[0].text_input("place_ar",  item.get("place_ar", ""),  key=f"a_a_{uid}", label_visibility="collapsed")
        item["place_lat"] = r[1].text_input("place_lat", item.get("place_lat", ""), key=f"a_l_{uid}", label_visibility="collapsed")
        current_type = item.get("type", "study")
        type_index = activity_types.index(current_type) if current_type in activity_types else 0
        item["type"] = r[2].selectbox("type", activity_types, index=type_index, key=f"a_t_{uid}", label_visibility="collapsed")
        item["id"]   = r[3].text_input("id", item.get("id", ""), key=f"a_i_{uid}", label_visibility="collapsed")
        if r[4].button("❌", key=f"a_del_{uid}"):
            d["activities"].pop(i)
            st.rerun()

    if st.button("＋ add activity"):
        d["activities"].append({
            "ui_id": str(uuid.uuid4()),
            "place_ar": "",
            "place_lat": "",
            "type": "study",
            "id": ""
        })
        st.rerun()

    # ===================================================
    # --- Institutions セクション ---
    # ===================================================
    st.divider()
    st.subheader("🏛️ Institutions")

    h5 = st.columns([2, 1, 0.3])
    h5[0].caption("Name")
    h5[1].caption("Wikidata ID")
    h5[2].caption("Del")

    for i, item in enumerate(d.get("institutions", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([2, 1, 0.3])
        item["name"] = r[0].text_input("name", item.get("name", ""), key=f"i_n_{uid}", label_visibility="collapsed")
        item["id"]   = r[1].text_input("id",   item.get("id", ""),   key=f"i_i_{uid}", label_visibility="collapsed")
        if r[2].button("❌", key=f"i_del_{uid}"):
            d["institutions"].pop(i)
            st.rerun()

    if st.button("＋ add institution"):
        d["institutions"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "",
            "id": ""
        })
        st.rerun()

    # ===================================================
    # --- Family セクション ---
    # ===================================================
    st.divider()
    st.subheader("👨‍👩‍👧 Family Relations")

    h6 = st.columns([1, 1, 1, 0.3])
    h6[0].caption("Name")
    h6[1].caption("Relation")
    h6[2].caption("Person ID")
    h6[3].caption("Del")

    for i, item in enumerate(d.get("family", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 0.3])
        item["name"]     = r[0].text_input("name",     item.get("name", ""),     key=f"f_n_{uid}", label_visibility="collapsed")
        item["relation"] = r[1].text_input("relation", item.get("relation", ""), key=f"f_r_{uid}", label_visibility="collapsed")
        item["id"]       = r[2].text_input("id",       item.get("id", ""),       key=f"f_i_{uid}", label_visibility="collapsed")
        if r[3].button("❌", key=f"f_del_{uid}"):
            d["family"].pop(i)
            st.rerun()

    if st.button("＋ add family member"):
        d["family"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "",
            "relation": "",
            "id": "TMP-P-00000"
        })
        st.rerun()


# ===================================================
# --- 7. TEI-XML エクスポート ---
# ===================================================
st.divider()
st.header("3. TEI-XML Export")

xml_lines = []
xml_lines.append(f'<person @xml:id="{d["aind_id"]}" @source="#source_{d["original_id"]}">')
xml_lines.append(f'    <persName @type="full" @xml:lang="ar">{d["full_name"]}</persName>')
xml_lines.append(f'    <persName @type="name_only" @xml:lang="ar">{d["name_only"]}</persName>')

for n in d.get("nisbahs", []):
    if n.get("ar"):
        xml_lines.append(f'    <persName @type="nisbah" @xml:lang="ar" @ref="{fr(n.get("id"))}">{n.get("ar")}</persName>')

if d["madhhab"]["id"]:
    xml_lines.append(f'    <affiliation @type="madhhab" @ref="wd:{d["madhhab"]["id"]}">{d["madhhab"]["lat"]}</affiliation>')

if d.get("birth_h") or d.get("birth_g"):
    xml_lines.append(f'    <birth @when-custom="{d["birth_h"]}" @when="{convert_h_to_g(d["birth_h"])}"/>')

if d.get("death_h") or d.get("death_g"):
    xml_lines.append(f'    <death @when-custom="{d["death_h"]}" @when="{convert_h_to_g(d["death_h"])}"/>')

xml_lines.append('    <listRelation>')

for t in d.get("teachers", []):
    xml_lines.append(f'        <relation @name="teacher" @active="{fr(t.get("id"))}" @passive="#{d["aind_id"]}">')
    if t.get("subject"):
        xml_lines.append(f'            <desc @ref="{fr(t.get("subject_id"))}">{t.get("subject")}</desc>')
    xml_lines.append('        </relation>')

for s in d.get("students", []):
    xml_lines.append(f'        <relation @name="student" @active="#{d["aind_id"]}" @passive="{fr(s.get("id"))}">')
    if s.get("subject"):
        xml_lines.append(f'            <desc @ref="{fr(s.get("subject_id"))}">{s.get("subject")}</desc>')
    xml_lines.append('        </relation>')

for fam in d.get("family", []):
    xml_lines.append(f'        <relation @name="family" @active="{fr(fam.get("id"))}" @passive="#{d["aind_id"]}" @subtype="{fam.get("relation", "")}">{fam.get("name", "")}</relation>')

xml_lines.append('    </listRelation>')

for a in d.get("activities", []):
    if a.get("place_ar"):
        xml_lines.append(f'    <residence @subtype="{a.get("type", "")}" @ref="{fr(a.get("id"))}">{a.get("place_ar")}</residence>')

for inst in d.get("institutions", []):
    if inst.get("name"):
        xml_lines.append(f'    <affiliation @type="institution" @ref="{fr(inst.get("id"))}">{inst.get("name")}</affiliation>')

if d.get("translation_jp"):
    xml_lines.append(f'    <note @type="translation" @xml:lang="ja">{d["translation_jp"]}</note>')
if d.get("translation_en"):
    xml_lines.append(f'    <note @type="translation" @xml:lang="en">{d["translation_en"]}</note>')

xml_lines.append("</person>")

xml_str = "\n".join(xml_lines)
st.code(xml_str, language="xml")

# ダウンロードボタン
st.download_button(
    label="💾 XMLをダウンロード",
    data=xml_str,
    file_name=f"{d['aind_id']}.xml",
    mime="application/xml"
)
