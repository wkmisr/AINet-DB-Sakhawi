import streamlit as st
import google.generativeai as genai
import json
import re
import uuid

# --- 1. ページ設定 ---
st.set_page_config(page_title="AINet-DB Pro (Bilingual Translation)", layout="wide", initial_sidebar_state="expanded")

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
    if rid.startswith("Q") and rid[1:].isdigit():
        return f"wd:{rid}"
    if "GeoNames_" in rid:
        return f"gn:{rid.replace('GeoNames_', '')}"
    if rid.isdigit():
        return f"gn:{rid}"
    return rid

def move_item(lst, index, direction):
    new_index = index + direction
    if 0 <= new_index < len(lst):
        lst[index], lst[new_index] = lst[new_index], lst[index]

# --- 4. 定数 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}
INSTITUTION_TYPES = ["study", "teach", "reside", "founded", "affiliated", "graduated", "employed", "visit", "other"]
ACTIVITY_TYPES    = ["study", "buried", "reside", "visit", "born", "died", "other"]
LAQAB_TYPES       = ["laqab", "shuhrah", "kunyah"]
LAQAB_LABELS      = {"laqab": "laqab（号）", "shuhrah": "shuhrah（通称）", "kunyah": "kunyah（クンヤ）"}

# --- 5. セッション状態の初期化 ---
if 'data_v17' not in st.session_state:
    st.session_state.data_v17 = {
        "aind_id": "AIND-D0000", "original_id": "",
        "full_name": "", "name_only": "", "full_name_lat": "",
        "sex": "Male", "certainty": "High",
        "birth_h": "", "birth_g": "", "death_h": "", "death_g": "",
        "madhhab": {"lat": "Unknown / Other", "id": "", "custom_name": "", "custom_id": ""},
        "sufi_order": {"name": "", "id": ""},
        "nisbahs": [], "laqabs": [],
        "activities": [], "teachers": [], "students": [],
        "institutions": [], "offices": [], "family": [],
        "person_notes": "",
        "source_text": "", "translation_jp": "", "translation_en": ""
    }

d = st.session_state.data_v17

# ===================================================
# --- 6. メインUI ---
# ===================================================



st.title("🌙 AINet-DB Researcher Pro")

