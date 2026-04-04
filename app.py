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
    """IDを適切なプレフィックス付きの参照文字列に変換する。
    TMP-X-XXXXX → #TMP-X-XXXXX
    Q数字        → wd:Q数字
    数字のみ      → gn:数字
    その他        → そのまま
    """
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
    """リスト内のアイテムを上下に移動する（-1=上, +1=下）"""
    new_index = index + direction
    if 0 <= new_index < len(lst):
        lst[index], lst[new_index] = lst[new_index], lst[index]

# --- 4. データ定義 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)": "Q160851",
    "Maliki (マーリク派)": "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)": "Q191314",
    "Unknown / Other": ""
}

INSTITUTION_TYPES = [
    "study", "teach", "reside", "founded", "affiliated",
    "graduated", "employed", "visit", "other"
]

ACTIVITY_TYPES = ["study", "buried", "reside", "visit", "born", "died", "other"]

# --- 5. セッション状態の初期化 ---
if 'data_v16' not in st.session_state:
    st.session_state.data_v16 = {
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
        "laqabs": [],
        "activities": [],
        "teachers": [],
        "students": [],
        "institutions": [],
        "offices": [],
        "family": [],
        "source_text": "",
        "translation_jp": "",
        "translation_en": ""
    }

d = st.session_state.data_v16

# ===================================================
# ヘルパー: 並び替えボタン付きセクションの共通部品
# ===================================================
def reorder_buttons(section_key, index, total):
    """上下移動ボタンを描画し、押されたら移動してrerun"""
    btn_up   = st.button("▲", key=f"up_{section_key}_{index}",   disabled=(index == 0))
    btn_down = st.button("▼", key=f"dn_{section_key}_{index}",   disabled=(index == total - 1))
    if btn_up:
        move_item(d[section_key], index, -1)
        st.rerun()
    if btn_down:
        move_item(d[section_key], index, +1)
        st.rerun()

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
You are a professional historian of Islamic studies. Extract data from the source text into JSON.

【Translation】
- translation_jp: Accurate academic Japanese translation of the full text.
- translation_en: Accurate academic English translation of the full text.

【ID Rules】
- Places: Use real GeoNames numeric ID if known (e.g. "104515" for Mecca). Otherwise "TMP-L-00000".
- Institutions: Use real Wikidata Q-ID if known. Otherwise "TMP-I-00000".
- Offices/Positions: Use Wikidata Q-ID if known. Otherwise "TMP-O-00000".
- Persons: Use Wikidata Q-ID if known. Otherwise "TMP-P-00000".

【Teachers / Students】
- subject: academic discipline (e.g. "Hadith", "Fiqh", "Arabic").
- subject_id: TMP-S-00000 unless a real ID is known.
- text_ar / text_lat: specific book title if mentioned; otherwise leave empty.

【Laqab / Shuhrah / Kunyah】
- laqab: honorific title (e.g. زين الدين).
- shuhrah: popular name/epithet the person was known by.
- kunyah: teknonym starting with أبو / أم.
- Extract all that appear in the text.

【Institutions】
- Record in the ORDER they appear in the text (seq starts at 1).
- type: the person's relationship to the institution.
  Allowed values: study | teach | reside | founded | affiliated | graduated | employed | visit | other
- name_ar: Arabic name. name_lat: Latinized name.

【Offices】
- Record offices/positions held, in the ORDER they appear or were held.
- seq: sequential order number starting from 1.
- name_ar: Arabic title of the office (e.g. "قاضي القضاة").
- name_lat: Latinized title (e.g. "Qadi al-Qudat").
- id: Wikidata Q-ID or TMP-O-00000.

【Activities】
- Record in the ORDER they appear in the text (seq starts at 1).

