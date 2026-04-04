import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import re
import uuid
import requests

# --- 1. ページ設定 ---
st.set_page_config(page_title="AINet-DB Pro", layout="wide", initial_sidebar_state="expanded")

# --- 2. API設定 ---
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
        return str(int(int(h_clean) * 0.97 + 622))
    except Exception:
        return ""

def fr(rid):
    """
    IDを適切なプレフィックス付き参照文字列に変換する。
    ルール:
      - すでにプレフィックスがある場合はそのまま返す
      - 数値のみ → gn:  (GeoNames: 地名に使用)
      - Q + 数値  → wd: (Wikidata: 概念・組織に使用)
      - TMP-      → #   (内部仮ID)
      - その他    → #   (フォールバック)
    """
    if not rid:
        return ""
    rid = str(rid).strip()
    # すでにプレフィックスがある場合はそのまま
    if rid.startswith(("#", "wd:", "gn:")):
        return rid
    if rid.startswith("TMP-"):
        return f"#{rid}"
    # 数値のみ → GeoNames
    if rid.isdigit():
        return f"gn:{rid}"
    # Q + 数値 → Wikidata
    if rid.startswith("Q") and rid[1:].isdigit():
        return f"wd:{rid}"
    # GeoNames_ プレフィックスの旧形式
    if "GeoNames_" in rid:
        return f"gn:{rid.replace('GeoNames_', '')}"
    return f"#{rid}"

def move_item(lst, index, direction):
    new_index = index + direction
    if 0 <= new_index < len(lst):
        lst[index], lst[new_index] = lst[new_index], lst[index]

# --- 4. ID Master シート読み込み ---
ID_MASTER_URL = "https://docs.google.com/spreadsheets/d/1MSwfebHM1Ak39Qqk7ZMrFhoHhE4COxd9PyQs2tTujuk/export?format=csv"

@st.cache_data(ttl=300)
def load_id_master():
    """GoogleスプレッドシートからID Masterを読み込みCSV→辞書化する"""
    try:
        resp = requests.get(ID_MASTER_URL, timeout=10)
        resp.encoding = "utf-8"
        lines = resp.text.strip().split("\n")
        records = []
        if not lines:
            return []
        headers = [h.strip() for h in lines[0].split(",")]
        for line in lines[1:]:
            vals = [v.strip() for v in line.split(",")]
            row = dict(zip(headers, vals))
            records.append(row)
        return records
    except Exception as e:
        return []

def id_master_to_prompt_text(records):
    """ID Masterの内容をプロンプト埋め込み用テキストに変換
    列構成: Category | Arabic | Latin | ID | Note
    """
    if not records:
        return "(ID Master not available)"
    lines = ["Use these known IDs when they match entities in the text:"]
    for r in records:
        category = r.get("Category", "")
        arabic   = r.get("Arabic",   "")
        latin    = r.get("Latin",    "")
        id_val   = r.get("ID",       "")
        note     = r.get("Note",     "")
        if not id_val:
            continue
        # 表示名: アラビア語があればそれを優先、なければLatin
        display  = arabic if arabic else latin
        label    = f"{display}"
        if latin and arabic:
            label += f" ({latin})"
        if category:
            label += f" [{category}]"
        if note:
            label += f" — {note}"
        lines.append(f"  - {label} → {id_val}")
    return "\n".join(lines)

# --- 5. 定数 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)":    "Q160851",
    "Maliki (マーリク派)":      "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)":   "Q191314",
    "Unknown / Other":          ""
}
INSTITUTION_TYPES = ["study","teach","reside","founded","affiliated","graduated","employed","visit","other"]
ACTIVITY_TYPES    = ["study","buried","reside","visit","born","died","other"]
LAQAB_TYPES       = ["laqab","shuhrah","kunyah"]
LAQAB_LABELS      = {"laqab":"laqab（号）","shuhrah":"shuhrah（通称）","kunyah":"kunyah（クンヤ）"}

FAMILY_RELATIONS = [
    ("father",      "Father（父）"),
    ("mother",      "Mother（母）"),
    ("son",         "Son（息子）"),
    ("daughter",    "Daughter（娘）"),
    ("brother",     "Brother（兄弟）"),
    ("sister",      "Sister（姉妹）"),
    ("p_uncle",     "Paternal Uncle（父方叔父）"),
    ("m_uncle",     "Maternal Uncle（母方叔父）"),
    ("grandfather", "Grandfather（祖父）"),
    ("spouse",      "Spouse（配偶者）"),
    ("descendant",  "Descendant（子孫）"),
    ("ancestor",    "Ancestor（先祖）"),
    ("other",       "Other / Unknown（その他）"),
]
FAMILY_RELATION_KEYS   = [r[0] for r in FAMILY_RELATIONS]
FAMILY_RELATION_LABELS = {r[0]: r[1] for r in FAMILY_RELATIONS}