# ===================================================
# --- サイドバー: 史料解析 ---
# ===================================================
with st.sidebar:
    st.header("1. Source & Bilingual Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=400)

    if st.button("🔍 解析する"):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("解析中..."):
                try:
                    model = get_working_model()
                    prompt = f"""
You are a professional historian of Islamic studies. Extract data from the source text into JSON.

【Translation】
- translation_jp: Accurate academic Japanese translation of the full text.
- translation_en: Accurate academic English translation of the full text.

【ID Rules】
- Places: GeoNames numeric ID if known (e.g. "104515"). Otherwise "TMP-L-00000".
- Institutions: Wikidata Q-ID if known. Otherwise "TMP-I-00000".
- Offices: Wikidata Q-ID if known. Otherwise "TMP-O-00000".
- Persons: Wikidata Q-ID if known. Otherwise "TMP-P-00000".

【Laqab / Shuhrah / Kunyah】
- laqab: honorific title (e.g. زين الدين).
- shuhrah: popular epithet.
- kunyah: teknonym starting with أبو / أم.

【Teachers / Students】
- subject: discipline (e.g. "Hadith", "Fiqh").
- subject_id: TMP-S-00000 unless known.
- text_ar / text_lat: book title if mentioned, else empty.
- learn_date: date or year of learning if mentioned, else empty.
- learn_place_ar / learn_place_lat: place of learning if mentioned.
- learn_place_id: GeoNames ID or TMP-L-00000.

【Institutions】
- Record named institutions (madrasa, mosque, library, etc.) and the person's relationship to them.
- Do NOT include here mere city/region stays without a named institution (use activities instead).
- In ORDER they appear. seq starts at 1.
- type: study|teach|reside|founded|affiliated|graduated|employed|visit|other

【Offices】
- In ORDER held. seq starts at 1.
- place_ar / place_lat / place_id: city/region if mentioned.
- inst_name / inst_id: institution if mentioned.
- appoint_date / retire_date: dates if mentioned.

【Activities / Places】
- Record GEOGRAPHIC events only: birth, death, burial, residence, travel.
- Do NOT include institutional affiliations here (use institutions instead).
- In ORDER they appear. seq starts at 1.

Return ONLY valid JSON, NO markdown fences:
{{
    "original_id": "", "full_name": "", "name_only": "",
    "birth_h": "", "death_h": "", "madhhab_name": "",
    "nisbahs": [{{"ar": "", "lat": "", "id": "TMP-L-00000"}}],
    "laqabs": [{{"type": "laqab", "ar": "", "lat": ""}}],
    "activities": [{{"seq": 1, "place_ar": "", "place_lat": "", "type": "study", "id": ""}}],
    "teachers": [{{
        "name": "", "id": "TMP-P-00000",
        "subject": "", "subject_id": "TMP-S-00000",
        "text_ar": "", "text_lat": "",
        "learn_date": "", "learn_place_ar": "", "learn_place_lat": "", "learn_place_id": ""
    }}],
    "students": [{{
        "name": "", "id": "TMP-P-00000",
        "subject": "", "subject_id": "TMP-S-00000",
        "text_ar": "", "text_lat": "",
        "teach_date": "", "teach_place_ar": "", "teach_place_lat": "", "teach_place_id": ""
    }}],
    "institutions": [{{"seq": 1, "name_ar": "", "name_lat": "", "type": "study", "id": "TMP-I-00000"}}],
    "offices": [{{
        "seq": 1, "name_ar": "", "name_lat": "", "id": "TMP-O-00000",
        "place_ar": "", "place_lat": "", "place_id": "",
        "inst_name": "", "inst_id": "",
        "appoint_date": "", "retire_date": ""
    }}],
    "translation_jp": "", "translation_en": ""
}}
Text: {source_input}
"""
                    response = model.generate_content(prompt)
                    raw = re.sub(r"```json|```", "", response.text).strip()
                    m = re.search(r"\{.*\}", raw, re.DOTALL)
                    if m:
                        res = json.loads(m.group())
                        for k in ["teachers","students","activities","nisbahs","laqabs","family","institutions","offices"]:
                            if k in res:
                                for item in res[k]:
                                    item["ui_id"] = str(uuid.uuid4())
                                d[k] = res[k]
                        for f in ["original_id","full_name","name_only","birth_h","death_h","translation_jp","translation_en"]:
                            if f in res:
                                d[f] = res[f]
                        d["birth_g"] = convert_h_to_g(d["birth_h"])
                        d["death_g"] = convert_h_to_g(d["death_h"])
                        st.success("解析完了")
                        st.rerun()
                    else:
                        st.error("JSONの抽出に失敗しました。")
                        st.text(response.text[:500])
                except Exception as e:
                    st.error(f"解析エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

    if d.get("translation_jp") or d.get("translation_en"):
        t1, t2 = st.tabs(["🇯🇵 日本語訳", "🇺🇸 English"])
        with t1: st.info(d["translation_jp"])
        with t2: st.info(d["translation_en"])


# ===================================================
# --- メタデータエディタ ---
# ===================================================
st.header("2. Metadata Editor")

# --- 基本情報 ---
c1, c2 = st.columns(2)
d["aind_id"]     = c1.text_input("@xml:id", d["aind_id"])
d["original_id"] = c2.text_input("@source", d["original_id"])
d["full_name"]   = st.text_input("persName (Full Arabic)", d["full_name"])
d["name_only"]   = st.text_input("persName (Ism/Father/GF)", d["name_only"])

# ===================================================
# --- Nisbahs ---
# ===================================================
st.divider()
st.subheader("🏷️ Nisbahs")
nh = st.columns([1, 1, 1, 0.3])
nh[0].caption("Arabic"); nh[1].caption("Latinized"); nh[2].caption("ID (TMP-L- / Q)"); nh[3].caption("Del")
for i, item in enumerate(d.get("nisbahs", [])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1, 1, 1, 0.3])
    item["ar"]  = r[0].text_input("ar",  item.get("ar",""),  key=f"n_a_{uid}", label_visibility="collapsed")
    item["lat"] = r[1].text_input("lat", item.get("lat",""), key=f"n_l_{uid}", label_visibility="collapsed")
    item["id"]  = r[2].text_input("id",  item.get("id",""),  key=f"n_i_{uid}", label_visibility="collapsed", placeholder="TMP-L-00001 / Q数字")
    if r[3].button("❌", key=f"n_del_{uid}"):
        d["nisbahs"].pop(i); st.rerun()
if st.button("＋ add nisbah"):
    d["nisbahs"].append({"ui_id": str(uuid.uuid4()), "ar": "", "lat": "", "id": "TMP-L-00000"}); st.rerun()

# ===================================================
# --- Laqab / Shuhrah / Kunyah ---
# ===================================================
st.divider()
st.subheader("🔤 Laqab / Shuhrah / Kunyah")
lh = st.columns([1, 1, 1, 0.3])
lh[0].caption("Type"); lh[1].caption("Arabic"); lh[2].caption("Latinized"); lh[3].caption("Del")
for i, item in enumerate(d.get("laqabs", [])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1, 1, 1, 0.3])
    cur = item.get("type","laqab")
    item["type"] = r[0].selectbox("type", LAQAB_TYPES, format_func=lambda x: LAQAB_LABELS[x],
                                   index=LAQAB_TYPES.index(cur) if cur in LAQAB_TYPES else 0,
                                   key=f"lq_t_{uid}", label_visibility="collapsed")
    item["ar"]  = r[1].text_input("ar",  item.get("ar",""),  key=f"lq_a_{uid}", label_visibility="collapsed", placeholder="例: زين الدين / أبو بكر")
    item["lat"] = r[2].text_input("lat", item.get("lat",""), key=f"lq_l_{uid}", label_visibility="collapsed", placeholder="例: Zayn al-Din / Abu Bakr")
    if r[3].button("❌", key=f"lq_del_{uid}"):
        d["laqabs"].pop(i); st.rerun()