Return ONLY valid JSON with NO markdown fences:
{{
    "original_id": "",
    "full_name": "",
    "name_only": "",
    "birth_h": "",
    "death_h": "",
    "madhhab_name": "",
    "nisbahs": [{{"ar": "", "lat": "", "id": "TMP-L-00000"}}],
    "laqabs": [{{"type": "laqab", "ar": "", "lat": ""}}],
    "activities": [{{
        "seq": 1,
        "place_ar": "", "place_lat": "",
        "type": "study",
        "id": ""
    }}],
    "teachers": [{{
        "name": "", "id": "TMP-P-00000",
        "subject": "", "subject_id": "TMP-S-00000",
        "text_ar": "", "text_lat": ""
    }}],
    "students": [{{
        "name": "", "id": "TMP-P-00000",
        "subject": "", "subject_id": "TMP-S-00000",
        "text_ar": "", "text_lat": ""
    }}],
    "institutions": [{{
        "seq": 1,
        "name_ar": "", "name_lat": "",
        "type": "study",
        "id": "TMP-I-00000"
    }}],
    "offices": [{{
        "seq": 1,
        "name_ar": "", "name_lat": "",
        "id": "TMP-O-00000"
    }}],
    "translation_jp": "",
    "translation_en": ""
}}
Text: {source_input}
"""
                    response = model.generate_content(prompt)
                    raw = response.text
                    raw = re.sub(r"```json|```", "", raw).strip()
                    json_match_obj = re.search(r"\{.*\}", raw, re.DOTALL)

                    if json_match_obj:
                        res_json = json.loads(json_match_obj.group())

                        list_keys = ["teachers", "students", "activities", "nisbahs", "laqabs", "family", "institutions", "offices"]
                        for k in list_keys:
                            if k in res_json:
                                for item in res_json[k]:
                                    item["ui_id"] = str(uuid.uuid4())
                                d[k] = res_json[k]

                        scalar_fields = [
                            "original_id", "full_name", "name_only",
                            "birth_h", "death_h",
                            "translation_jp", "translation_en"
                        ]
                        for field in scalar_fields:
                            if field in res_json:
                                d[field] = res_json[field]

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
    d["full_name"]   = st.text_input("persName (Full Arabic)", d["full_name"])
    d["name_only"]   = st.text_input("persName (Ism/Father/GF)", d["name_only"])

    # --- Nisbahs ---
    st.divider()
    st.subheader("🏷️ Nisbahs")

    h3 = st.columns([1, 1, 1, 0.3])
    h3[0].caption("Arabic")
    h3[1].caption("Latinized")
    h3[2].caption("ID (TMP-L-XXXXX / Q)")
    h3[3].caption("Del")

    for i, item in enumerate(d.get("nisbahs", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 0.3])
        item["ar"]  = r[0].text_input("ar",  item.get("ar", ""),  key=f"n_a_{uid}", label_visibility="collapsed")
        item["lat"] = r[1].text_input("lat", item.get("lat", ""), key=f"n_l_{uid}", label_visibility="collapsed")
        item["id"]  = r[2].text_input("id",  item.get("id", ""),  key=f"n_i_{uid}", label_visibility="collapsed", placeholder="TMP-L-00001 または Q数字")
        if r[3].button("❌", key=f"n_del_{uid}"):
            d["nisbahs"].pop(i)
            st.rerun()

    if st.button("＋ add nisbah"):
        d["nisbahs"].append({
            "ui_id": str(uuid.uuid4()),
            "ar": "", "lat": "", "id": "TMP-L-00000"
        })
        st.rerun()

    # --- Laqab / Shuhrah / Kunyah ---
    st.divider()
    st.subheader("🔤 Laqab / Shuhrah / Kunyah")

    LAQAB_TYPES = ["laqab", "shuhrah", "kunyah"]
    laqab_type_labels = {
        "laqab": "laqab（号）",
        "shuhrah": "shuhrah（通称）",
        "kunyah": "kunyah（クンヤ）"
    }

    lq_h = st.columns([1, 1, 1, 0.3])
    lq_h[0].caption("Type")
    lq_h[1].caption("Arabic")
    lq_h[2].caption("Latinized")
    lq_h[3].caption("Del")

    for i, item in enumerate(d.get("laqabs", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        r = st.columns([1, 1, 1, 0.3])
        cur_ltype = item.get("type", "laqab")
        ltype_index = LAQAB_TYPES.index(cur_ltype) if cur_ltype in LAQAB_TYPES else 0
        item["type"] = r[0].selectbox("type", LAQAB_TYPES,
                                       format_func=lambda x: laqab_type_labels[x],
                                       index=ltype_index,
                                       key=f"lq_t_{uid}", label_visibility="collapsed")
        item["ar"]  = r[1].text_input("ar",  item.get("ar", ""),  key=f"lq_a_{uid}", label_visibility="collapsed", placeholder="例: زين الدين / أبو بكر")
        item["lat"] = r[2].text_input("lat", item.get("lat", ""), key=f"lq_l_{uid}", label_visibility="collapsed", placeholder="例: Zayn al-Din / Abu Bakr")
        if r[3].button("❌", key=f"lq_del_{uid}"):
            d["laqabs"].pop(i)
            st.rerun()

    if st.button("＋ add laqab / shuhrah / kunyah"):
        d["laqabs"].append({
            "ui_id": str(uuid.uuid4()),
            "type": "laqab", "ar": "", "lat": ""
        })
        st.rerun()

    # --- 生没年 ---
    dc1, dc2, dc3, dc4 = st.columns(4)
    d["birth_h"] = dc1.text_input("Birth (H)", d["birth_h"])
    dc2.text_input("Birth (G)", value=convert_h_to_g(d["birth_h"]), disabled=True)
    d["death_h"] = dc3.text_input("Death (H)", d["death_h"])
    dc4.text_input("Death (G)", value=convert_h_to_g(d["death_h"]), disabled=True)

    # --- Madhhab ---
    m_col1, m_col2 = st.columns(2)
    madhhab_keys  = list(MADHHAB_DATA.keys())
    current_madhhab = d["madhhab"]["lat"]
    default_index   = madhhab_keys.index(current_madhhab) if current_madhhab in madhhab_keys else 4
    selected_m = m_col1.selectbox("⚖️ Madhhab", options=madhhab_keys, index=default_index)
    d["madhhab"] = {"lat": selected_m, "id": MADHHAB_DATA[selected_m]}
    m_col2.text_input("Wikidata ID", value=d["madhhab"]["id"], disabled=True)

    # ===================================================
    # --- Teachers ---
    # ===================================================
    st.divider()
    st.subheader("🎓 Teachers & Subjects")

    for i, item in enumerate(d.get("teachers", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        with st.container():
            r1 = st.columns([1.2, 1, 1, 1, 0.3])
            r1[0].caption("Name")
            r1[1].caption("Person ID")
            r1[2].caption("Subject")
            r1[3].caption("Subject ID")
            item["name"]       = r1[0].text_input("Name",       item.get("name", ""),       key=f"t_n_{uid}",  label_visibility="collapsed")
            item["id"]         = r1[1].text_input("Person ID",  item.get("id", ""),         key=f"t_i_{uid}",  label_visibility="collapsed")
            item["subject"]    = r1[2].text_input("Subject",    item.get("subject", ""),    key=f"t_s_{uid}",  label_visibility="collapsed")
            item["subject_id"] = r1[3].text_input("Subject ID", item.get("subject_id", ""), key=f"t_si_{uid}", label_visibility="collapsed")
            if r1[4].button("❌", key=f"t_del_{uid}"):
                d["teachers"].pop(i)
                st.rerun()

            r2 = st.columns([1, 1])
            r2[0].caption("📖 Text (Arabic)")
            r2[1].caption("📖 Text (Latinized)")
            item["text_ar"]  = r2[0].text_input("text_ar",  item.get("text_ar", ""),  key=f"t_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
            item["text_lat"] = r2[1].text_input("text_lat", item.get("text_lat", ""), key=f"t_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")

        st.markdown("---")

    if st.button("＋ add teacher"):
        d["teachers"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "", "id": "TMP-P-00000",
            "subject": "", "subject_id": "TMP-S-00000",
            "text_ar": "", "text_lat": ""
        })
        st.rerun()

    # ===================================================
    # --- Students ---
    # ===================================================
    st.divider()
    st.subheader("🧑‍🎓 Students & Subjects")

    for i, item in enumerate(d.get("students", [])):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        with st.container():
            r1 = st.columns([1.2, 1, 1, 1, 0.3])
            r1[0].caption("Name")
            r1[1].caption("Person ID")
            r1[2].caption("Subject")
            r1[3].caption("Subject ID")
            item["name"]       = r1[0].text_input("Name",       item.get("name", ""),       key=f"s_n_{uid}",  label_visibility="collapsed")
            item["id"]         = r1[1].text_input("Person ID",  item.get("id", ""),         key=f"s_i_{uid}",  label_visibility="collapsed")
            item["subject"]    = r1[2].text_input("Subject",    item.get("subject", ""),    key=f"s_s_{uid}",  label_visibility="collapsed")
            item["subject_id"] = r1[3].text_input("Subject ID", item.get("subject_id", ""), key=f"s_si_{uid}", label_visibility="collapsed")
            if r1[4].button("❌", key=f"s_del_{uid}"):
                d["students"].pop(i)
                st.rerun()

            r2 = st.columns([1, 1])
            r2[0].caption("📖 Text (Arabic)")
            r2[1].caption("📖 Text (Latinized)")
            item["text_ar"]  = r2[0].text_input("text_ar",  item.get("text_ar", ""),  key=f"s_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
            item["text_lat"] = r2[1].text_input("text_lat", item.get("text_lat", ""), key=f"s_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")

        st.markdown("---")

    if st.button("＋ add student"):
        d["students"].append({
            "ui_id": str(uuid.uuid4()),
            "name": "", "id": "TMP-P-00000",
            "subject": "", "subject_id": "TMP-S-00000",
            "text_ar": "", "text_lat": ""
        })
        st.rerun()

    # ===================================================
    # --- Activities（順序付き・並び替え可） ---
    # ===================================================
    st.divider()
    st.subheader("📍 Activities / Places")
    st.caption("▲▼ で順番を入れ替えられます。順番は seq 属性として XML に反映されます。")

    acts = d.get("activities", [])
    total_acts = len(acts)

    for i, item in enumerate(acts):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        # seq を常に現在のリスト位置に同期
        item["seq"] = i + 1

        with st.container():
            # ヘッダ行: seq番号 ＋ 並び替えボタン
            hcol = st.columns([0.15, 0.25, 3])
            hcol[0].markdown(f"**#{i+1}**")
            with hcol[1]:
                if st.button("▲", key=f"act_up_{uid}", disabled=(i == 0)):
                    move_item(d["activities"], i, -1)
                    st.rerun()
                if st.button("▼", key=f"act_dn_{uid}", disabled=(i == total_acts - 1)):
                    move_item(d["activities"], i, +1)
                    st.rerun()

            # データ入力行
            r = st.columns([1, 1, 1, 1.3, 0.3])
            r[0].caption("Place (Arabic)")
            r[1].caption("Place (Latin)")
            r[2].caption("Type")
            r[3].caption("ID: GeoNames / TMP-L- / Q")
            item["place_ar"]  = r[0].text_input("place_ar",  item.get("place_ar", ""),  key=f"a_a_{uid}", label_visibility="collapsed")
            item["place_lat"] = r[1].text_input("place_lat", item.get("place_lat", ""), key=f"a_l_{uid}", label_visibility="collapsed")
            cur_type    = item.get("type", "study")
            type_index  = ACTIVITY_TYPES.index(cur_type) if cur_type in ACTIVITY_TYPES else 0
            item["type"] = r[2].selectbox("type", ACTIVITY_TYPES, index=type_index, key=f"a_t_{uid}", label_visibility="collapsed")
            item["id"]   = r[3].text_input("id", item.get("id", ""), key=f"a_i_{uid}", label_visibility="collapsed", placeholder="例: 104515 / TMP-L-00001 / Q12345")
            if r[4].button("❌", key=f"a_del_{uid}"):
                d["activities"].pop(i)
                st.rerun()

        st.markdown("---")

    if st.button("＋ add activity"):
        d["activities"].append({
            "ui_id": str(uuid.uuid4()),
            "seq": len(d["activities"]) + 1,
            "place_ar": "", "place_lat": "", "type": "study", "id": ""
        })
        st.rerun()

    # ===================================================
    # --- Institutions（順序付き・並び替え可・Type追加） ---
    # ===================================================
    st.divider()
    st.subheader("🏛️ Institutions")
    st.caption("▲▼ で順番を入れ替えられます。順番は seq 属性として XML に反映されます。")

    insts = d.get("institutions", [])
    total_insts = len(insts)

    for i, item in enumerate(insts):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        # 旧データ互換
        if "name" in item and "name_ar" not in item:
            item["name_ar"] = item.pop("name")

        item["seq"] = i + 1

        with st.container():
            hcol = st.columns([0.15, 0.25, 3])
            hcol[0].markdown(f"**#{i+1}**")
            with hcol[1]:
                if st.button("▲", key=f"ins_up_{uid}", disabled=(i == 0)):
                    move_item(d["institutions"], i, -1)
                    st.rerun()
                if st.button("▼", key=f"ins_dn_{uid}", disabled=(i == total_insts - 1)):
                    move_item(d["institutions"], i, +1)
                    st.rerun()

            r = st.columns([1, 1, 1, 1.2, 0.3])
            r[0].caption("Name (Arabic)")
            r[1].caption("Name (Latin)")
            r[2].caption("Type")
            r[3].caption("ID: Q / TMP-I- / GeoNames")
            item["name_ar"]  = r[0].text_input("name_ar",  item.get("name_ar", ""),  key=f"i_a_{uid}", label_visibility="collapsed", placeholder="アラビア語名")
            item["name_lat"] = r[1].text_input("name_lat", item.get("name_lat", ""), key=f"i_l_{uid}", label_visibility="collapsed", placeholder="Latinized name")
            cur_itype   = item.get("type", "study")
            itype_index = INSTITUTION_TYPES.index(cur_itype) if cur_itype in INSTITUTION_TYPES else 0
            item["type"] = r[2].selectbox("type", INSTITUTION_TYPES, index=itype_index, key=f"i_t_{uid}", label_visibility="collapsed")
            item["id"]   = r[3].text_input("id", item.get("id", ""), key=f"i_i_{uid}", label_visibility="collapsed", placeholder="例: Q12345 / TMP-I-00001 / 104515")
            if r[4].button("❌", key=f"i_del_{uid}"):
                d["institutions"].pop(i)
                st.rerun()

        st.markdown("---")

    if st.button("＋ add institution"):
        d["institutions"].append({
            "ui_id": str(uuid.uuid4()),
            "seq": len(d["institutions"]) + 1,
            "name_ar": "", "name_lat": "", "type": "study", "id": "TMP-I-00000"
        })
        st.rerun()

    # ===================================================
    # --- Offices（官職・順序付き・並び替え可） ---
    # ===================================================
    st.divider()
    st.subheader("🏅 Offices / Positions")
    st.caption("官職・役職を保有した順に記録します。▲▼ で順番を入れ替えられます。")

    offices = d.get("offices", [])
    total_offices = len(offices)

    for i, item in enumerate(offices):
        if "ui_id" not in item:
            item["ui_id"] = str(uuid.uuid4())
        uid = item["ui_id"]

        item["seq"] = i + 1

        with st.container():
            hcol = st.columns([0.15, 0.25, 3])
            hcol[0].markdown(f"**#{i+1}**")
            with hcol[1]:
                if st.button("▲", key=f"off_up_{uid}", disabled=(i == 0)):
                    move_item(d["offices"], i, -1)
                    st.rerun()
                if st.button("▼", key=f"off_dn_{uid}", disabled=(i == total_offices - 1)):
                    move_item(d["offices"], i, +1)
                    st.rerun()

            r = st.columns([1.2, 1.2, 1.2, 0.3])
            r[0].caption("Name (Arabic)")
            r[1].caption("Name (Latinized)")
            r[2].caption("ID: Q / TMP-O-")
            item["name_ar"]  = r[0].text_input("name_ar",  item.get("name_ar", ""),  key=f"o_a_{uid}", label_visibility="collapsed", placeholder="例: قاضي القضاة")
            item["name_lat"] = r[1].text_input("name_lat", item.get("name_lat", ""), key=f"o_l_{uid}", label_visibility="collapsed", placeholder="例: Qadi al-Qudat")
            item["id"]       = r[2].text_input("id",       item.get("id", ""),       key=f"o_i_{uid}", label_visibility="collapsed", placeholder="例: Q12345 / TMP-O-00001")
            if r[3].button("❌", key=f"o_del_{uid}"):
                d["offices"].pop(i)
                st.rerun()

        st.markdown("---")

    if st.button("＋ add office"):
        d["offices"].append({
            "ui_id": str(uuid.uuid4()),
            "seq": len(d["offices"]) + 1,
            "name_ar": "", "name_lat": "", "id": "TMP-O-00000"
        })
        st.rerun()

    # ===================================================
    # --- Family ---
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
            "name": "", "relation": "", "id": "TMP-P-00000"
        })
        st.rerun()


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
        xml_lines.append(
            f'    <persName type="nisbah" xml:lang="ar" ref="{fr(n.get("id"))}">'
            f'{n.get("ar")}</persName>'
        )

for lq in d.get("laqabs", []):
    if lq.get("ar"):
        xml_lines.append(
            f'    <persName type="{lq.get("type", "laqab")}" xml:lang="ar">'
            f'{lq.get("ar")}</persName>'
        )

if d["madhhab"]["id"]:
    xml_lines.append(
        f'    <affiliation type="madhhab" ref="wd:{d["madhhab"]["id"]}">'
        f'{d["madhhab"]["lat"]}</affiliation>'
    )

if d.get("birth_h"):
    xml_lines.append(
        f'    <birth when-custom="{d["birth_h"]}" when="{convert_h_to_g(d["birth_h"])}"/>'
    )
if d.get("death_h"):
    xml_lines.append(
        f'    <death when-custom="{d["death_h"]}" when="{convert_h_to_g(d["death_h"])}"/>'
    )

# listRelation: teachers / students / family
xml_lines.append('    <listRelation>')

for t in d.get("teachers", []):
    xml_lines.append(
        f'        <relation name="teacher" active="{fr(t.get("id"))}" passive="#{d["aind_id"]}">'
    )
    if t.get("subject"):
        xml_lines.append(
            f'            <desc ref="{fr(t.get("subject_id", ""))}">{t.get("subject")}</desc>'
        )
    if t.get("text_ar"):
        xml_lines.append(f'            <bibl xml:lang="ar">{t["text_ar"]}</bibl>')
    if t.get("text_lat"):
        xml_lines.append(f'            <bibl xml:lang="lat">{t["text_lat"]}</bibl>')
    xml_lines.append('        </relation>')

for s in d.get("students", []):
    xml_lines.append(
        f'        <relation name="student" active="#{d["aind_id"]}" passive="{fr(s.get("id"))}">'
    )
    if s.get("subject"):
        xml_lines.append(
            f'            <desc ref="{fr(s.get("subject_id", ""))}">{s.get("subject")}</desc>'
        )
    if s.get("text_ar"):
        xml_lines.append(f'            <bibl xml:lang="ar">{s["text_ar"]}</bibl>')
    if s.get("text_lat"):
        xml_lines.append(f'            <bibl xml:lang="lat">{s["text_lat"]}</bibl>')
    xml_lines.append('        </relation>')

for fam in d.get("family", []):
    xml_lines.append(
        f'        <relation name="family" active="{fr(fam.get("id"))}" '
        f'passive="#{d["aind_id"]}" subtype="{fam.get("relation", "")}">'
        f'{fam.get("name", "")}</relation>'
    )

xml_lines.append('    </listRelation>')

# Activities（seq属性付き）
for a in d.get("activities", []):
    if a.get("place_ar"):
        xml_lines.append(
            f'    <residence seq="{a.get("seq", "")}" subtype="{a.get("type", "")}" '
            f'ref="{fr(a.get("id"))}">{a.get("place_ar")}</residence>'
        )

# Institutions（seq属性・type属性・orgName二言語）
for inst in d.get("institutions", []):
    name_ar  = inst.get("name_ar",  inst.get("name", ""))
    name_lat = inst.get("name_lat", "")
    inst_ref = fr(inst.get("id", ""))
    if name_ar or name_lat:
        xml_lines.append(
            f'    <affiliation type="institution" subtype="{inst.get("type", "")}" '
            f'seq="{inst.get("seq", "")}" ref="{inst_ref}">'
        )
        if name_ar:
            xml_lines.append(f'        <orgName xml:lang="ar">{name_ar}</orgName>')
        if name_lat:
            xml_lines.append(f'        <orgName xml:lang="lat">{name_lat}</orgName>')
        xml_lines.append('    </affiliation>')

# Offices（seq属性付き）
for off in d.get("offices", []):
    name_ar  = off.get("name_ar", "")
    name_lat = off.get("name_lat", "")
    off_ref  = fr(off.get("id", ""))
    if name_ar or name_lat:
        xml_lines.append(
            f'    <state type="office" seq="{off.get("seq", "")}" ref="{off_ref}">'
        )
        if name_ar:
            xml_lines.append(f'        <label xml:lang="ar">{name_ar}</label>')
        if name_lat:
            xml_lines.append(f'        <label xml:lang="lat">{name_lat}</label>')
        xml_lines.append('    </state>')

if d.get("translation_jp"):
    xml_lines.append(f'    <note type="translation" xml:lang="ja">{d["translation_jp"]}</note>')
if d.get("translation_en"):
    xml_lines.append(f'    <note type="translation" xml:lang="en">{d["translation_en"]}</note>')

xml_lines.append("</person>")

xml_str = "\n".join(xml_lines)
st.code(xml_str, language="xml")

st.download_button(
    label="💾 XMLをダウンロード",
    data=xml_str,
    file_name=f"{d['aind_id']}.xml",
    mime="application/xml"
)