# --- 6. セッション状態の初期化 ---
if 'data_v18' not in st.session_state:
    st.session_state.data_v18 = {
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

d = st.session_state.data_v18

# ===================================================
# --- 7. サイドバー: 史料解析 ---
# ===================================================
with st.sidebar:
    st.header("1. Source & Bilingual Analysis")
    source_input = st.text_area("史料テキスト (Arabic)", value=d["source_text"], height=380)

    if st.button("🔍 解析する", use_container_width=True):
        if source_input:
            d["source_text"] = source_input
            with st.spinner("解析中..."):
                try:
                    id_records  = load_id_master()
                    id_master_text = id_master_to_prompt_text(id_records)

                    model = get_working_model()
                    prompt = f"""
You are a professional historian of Islamic studies. Extract data from the source text into JSON.

【ID Master — use these IDs for matching entities】
{id_master_text}

【ID Rules (when not in ID Master)】
- Places/geography: GeoNames numeric ID (e.g. "104515"). Otherwise "TMP-L-00000".
  → gn: prefix will be applied automatically.
- Institutions/concepts/orders: Wikidata Q-ID (e.g. "Q12345"). Otherwise "TMP-I-00000".
  → wd: prefix will be applied automatically.
- Persons: Wikidata Q-ID if known. Otherwise "TMP-P-00000".
- Texts/books: Wikidata Q-ID if known. Otherwise "TMP-T-00000".

【Translation】
- translation_jp: Accurate academic Japanese translation.
- translation_en: Accurate academic English translation.

【Laqab / Shuhrah / Kunyah】
- laqab: honorific title. shuhrah: popular epithet. kunyah: أبو/أم teknonym.

【Teachers / Students】
- subject/subject_id: discipline and its ID.
- text_ar/text_lat/text_id: book title (Arabic, Latin, ID) if mentioned.
- learn_date/teach_date: date if mentioned.
- learn_place_ar/learn_place_lat/learn_place_id: place if mentioned (GeoNames ID for places).
- teach_place_ar/teach_place_lat/teach_place_id: same for students.

【Activities / Places】
- GEOGRAPHIC events only (birth, death, burial, residence, travel). No institution names here.

【Institutions】
- Named institutions only (madrasa, mosque, etc.). No mere city stays here.
- type: study|teach|reside|founded|affiliated|graduated|employed|visit|other

【Offices】
- place_ar/place_lat/place_id, inst_name/inst_id, appoint_date/retire_date if mentioned.

Return ONLY valid JSON, NO markdown:
{{
    "original_id":"","full_name":"","name_only":"",
    "birth_h":"","death_h":"","madhhab_name":"",
    "nisbahs":[{{"ar":"","lat":"","id":"TMP-L-00000"}}],
    "laqabs":[{{"type":"laqab","ar":"","lat":""}}],
    "activities":[{{"seq":1,"place_ar":"","place_lat":"","type":"reside","id":""}}],
    "teachers":[{{
        "name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000",
        "text_ar":"","text_lat":"","text_id":"TMP-T-00000",
        "learn_date":"","learn_place_ar":"","learn_place_lat":"","learn_place_id":""
    }}],
    "students":[{{
        "name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000",
        "text_ar":"","text_lat":"","text_id":"TMP-T-00000",
        "teach_date":"","teach_place_ar":"","teach_place_lat":"","teach_place_id":""
    }}],
    "institutions":[{{"seq":1,"name_ar":"","name_lat":"","type":"study","id":"TMP-I-00000"}}],
    "offices":[{{
        "seq":1,"name_ar":"","name_lat":"","id":"TMP-O-00000",
        "place_ar":"","place_lat":"","place_id":"",
        "inst_name":"","inst_id":"",
        "appoint_date":"","retire_date":""
    }}],
    "translation_jp":"","translation_en":""
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
                        st.error("JSON抽出失敗")
                        st.text(response.text[:400])
                except Exception as e:
                    st.error(f"エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

    # ID Master状態表示
    with st.expander("📋 ID Master 状態", expanded=False):
        records = load_id_master()
        if records:
            st.success(f"{len(records)} 件読み込み済み")
            st.dataframe(records, use_container_width=True)
        else:
            st.warning("ID Master を読み込めませんでした。スプレッドシートの共有設定を確認してください。")
        if st.button("🔄 再読み込み"):
            st.cache_data.clear()
            st.rerun()

    # 翻訳表示
    if d.get("translation_jp") or d.get("translation_en"):
        t1, t2 = st.tabs(["🇯🇵 日本語訳", "🇺🇸 English"])
        with t1: st.info(d["translation_jp"])
        with t2: st.info(d["translation_en"])

# ===================================================
# --- 8. メインエリア: メタデータエディタ ---
# ===================================================
st.title("🌙 AINet-DB Researcher Pro")
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
nh = st.columns([1,1,1,0.3])
nh[0].caption("Arabic"); nh[1].caption("Latinized"); nh[2].caption("ID (TMP-L- / GeoNames数字)"); nh[3].caption("Del")
for i, item in enumerate(d.get("nisbahs",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1,1,1,0.3])
    item["ar"]  = r[0].text_input("ar",  item.get("ar",""),  key=f"n_a_{uid}", label_visibility="collapsed")
    item["lat"] = r[1].text_input("lat", item.get("lat",""), key=f"n_l_{uid}", label_visibility="collapsed")
    item["id"]  = r[2].text_input("id",  item.get("id",""),  key=f"n_i_{uid}", label_visibility="collapsed", placeholder="TMP-L-00001")
    if r[3].button("❌", key=f"n_del_{uid}"):
        d["nisbahs"].pop(i); st.rerun()
if st.button("＋ add nisbah"):
    d["nisbahs"].append({"ui_id":str(uuid.uuid4()),"ar":"","lat":"","id":"TMP-L-00000"}); st.rerun()

# ===================================================
# --- Laqab / Shuhrah / Kunyah ---
# ===================================================
st.divider()
st.subheader("🔤 Laqab / Shuhrah / Kunyah")
lh = st.columns([1,1,1,0.3])
lh[0].caption("Type"); lh[1].caption("Arabic"); lh[2].caption("Latinized"); lh[3].caption("Del")
for i, item in enumerate(d.get("laqabs",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1,1,1,0.3])
    cur = item.get("type","laqab")
    item["type"] = r[0].selectbox("type", LAQAB_TYPES,
                                   format_func=lambda x: LAQAB_LABELS[x],
                                   index=LAQAB_TYPES.index(cur) if cur in LAQAB_TYPES else 0,
                                   key=f"lq_t_{uid}", label_visibility="collapsed")
    item["ar"]  = r[1].text_input("ar",  item.get("ar",""),  key=f"lq_a_{uid}", label_visibility="collapsed", placeholder="例: زين الدين / أبو بكر")
    item["lat"] = r[2].text_input("lat", item.get("lat",""), key=f"lq_l_{uid}", label_visibility="collapsed", placeholder="例: Zayn al-Din / Abu Bakr")
    if r[3].button("❌", key=f"lq_del_{uid}"):
        d["laqabs"].pop(i); st.rerun()
if st.button("＋ add laqab / shuhrah / kunyah"):
    d["laqabs"].append({"ui_id":str(uuid.uuid4()),"type":"laqab","ar":"","lat":""}); st.rerun()

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
cur_m   = d["madhhab"]["lat"]
def_idx = madhhab_keys.index(cur_m) if cur_m in madhhab_keys else 4
m_col1, m_col2 = st.columns(2)
selected_m  = m_col1.selectbox("⚖️ Madhhab", options=madhhab_keys, index=def_idx)
wikidata_id = MADHHAB_DATA[selected_m]
m_col2.text_input("Wikidata ID", value=wikidata_id, disabled=True)
if selected_m == "Unknown / Other":
    uo1, uo2 = st.columns(2)
    custom_name = uo1.text_input("Madhhab name (free text)", value=d["madhhab"].get("custom_name",""), key="madhhab_custom_name")
    custom_id   = uo2.text_input("Madhhab ID (Q / TMP-)",    value=d["madhhab"].get("custom_id",""),   key="madhhab_custom_id")
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
d["sufi_order"]["id"]   = sf2.text_input("Sufi Order ID (Q / TMP-)", value=d["sufi_order"].get("id",""), placeholder="例: Q123456")

# ===================================================
# --- Teachers ---
# ===================================================
st.divider()
st.subheader("🎓 Teachers & Subjects")
for i, item in enumerate(d.get("teachers",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        # 行1: Name / Person ID / Subject / Subject ID / Del
        r1 = st.columns([1.2,1,1,1,0.3])
        r1[0].caption("Name"); r1[1].caption("Person ID"); r1[2].caption("Subject"); r1[3].caption("Subject ID")
        item["name"]       = r1[0].text_input("Name",    item.get("name",""),       key=f"t_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r1[1].text_input("PID",     item.get("id",""),         key=f"t_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r1[2].text_input("Subject", item.get("subject",""),    key=f"t_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r1[3].text_input("SID",     item.get("subject_id",""), key=f"t_si_{uid}", label_visibility="collapsed")
        if r1[4].button("❌", key=f"t_del_{uid}"):
            d["teachers"].pop(i); st.rerun()
        # 行2: Text Arabic / Text Latinized / Text ID
        r2 = st.columns([1,1,1])
        r2[0].caption("📖 Text (Arabic)"); r2[1].caption("📖 Text (Latinized)"); r2[2].caption("📖 Text ID (Q / TMP-T-)")
        item["text_ar"]  = r2[0].text_input("tar",  item.get("text_ar",""),  key=f"t_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r2[1].text_input("tlat", item.get("text_lat",""), key=f"t_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        item["text_id"]  = r2[2].text_input("tid",  item.get("text_id",""),  key=f"t_ti_{uid}", label_visibility="collapsed", placeholder="例: Q208507 / TMP-T-00001")
        # 行3: Learning Date / Place Ar / Place Lat / Place ID
        r3 = st.columns([1,1,1,1])
        r3[0].caption("📅 Learning Date"); r3[1].caption("📍 Place (Arabic)"); r3[2].caption("📍 Place (Latin)"); r3[3].caption("Place ID (GeoNames)")
        item["learn_date"]      = r3[0].text_input("ldate", item.get("learn_date",""),      key=f"t_ld_{uid}",  label_visibility="collapsed", placeholder="例: 880H")
        item["learn_place_ar"]  = r3[1].text_input("lpar",  item.get("learn_place_ar",""),  key=f"t_lpa_{uid}", label_visibility="collapsed")
        item["learn_place_lat"] = r3[2].text_input("lplat", item.get("learn_place_lat",""), key=f"t_lpl_{uid}", label_visibility="collapsed")
        item["learn_place_id"]  = r3[3].text_input("lpid",  item.get("learn_place_id",""),  key=f"t_lpi_{uid}", label_visibility="collapsed", placeholder="GeoNames数字 / TMP-L-")
    st.markdown("---")
if st.button("＋ add teacher"):
    d["teachers"].append({"ui_id":str(uuid.uuid4()),"name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000",
        "text_ar":"","text_lat":"","text_id":"TMP-T-00000",
        "learn_date":"","learn_place_ar":"","learn_place_lat":"","learn_place_id":""}); st.rerun()

# ===================================================
# --- Students ---
# ===================================================
st.divider()
st.subheader("🧑‍🎓 Students & Subjects")
for i, item in enumerate(d.get("students",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        r1 = st.columns([1.2,1,1,1,0.3])
        r1[0].caption("Name"); r1[1].caption("Person ID"); r1[2].caption("Subject"); r1[3].caption("Subject ID")
        item["name"]       = r1[0].text_input("Name",    item.get("name",""),       key=f"s_n_{uid}",  label_visibility="collapsed")
        item["id"]         = r1[1].text_input("PID",     item.get("id",""),         key=f"s_i_{uid}",  label_visibility="collapsed")
        item["subject"]    = r1[2].text_input("Subject", item.get("subject",""),    key=f"s_s_{uid}",  label_visibility="collapsed")
        item["subject_id"] = r1[3].text_input("SID",     item.get("subject_id",""), key=f"s_si_{uid}", label_visibility="collapsed")
        if r1[4].button("❌", key=f"s_del_{uid}"):
            d["students"].pop(i); st.rerun()
        r2 = st.columns([1,1,1])
        r2[0].caption("📖 Text (Arabic)"); r2[1].caption("📖 Text (Latinized)"); r2[2].caption("📖 Text ID (Q / TMP-T-)")
        item["text_ar"]  = r2[0].text_input("tar",  item.get("text_ar",""),  key=f"s_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r2[1].text_input("tlat", item.get("text_lat",""), key=f"s_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        item["text_id"]  = r2[2].text_input("tid",  item.get("text_id",""),  key=f"s_ti_{uid}", label_visibility="collapsed", placeholder="例: Q208507 / TMP-T-00001")
        r3 = st.columns([1,1,1,1])
        r3[0].caption("📅 Teaching Date"); r3[1].caption("📍 Place (Arabic)"); r3[2].caption("📍 Place (Latin)"); r3[3].caption("Place ID (GeoNames)")
        item["teach_date"]      = r3[0].text_input("tdate", item.get("teach_date",""),      key=f"s_td_{uid}",  label_visibility="collapsed", placeholder="例: 880H")
        item["teach_place_ar"]  = r3[1].text_input("tpar",  item.get("teach_place_ar",""),  key=f"s_tpa_{uid}", label_visibility="collapsed")
        item["teach_place_lat"] = r3[2].text_input("tplat", item.get("teach_place_lat",""), key=f"s_tpl_{uid}", label_visibility="collapsed")
        item["teach_place_id"]  = r3[3].text_input("tpid",  item.get("teach_place_id",""),  key=f"s_tpi_{uid}", label_visibility="collapsed", placeholder="GeoNames数字 / TMP-L-")
    st.markdown("---")
if st.button("＋ add student"):
    d["students"].append({"ui_id":str(uuid.uuid4()),"name":"","id":"TMP-P-00000",
        "subject":"","subject_id":"TMP-S-00000",
        "text_ar":"","text_lat":"","text_id":"TMP-T-00000",
        "teach_date":"","teach_place_ar":"","teach_place_lat":"","teach_place_id":""}); st.rerun()

# ===================================================
# --- Activities ---
# ===================================================
st.divider()
st.subheader("📍 Activities / Places")
st.caption("機関名を伴わない地理的イベント（居住・移動・出生・死亡・埋葬）を記録。機関との関わりは Institutions へ。▲▼ で並び替え可。")
acts = d.get("activities",[])
for i, item in enumerate(acts):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15,0.25,3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"act_up_{uid}", disabled=(i==0)):
                move_item(d["activities"],i,-1); st.rerun()
            if st.button("▼", key=f"act_dn_{uid}", disabled=(i==len(acts)-1)):
                move_item(d["activities"],i,+1); st.rerun()
        r = st.columns([1,1,1,1.3,0.3])
        r[0].caption("Place (Arabic)"); r[1].caption("Place (Latin)"); r[2].caption("Type"); r[3].caption("ID (GeoNames数字)")
        item["place_ar"]  = r[0].text_input("par",  item.get("place_ar",""),  key=f"a_a_{uid}", label_visibility="collapsed")
        item["place_lat"] = r[1].text_input("plat", item.get("place_lat",""), key=f"a_l_{uid}", label_visibility="collapsed")
        ct = item.get("type","reside")
        item["type"] = r[2].selectbox("type", ACTIVITY_TYPES,
                                       index=ACTIVITY_TYPES.index(ct) if ct in ACTIVITY_TYPES else 0,
                                       key=f"a_t_{uid}", label_visibility="collapsed")
        item["id"] = r[3].text_input("id", item.get("id",""), key=f"a_i_{uid}", label_visibility="collapsed", placeholder="例: 104515（GeoNames）")
        if r[4].button("❌", key=f"a_del_{uid}"):
            d["activities"].pop(i); st.rerun()
    st.markdown("---")
if st.button("＋ add activity"):
    d["activities"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["activities"])+1,
        "place_ar":"","place_lat":"","type":"reside","id":""}); st.rerun()

# ===================================================
# --- Institutions ---
# ===================================================
st.divider()
st.subheader("🏛️ Institutions")
st.caption("名前のある機関（マドラサ・モスク・図書館等）との関わりを記録。単純な居住・移動は Activities へ。▲▼ で並び替え可。ID は Wikidata Q 推奨。")
insts = d.get("institutions",[])
for i, item in enumerate(insts):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    if "name" in item and "name_ar" not in item: item["name_ar"] = item.pop("name")
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15,0.25,3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"ins_up_{uid}", disabled=(i==0)):
                move_item(d["institutions"],i,-1); st.rerun()
            if st.button("▼", key=f"ins_dn_{uid}", disabled=(i==len(insts)-1)):
                move_item(d["institutions"],i,+1); st.rerun()
        r = st.columns([1,1,1,1.2,0.3])
        r[0].caption("Name (Arabic)"); r[1].caption("Name (Latin)"); r[2].caption("Type"); r[3].caption("ID (Q / TMP-I-)")
        item["name_ar"]  = r[0].text_input("nar",  item.get("name_ar",""),  key=f"i_a_{uid}", label_visibility="collapsed")
        item["name_lat"] = r[1].text_input("nlat", item.get("name_lat",""), key=f"i_l_{uid}", label_visibility="collapsed")
        ct = item.get("type","study")
        item["type"] = r[2].selectbox("type", INSTITUTION_TYPES,
                                       index=INSTITUTION_TYPES.index(ct) if ct in INSTITUTION_TYPES else 0,
                                       key=f"i_t_{uid}", label_visibility="collapsed")
        item["id"] = r[3].text_input("id", item.get("id",""), key=f"i_i_{uid}", label_visibility="collapsed", placeholder="例: Q12345 / TMP-I-00001")
        if r[4].button("❌", key=f"i_del_{uid}"):
            d["institutions"].pop(i); st.rerun()
    st.markdown("---")
if st.button("＋ add institution"):
    d["institutions"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["institutions"])+1,
        "name_ar":"","name_lat":"","type":"study","id":"TMP-I-00000"}); st.rerun()

# ===================================================
# --- Offices ---
# ===================================================
st.divider()
st.subheader("🏅 Offices / Positions")
st.caption("保有した順に記録。▲▼ で並び替え可。Place ID は GeoNames 数字、Institution ID は Wikidata Q 推奨。")
offices = d.get("offices",[])
for i, item in enumerate(offices):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1
    with st.container():
        hc = st.columns([0.15,0.25,3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"off_up_{uid}", disabled=(i==0)):
                move_item(d["offices"],i,-1); st.rerun()
            if st.button("▼", key=f"off_dn_{uid}", disabled=(i==len(offices)-1)):
                move_item(d["offices"],i,+1); st.rerun()
        r1 = st.columns([1.5,1.5,0.3])
        r1[0].caption("Office Name (Arabic)"); r1[1].caption("Office Name (Latinized)")
        item["name_ar"]  = r1[0].text_input("onar",  item.get("name_ar",""),  key=f"o_a_{uid}", label_visibility="collapsed", placeholder="例: قاضي القضاة")
        item["name_lat"] = r1[1].text_input("onlat", item.get("name_lat",""), key=f"o_l_{uid}", label_visibility="collapsed", placeholder="例: Qadi al-Qudat")
        if r1[2].button("❌", key=f"o_del_{uid}"):
            d["offices"].pop(i); st.rerun()
        r2 = st.columns([1,1,1])
        r2[0].caption("Office ID (Q / TMP-O-)"); r2[1].caption("📅 Appointment Date"); r2[2].caption("📅 Retirement Date")
        item["id"]           = r2[0].text_input("oid",  item.get("id",""),           key=f"o_i_{uid}",  label_visibility="collapsed", placeholder="Q12345 / TMP-O-00001")
        item["appoint_date"] = r2[1].text_input("apdt", item.get("appoint_date",""), key=f"o_ad_{uid}", label_visibility="collapsed", placeholder="例: 880H")
        item["retire_date"]  = r2[2].text_input("rtdt", item.get("retire_date",""),  key=f"o_rd_{uid}", label_visibility="collapsed", placeholder="例: 890H")
        r3 = st.columns([1,1,1])
        r3[0].caption("📍 Place (Arabic)"); r3[1].caption("📍 Place (Latin)"); r3[2].caption("Place ID (GeoNames数字)")
        item["place_ar"]  = r3[0].text_input("opar",  item.get("place_ar",""),  key=f"o_pa_{uid}", label_visibility="collapsed")
        item["place_lat"] = r3[1].text_input("oplat", item.get("place_lat",""), key=f"o_pl_{uid}", label_visibility="collapsed")
        item["place_id"]  = r3[2].text_input("opid",  item.get("place_id",""),  key=f"o_pi_{uid}", label_visibility="collapsed", placeholder="例: 104515")
        r4 = st.columns([1.5,1.5])
        r4[0].caption("🏛️ Institution Name"); r4[1].caption("Institution ID (Q / TMP-I-)")
        item["inst_name"] = r4[0].text_input("oiname", item.get("inst_name",""), key=f"o_in_{uid}", label_visibility="collapsed")
        item["inst_id"]   = r4[1].text_input("oiid",   item.get("inst_id",""),   key=f"o_ii_{uid}", label_visibility="collapsed", placeholder="Q12345 / TMP-I-00001")
    st.markdown("---")
if st.button("＋ add office"):
    d["offices"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["offices"])+1,
        "name_ar":"","name_lat":"","id":"TMP-O-00000",
        "place_ar":"","place_lat":"","place_id":"",
        "inst_name":"","inst_id":"","appoint_date":"","retire_date":""}); st.rerun()

# ===================================================
# --- Family ---
# ===================================================
st.divider()
st.subheader("👨‍👩‍👧 Family Relations")
for i, item in enumerate(d.get("family",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        r = st.columns([1.2, 1.2, 1, 0.3])
        r[0].caption("Name"); r[1].caption("Relation"); r[2].caption("Person ID")
        item["name"] = r[0].text_input("name", item.get("name",""), key=f"f_n_{uid}", label_visibility="collapsed")
        cur_rel = item.get("relation","other")
        if cur_rel not in FAMILY_RELATION_KEYS:
            cur_rel = "other"
        item["relation"] = r[1].selectbox(
            "relation", FAMILY_RELATION_KEYS,
            format_func=lambda x: FAMILY_RELATION_LABELS[x],
            index=FAMILY_RELATION_KEYS.index(cur_rel),
            key=f"f_r_{uid}", label_visibility="collapsed"
        )
        item["id"] = r[2].text_input("id", item.get("id",""), key=f"f_i_{uid}", label_visibility="collapsed")
        if r[3].button("❌", key=f"f_del_{uid}"):
            d["family"].pop(i); st.rerun()
        # Other選択時に自由記入欄を表示
        if item["relation"] == "other":
            item["relation_note"] = st.text_input(
                "Relation (free text)",
                value=item.get("relation_note",""),
                key=f"f_rn_{uid}",
                placeholder="例: 義父、師匠の息子など"
            )
    st.markdown("---")
if st.button("＋ add family member"):
    d["family"].append({"ui_id":str(uuid.uuid4()),"name":"","relation":"father","relation_note":"","id":"TMP-P-00000"}); st.rerun()

# ===================================================
# --- Person Notes ---
# ===================================================
st.divider()
st.subheader("📝 Person Notes")
st.caption("性格・評判・特筆すべき成果・日常生活の様子など")
d["person_notes"] = st.text_area("Notes", value=d.get("person_notes",""), height=150,
    placeholder="例: 温厚で寛容な人柄で知られ、多くの学者から尊敬を集めた。")

# ===================================================
# --- 9. TEI-XML エクスポート ---
# ===================================================
st.divider()
st.header("3. TEI-XML Export")

def build_xml(d):
    x = []

    # --- person要素: @source → @corresp に変更 ---
    x.append(f'<person xml:id="{d["aind_id"]}" corresp="#source_{d["original_id"]}">')

    # --- persName ---
    x.append(f'    <persName type="full" xml:lang="ar">{d["full_name"]}</persName>')
    x.append(f'    <persName type="name_only" xml:lang="ar">{d["name_only"]}</persName>')

    for n in d.get("nisbahs",[]):
        if n.get("ar"):
            x.append(f'    <persName type="nisbah" xml:lang="ar" ref="{fr(n.get("id"))}">{n["ar"]}</persName>')

    for lq in d.get("laqabs",[]):
        if lq.get("ar"):
            x.append(f'    <persName type="{lq.get("type","laqab")}" xml:lang="ar">{lq["ar"]}</persName>')

    # --- affiliation: Madhhab ---
    if d["madhhab"]["lat"] == "Unknown / Other":
        cn = d["madhhab"].get("custom_name","")
        ci = d["madhhab"].get("custom_id","")
        if cn or ci:
            x.append(f'    <affiliation type="madhhab" ref="{fr(ci)}">{cn}</affiliation>')
    elif d["madhhab"]["id"]:
        x.append(f'    <affiliation type="madhhab" ref="wd:{d["madhhab"]["id"]}">{d["madhhab"]["lat"]}</affiliation>')

    # --- affiliation: Sufi Order ---
    if d["sufi_order"].get("name"):
        x.append(f'    <affiliation type="sufiOrder" ref="{fr(d["sufi_order"].get("id",""))}">{d["sufi_order"]["name"]}</affiliation>')

    # --- birth / death ---
    if d.get("birth_h"):
        x.append(f'    <birth when-custom="{d["birth_h"]}" when="{convert_h_to_g(d["birth_h"])}"/>')
    if d.get("death_h"):
        x.append(f'    <death when-custom="{d["death_h"]}" when="{convert_h_to_g(d["death_h"])}"/>')

    # --- listRelation: teachers / students / family ---
    relations = []

    for t in d.get("teachers",[]):
        lines = [f'        <relation type="personal" name="teacher" active="{fr(t.get("id"))}" passive="#{d["aind_id"]}">']
        if t.get("subject"):
            lines.append(f'            <desc ref="{fr(t.get("subject_id",""))}">{t["subject"]}</desc>')
        if t.get("text_ar") or t.get("text_lat"):
            tid = fr(t.get("text_id",""))
            ref_attr = f' ref="{tid}"' if tid else ""
            if t.get("text_ar"):
                lines.append(f'            <bibl xml:lang="ar"{ref_attr}>{t["text_ar"]}</bibl>')
            if t.get("text_lat"):
                lines.append(f'            <bibl xml:lang="lat"{ref_attr}>{t["text_lat"]}</bibl>')
        # learning event: placeNameで地名を内包
        if t.get("learn_date") or t.get("learn_place_ar"):
            da = f' when="{t["learn_date"]}"' if t.get("learn_date") else ""
            pr = f' where="{fr(t.get("learn_place_id",""))}"' if t.get("learn_place_id") else ""
            if t.get("learn_place_ar"):
                lines.append(f'            <event type="learning"{da}{pr}><placeName>{t.get("learn_place_ar","")}</placeName></event>')
            else:
                lines.append(f'            <event type="learning"{da}{pr}/>')
        lines.append('        </relation>')
        relations.extend(lines)

    for s in d.get("students",[]):
        lines = [f'        <relation type="personal" name="student" active="#{d["aind_id"]}" passive="{fr(s.get("id"))}">']
        if s.get("subject"):
            lines.append(f'            <desc ref="{fr(s.get("subject_id",""))}">{s["subject"]}</desc>')
        if s.get("text_ar") or s.get("text_lat"):
            tid = fr(s.get("text_id",""))
            ref_attr = f' ref="{tid}"' if tid else ""
            if s.get("text_ar"):
                lines.append(f'            <bibl xml:lang="ar"{ref_attr}>{s["text_ar"]}</bibl>')
            if s.get("text_lat"):
                lines.append(f'            <bibl xml:lang="lat"{ref_attr}>{s["text_lat"]}</bibl>')
        if s.get("teach_date") or s.get("teach_place_ar"):
            da = f' when="{s["teach_date"]}"' if s.get("teach_date") else ""
            pr = f' where="{fr(s.get("teach_place_id",""))}"' if s.get("teach_place_id") else ""
            if s.get("teach_place_ar"):
                lines.append(f'            <event type="teaching"{da}{pr}><placeName>{s.get("teach_place_ar","")}</placeName></event>')
            else:
                lines.append(f'            <event type="teaching"{da}{pr}/>')
        lines.append('        </relation>')
        relations.extend(lines)

    for fam in d.get("family",[]):
        rel      = fam.get("relation","other")
        rel_note = fam.get("relation_note","")
        subtype  = rel_note if (rel == "other" and rel_note) else rel
        # family: TEI の <relation> は @name ではなく @type を使う
        fam_ref  = fr(fam.get("id",""))
        ref_attr = f' ref="{fam_ref}"' if fam_ref else ""
        relations.append(
            f'        <relation type="personal" subtype="{subtype}" ' +
            f'active="{fam_ref}" passive="#{d["aind_id"]}">' +
            f'<desc>{fam.get("name","")}</desc></relation>'
        )

    if relations:
        x.append('    <listRelation>')
        x.extend(relations)
        x.append('    </listRelation>')

    # --- Activities: born/died → birth/death event、その他 → residence ---
    # TEI: @seq は非標準 → @n を使用
    # married → <event type="marriage">
    # born    → <event type="birth"> + <placeName>
    # died    → <event type="death"> + <placeName>
    for a in d.get("activities",[]):
        if not a.get("place_ar"):
            continue
        n_attr  = f' n="{a.get("seq","")}"'
        ref_att = f' ref="{fr(a.get("id"))}"' if a.get("id") else ""
        atype   = a.get("type","reside")

        if atype == "born":
            x.append(f'    <event type="birth"{n_attr}><placeName{ref_att}>{a["place_ar"]}</placeName></event>')
        elif atype == "died":
            x.append(f'    <event type="death"{n_attr}><placeName{ref_att}>{a["place_ar"]}</placeName></event>')
        elif atype == "buried":
            x.append(f'    <event type="burial"{n_attr}><placeName{ref_att}>{a["place_ar"]}</placeName></event>')
        else:
            # reside / visit / study / other → <residence>
            x.append(f'    <residence n="{a.get("seq","")}" type="{atype}"{ref_att}><placeName>{a["place_ar"]}</placeName></residence>')

    # --- Institutions: @seq → @n, @subtype → @type ---
    for inst in d.get("institutions",[]):
        na = inst.get("name_ar", inst.get("name",""))
        nl = inst.get("name_lat","")
        if not (na or nl):
            continue
        inst_ref = fr(inst.get("id",""))
        ref_att  = f' ref="{inst_ref}"' if inst_ref else ""
        x.append(f'    <affiliation n="{inst.get("seq","")}" type="{inst.get("type","")}"{ ref_att}>')
        if na: x.append(f'        <orgName xml:lang="ar">{na}</orgName>')
        if nl: x.append(f'        <orgName xml:lang="lat">{nl}</orgName>')
        x.append('    </affiliation>')

    # --- Offices: <state> + 内部要素 ---
    # TEI <state> は人物の状態・身分を表す要素として適切
    for off in d.get("offices",[]):
        if not (off.get("name_ar") or off.get("name_lat")):
            continue
        off_ref = fr(off.get("id",""))
        ref_att = f' ref="{off_ref}"' if off_ref else ""
        x.append(f'    <state n="{off.get("seq","")}" type="office"{ref_att}>')
        if off.get("name_ar"):
            x.append(f'        <label xml:lang="ar">{off["name_ar"]}</label>')
        if off.get("name_lat"):
            x.append(f'        <label xml:lang="lat">{off["name_lat"]}</label>')
        if off.get("appoint_date"):
            x.append(f'        <date type="appointment" when-custom="{off["appoint_date"]}"/>')
        if off.get("retire_date"):
            x.append(f'        <date type="retirement" when-custom="{off["retire_date"]}"/>')
        if off.get("place_ar") or off.get("place_id"):
            pr = fr(off.get("place_id",""))
            ref_p = f' ref="{pr}"' if pr else ""
            x.append(f'        <placeName{ref_p}>{off.get("place_ar","")}</placeName>')
        if off.get("inst_name") or off.get("inst_id"):
            ir = fr(off.get("inst_id",""))
            ref_i = f' ref="{ir}"' if ir else ""
            x.append(f'        <orgName{ref_i}>{off.get("inst_name","")}</orgName>')
        x.append('    </state>')

    # --- notes ---
    if d.get("person_notes"):
        x.append(f'    <note type="personalia" xml:lang="ja">{d["person_notes"]}</note>')
    if d.get("translation_jp"):
        x.append(f'    <note type="translation" xml:lang="ja">{d["translation_jp"]}</note>')
    if d.get("translation_en"):
        x.append(f'    <note type="translation" xml:lang="en">{d["translation_en"]}</note>')

    x.append("</person>")
    return "\n".join(x)

xml_str = build_xml(d)
st.code(xml_str, language="xml")

# クリップボードコピーボタン（JavaScriptで実装）
copy_js = f"""
<button onclick="
    navigator.clipboard.writeText({repr(xml_str)}).then(function() {{
        this.textContent = '✅ コピーしました';
        this.style.background = '#28a745';
        setTimeout(() => {{
            this.textContent = '📋 XMLをクリップボードにコピー';
            this.style.background = '#0066cc';
        }}, 2000);
    }}.bind(this));
" style="
    background:#0066cc; color:white; border:none;
    padding:0.5rem 1.2rem; border-radius:6px;
    font-size:1rem; cursor:pointer; margin-top:0.5rem;
">📋 XMLをクリップボードにコピー</button>
"""
components.html(copy_js, height=60)


# ===================================================
# --- 10. スプレッドシート書き込み ---
# ===================================================
st.divider()
st.header("4. スプレッドシートに保存")

DATASET_SHEET_ID = "1tCoRH0NEwZpgig2DePCVoldU_PSNAdDW9QKkn2KlNp8"

# 列定義（スプレッドシートのヘッダー順）
# 担当者 | AIND-D-XXXX | 12digitsID | persName(Full Arabic) | persName(Ism/Father/GF) | Birth(H) | Death(H) | Madhhab
SHEET_COLUMNS = [
    "担当者",
    "AIND-D-XXXX",
    "12digitsID",
    "persName (Full Arabic)",
    "persName (Ism/Father/GF)",
    "Birth (H)",
    "Death (H)",
    "Madhhab",
]

def get_gspread_client():
    """st.secretsのService AccountJSONからgspreadクライアントを生成"""
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def build_row(data, assignee):
    """現在のデータから書き込み行を生成"""
    # Madhhab表示文字列
    if data["madhhab"]["lat"] == "Unknown / Other":
        madhhab_str = data["madhhab"].get("custom_name", "")
    else:
        madhhab_str = data["madhhab"]["lat"]

    return [
        assignee,                          # 担当者
        data.get("aind_id", ""),           # AIND-D-XXXX
        data.get("original_id", ""),       # 12digitsID (@source)
        data.get("full_name", ""),         # persName (Full Arabic)
        data.get("name_only", ""),         # persName (Ism/Father/GF)
        data.get("birth_h", ""),           # Birth (H)
        data.get("death_h", ""),           # Death (H)
        madhhab_str,                       # Madhhab
    ]

def find_row_by_id(worksheet, original_id):
    """12digitsID列（3列目=index2）でoriginal_idを検索し、行番号を返す（なければNone）"""
    try:
        col_values = worksheet.col_values(3)  # 3列目 = 12digitsID
        for idx, val in enumerate(col_values):
            if val.strip() == str(original_id).strip():
                return idx + 1  # gspreadは1-indexed
        return None
    except Exception:
        return None

# --- UI ---
st.caption(
    "スプレッドシートに書き込むには、Streamlit Cloud の Secrets に "
    "`[gcp_service_account]` セクションでService AccountのJSONを登録し、"
    "スプレッドシートをそのアカウントのメールアドレスに共有してください。"
)

ASSIGNEE_OPTIONS = ["Ito", "Kumakura", "Miura", "Ota", "Shinoda", "Assistant A", "Assistant B"]
assignee = st.selectbox("担当者", options=ASSIGNEE_OPTIONS,
    index=ASSIGNEE_OPTIONS.index(st.session_state.get("assignee", "Kumakura"))
          if st.session_state.get("assignee") in ASSIGNEE_OPTIONS else 0,
    key="assignee_input")
st.session_state["assignee"] = assignee

col_prev, col_save = st.columns([2, 1])

# プレビュー
with col_prev:
    st.markdown("**書き込み内容プレビュー**")
    preview_row = build_row(d, assignee)
    preview_df  = dict(zip(SHEET_COLUMNS, preview_row))
    st.table(preview_df)

# 保存ボタン
with col_save:
    st.markdown("&nbsp;", unsafe_allow_html=True)  # 縦位置調整
    if st.button("📤 スプレッドシートに保存", use_container_width=True, type="primary"):
        if not assignee:
            st.error("担当者名を入力してください。")
        elif not d.get("original_id"):
            st.error("@source (12digitsID) が空です。入力してから保存してください。")
        else:
            try:
                gc        = get_gspread_client()
                sh        = gc.open_by_key(DATASET_SHEET_ID)
                ws        = sh.get_worksheet(0)  # 最初のシート
                row_data  = build_row(d, assignee)
                row_num   = find_row_by_id(ws, d["original_id"])

                if row_num:
                    # 既存行を更新
                    ws.update(f"A{row_num}:H{row_num}", [row_data])
                    st.success(f"✅ 行 {row_num} を更新しました（12digitsID: {d['original_id']}）")
                else:
                    # 新規行を追加
                    ws.append_row(row_data, value_input_option="USER_ENTERED")
                    st.success(f"✅ 新規行を追加しました（12digitsID: {d['original_id']}）")

            except ImportError as e:
                st.error(f"ライブラリ不足: {e}\nrequirements.txt に gspread と google-auth を追加してください。")
            except Exception as e:
                import traceback
                st.error(f"保存エラー: {type(e).__name__}: {e}")
                st.code(traceback.format_exc())
                