if st.button("＋ add laqab / shuhrah / kunyah"):
    d["laqabs"].append({"ui_id": str(uuid.uuid4()), "type": "laqab", "ar": "", "lat": ""}); st.rerun()

# --- 生没年 ---
st.divider()
dc1, dc2, dc3, dc4 = st.columns(4)
d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]), disabled=True)
d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]), disabled=True)

# ===================================================
# --- Madhhab ---
# ===================================================
st.divider()
madhhab_keys = list(MADHHAB_DATA.keys())
cur_m = d["madhhab"]["lat"]
def_idx = madhhab_keys.index(cur_m) if cur_m in madhhab_keys else 4
m_col1, m_col2 = st.columns(2)
selected_m = m_col1.selectbox("⚖️ Madhhab", options=madhhab_keys, index=def_idx)
wikidata_id = MADHHAB_DATA[selected_m]
m_col2.text_input("Wikidata ID", value=wikidata_id, disabled=True)

if selected_m == "Unknown / Other":
    uo1, uo2 = st.columns(2)
    custom_name = uo1.text_input("Madhhab name (free text)", value=d["madhhab"].get("custom_name",""), key="madhhab_custom_name")
    custom_id   = uo2.text_input("Madhhab ID (TMP- / Q)", value=d["madhhab"].get("custom_id",""), key="madhhab_custom_id")
    d["madhhab"] = {"lat": selected_m, "id": "", "custom_name": custom_name, "custom_id": custom_id}
else:
    d["madhhab"] = {"lat": selected_m, "id": wikidata_id, "custom_name": "", "custom_id": ""}

# ===================================================
# --- Sufi Order ---
# ===================================================
st.divider()
st.subheader("☪️ Sufi Order")
sf1, sf2 = st.columns(2)
d["sufi_order"]["name"] = sf1.text_input("Sufi Order (free text)", value=d["sufi_order"].get("name",""), placeholder="例: Qadiriyya / القادرية")
d["sufi_order"]["id"]   = sf2.text_input("Sufi Order ID (Q / TMP-)", value=d["sufi_order"].get("id",""),  placeholder="例: Q123456 / TMP-O-00001")

# ===================================================
# --- Teachers ---
# ===================================================
st.divider()
st.subheader("🎓 Teachers & Subjects")
for i, item in enumerate(d.get("teachers", [])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        # 行1: Name / Person ID / Subject / Subject ID / Del
        r1 = st.columns([1.2, 1, 1, 1, 0.3])
        r1[0].caption("Name"); r1[1].caption("Person ID"); r1[2].caption("Subject"); r1[3].caption("Subject ID")
        item["name"]       = r1[0].text_input("Name",      item.get("name",""),       key=f"t_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r1[1].text_input("PID",       item.get("id",""),         key=f"t_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r1[2].text_input("Subject",   item.get("subject",""),    key=f"t_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r1[3].text_input("SID",       item.get("subject_id",""), key=f"t_si_{uid}", label_visibility="collapsed")
        if r1[4].button("❌", key=f"t_del_{uid}"):
            d["teachers"].pop(i); st.rerun()
        # 行2: Text (Arabic) / Text (Latinized)
        r2 = st.columns([1, 1])
        r2[0].caption("📖 Text (Arabic)"); r2[1].caption("📖 Text (Latinized)")
        item["text_ar"]  = r2[0].text_input("text_ar",  item.get("text_ar",""),  key=f"t_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r2[1].text_input("text_lat", item.get("text_lat",""), key=f"t_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        # 行3: Learning Date / Place (Arabic) / Place (Latin) / Place ID
        r3 = st.columns([1, 1, 1, 1])
        r3[0].caption("📅 Learning Date"); r3[1].caption("📍 Place (Arabic)"); r3[2].caption("📍 Place (Latin)"); r3[3].caption("Place ID")
        item["learn_date"]      = r3[0].text_input("ldate", item.get("learn_date",""),      key=f"t_ld_{uid}", label_visibility="collapsed", placeholder="例: 880H / 1475CE")
        item["learn_place_ar"]  = r3[1].text_input("lpar",  item.get("learn_place_ar",""),  key=f"t_lpa_{uid}", label_visibility="collapsed")
        item["learn_place_lat"] = r3[2].text_input("lplat", item.get("learn_place_lat",""), key=f"t_lpl_{uid}", label_visibility="collapsed")
        item["learn_place_id"]  = r3[3].text_input("lpid",  item.get("learn_place_id",""),  key=f"t_lpi_{uid}", label_visibility="collapsed", placeholder="GeoNames / TMP-L-")
    st.markdown("---")
if st.button("＋ add teacher"):
    d["teachers"].append({"ui_id": str(uuid.uuid4()), "name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000","text_ar":"","text_lat":"",
        "learn_date":"","learn_place_ar":"","learn_place_lat":"","learn_place_id":""}); st.rerun()

# ===================================================
# --- Students ---
# ===================================================
st.divider()
st.subheader("🧑‍🎓 Students & Subjects")
for i, item in enumerate(d.get("students", [])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        r1 = st.columns([1.2, 1, 1, 1, 0.3])
        r1[0].caption("Name"); r1[1].caption("Person ID"); r1[2].caption("Subject"); r1[3].caption("Subject ID")
        item["name"]       = r1[0].text_input("Name",    item.get("name",""),       key=f"s_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r1[1].text_input("PID",     item.get("id",""),         key=f"s_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r1[2].text_input("Subject", item.get("subject",""),    key=f"s_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r1[3].text_input("SID",     item.get("subject_id",""), key=f"s_si_{uid}", label_visibility="collapsed")
        if r1[4].button("❌", key=f"s_del_{uid}"):
            d["students"].pop(i); st.rerun()
        r2 = st.columns([1, 1])
        r2[0].caption("📖 Text (Arabic)"); r2[1].caption("📖 Text (Latinized)")
        item["text_ar"]  = r2[0].text_input("text_ar",  item.get("text_ar",""),  key=f"s_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r2[1].text_input("text_lat", item.get("text_lat",""), key=f"s_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        r3 = st.columns([1, 1, 1, 1])
        r3[0].caption("📅 Teaching Date"); r3[1].caption("📍 Place (Arabic)"); r3[2].caption("📍 Place (Latin)"); r3[3].caption("Place ID")
        item["teach_date"]      = r3[0].text_input("tdate", item.get("teach_date",""),      key=f"s_td_{uid}", label_visibility="collapsed", placeholder="例: 880H / 1475CE")
        item["teach_place_ar"]  = r3[1].text_input("tpar",  item.get("teach_place_ar",""),  key=f"s_tpa_{uid}", label_visibility="collapsed")
        item["teach_place_lat"] = r3[2].text_input("tplat", item.get("teach_place_lat",""), key=f"s_tpl_{uid}", label_visibility="collapsed")
        item["teach_place_id"]  = r3[3].text_input("tpid",  item.get("teach_place_id",""),  key=f"s_tpi_{uid}", label_visibility="collapsed", placeholder="GeoNames / TMP-L-")
    st.markdown("---")
if st.button("＋ add student"):
    d["students"].append({"ui_id": str(uuid.uuid4()), "name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000","text_ar":"","text_lat":"",
        "teach_date":"","teach_place_ar":"","teach_place_lat":"","teach_place_id":""}); st.rerun()

# ===================================================
# --- Activities ---
# ===================================================
st.divider()
st.subheader("📍 Activities / Places")
st.caption("機関名を伴わない地理的イベント（居住・移動・出生・死亡・埋葬など）を記録します。機関との関わりは Institutions へ。▲▼ で順番を入れ替えられます。")
acts = d.get("activities", [])
for i, item in enumerate(acts):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"act_up_{uid}", disabled=(i==0)):
                move_item(d["activities"], i, -1); st.rerun()
            if st.button("▼", key=f"act_dn_{uid}", disabled=(i==len(acts)-1)):
                move_item(d["activities"], i, +1); st.rerun()
        r = st.columns([1, 1, 1, 1.3, 0.3])
        r[0].caption("Place (Arabic)"); r[1].caption("Place (Latin)"); r[2].caption("Type"); r[3].caption("ID")
        item["place_ar"]  = r[0].text_input("par",  item.get("place_ar",""),  key=f"a_a_{uid}", label_visibility="collapsed")
        item["place_lat"] = r[1].text_input("plat", item.get("place_lat",""), key=f"a_l_{uid}", label_visibility="collapsed")
        ct = item.get("type","study")
        item["type"] = r[2].selectbox("type", ACTIVITY_TYPES, index=ACTIVITY_TYPES.index(ct) if ct in ACTIVITY_TYPES else 0, key=f"a_t_{uid}", label_visibility="collapsed")
        item["id"]   = r[3].text_input("id", item.get("id",""), key=f"a_i_{uid}", label_visibility="collapsed", placeholder="GeoNames / TMP-L- / Q")
        if r[4].button("❌", key=f"a_del_{uid}"):
            d["activities"].pop(i); st.rerun()
    st.markdown("---")
if st.button("＋ add activity"):
    d["activities"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["activities"])+1,"place_ar":"","place_lat":"","type":"study","id":""}); st.rerun()

# ===================================================
# --- Institutions ---
# ===================================================
st.divider()
st.subheader("🏛️ Institutions")
st.caption("特定の機関（マドラサ・モスク・図書館など）との関わりを記録します。単純な居住・移動は Activities へ。▲▼ で順番を入れ替えられます。")
insts = d.get("institutions", [])
for i, item in enumerate(insts):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    if "name" in item and "name_ar" not in item: item["name_ar"] = item.pop("name")
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"ins_up_{uid}", disabled=(i==0)):
                move_item(d["institutions"], i, -1); st.rerun()
            if st.button("▼", key=f"ins_dn_{uid}", disabled=(i==len(insts)-1)):
                move_item(d["institutions"], i, +1); st.rerun()
        r = st.columns([1, 1, 1, 1.2, 0.3])
        r[0].caption("Name (Arabic)"); r[1].caption("Name (Latin)"); r[2].caption("Type"); r[3].caption("ID: Q / TMP-I-")
        item["name_ar"]  = r[0].text_input("nar",  item.get("name_ar",""),  key=f"i_a_{uid}", label_visibility="collapsed")
        item["name_lat"] = r[1].text_input("nlat", item.get("name_lat",""), key=f"i_l_{uid}", label_visibility="collapsed")
        ct = item.get("type","study")
        item["type"] = r[2].selectbox("type", INSTITUTION_TYPES, index=INSTITUTION_TYPES.index(ct) if ct in INSTITUTION_TYPES else 0, key=f"i_t_{uid}", label_visibility="collapsed")
        item["id"]   = r[3].text_input("id", item.get("id",""), key=f"i_i_{uid}", label_visibility="collapsed", placeholder="Q12345 / TMP-I-00001")
        if r[4].button("❌", key=f"i_del_{uid}"):
            d["institutions"].pop(i); st.rerun()
    st.markdown("---")
if st.button("＋ add institution"):
    d["institutions"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["institutions"])+1,"name_ar":"","name_lat":"","type":"study","id":"TMP-I-00000"}); st.rerun()

# ===================================================
# --- Offices ---
# ===================================================
st.divider()
st.subheader("🏅 Offices / Positions")
st.caption("保有した順に記録します。▲▼ で順番を入れ替えられます。")
offices = d.get("offices", [])
for i, item in enumerate(offices):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"off_up_{uid}", disabled=(i==0)):
                move_item(d["offices"], i, -1); st.rerun()
            if st.button("▼", key=f"off_dn_{uid}", disabled=(i==len(offices)-1)):
                move_item(d["offices"], i, +1); st.rerun()
        # 行1: Office name / ID / Del
        r1 = st.columns([1.5, 1.5, 0.3])
        r1[0].caption("Office Name (Arabic)"); r1[1].caption("Office Name (Latinized)")
        item["name_ar"]  = r1[0].text_input("onar",  item.get("name_ar",""),  key=f"o_a_{uid}", label_visibility="collapsed", placeholder="例: قاضي القضاة")
        item["name_lat"] = r1[1].text_input("onlat", item.get("name_lat",""), key=f"o_l_{uid}", label_visibility="collapsed", placeholder="例: Qadi al-Qudat")
        if r1[2].button("❌", key=f"o_del_{uid}"):
            d["offices"].pop(i); st.rerun()
        # 行2: Office ID / Appointment Date / Retirement Date
        r2 = st.columns([1, 1, 1])
        r2[0].caption("Office ID (Q / TMP-O-)"); r2[1].caption("📅 Appointment Date"); r2[2].caption("📅 Retirement Date")
        item["id"]           = r2[0].text_input("oid",  item.get("id",""),           key=f"o_i_{uid}",  label_visibility="collapsed", placeholder="Q12345 / TMP-O-00001")
        item["appoint_date"] = r2[1].text_input("apdt", item.get("appoint_date",""), key=f"o_ad_{uid}", label_visibility="collapsed", placeholder="例: 880H / 1475CE")
        item["retire_date"]  = r2[2].text_input("rtdt", item.get("retire_date",""),  key=f"o_rd_{uid}", label_visibility="collapsed", placeholder="例: 890H / 1485CE")
        # 行3: Place (City/Region Arabic) / Latin / Place ID
        r3 = st.columns([1, 1, 1])
        r3[0].caption("📍 Place (Arabic)"); r3[1].caption("📍 Place (Latin)"); r3[2].caption("Place ID")
        item["place_ar"]  = r3[0].text_input("opar",  item.get("place_ar",""),  key=f"o_pa_{uid}", label_visibility="collapsed")
        item["place_lat"] = r3[1].text_input("oplat", item.get("place_lat",""), key=f"o_pl_{uid}", label_visibility="collapsed")
        item["place_id"]  = r3[2].text_input("opid",  item.get("place_id",""),  key=f"o_pi_{uid}", label_visibility="collapsed", placeholder="GeoNames / TMP-L- / Q")
        # 行4: Institution / Institution ID
        r4 = st.columns([1.5, 1.5])
        r4[0].caption("🏛️ Institution Name"); r4[1].caption("Institution ID")
        item["inst_name"] = r4[0].text_input("oiname", item.get("inst_name",""), key=f"o_in_{uid}", label_visibility="collapsed")
        item["inst_id"]   = r4[1].text_input("oiid",   item.get("inst_id",""),   key=f"o_ii_{uid}", label_visibility="collapsed", placeholder="Q12345 / TMP-I-00001")
    st.markdown("---")
if st.button("＋ add office"):
    d["offices"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["offices"])+1,
        "name_ar":"","name_lat":"","id":"TMP-O-00000",
        "place_ar":"","place_lat":"","place_id":"",
        "inst_name":"","inst_id":"",
        "appoint_date":"","retire_date":""}); st.rerun()

# ===================================================
# --- Family ---
# ===================================================
st.divider()
st.subheader("👨‍👩‍👧 Family Relations")
fh = st.columns([1, 1, 1, 0.3])
fh[0].caption("Name"); fh[1].caption("Relation"); fh[2].caption("Person ID"); fh[3].caption("Del")
for i, item in enumerate(d.get("family", [])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1, 1, 1, 0.3])
    item["name"]     = r[0].text_input("name",     item.get("name",""),     key=f"f_n_{uid}", label_visibility="collapsed")
    item["relation"] = r[1].text_input("relation", item.get("relation",""), key=f"f_r_{uid}", label_visibility="collapsed")
    item["id"]       = r[2].text_input("id",       item.get("id",""),       key=f"f_i_{uid}", label_visibility="collapsed")
    if r[3].button("❌", key=f"f_del_{uid}"):
        d["family"].pop(i); st.rerun()
if st.button("＋ add family member"):
    d["family"].append({"ui_id":str(uuid.uuid4()),"name":"","relation":"","id":"TMP-P-00000"}); st.rerun()

# ===================================================
# --- Person Notes ---
# ===================================================
st.divider()
st.subheader("📝 Person Notes")
st.caption("性格・評判・特筆すべき成果・日常生活の様子など、人物に関する自由記述")
d["person_notes"] = st.text_area("Notes", value=d.get("person_notes",""), height=150,
                                  placeholder="例: 温厚で寛容な人柄で知られ、多くの学者から尊敬を集めた。生涯を通じて数百名の弟子を育てた。")


# ===================================================
# --- 7. TEI-XML エクスポート ---
# ===================================================
st.divider()
st.header("3. TEI-XML Export")

xml_lines = []
xml_lines.append(f'<person xml:id="{d["aind_id"]}" source="#source_{d["original_id"]}">')
xml_lines.append(f'    <persName type="full" xml:lang="ar">{d["full_name"]}</persName>')
xml_lines.append(f'    <persName type="name_only" xml:lang="ar">{d["name_only"]}</persName>')

for n in d.get("nisbahs", []):
    if n.get("ar"):
        xml_lines.append(f'    <persName type="nisbah" xml:lang="ar" ref="{fr(n.get("id"))}">{n["ar"]}</persName>')

for lq in d.get("laqabs", []):
    if lq.get("ar"):
        xml_lines.append(f'    <persName type="{lq.get("type","laqab")}" xml:lang="ar">{lq["ar"]}</persName>')

# Madhhab
if d["madhhab"]["lat"] == "Unknown / Other":
    if d["madhhab"].get("custom_name") or d["madhhab"].get("custom_id"):
        xml_lines.append(f'    <affiliation type="madhhab" ref="{fr(d["madhhab"].get("custom_id",""))}">{d["madhhab"].get("custom_name","")}</affiliation>')
elif d["madhhab"]["id"]:
    xml_lines.append(f'    <affiliation type="madhhab" ref="wd:{d["madhhab"]["id"]}">{d["madhhab"]["lat"]}</affiliation>')

# Sufi Order
if d["sufi_order"].get("name"):
    xml_lines.append(f'    <affiliation type="sufiOrder" ref="{fr(d["sufi_order"].get("id",""))}">{d["sufi_order"]["name"]}</affiliation>')

if d.get("birth_h"):
    xml_lines.append(f'    <birth when-custom="{d["birth_h"]}" when="{convert_h_to_g(d["birth_h"])}"/>')
if d.get("death_h"):
    xml_lines.append(f'    <death when-custom="{d["death_h"]}" when="{convert_h_to_g(d["death_h"])}"/>')

xml_lines.append('    <listRelation>')

for t in d.get("teachers", []):
    xml_lines.append(f'        <relation name="teacher" active="{fr(t.get("id"))}" passive="#{d["aind_id"]}">')
    if t.get("subject"):
        xml_lines.append(f'            <desc ref="{fr(t.get("subject_id",""))}">{t["subject"]}</desc>')
    if t.get("text_ar"):
        xml_lines.append(f'            <bibl xml:lang="ar">{t["text_ar"]}</bibl>')
    if t.get("text_lat"):
        xml_lines.append(f'            <bibl xml:lang="lat">{t["text_lat"]}</bibl>')
    if t.get("learn_date") or t.get("learn_place_ar"):
        date_attr  = f' when="{t["learn_date"]}"' if t.get("learn_date") else ""
        place_ref  = f' ref="{fr(t.get("learn_place_id",""))}"' if t.get("learn_place_id") else ""
        place_text = t.get("learn_place_ar","")
        xml_lines.append(f'            <event type="learning"{date_attr}{place_ref}>{place_text}</event>')
    xml_lines.append('        </relation>')

for s in d.get("students", []):
    xml_lines.append(f'        <relation name="student" active="#{d["aind_id"]}" passive="{fr(s.get("id"))}">')
    if s.get("subject"):
        xml_lines.append(f'            <desc ref="{fr(s.get("subject_id",""))}">{s["subject"]}</desc>')
    if s.get("text_ar"):
        xml_lines.append(f'            <bibl xml:lang="ar">{s["text_ar"]}</bibl>')
    if s.get("text_lat"):
        xml_lines.append(f'            <bibl xml:lang="lat">{s["text_lat"]}</bibl>')
    if s.get("teach_date") or s.get("teach_place_ar"):
        date_attr  = f' when="{s["teach_date"]}"' if s.get("teach_date") else ""
        place_ref  = f' ref="{fr(s.get("teach_place_id",""))}"' if s.get("teach_place_id") else ""
        place_text = s.get("teach_place_ar","")
        xml_lines.append(f'            <event type="teaching"{date_attr}{place_ref}>{place_text}</event>')
    xml_lines.append('        </relation>')

for fam in d.get("family", []):
    xml_lines.append(f'        <relation name="family" active="{fr(fam.get("id"))}" passive="#{d["aind_id"]}" subtype="{fam.get("relation","")}">{fam.get("name","")}</relation>')

xml_lines.append('    </listRelation>')

for a in d.get("activities", []):
    if a.get("place_ar"):
        xml_lines.append(f'    <residence seq="{a.get("seq","")}" subtype="{a.get("type","")}" ref="{fr(a.get("id"))}">{a["place_ar"]}</residence>')

for inst in d.get("institutions", []):
    name_ar  = inst.get("name_ar", inst.get("name",""))
    name_lat = inst.get("name_lat","")
    if name_ar or name_lat:
        xml_lines.append(f'    <affiliation type="institution" subtype="{inst.get("type","")}" seq="{inst.get("seq","")}" ref="{fr(inst.get("id",""))}">')
        if name_ar:  xml_lines.append(f'        <orgName xml:lang="ar">{name_ar}</orgName>')
        if name_lat: xml_lines.append(f'        <orgName xml:lang="lat">{name_lat}</orgName>')
        xml_lines.append('    </affiliation>')

for off in d.get("offices", []):
    if off.get("name_ar") or off.get("name_lat"):
        xml_lines.append(f'    <state type="office" seq="{off.get("seq","")}" ref="{fr(off.get("id",""))}">')
        if off.get("name_ar"):      xml_lines.append(f'        <label xml:lang="ar">{off["name_ar"]}</label>')
        if off.get("name_lat"):     xml_lines.append(f'        <label xml:lang="lat">{off["name_lat"]}</label>')
        if off.get("appoint_date"): xml_lines.append(f'        <date type="appointment">{off["appoint_date"]}</date>')
        if off.get("retire_date"):  xml_lines.append(f'        <date type="retirement">{off["retire_date"]}</date>')
        if off.get("place_ar") or off.get("place_id"):
            xml_lines.append(f'        <placeName ref="{fr(off.get("place_id",""))}">{off.get("place_ar","")}</placeName>')
        if off.get("inst_name") or off.get("inst_id"):
            xml_lines.append(f'        <orgName ref="{fr(off.get("inst_id",""))}">{off.get("inst_name","")}</orgName>')
        xml_lines.append('    </state>')

if d.get("person_notes"):
    xml_lines.append(f'    <note type="personalia">{d["person_notes"]}</note>')
if d.get("translation_jp"):
    xml_lines.append(f'    <note type="translation" xml:lang="ja">{d["translation_jp"]}</note>')
if d.get("translation_en"):
    xml_lines.append(f'    <note type="translation" xml:lang="en">{d["translation_en"]}</note>')

xml_lines.append("</person>")

xml_str = "\n".join(xml_lines)
st.code(xml_str, language="xml")
st.download_button(label="💾 XMLをダウンロード", data=xml_str,
                   file_name=f"{d['aind_id']}.xml", mime="application/xml")
