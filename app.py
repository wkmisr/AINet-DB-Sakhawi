import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import re
import uuid
import requests

# --- 1. ページ設定 ---
st.set_page_config(page_title="AINet-DB Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
section[data-testid="stSidebar"] .stTextArea textarea {
    font-size: 1.25rem !important;
    line-height: 1.6 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    PREFERRED_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.0-flash-lite',
        'gemini-1.5-flash',
    ]
    try:
        available = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
            and 'tts' not in m.name
            and 'vision' not in m.name
        ]
        for preferred in PREFERRED_MODELS:
            for m in available:
                if preferred in m:
                    return genai.GenerativeModel(m)
        if available:
            return genai.GenerativeModel(available[0])
    except Exception:
        pass
    return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ユーティリティ関数 ---
def convert_h_to_g(h_date):
    """ヒジュラ暦 → 西暦変換。入力の精度(年/年月/年月日)に出力を合わせる。
    convertdate(歴史的範囲対応)を優先し、利用不可時は簡易計算で年のみ返す。"""
    try:
        s = str(h_date).strip() if h_date is not None else ""
        if not s:
            return ""
        parts = s.split("-")
        h_year_str = re.sub(r"\D", "", parts[0])
        if not h_year_str:
            return ""
        h_year = int(h_year_str)
        h_month = int(parts[1]) if len(parts) > 1 and parts[1].strip() else 1
        h_day   = int(parts[2]) if len(parts) > 2 and parts[2].strip() else 1

        try:
            from convertdate import islamic
            gy, gm, gd = islamic.to_gregorian(h_year, h_month, h_day)
            if len(parts) >= 3:
                return f"{gy:04d}-{gm:02d}-{gd:02d}"
            elif len(parts) == 2:
                return f"{gy:04d}-{gm:02d}"
            else:
                return f"{gy:04d}"
        except ImportError:
            # フォールバック: 年だけの簡易計算
            return str(int(h_year * 0.97 + 622))
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

def escape_xml(s):
    """要素中身用の XML エスケープ(必須最小限)。"""
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def escape_xml_attr(s):
    """属性値用の XML エスケープ(完全版)。"""
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

def detect_lang(text):
    """note / desc 等の中身から xml:lang 値を推定(多数決方式)。"""
    if not text:
        return "en"
    s = str(text)
    ja_chars = len(re.findall(r'[぀-ゟ゠-ヿ一-鿿]', s))
    ar_chars = len(re.findall(r'[؀-ۿ]', s))
    en_chars = len(re.findall(r'[a-zA-Z]', s))
    counts = [("ja", ja_chars), ("ar", ar_chars), ("en", en_chars)]
    counts.sort(key=lambda x: x[1], reverse=True)
    if counts[0][1] == 0:
        return "en"
    return counts[0][0]

def is_id_format(s):
    """文字列が ID 形式(TMP-X-NNNNN, Qnnn, gn:nnn, 数字)かどうか判定"""
    if not s:
        return False
    s = str(s).strip()
    return bool(re.match(r"^(TMP-[A-Z]-\d+|Q\d+|gn:\d+|\d+)$", s))

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

@st.cache_data(ttl=300)
def build_method_field_dicts():
    """ID-Master から Method/Field 辞書を動的構築"""
    records = load_id_master()
    method_dict = {}
    field_dict = {}

    for r in records:
        if r.get("Category") != "Subject":
            continue
        id_val = r.get("ID", "").strip()
        if not id_val:
            continue

        entry = {
            "ar":  r.get("Arabic", "").strip(),
            "lat": r.get("Latin",  "").strip(),
            "ja":  r.get("Note",   "").strip(),
        }

        if id_val in METHOD_IDS:
            method_dict[id_val] = entry
        elif id_val in FIELD_IDS:
            field_dict[id_val] = entry

    return method_dict, field_dict


def format_method_field_label(id_, entry):
    """ラベル文字列を生成: 'سمع (samiʿa) — 聴聞した'"""
    parts = []
    if entry.get("ar"):  parts.append(entry["ar"])
    if entry.get("lat"): parts.append(f"({entry['lat']})")
    if entry.get("ja"):  parts.append(f"— {entry['ja']}")
    return " ".join(parts) if parts else id_


def render_method_field_input(container, value, options_dict, key, placeholder=""):
    """
    Method/Field 用の入力UI(プルダウン + 自由記述切替)。

    Args:
        container: streamlit カラムまたは container
        value: 現在の値
        options_dict: {id: {ar, lat, ja}}
        key: streamlit key prefix
        placeholder: テキスト入力用 placeholder

    Returns:
        ユーザーが選択/入力した値
    """
    is_known_id = value in options_dict

    options = [("", "— 未選択 —")]
    options.extend(
        (id_, format_method_field_label(id_, v))
        for id_, v in sorted(options_dict.items())
    )
    options.append(("__custom__", "✏️ Other(自由記述)"))

    option_keys = [o[0] for o in options]
    option_labels = {o[0]: o[1] for o in options}

    if is_known_id:
        cur_key = value
    elif value:
        cur_key = "__custom__"
    else:
        cur_key = ""

    cur_idx = option_keys.index(cur_key) if cur_key in option_keys else 0

    selected = container.selectbox(
        "select",
        option_keys,
        format_func=lambda x: option_labels[x],
        index=cur_idx,
        key=f"{key}_sel",
        label_visibility="collapsed",
    )

    if selected == "__custom__":
        custom_value = container.text_input(
            "custom",
            value if not is_known_id else "",
            key=f"{key}_txt",
            label_visibility="collapsed",
            placeholder=placeholder,
        )
        return custom_value
    elif selected == "":
        return ""
    else:
        return selected

# --- 5. 定数 ---
MADHHAB_DATA = {
    "Hanafi (ハナフィー派)":    "Q160851",
    "Maliki (マーリク派)":      "Q48221",
    "Shafi'i (シャーフィイー派)": "Q82245",
    "Hanbali (ハンバリー派)":   "Q191314",
    "Unknown / Other":          ""
}
INSTITUTION_TYPES = ["study","teach","reside","founded","affiliated","graduated","employed","visit","buried","other"]

ACTIVITY_TYPES = [
    "born", "died", "buried",
    "reside", "visit", "travel", "study",
    "hajj", "umrah",
    "other",
]

LAQAB_TYPES  = ["laqab", "shuhrah", "kunyah", "honorific"]
LAQAB_LABELS = {
    "laqab":     "laqab(号)",
    "shuhrah":   "shuhrah(通称)",
    "kunyah":    "kunyah(クンヤ)",
    "honorific": "honorific(敬称)",
}

FAMILY_RELATIONS = [
    ("father",         "Father (父)"),
    ("mother",         "Mother (母)"),
    ("son",            "Son (息子)"),
    ("daughter",       "Daughter (娘)"),
    ("brother",        "Brother (兄弟)"),
    ("sister",         "Sister (姉妹)"),
    ("spouse",         "Spouse (配偶者)"),
    ("grandfather",    "Grandfather (祖父)"),
    ("grandmother",    "Grandmother (祖母)"),
    ("uncle",          "Uncle (おじ)"),
    ("aunt",           "Aunt (おば)"),
    ("cousin",         "Cousin (いとこ)"),
    ("siblings_child", "Sibling's child (甥・姪)"),
    ("ancestor",       "Ancestor (先祖)"),
    ("descendant",     "Descendant (子孫)"),
    ("other",          "Other / Unknown (その他)"),
]
FAMILY_RELATION_KEYS   = [r[0] for r in FAMILY_RELATIONS]
FAMILY_RELATION_LABELS = {r[0]: r[1] for r in FAMILY_RELATIONS}

# === 新規定数 ===

# Sex
SEX_OPTIONS = [
    ("M", "Male (男性)"),
    ("F", "Female (女性)"),
    ("U", "Unknown (不明)"),
]

# Date certainty
DATE_CERT_OPTIONS = [
    ("",       "(未指定)"),
    ("high",   "High (確実)"),
    ("medium", "Medium (おそらく)"),
    ("low",    "Low (推定)"),
]

# Bio Events types
BIO_EVENT_TYPES = [
    ("political",  "Political (政治的事件)"),
    ("cultural",   "Cultural (著作・知的活動)"),
    ("religious",  "Religious (宗教的事件)"),
    ("other",      "Other (その他)"),
]

# Social Relations types
SOCIAL_RELATION_TYPES = [
    ("patron",        "Patron (庇護者)"),
    ("client",        "Client (被庇護者)"),
    ("colleague",     "Colleague (同僚)"),
    ("rival",         "Rival (論敵)"),
    ("friend",        "Friend (友人)"),
    ("correspondent", "Correspondent (書簡相手)"),
    ("successor",     "Successor (後継者)"),
    ("predecessor",   "Predecessor (前任者)"),
    ("other",         "Other (その他)"),
]

# === Method/Field 振り分け用 ID セット ===
METHOD_IDS = {
    "TMP-S-00003", "TMP-S-00004", "TMP-S-00005", "TMP-S-00006",
    "TMP-S-00008", "TMP-S-00009", "TMP-S-00010", "TMP-S-00011",
    "TMP-S-00014", "TMP-S-00015", "TMP-S-00016", "TMP-S-00025",
    "TMP-S-00026", "TMP-S-00027", "TMP-S-00028", "TMP-S-00029",
    "TMP-S-00030", "TMP-S-00031", "TMP-S-00032", "TMP-S-00033",
    "TMP-S-00034", "TMP-S-00035", "TMP-S-00036", "TMP-S-00037",
    "TMP-S-00038", "TMP-S-00039", "TMP-S-00040", "TMP-S-00041",
    "TMP-S-00042", "TMP-S-00043",
}

FIELD_IDS = {
    "TMP-S-00001", "TMP-S-00002", "TMP-S-00007", "Q484181",
    "TMP-S-00012", "TMP-S-00013", "Q1817983", "Q1866303",
    "TMP-S-00017", "TMP-S-00018", "TMP-S-00020", "TMP-S-00021",
    "TMP-S-00022", "TMP-S-00023", "TMP-S-00024",
    "TMP-S-00044", "TMP-S-00045", "TMP-S-00046", "TMP-S-00047",
    "TMP-S-00048", "TMP-S-00049", "TMP-S-00050", "TMP-S-00051",
    "TMP-S-00052", "TMP-S-00053", "TMP-S-00054", "TMP-S-00055",
    "TMP-S-00056", "TMP-S-00057", "TMP-S-00058", "TMP-S-00059",
    "TMP-S-00060", "TMP-S-00061", "TMP-S-00062", "TMP-S-00063",
    "TMP-S-00064", "TMP-S-00065", "TMP-S-00066",
}

# --- 6. データ構造定義・migration・プロンプト反映 ---

DEFAULT_DATA_V19 = {
    # === 基本識別情報 ===
    "aind_id": "AIND-D0000",
    "original_id": "",

    # === 名前 ===
    "full_name": "",
    "name_only": "",
    "full_name_lat": "",

    # === 基本属性 ===
    "sex": "U",
    "certainty": "High",

    # === 生没年 ===
    "birth_h": "",
    "birth_cert": "",
    "birth_note": "",
    "birth_g": "",
    "death_h": "",
    "death_cert": "",
    "death_note": "",
    "death_g": "",

    # === 法学派 ===
    "madhhab": {
        "lat": "Unknown / Other",
        "id": "",
        "custom_name": "",
        "custom_id": "",
    },

    # === スーフィー教団 ===
    "sufi_order": {"name": "", "id": ""},

    # === ニスバ・ラカブ ===
    "nisbahs": [],
    "laqabs": [],

    # === 学問関係 ===
    "teachers": [],
    "students": [],

    # === 地理・機関・職位 ===
    "activities": [],
    "institutions": [],
    "offices": [],

    # === 家族 ===
    "family": [],

    # === 新規セクション ===
    "bio_events": [],
    "social_relations": [],

    # === メモ・翻訳 ===
    "person_notes": "",
    "editors_notes": "",
    "source_text": "",
    "translation_jp": "",
    "translation_en": "",
}

RELATION_MIGRATION = {
    "p_uncle":           "uncle",
    "m_uncle":           "uncle",
    "brothers_son":      "siblings_child",
    "brothers_daughter": "siblings_child",
    "sisters_son":       "siblings_child",
    "sisters_daughter":  "siblings_child",
    "father":            "father",
    "mother":            "mother",
    "son":               "son",
    "daughter":          "daughter",
    "brother":           "brother",
    "sister":            "sister",
    "spouse":            "spouse",
    "grandfather":       "grandfather",
    "grandmother":       "grandmother",
    "uncle":             "uncle",
    "aunt":              "aunt",
    "cousin":            "cousin",
    "siblings_child":    "siblings_child",
    "ancestor":          "ancestor",
    "descendant":        "descendant",
    "other":             "other",
}


def migrate_teacher_student(old_item):
    """旧 teacher/student → 新スキーマへ"""
    old_subject    = old_item.get("subject", "").strip()
    old_subject_id = old_item.get("subject_id", "").strip()
    field_value    = old_subject_id if old_subject_id else old_subject

    return {
        "ui_id":           old_item.get("ui_id", str(uuid.uuid4())),
        "seq":             old_item.get("seq", 0),
        "name":            old_item.get("name", ""),
        "id":              old_item.get("id", ""),
        "method_id":       old_item.get("method_id", ""),
        "field_id":        old_item.get("field_id", field_value),
        "text_ar":         old_item.get("text_ar", ""),
        "text_lat":        old_item.get("text_lat", ""),
        "text_id":         old_item.get("text_id", ""),
        "learn_date":      old_item.get("learn_date", ""),
        "teach_date":      old_item.get("teach_date", ""),
        "learn_place_ar":  old_item.get("learn_place_ar", ""),
        "learn_place_lat": old_item.get("learn_place_lat", ""),
        "learn_place_id":  old_item.get("learn_place_id", ""),
        "teach_place_ar":  old_item.get("teach_place_ar", ""),
        "teach_place_lat": old_item.get("teach_place_lat", ""),
        "teach_place_id":  old_item.get("teach_place_id", ""),
    }


def migrate_activity(old_item):
    """activities の旧→新変換(date系を追加)"""
    new_item = dict(old_item)
    new_item.setdefault("date_h", "")
    new_item.setdefault("date_cert", "")
    new_item.setdefault("date_note", "")
    return new_item


def migrate_family(old_item):
    new_item = dict(old_item)
    old_rel = old_item.get("relation", "other")
    new_item["relation"] = RELATION_MIGRATION.get(old_rel, "other")
    return new_item


def migrate_v18_to_v19(old_data):
    """data_v18 → data_v19 への一括 migration"""
    new_data = json.loads(json.dumps(DEFAULT_DATA_V19))  # deep copy

    simple_fields = [
        "aind_id", "original_id", "full_name", "name_only", "full_name_lat",
        "certainty", "birth_h", "birth_g", "death_h", "death_g",
        "madhhab", "sufi_order", "nisbahs", "laqabs",
        "institutions", "offices", "person_notes", "editors_notes",
        "source_text", "translation_jp", "translation_en",
    ]
    for f in simple_fields:
        if f in old_data:
            new_data[f] = old_data[f]

    # sex の変換
    old_sex = old_data.get("sex", "")
    if old_sex == "Male":
        new_data["sex"] = "M"
    elif old_sex == "Female":
        new_data["sex"] = "F"
    elif old_sex in ("M", "F", "U"):
        new_data["sex"] = old_sex
    else:
        new_data["sex"] = "U"

    new_data["teachers"] = [
        migrate_teacher_student(t) for t in old_data.get("teachers", [])
    ]
    new_data["students"] = [
        migrate_teacher_student(s) for s in old_data.get("students", [])
    ]
    new_data["activities"] = [
        migrate_activity(a) for a in old_data.get("activities", [])
    ]
    new_data["family"] = [
        migrate_family(f) for f in old_data.get("family", [])
    ]

    # 新規配列はそのままコピー(既存があれば維持)
    for key in ("bio_events", "social_relations"):
        if key in old_data and isinstance(old_data[key], list):
            new_data[key] = old_data[key]

    return new_data


# === ID 統計・採番ヘルパー(機能 A / C 用) ===

TMP_ID_PREFIXES = {
    "TMP-P-": ("人物",   6),
    "TMP-N-": ("ニスバ", 5),
    "TMP-L-": ("地名",   5),
    "TMP-I-": ("機関",   5),
    "TMP-O-": ("役職",   5),
    "TMP-T-": ("書物",   5),
    "TMP-S-": ("分野",   5),
}


def get_used_numbers(records, prefix):
    """ID-Master から指定プレフィックスの使用済み番号を取得"""
    used = set()
    for r in records:
        id_val = (r.get("ID", "") or "").strip()
        if id_val.startswith(prefix):
            try:
                num = int(id_val[len(prefix):])
                used.add(num)
            except ValueError:
                pass
    return used


def get_id_stats_per_category(records):
    """ID-Master から各 TMP- カテゴリの統計情報を取得
    Returns: {prefix: {label, max, next, gaps, digits}}
    """
    result = {}
    for prefix, (label, digits) in TMP_ID_PREFIXES.items():
        used = get_used_numbers(records, prefix)
        if not used:
            result[prefix] = {"label": label, "max": 0, "next": 1,
                              "gaps": [], "digits": digits}
        else:
            max_num = max(used)
            full_range = set(range(1, max_num + 1))
            gaps = sorted(full_range - used)
            result[prefix] = {
                "label": label,
                "max": max_num,
                "next": max_num + 1,
                "gaps": gaps,
                "digits": digits,
            }
    return result


def get_next_tmp_number(used_numbers, session_used):
    """次の番号を返す(欠番優先 → 最大+1)"""
    all_used = used_numbers | session_used
    if not all_used:
        return 1
    max_used = max(all_used)
    full_range = set(range(1, max_used + 1))
    gaps = full_range - all_used
    if gaps:
        return min(gaps)
    return max_used + 1


_PLACEHOLDER_RE = re.compile(r"^TMP-[A-Z]-0+$")


def is_placeholder_id(id_str):
    """TMP-X-00000 / TMP-X-000000 のようなプレースホルダーか判定。
    空文字も「採番されていない」扱いで True を返す。
    """
    if not id_str:
        return True
    return bool(_PLACEHOLDER_RE.match(str(id_str).strip()))


# 自動採番の対象フィールド: (section, field, prefix)
TMP_FIELDS_BY_PREFIX = [
    ("nisbahs",          "id",              "TMP-L-"),
    ("teachers",         "id",              "TMP-P-"),
    ("teachers",         "text_id",         "TMP-T-"),
    ("teachers",         "learn_place_id",  "TMP-L-"),
    ("students",         "id",              "TMP-P-"),
    ("students",         "text_id",         "TMP-T-"),
    ("students",         "teach_place_id",  "TMP-L-"),
    ("activities",       "id",              "TMP-L-"),
    ("institutions",     "id",              "TMP-I-"),
    ("offices",          "id",              "TMP-O-"),
    ("offices",          "place_id",        "TMP-L-"),
    ("offices",          "inst_id",         "TMP-I-"),
    ("family",           "id",              "TMP-P-"),
    ("bio_events",       "place_id",        "TMP-L-"),
    ("social_relations", "person_id",       "TMP-P-"),
]


def auto_assign_tmp_ids_in_data(d, silent=False):
    """data 内のプレースホルダー TMP-ID(TMP-X-0...0)を空き番号に置換。
    欠番優先 → 最大番号+1 の順で採番する。
    既に確定した ID(TMP-L-00042 や Q12345 など)と空欄は触らない。

    silent=True の場合は st.success/info を出さず、st.rerun も呼ばない
    (Gemini 解析直後など、呼び出し側の処理が続く場合に使用)。
    """
    records = load_id_master()

    session_used = {p: set() for p in TMP_ID_PREFIXES}
    used_per_prefix = {
        p: get_used_numbers(records, p) for p in TMP_ID_PREFIXES
    }

    def assign_id(prefix):
        digits = TMP_ID_PREFIXES[prefix][1]
        next_num = get_next_tmp_number(
            used_per_prefix[prefix], session_used[prefix]
        )
        session_used[prefix].add(next_num)
        return f"{prefix}{next_num:0{digits}d}"

    count = 0
    for section, field, prefix in TMP_FIELDS_BY_PREFIX:
        for item in d.get(section, []):
            current = str(item.get(field, "") or "").strip()
            # プレースホルダー(TMP-X-0...0)で、かつプレフィックスが一致するときだけ採番。
            # 空欄は触らない(ユーザーが意図的に未指定にした場合の誤採番を防ぐ)。
            if current and is_placeholder_id(current) and current.startswith(prefix):
                item[field] = assign_id(prefix)
                count += 1

    if not silent:
        if count > 0:
            st.success(f"{count} 個の ID を採番しました。")
        else:
            st.info("採番すべきプレースホルダーはありません。")
        st.rerun()


# === 翻字一括補完ヘルパー(機能 B 用) ===

LATIN_TRANSLITERATE_PAIRS = [
    ("nisbahs",      ("ar",             "lat")),
    ("laqabs",       ("ar",             "lat")),
    ("teachers",     ("text_ar",        "text_lat")),
    ("teachers",     ("learn_place_ar", "learn_place_lat")),
    ("students",     ("text_ar",        "text_lat")),
    ("students",     ("teach_place_ar", "teach_place_lat")),
    ("activities",   ("place_ar",       "place_lat")),
    ("institutions", ("name_ar",        "name_lat")),
    ("offices",      ("name_ar",        "name_lat")),
    ("offices",      ("place_ar",       "place_lat")),
    ("bio_events",   ("place_ar",       "place_lat")),
]


def collect_empty_latin_fields(d):
    """空のラテン欄に対応するアラビア語を収集
    Returns: [((section, idx, lat_field), ar_value), ...]
    """
    targets = []
    for section, (ar_field, lat_field) in LATIN_TRANSLITERATE_PAIRS:
        for i, item in enumerate(d.get(section, [])):
            ar_val = (item.get(ar_field, "") or "").strip()
            lat_val = (item.get(lat_field, "") or "").strip()
            if ar_val and not lat_val:
                targets.append(((section, i, lat_field), ar_val))
    return targets


def apply_transliterations(d, targets, results):
    """翻字結果を空欄に書き戻す。再確認込みで既存値は絶対に上書きしない。"""
    for (path, _), result in zip(targets, results):
        section, idx, field = path
        if not isinstance(result, str):
            continue
        if not (d[section][idx].get(field, "") or "").strip():
            d[section][idx][field] = result.strip()


def transliterate_empty_latin_fields(d):
    """メイン関数: 空のラテン欄を IJMES 翻字で一括補完。"""
    targets = collect_empty_latin_fields(d)
    if not targets:
        st.info("補完すべき空欄がありません。")
        return

    items = [t[1] for t in targets]

    prompt = f"""
You are an expert Arabic-to-Latin transliterator using IJMES standards.

IJMES rules:
- ع → ʿ (U+02BF)
- ء → ʾ (U+02BE)
- ث = th, ج = j, ذ = dh, ش = sh, غ = gh, خ = kh
- Long vowels with macrons: ā, ī, ū
- Emphatic consonants: ḥ, ṣ, ḍ, ṭ, ẓ
- Definite article always "al-" (do not assimilate to sun letters)
- Alif maqṣūra (ى) is transliterated as ā (same as regular alif)
  Examples: موسى → Mūsā, مصطفى → Muṣṭafā, عيسى → ʿĪsā
- Tā marbūṭa (ة) is dropped at end of word in non-construct state
- Preserve names and titles in their conventional academic forms

Transliterate each item in the input array. Return ONLY a valid JSON array
of strings in the same order as input. No markdown fences, no explanation.

Input items:
{json.dumps(items, ensure_ascii=False)}
"""

    with st.spinner(f"{len(items)} 項目の翻字を生成中..."):
        try:
            model = get_working_model()
            response = model.generate_content(prompt)
            raw = re.sub(r"```json|```", "", response.text).strip()
            results = json.loads(raw)

            if isinstance(results, list) and len(results) == len(items):
                apply_transliterations(d, targets, results)
                st.success(f"{len(items)} 項目を補完しました。")
                st.rerun()
            else:
                actual = len(results) if isinstance(results, list) else "不明"
                st.error(
                    f"翻字結果の数が合いません(期待 {len(items)}、実際 {actual})"
                )
        except Exception as e:
            st.error(f"翻字エラー: {type(e).__name__}: {e}")


def apply_prompt_madhhab(data, madhhab_name):
    """プロンプトの madhhab_name を data.madhhab に展開"""
    name = (madhhab_name or "").strip()
    if not name:
        return

    for key, qid in MADHHAB_DATA.items():
        latin_part = key.split(" ")[0]  # 例: "Hanafi"
        if name.lower() == latin_part.lower():
            data["madhhab"]["lat"] = key
            data["madhhab"]["id"] = qid
            data["madhhab"]["custom_name"] = ""
            data["madhhab"]["custom_id"] = ""
            return

    # 標準4派にマッチしない場合は custom 扱い
    data["madhhab"]["lat"] = "Unknown / Other"
    data["madhhab"]["id"] = ""
    data["madhhab"]["custom_name"] = name
    data["madhhab"]["custom_id"] = ""


def apply_prompt_result(data, prompt_result):
    """Gemini の返り値を data_v19 に最大限自動反映する。"""
    simple_fields = [
        "aind_id", "original_id", "full_name", "name_only", "full_name_lat",
        "translation_jp", "translation_en",
    ]
    for f in simple_fields:
        if f in prompt_result:
            data[f] = prompt_result[f]

    # sex
    sex = prompt_result.get("sex", "U")
    data["sex"] = sex if sex in ("M", "F", "U") else "U"

    # 生没年(年・確実性・注記)
    for prefix in ("birth", "death"):
        for suffix in ("h", "cert", "note"):
            key = f"{prefix}_{suffix}"
            if key in prompt_result:
                data[key] = prompt_result[key]
        # G暦は H から自動計算
        data[f"{prefix}_g"] = convert_h_to_g(data[f"{prefix}_h"])

    # 法学派
    apply_prompt_madhhab(data, prompt_result.get("madhhab_name", ""))

    # 配列フィールド(ui_id 自動付与)
    array_fields = [
        "nisbahs", "laqabs", "activities",
        "teachers", "students",
        "institutions", "offices", "family",
        "bio_events", "social_relations",
    ]
    for f in array_fields:
        if f in prompt_result and isinstance(prompt_result[f], list):
            items = prompt_result[f]
            for item in items:
                if isinstance(item, dict) and "ui_id" not in item:
                    item["ui_id"] = str(uuid.uuid4())
            data[f] = items

    # Gemini が返した TMP-X-00000 プレースホルダーを空き番号で採番
    auto_assign_tmp_ids_in_data(data, silent=True)


# --- セッション状態の初期化 ---
if 'data_v19' not in st.session_state:
    if 'data_v18' in st.session_state:
        st.session_state.data_v19 = migrate_v18_to_v19(
            st.session_state.data_v18
        )
    else:
        st.session_state.data_v19 = json.loads(json.dumps(DEFAULT_DATA_V19))

d = st.session_state.data_v19

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
You are a professional historian of Islamic studies specializing in
the Mamluk period and the works of al-Sakhāwī. Extract structured data
from the source text into JSON.

============================================================
【1. SOURCE TEXT FORMAT】
============================================================
The source text begins with a marker:
  ###$ID_NUMBER$# AIND-D00XXX [biographical text]
- ID_NUMBER (12 digits): the original source ID. → "original_id"
- AIND-D00XXX: the project's AIND ID. → "aind_id" (keep "AIND-D" prefix)

============================================================
【2. ID MASTER — USE THESE IDs FIRST】
============================================================
{id_master_text}

When an entity in the text matches an entry above, use that ID.
If no match exists, follow the ID rules in section 3.

============================================================
【3. ID RULES (when not in ID Master)】
============================================================
- Persons: Wikidata Q-ID if known. Otherwise "TMP-P-000000" (6 digits).
- Places/geography: GeoNames numeric ID (digits only). Otherwise "TMP-L-00000" (5 digits).
- Institutions/concepts/orders: Wikidata Q-ID. Otherwise "TMP-I-00000" (5 digits).
- Texts/books: Wikidata Q-ID if known. Otherwise "TMP-T-00000" (5 digits).
- Subjects/methods/fields: TMP-S-XXXXX from Method/Field lists below.
  If no match, "TMP-S-00000".
- Nisbahs: "TMP-N-00000" (5 digits).
- Offices: "TMP-O-00000" (5 digits).

NOTE: Persons use 6-digit TMP-P-XXXXXX. All other TMP- categories
use 5-digit format. ID-Master entries with legacy 5-digit person IDs
(TMP-P-XXXXX) remain valid — both lengths are accepted.

============================================================
【4. TRANSLATION】
============================================================
- translation_jp: Accurate academic Japanese translation.
- translation_en: Accurate academic English translation.

============================================================
【5. FULL NAME — IMPORTANT POLICY】
============================================================
- "full_name" must include EVERYTHING up to and including madhhab/nisbah.
- When in doubt whether to include a token, INCLUDE it (do not delete).
- Example: محمد بن أحمد الشافعي الدمشقي → keep all tokens.
- "name_only" = Ism + father + grandfather only (e.g. محمد بن أحمد بن علي).

============================================================
【6. MADHHAB — IMPORTANT POLICY】
============================================================
- If the text contains a madhhab indicator (e.g. الشافعي / الحنفي /
  المالكي / الحنبلي), record it ONLY in "madhhab_name".
- DO NOT also record it as a nisbah.
- Use Latin form: "Hanafi" / "Maliki" / "Shafi'i" / "Hanbali".
- If the form is ambiguous or the madhhab is unclear, leave empty.

============================================================
【7. GENDER】
============================================================
- "sex": "M" / "F" / "U" (Male / Female / Unknown).
- Default to "M" only if the source clearly uses masculine forms
  AND no female indicators are present. Otherwise "U".

============================================================
【8. NISBAHS】
============================================================
- Geographical, tribal, or family nisbahs only.
- DO NOT include madhhab-derived nisbahs (الشافعي etc.) here —
  those go in "madhhab_name".
- Place ID (when nisbah refers to a place): GeoNames numeric ID
  if known, otherwise "TMP-L-00000".

============================================================
【9. LAQAB / SHUHRAH / KUNYAH / HONORIFIC】
============================================================
"type" must be one of:
- "laqab"     : honorific epithet (e.g. زين الدين, تقي الدين)
- "shuhrah"   : popular epithet by which the person is known
- "kunyah"    : teknonym (أبو / أم + name)
- "honorific" : pure honorific (الشيخ, الإمام, الحافظ, العلامة)
                — only if used as fixed personal designation,
                NOT as generic respectful mention.

============================================================
【10. DATES (Birth / Death)】
============================================================
- "birth_h" / "death_h": Hijri year string. Examples:
    "850"            (year only)
    "850-09"         (year-month)
    "850-09-15"      (year-month-day)
- Approximate forms ("Ca. 850", "before 850", "after 850") and
  alternative readings should be put in the "_note" field, NOT
  embedded in the year string.
- "birth_cert" / "death_cert": "high" / "medium" / "low" / "" (empty).
- "birth_note" / "death_note": free text for approximations,
  variant readings, or evidential basis.
  Write in ENGLISH for international database compatibility.
  Arabic terms / titles / proper nouns may be quoted directly
  (e.g., "according to تاريخ الإسلام"). Do NOT write in Japanese.

============================================================
【11. TEACHERS / STUDENTS — METHOD × FIELD】
============================================================
Each teacher/student record has TWO axes: method and field.

(A) "method_id" — HOW the learning happened.
    Use one of the following TMP-S- IDs:

    TMP-S-00003  samiʿa       (سمع)         listening
    TMP-S-00004  ajāza/ijāza  (أجاز/إجازة)  granted/received ijaza
                                              (includes general ijaza)
    TMP-S-00005  ṣuḥba w/intibāh (صحبة)     companionship & attention
    TMP-S-00006  ʿaraḍa       (عرض)         presentation
    TMP-S-00008  akhadha      (أخذ)         took / acquired
    TMP-S-00009  darasa       (درس)         studied
    TMP-S-00010  talā         (تلا)         recited (Qurʾān)
    TMP-S-00011  rawā         (روى)         transmitted
    TMP-S-00014  lāzama       (لازم)        sustained discipleship
    TMP-S-00015  al-Istimlāʾ  (الاستملاء)   dictation-taking
    TMP-S-00016  laqiya       (لقي)         met
    TMP-S-00025  qaraʾa       (قرأ)         read aloud
    TMP-S-00026  kataba       (كتب)         wrote / copied
    TMP-S-00027  ḥafiẓa       (حفظ)         memorized
    TMP-S-00028  ḥaḍara       (حضر)         attended
    TMP-S-00029  jamaʿa       (جمع)         compiled
    TMP-S-00030  ḥaddatha     (حدث)         transmitted ḥadīth
    TMP-S-00031  ijtamaʿa     (اجتمع)       met
    TMP-S-00032  tafaqqaha    (تفقه)        studied fiqh
    TMP-S-00033  baraʿa       (برع)         excelled
    TMP-S-00034  ṣaḥiba       (صحب)         accompanied
    TMP-S-00035  takharraja   (تخرج)        graduated
    TMP-S-00036  mahara       (مهر)         mastered
    TMP-S-00037  aftā         (أفتى)        issued fatwa
    TMP-S-00038  amlā         (أملى)        dictated
    TMP-S-00039  talaqqā      (تلقى)        received
    TMP-S-00040  anshada      (أنشد)        recited poetry
    TMP-S-00041  rāfaqa       (رافق)        accompanied
    TMP-S-00042  ʿallaqa      (علق)         annotated
    TMP-S-00043  taʾaddaba    (تأدب)        learned literature

    If no ID matches, put the free-text method description in
    "method_id" itself (it is a single field that accepts either
    an ID or free text).

    Note: "method_id" describes what THE SUBJECT did. The direction
    (received vs. granted) is determined by whether the record
    goes into "teachers" or "students" array.

(B) "field_id" — WHAT was studied.
    Use one of the following IDs:

    TMP-S-00001  al-ʿArabiyya         (العربية)
    TMP-S-00002  al-Ḥadīth            (الحديث)
    TMP-S-00007  al-Ḥisāb             (الحساب)
    Q484181      al-Fiqh              (الفقه)
    TMP-S-00012  al-Qirāʾāt al-ʿAshr  (القراءات العشر)
    TMP-S-00013  al-Qirāʾāt al-Sabʿ   (القراءات السبع)
    Q1817983     al-Qirāʾāt           (القراءات)
    Q1866303     al-Naḥw              (النحو)
    TMP-S-00017  al-Tafsīr            (التفسير)
    TMP-S-00018  al-Aṣlayn            (الأصلين)
    TMP-S-00020  al-Ṣarf              (الصرف)
    TMP-S-00021  Uṣūl al-fiqh         (أصول الفقه)
    TMP-S-00022  ʿIlm al-Waqt         (علم الوقت)
    TMP-S-00023  al-Taṣawwuf          (التصوف)
    TMP-S-00024  al-Farāʾiḍ           (الفرائض)
    TMP-S-00044  Uṣūl al-Dīn          (أصول الدين)
    TMP-S-00045  al-Kalām             (الكلام)
    TMP-S-00046  al-Adab              (الأدب)
    TMP-S-00047  al-Lugha             (اللغة)
    TMP-S-00048  al-Balāgha           (البلاغة)
    TMP-S-00049  al-Maʿānī            (المعاني)
    TMP-S-00050  al-Bayān             (البيان)
    TMP-S-00051  al-Badīʿ             (البديع)
    TMP-S-00052  al-ʿArūḍ             (العروض)
    TMP-S-00053  al-Qāfiya            (القافية)
    TMP-S-00054  al-Manṭiq            (المنطق)
    TMP-S-00055  al-Ṭibb              (الطب)
    TMP-S-00056  al-Falak             (الفلك)
    TMP-S-00057  al-Hayʾa             (الهيئة)
    TMP-S-00058  al-Falsafa           (الفلسفة)
    TMP-S-00059  al-Handasa           (الهندسة)
    TMP-S-00060  al-Jabr              (الجبر)
    TMP-S-00061  al-Muqābala          (المقابلة)
    TMP-S-00062  al-Sīra              (السيرة)
    TMP-S-00063  al-Tārīkh            (التاريخ)
    TMP-S-00064  al-Ansāb             (الأنساب)
    TMP-S-00065  ʿIlm al-Rijāl        (الرجال)
    TMP-S-00066  Muṣṭalaḥ al-Ḥadīth   (مصطلح الحديث)

    If no ID matches, put the free-text field name in
    "field_id" itself (single field accepting ID or free text).

DO NOT record text-coverage info (من أوله إلى آخره / إلى باب كذا /
بعضه). Ignore range qualifiers entirely.

============================================================
【12. ACTIVITIES (geographic life events)】
============================================================
Geographic events: any event whose primary nature is movement to,
or presence in, a specific place.

"type" must be one of:
    born     birth (use with birth date if available)
    died     death
    buried   burial
    reside   long-term residence
    visit    travel / short visit (default for travel events)
    travel   journey (use when emphasis is on the journey itself)
    study    travel for study purposes
    hajj     pilgrimage to Mecca — USE ONLY when text explicitly
             says حج / حجّ / حجة
    umrah    minor pilgrimage — USE ONLY when text explicitly
             says عمرة
    other    none of the above

IMPORTANT — Hajj judgment:
- "ذهب إلى مكة" or similar without حج/حجّ → type = "visit"
- "حج" or "حجّ سنة كذا" → type = "hajj"
- When in doubt between hajj and visit, choose "visit".

DO NOT include named institutions here (those → "institutions").

Each activity has:
    "type"       : one of the above
    "place_ar", "place_lat", "place_id"
    "date_h"     : year (or year-month, year-month-day)
    "date_cert"  : "high" / "medium" / "low" / ""
    "date_note"  : free text in ENGLISH (e.g. "Ca. 850", "before 850").
                   Arabic terms may be quoted. Do NOT write in Japanese.

============================================================
【13. INSTITUTIONS】
============================================================
- Named institutions only (madrasa, mosque, khanqah, etc.).
- "type": study / teach / reside / founded / affiliated /
          graduated / employed / visit / buried / other
- A single trip to a city is NOT an institution.

============================================================
【14. OFFICES】
============================================================
- For positions held in MULTIPLE places (e.g. "served as muezzin
  in both holy cities"), create SEPARATE office entries — one per place.
- DO NOT combine into "Mecca; Medina" in a single field.
- Special case: when the source says "الحرمين" (Haramayn) without
  specifying which two:
    "Haramayn 1" (Mecca + Medina) → ID per ID Master
    "Haramayn 2" (Jerusalem + Hebron) → ID per ID Master
- Fields: name_ar, name_lat, place_ar, place_lat, place_id,
          inst_name, inst_id, appoint_date, retire_date

============================================================
【15. BIOGRAPHICAL EVENTS — NEW (provisional)】
============================================================
Life events that are NOT primarily about geographic movement.

"type" must be one of FOUR broad categories:

    political  political incidents, accusations, exile, factional
               disputes, mamluk politics, encounters with rulers

    cultural   intellectual / literary activity:
               - composing books or poems
               - writing commentaries
               - compiling collections
               - versifying scientific content
               - any authorial achievement

    religious  religious experiences and acts:
               - funerals (their location, time, attendees)
               - conversion
               - religious visions / dreams
               - mystical experiences

    other      events not fitting above categories
               (e.g. plague affliction, natural disasters, illnesses,
                personal life events outside the above)

The "type" is intentionally broad. Specific details go in "description".

Each event:
    "type"       : political / cultural / religious / other
    "date_h", "date_cert", "date_note"
    "place_ar", "place_lat", "place_id"
    "description": free text in ENGLISH — REQUIRED.
                   For international database compatibility, write descriptions
                   in English. Arabic titles and proper nouns may be quoted
                   directly (e.g., 『الشاطبية』, names of people, places).
                   Do NOT write in Japanese.
                   For cultural events, include the title of the work.
                   For political events, include the nature of the incident.
                   For religious events, include the specific practice.
                   For other, describe what happened.
    "date_note"  : free text in ENGLISH. Same policy as description.

Examples:
    "خرج للجهاد سنة 875" →
        type=political, date_h="875", description="went out to military campaign (jihād)"
    "ألف الحلاوة السكرية" →
        type=cultural, description='composed 『الحلاوة السكرية』'
    "شرح المنهاج" →
        type=cultural, description='wrote a commentary on 『المنهاج』'
    "نظم الفرائض" →
        type=cultural, description="versified inheritance law"
    "صلي عليه بالجامع الأزهر" →
        type=religious, place_ar="الأزهر",
        description="funeral prayer held at al-Azhar Mosque"
    "أصابه الطاعون" →
        type=other, description="afflicted by the plague"

============================================================
【16. SOCIAL RELATIONS — NEW (provisional)】
============================================================
Non-family, non-teacher/student social ties.

    "type"        : patron / client / colleague / rival / friend /
                    correspondent / successor / predecessor / other
    "type_other"  : if type = "other"
    "person_name" : name in Arabic
    "person_id"   : Wikidata Q-ID or TMP-P-000000
    "description" : free text in ENGLISH. Arabic names / terms may be quoted.
                    Do NOT write in Japanese.

============================================================
【17. FAMILY — EXPLICIT MENTIONS ONLY】
============================================================
EXTRACT ONLY family relations that are EXPLICITLY stated in the text.

EXTRACT (explicit relational vocabulary present):
    - "والده فلان" / "أبوه فلان"               → father
    - "والدته فلانة" / "أمه فلانة"             → mother
    - "ابنه فلان" / "ولده فلان"                → son
    - "ابنته فلانة" / "بنته فلانة"             → daughter
    - "أخوه فلان"                              → brother
    - "أخته فلانة"                             → sister
    - "زوجته فلانة" / "زوجها فلان"             → spouse
    - "جده فلان" / "جدته فلانة"                → grandfather / grandmother
    - "عمه فلان" / "خاله فلان"                 → uncle
    - "عمته فلانة" / "خالته فلانة"             → aunt
    - "ابن عمه" / "ابن خاله" / "ابنة عمه" etc → cousin
    - "ابن أخيه" / "ابنة أخته" etc             → siblings_child
    - "صهره" (son-in-law) / "ختنه" etc         → other

DO NOT EXTRACT:
    - Ancestors implied by the nasab chain (محمد بن أحمد بن علي).
      Do NOT decompose ابن chains into family entries.
      The full_name and name_only fields already preserve nasab info.
    - Sons implied by kunyah (أبو بكر does NOT imply son بكر in family).
      The kunyah is recorded in laqabs only.
    - Vague relational terms without named individual
      (e.g. "أهله", "أقاربه", "ذريته" without specific names).

== relation KEYS (use these exact 14 values) ==
    father, mother, son, daughter, brother, sister, spouse,
    grandfather, grandmother,
    uncle      (paternal/maternal NOT distinguished)
    aunt       (paternal/maternal NOT distinguished)
    cousin     (no distinction by line or gender)
    siblings_child  (nephew/niece, no distinction by line or gender)
    other      (in-laws, distant relatives, unclear relations)

== EXAMPLES ==

    "والده الشيخ أحمد" →
        family += [{{"relation":"father", "name":"الشيخ أحمد"}}]

    "أخوه محمد، الفقيه" →
        family += [{{"relation":"brother", "name":"محمد"}}]

    "ابن عمه علي" →
        family += [{{"relation":"cousin", "name":"علي"}}]

    "تزوج بفاطمة بنت فلان" →
        family += [{{"relation":"spouse", "name":"فاطمة بنت فلان"}}]

    "محمد بن أحمد بن علي بن حسن" (NO explicit relational vocabulary) →
        family += []  ← do NOT extract father/grandfather/etc from nasab.
                       The names are preserved in full_name/name_only.

== CRITICAL ==
- Extract ONLY when the text uses an explicit relational word
  (والد, أم, ابن, ابنة, أخ, أخت, زوج, جد, عم, خال, etc.).
- If only the nasab chain is given (with بن), extract NOTHING for family.
- If only a kunyah is given (أبو فلان), extract NOTHING for family.
- Use empty "name" only when the relation is mentioned but the
  individual is not named (e.g. "أمه" alone with no name).

============================================================
【18. NEGATIVE INSTRUCTIONS — DO NOT INCLUDE】
============================================================
- Collective nouns: وغيره / جماعة / آخرون / غير واحد / etc.
  These are vague and should be SKIPPED entirely.
- Text coverage qualifiers: من أوله إلى آخره / إلى باب كذا /
  بعضه / etc. Ignore these.
- Generic honorifics in passing mentions (الشيخ, الإمام) when not
  used as a fixed personal designation.
- Madhhab as nisbah (الشافعي as nisbah). Always route to madhhab_name.
- Family relations implied by nasab chain or kunyah (see section 17).

============================================================
【19. OUTPUT FORMAT】
============================================================
Return ONLY valid JSON. No markdown fences. No commentary.

{{
  "aind_id": "",
  "original_id": "",
  "full_name": "",
  "name_only": "",
  "sex": "U",
  "birth_h": "", "birth_cert": "", "birth_note": "",
  "death_h": "", "death_cert": "", "death_note": "",
  "madhhab_name": "",
  "nisbahs": [
    {{"ar": "", "lat": "", "id": "TMP-L-00000"}}
  ],
  "laqabs": [
    {{"type": "laqab", "ar": "", "lat": ""}}
  ],
  "activities": [
    {{
      "seq": 1, "type": "reside",
      "place_ar": "", "place_lat": "", "id": "",
      "date_h": "", "date_cert": "", "date_note": ""
    }}
  ],
  "teachers": [
    {{
      "seq": 1,
      "name": "", "id": "TMP-P-000000",
      "method_id": "",
      "field_id": "",
      "text_ar": "", "text_lat": "", "text_id": "TMP-T-00000",
      "learn_date": "",
      "learn_place_ar": "", "learn_place_lat": "", "learn_place_id": ""
    }}
  ],
  "students": [
    {{
      "seq": 1,
      "name": "", "id": "TMP-P-000000",
      "method_id": "",
      "field_id": "",
      "text_ar": "", "text_lat": "", "text_id": "TMP-T-00000",
      "teach_date": "",
      "teach_place_ar": "", "teach_place_lat": "", "teach_place_id": ""
    }}
  ],
  "institutions": [
    {{"seq": 1, "name_ar": "", "name_lat": "", "type": "study",
      "id": "TMP-I-00000"}}
  ],
  "offices": [
    {{
      "seq": 1, "name_ar": "", "name_lat": "", "id": "TMP-O-00000",
      "place_ar": "", "place_lat": "", "place_id": "",
      "inst_name": "", "inst_id": "",
      "appoint_date": "", "retire_date": ""
    }}
  ],
  "bio_events": [
    {{
      "seq": 1,
      "type": "",
      "date_h": "", "date_cert": "", "date_note": "",
      "place_ar": "", "place_lat": "", "place_id": "",
      "description": ""
    }}
  ],
  "social_relations": [
    {{
      "seq": 1,
      "type": "", "type_other": "",
      "person_name": "", "person_id": "",
      "description": ""
    }}
  ],
  "family": [
    {{
      "relation": "father",
      "name": "", "id": "TMP-P-000000"
    }}
  ],
  "translation_jp": "",
  "translation_en": ""
}}

Text: {source_input}
"""
                    response = model.generate_content(prompt)
                    raw = re.sub(r"```json|```", "", response.text).strip()
                    m = re.search(r"\{.*\}", raw, re.DOTALL)
                    if m:
                        json_str = m.group()
                        try:
                            res = json.loads(json_str)
                        except json.JSONDecodeError:
                            json_str = re.sub(r'(?<!\\)\n', '\\n', json_str)
                            json_str = re.sub(r'(?<!\\)\r', '\\r', json_str)
                            res = json.loads(json_str)

                        apply_prompt_result(d, res)

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

            # カテゴリ別の最新ID/次ID/欠番
            st.markdown("**📊 カテゴリ別の最新ID(次に使うべき番号の参考)**")
            stats = get_id_stats_per_category(records)
            for prefix, info in stats.items():
                digits = info["digits"]
                if info["max"] > 0:
                    current = f"{prefix}{info['max']:0{digits}d}"
                else:
                    current = "(なし)"
                next_id = f"{prefix}{info['next']:0{digits}d}"
                st.caption(
                    f"  {prefix}({info['label']}): 最新 `{current}` → 次は `{next_id}`"
                )
                if info["gaps"]:
                    gaps_display = info["gaps"][:5]
                    gaps_str = ", ".join(f"{g:0{digits}d}" for g in gaps_display)
                    if len(info["gaps"]) > 5:
                        gaps_str += f" 他{len(info['gaps']) - 5}件"
                    st.caption(f"     欠番(優先): {gaps_str}")

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

# === ツールバー(翻字補完 / 採番更新 / クリア) ===
clr_c1, clr_c2, clr_c3, clr_c4 = st.columns([0.55, 0.15, 0.15, 0.15])
with clr_c2:
    if st.button("↗ 翻字を一括補完", use_container_width=True,
                 help="空のラテン欄を IJMES 翻字で一括補完(既存の入力は保持)"):
        transliterate_empty_latin_fields(d)
with clr_c3:
    if st.button("🔢 採番を更新", use_container_width=True,
                 help="プレースホルダー(TMP-X-00000)を空き番号で採番"):
        auto_assign_tmp_ids_in_data(d)
with clr_c4:
    if st.button("🗑️ 入力をクリア", use_container_width=True,
                 help="入力した全データをクリアします(担当者名は保持)"):
        st.session_state["_show_clear_confirm"] = True

if st.session_state.get("_show_clear_confirm"):
    st.warning("⚠️ 全ての入力データがクリアされます(担当者名は保持されます)。本当によろしいですか?")
    cc1, cc2, cc3 = st.columns([1, 1, 4])
    if cc1.button("✅ クリアする", type="primary"):
        saved_assignee = st.session_state.get("assignee", "")
        st.session_state.data_v19 = json.loads(json.dumps(DEFAULT_DATA_V19))
        if saved_assignee:
            st.session_state["assignee"] = saved_assignee
        st.session_state["_show_clear_confirm"] = False
        st.rerun()
    if cc2.button("キャンセル"):
        st.session_state["_show_clear_confirm"] = False
        st.rerun()

st.header("2. Metadata Editor")

# --- 基本情報 ---
c1, c2 = st.columns(2)
d["aind_id"]     = c1.text_input("@xml:id", d["aind_id"])
d["original_id"] = c2.text_input("@source", d["original_id"])
d["full_name"]   = st.text_input("persName (Full Arabic)", d["full_name"])
d["name_only"]   = st.text_input("persName (Ism/Father/GF)", d["name_only"])

# === Sex(M/F/U) ===
sex_col1, _ = st.columns([1, 3])
sex_keys   = [s[0] for s in SEX_OPTIONS]
sex_labels = {s[0]: s[1] for s in SEX_OPTIONS}
cur_sex = d.get("sex", "U")
if cur_sex not in sex_keys:
    cur_sex = "U"
d["sex"] = sex_col1.selectbox(
    "Sex",
    sex_keys,
    format_func=lambda x: sex_labels[x],
    index=sex_keys.index(cur_sex),
    key="sex_select",
)

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

# --- 生没年(cert / note 付き) ---
st.divider()
st.markdown("**📅 Birth / Death**")

cert_keys   = [c[0] for c in DATE_CERT_OPTIONS]
cert_labels = {c[0]: c[1] for c in DATE_CERT_OPTIONS}

# Birth
with st.container():
    bc1, bc2, bc3, bc4 = st.columns([1, 1, 1, 2])
    d["birth_h"] = bc1.text_input(
        "Birth (H)", d.get("birth_h", ""),
        placeholder="例: 850 / 850-09 / 850-09-15",
        help="ヒジュラ暦。年月日まで指定可",
    )
    bc2.text_input(
        "Birth (G)",
        value=convert_h_to_g(d.get("birth_h", "")),
        disabled=True,
    )
    cur_bcert = d.get("birth_cert", "")
    d["birth_cert"] = bc3.selectbox(
        "Birth Cert",
        cert_keys,
        format_func=lambda x: cert_labels[x],
        index=cert_keys.index(cur_bcert) if cur_bcert in cert_keys else 0,
        key="birth_cert_sel",
    )
    d["birth_note"] = bc4.text_input(
        "Birth Note",
        d.get("birth_note", ""),
        placeholder="例: Ca. 850 / before 850 / 異説あり",
    )

# Death
with st.container():
    xdc1, xdc2, xdc3, xdc4 = st.columns([1, 1, 1, 2])
    d["death_h"] = xdc1.text_input(
        "Death (H)", d.get("death_h", ""),
        placeholder="例: 902 / 902-04 / 902-04-15",
    )
    xdc2.text_input(
        "Death (G)",
        value=convert_h_to_g(d.get("death_h", "")),
        disabled=True,
    )
    cur_dcert = d.get("death_cert", "")
    d["death_cert"] = xdc3.selectbox(
        "Death Cert",
        cert_keys,
        format_func=lambda x: cert_labels[x],
        index=cert_keys.index(cur_dcert) if cur_dcert in cert_keys else 0,
        key="death_cert_sel",
    )
    d["death_note"] = xdc4.text_input(
        "Death Note",
        d.get("death_note", ""),
        placeholder="例: Ca. 902 / 異説あり(901)",
    )

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
st.caption(
    "学習関係を時系列順に記録。▲▼ で並び替え可。"
    "Method = どう学んだか、Field = 何を学んだか。"
)
method_dict, field_dict = build_method_field_dicts()

teachers = d.get("teachers", [])
for i, item in enumerate(teachers):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1

    with st.container():
        # ヘッダー: 番号 + ▲▼
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"t_up_{uid}", disabled=(i == 0)):
                move_item(d["teachers"], i, -1); st.rerun()
            if st.button("▼", key=f"t_dn_{uid}", disabled=(i == len(teachers)-1)):
                move_item(d["teachers"], i, +1); st.rerun()

        # 1行目: Name / Person ID / ❌
        r1 = st.columns([1.5, 1.2, 0.3])
        r1[0].caption("Name")
        r1[1].caption("Person ID (Q / TMP-P-)")
        item["name"] = r1[0].text_input(
            "Name", item.get("name", ""),
            key=f"t_n_{uid}", label_visibility="collapsed",
        )
        item["id"] = r1[1].text_input(
            "PID", item.get("id", ""),
            key=f"t_i_{uid}", label_visibility="collapsed",
            placeholder="例: Q12345 / TMP-P-000001",
        )
        if r1[2].button("❌", key=f"t_del_{uid}"):
            d["teachers"].pop(i); st.rerun()

        # 2行目: Method / Field
        r2 = st.columns([1.5, 1.5])
        r2[0].caption("📚 Method (学習方法)")
        r2[1].caption("📖 Field (学習分野)")
        item["method_id"] = render_method_field_input(
            r2[0],
            value=item.get("method_id", ""),
            options_dict=method_dict,
            key=f"t_m_{uid}",
            placeholder="プルダウン or ID/自由記述",
        )
        item["field_id"] = render_method_field_input(
            r2[1],
            value=item.get("field_id", ""),
            options_dict=field_dict,
            key=f"t_f_{uid}",
            placeholder="プルダウン or ID/自由記述",
        )

        # 3行目: Text Arabic / Text Latin / Text ID
        r3 = st.columns([1, 1, 1])
        r3[0].caption("📖 Text (Arabic)")
        r3[1].caption("📖 Text (Latinized)")
        r3[2].caption("📖 Text ID (Q / TMP-T-)")
        item["text_ar"]  = r3[0].text_input("tar",  item.get("text_ar",""),  key=f"t_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r3[1].text_input("tlat", item.get("text_lat",""), key=f"t_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        item["text_id"]  = r3[2].text_input("tid",  item.get("text_id",""),  key=f"t_ti_{uid}", label_visibility="collapsed", placeholder="例: Q208507 / TMP-T-00001")

        # 4行目: Date / Place
        r4 = st.columns([1, 1, 1, 1])
        r4[0].caption("📅 Learning Date")
        r4[1].caption("📍 Place (Arabic)")
        r4[2].caption("📍 Place (Latin)")
        r4[3].caption("Place ID (GeoNames)")
        item["learn_date"]      = r4[0].text_input("ldate", item.get("learn_date",""),      key=f"t_ld_{uid}",  label_visibility="collapsed", placeholder="例: 880H")
        item["learn_place_ar"]  = r4[1].text_input("lpar",  item.get("learn_place_ar",""),  key=f"t_lpa_{uid}", label_visibility="collapsed")
        item["learn_place_lat"] = r4[2].text_input("lplat", item.get("learn_place_lat",""), key=f"t_lpl_{uid}", label_visibility="collapsed")
        item["learn_place_id"]  = r4[3].text_input("lpid",  item.get("learn_place_id",""),  key=f"t_lpi_{uid}", label_visibility="collapsed", placeholder="GeoNames数字 / TMP-L-")
    st.markdown("---")

if st.button("＋ add teacher"):
    d["teachers"].append({
        "ui_id":          str(uuid.uuid4()),
        "seq":            len(d["teachers"]) + 1,
        "name":           "",
        "id":             "TMP-P-000000",
        "method_id":      "",
        "field_id":       "",
        "text_ar":        "", "text_lat": "", "text_id": "TMP-T-00000",
        "learn_date":     "",
        "learn_place_ar": "", "learn_place_lat": "", "learn_place_id": "",
    })
    st.rerun()

# ===================================================
# --- Students ---
# ===================================================
st.divider()
st.subheader("🧑‍🎓 Students & Subjects")
st.caption(
    "学生関係を時系列順に記録。▲▼ で並び替え可。"
    "Method = どう教えたか、Field = 何を教えたか。"
)

students = d.get("students", [])
for i, item in enumerate(students):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1

    with st.container():
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"s_up_{uid}", disabled=(i == 0)):
                move_item(d["students"], i, -1); st.rerun()
            if st.button("▼", key=f"s_dn_{uid}", disabled=(i == len(students)-1)):
                move_item(d["students"], i, +1); st.rerun()

        r1 = st.columns([1.5, 1.2, 0.3])
        r1[0].caption("Name")
        r1[1].caption("Person ID (Q / TMP-P-)")
        item["name"] = r1[0].text_input("Name", item.get("name",""), key=f"s_n_{uid}", label_visibility="collapsed")
        item["id"]   = r1[1].text_input("PID",  item.get("id",""),   key=f"s_i_{uid}", label_visibility="collapsed", placeholder="例: Q12345 / TMP-P-000001")
        if r1[2].button("❌", key=f"s_del_{uid}"):
            d["students"].pop(i); st.rerun()

        r2 = st.columns([1.5, 1.5])
        r2[0].caption("📚 Method (学習方法)")
        r2[1].caption("📖 Field (学習分野)")
        item["method_id"] = render_method_field_input(
            r2[0],
            value=item.get("method_id", ""),
            options_dict=method_dict,
            key=f"s_m_{uid}",
            placeholder="プルダウン or ID/自由記述",
        )
        item["field_id"] = render_method_field_input(
            r2[1],
            value=item.get("field_id", ""),
            options_dict=field_dict,
            key=f"s_f_{uid}",
            placeholder="プルダウン or ID/自由記述",
        )

        r3 = st.columns([1, 1, 1])
        r3[0].caption("📖 Text (Arabic)")
        r3[1].caption("📖 Text (Latinized)")
        r3[2].caption("📖 Text ID (Q / TMP-T-)")
        item["text_ar"]  = r3[0].text_input("tar",  item.get("text_ar",""),  key=f"s_ta_{uid}", label_visibility="collapsed", placeholder="例: الصحيح")
        item["text_lat"] = r3[1].text_input("tlat", item.get("text_lat",""), key=f"s_tl_{uid}", label_visibility="collapsed", placeholder="例: al-Sahih")
        item["text_id"]  = r3[2].text_input("tid",  item.get("text_id",""),  key=f"s_ti_{uid}", label_visibility="collapsed", placeholder="例: Q208507 / TMP-T-00001")

        r4 = st.columns([1, 1, 1, 1])
        r4[0].caption("📅 Teaching Date")
        r4[1].caption("📍 Place (Arabic)")
        r4[2].caption("📍 Place (Latin)")
        r4[3].caption("Place ID (GeoNames)")
        item["teach_date"]      = r4[0].text_input("tdate", item.get("teach_date",""),      key=f"s_td_{uid}",  label_visibility="collapsed", placeholder="例: 880H")
        item["teach_place_ar"]  = r4[1].text_input("tpar",  item.get("teach_place_ar",""),  key=f"s_tpa_{uid}", label_visibility="collapsed")
        item["teach_place_lat"] = r4[2].text_input("tplat", item.get("teach_place_lat",""), key=f"s_tpl_{uid}", label_visibility="collapsed")
        item["teach_place_id"]  = r4[3].text_input("tpid",  item.get("teach_place_id",""),  key=f"s_tpi_{uid}", label_visibility="collapsed", placeholder="GeoNames数字 / TMP-L-")
    st.markdown("---")

if st.button("＋ add student"):
    d["students"].append({
        "ui_id":          str(uuid.uuid4()),
        "seq":            len(d["students"]) + 1,
        "name":           "",
        "id":             "TMP-P-000000",
        "method_id":      "",
        "field_id":       "",
        "text_ar":        "", "text_lat": "", "text_id": "TMP-T-00000",
        "teach_date":     "",
        "teach_place_ar": "", "teach_place_lat": "", "teach_place_id": "",
    })
    st.rerun()

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

        # 日付行(date_h / date_cert / date_note)
        r2 = st.columns([1, 1, 2])
        r2[0].caption("📅 Date (H)"); r2[1].caption("Cert"); r2[2].caption("Date Note")
        item["date_h"] = r2[0].text_input(
            "dh", item.get("date_h", ""),
            key=f"a_dh_{uid}", label_visibility="collapsed",
            placeholder="例: 850 / 850-09",
        )
        cur_dcert = item.get("date_cert", "")
        a_cert_keys = [c[0] for c in DATE_CERT_OPTIONS]
        a_cert_labels = {c[0]: c[1] for c in DATE_CERT_OPTIONS}
        item["date_cert"] = r2[1].selectbox(
            "dc", a_cert_keys,
            format_func=lambda x: a_cert_labels[x],
            index=a_cert_keys.index(cur_dcert) if cur_dcert in a_cert_keys else 0,
            key=f"a_dc_{uid}", label_visibility="collapsed",
        )
        item["date_note"] = r2[2].text_input(
            "dn", item.get("date_note", ""),
            key=f"a_dn_{uid}", label_visibility="collapsed",
            placeholder="例: Ca. 850 / 異説あり",
        )
    st.markdown("---")
if st.button("＋ add activity"):
    d["activities"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["activities"])+1,
        "place_ar":"","place_lat":"","type":"reside","id":"",
        "date_h":"","date_cert":"","date_note":""}); st.rerun()

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
# --- Biographical Events ---
# ===================================================
st.divider()
st.subheader("📅 Biographical Events")
st.caption(
    "地理移動を伴わない人生のイベント(著作・政治事件・宗教的事件など)。"
    "ハッジは Activities へ。▲▼ で並び替え可。"
)

bio_events = d.get("bio_events", [])
be_type_keys   = [t[0] for t in BIO_EVENT_TYPES]
be_type_labels = {t[0]: t[1] for t in BIO_EVENT_TYPES}
be_cert_keys   = [c[0] for c in DATE_CERT_OPTIONS]
be_cert_labels = {c[0]: c[1] for c in DATE_CERT_OPTIONS}

for i, item in enumerate(bio_events):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1

    with st.container():
        # ヘッダー: 番号 + ▲▼
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"be_mvup_{uid}", disabled=(i == 0)):
                move_item(d["bio_events"], i, -1); st.rerun()
            if st.button("▼", key=f"be_mvdn_{uid}", disabled=(i == len(bio_events)-1)):
                move_item(d["bio_events"], i, +1); st.rerun()

        # 1行目: Type / Date / Cert / Date Note / ❌
        r1 = st.columns([1, 1, 0.7, 1.3, 0.3])
        r1[0].caption("Type")
        r1[1].caption("📅 Date (H)")
        r1[2].caption("Cert")
        r1[3].caption("Date Note")

        cur_type = item.get("type", "")
        type_options = [""] + be_type_keys
        type_labels_with_empty = {"": "— 未選択 —", **be_type_labels}
        item["type"] = r1[0].selectbox(
            "type",
            type_options,
            format_func=lambda x: type_labels_with_empty[x],
            index=type_options.index(cur_type) if cur_type in type_options else 0,
            key=f"be_t_{uid}", label_visibility="collapsed",
        )
        item["date_h"] = r1[1].text_input(
            "bdh", item.get("date_h", ""),
            key=f"be_dh_{uid}", label_visibility="collapsed",
            placeholder="例: 880",
        )
        cur_dcert = item.get("date_cert", "")
        item["date_cert"] = r1[2].selectbox(
            "bdc", be_cert_keys,
            format_func=lambda x: be_cert_labels[x],
            index=be_cert_keys.index(cur_dcert) if cur_dcert in be_cert_keys else 0,
            key=f"be_dc_{uid}", label_visibility="collapsed",
        )
        item["date_note"] = r1[3].text_input(
            "bdn", item.get("date_note", ""),
            key=f"be_dn_{uid}", label_visibility="collapsed",
            placeholder="例: Ca. 880",
        )
        if r1[4].button("❌", key=f"be_del_{uid}"):
            d["bio_events"].pop(i); st.rerun()

        # 2行目: Place
        r2 = st.columns([1, 1, 1])
        r2[0].caption("📍 Place (Arabic)")
        r2[1].caption("📍 Place (Latin)")
        r2[2].caption("Place ID")
        item["place_ar"]  = r2[0].text_input("bpa", item.get("place_ar",""),
            key=f"be_pa_{uid}", label_visibility="collapsed")
        item["place_lat"] = r2[1].text_input("bpl", item.get("place_lat",""),
            key=f"be_pl_{uid}", label_visibility="collapsed")
        item["place_id"]  = r2[2].text_input("bpi", item.get("place_id",""),
            key=f"be_pi_{uid}", label_visibility="collapsed",
            placeholder="GeoNames数字 / Q-ID")

        # 3行目: Description (REQUIRED)
        item["description"] = st.text_area(
            "Description (詳細・著作タイトルなど)",
            value=item.get("description", ""),
            height=60,
            key=f"be_desc_{uid}",
            placeholder="例: 『الحلاوة السكرية』(千句詩・相続法)を著した",
        )

    st.markdown("---")

if st.button("＋ add biographical event"):
    d["bio_events"].append({
        "ui_id":       str(uuid.uuid4()),
        "seq":         len(d["bio_events"]) + 1,
        "type":        "",
        "date_h":      "",
        "date_cert":   "",
        "date_note":   "",
        "place_ar":    "",
        "place_lat":   "",
        "place_id":    "",
        "description": "",
    })
    st.rerun()

# ===================================================
# --- Social Relations ---
# ===================================================
st.divider()
st.subheader("🤝 Social Relations")
st.caption(
    "家族でも師弟でもない社会的関係(庇護者・同僚・論敵など)。"
    "▲▼ で並び替え可。"
)

social_rels    = d.get("social_relations", [])
sr_type_keys   = [t[0] for t in SOCIAL_RELATION_TYPES]
sr_type_labels = {t[0]: t[1] for t in SOCIAL_RELATION_TYPES}

for i, item in enumerate(social_rels):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    item["seq"] = i + 1

    with st.container():
        # ヘッダー: 番号 + ▲▼
        hc = st.columns([0.15, 0.25, 3])
        hc[0].markdown(f"**#{i+1}**")
        with hc[1]:
            if st.button("▲", key=f"sr_mvup_{uid}", disabled=(i == 0)):
                move_item(d["social_relations"], i, -1); st.rerun()
            if st.button("▼", key=f"sr_mvdn_{uid}", disabled=(i == len(social_rels)-1)):
                move_item(d["social_relations"], i, +1); st.rerun()

        # 1行目: Type / Person Name / Person ID / ❌
        r1 = st.columns([1, 1.5, 1, 0.3])
        r1[0].caption("Type")
        r1[1].caption("Person Name")
        r1[2].caption("Person ID")

        cur_srtype = item.get("type", "")
        sr_type_options = [""] + sr_type_keys
        sr_type_labels_with_empty = {"": "— 未選択 —", **sr_type_labels}
        item["type"] = r1[0].selectbox(
            "srtype",
            sr_type_options,
            format_func=lambda x: sr_type_labels_with_empty[x],
            index=sr_type_options.index(cur_srtype) if cur_srtype in sr_type_options else 0,
            key=f"sr_t_{uid}", label_visibility="collapsed",
        )
        item["person_name"] = r1[1].text_input(
            "srpn", item.get("person_name", ""),
            key=f"sr_pn_{uid}", label_visibility="collapsed",
        )
        item["person_id"] = r1[2].text_input(
            "srpi", item.get("person_id", ""),
            key=f"sr_pi_{uid}", label_visibility="collapsed",
            placeholder="Q12345 / TMP-P-000001",
        )
        if r1[3].button("❌", key=f"sr_del_{uid}"):
            d["social_relations"].pop(i); st.rerun()

        # Other 選択時のみ自由記述欄
        if item["type"] == "other":
            item["type_other"] = st.text_input(
                "Type (free text)",
                value=item.get("type_other", ""),
                key=f"sr_to_{uid}",
                placeholder="例: 親戚の知人など",
            )

        # 2行目: Description
        item["description"] = st.text_area(
            "Description (関係の詳細)",
            value=item.get("description", ""),
            height=60,
            key=f"sr_desc_{uid}",
            placeholder="関係性の詳細・出会いの経緯など",
        )

    st.markdown("---")

if st.button("＋ add social relation"):
    d["social_relations"].append({
        "ui_id":       str(uuid.uuid4()),
        "seq":         len(d["social_relations"]) + 1,
        "type":        "",
        "type_other":  "",
        "person_name": "",
        "person_id":   "",
        "description": "",
    })
    st.rerun()

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

def build_persnames(x, d):
    if d.get("full_name"):
        x.append(f'    <persName type="full" xml:lang="ar">{escape_xml(d["full_name"])}</persName>')
    if d.get("name_only"):
        x.append(f'    <persName type="name_only" xml:lang="ar">{escape_xml(d["name_only"])}</persName>')

    for n in d.get("nisbahs", []):
        if n.get("ar"):
            ref_attr = f' ref="{fr(n.get("id",""))}"' if n.get("id") else ""
            x.append(
                f'    <persName type="nisbah" xml:lang="ar"{ref_attr}>'
                f'{escape_xml(n["ar"])}</persName>'
            )

    for lq in d.get("laqabs", []):
        if lq.get("ar"):
            t = lq.get("type", "laqab")
            x.append(
                f'    <persName type="{t}" xml:lang="ar">'
                f'{escape_xml(lq["ar"])}</persName>'
            )


def build_sex(x, d):
    sex = d.get("sex", "")
    if sex in ("M", "F", "U"):
        x.append(f'    <sex value="{sex}"/>')


def build_madhhab_and_sufi(x, d):
    m = d.get("madhhab", {})
    if m.get("lat") == "Unknown / Other":
        cn = m.get("custom_name", "")
        ci = m.get("custom_id", "")
        if cn or ci:
            ref_attr = f' ref="{fr(ci)}"' if ci else ""
            x.append(
                f'    <affiliation type="madhhab"{ref_attr}>'
                f'{escape_xml(cn)}</affiliation>'
            )
    elif m.get("id"):
        # "Shafi'i (シャーフィイー派)" → "Shafi'i"(日本語注釈は除去)
        madhhab_label = m.get("lat", "").split(" (")[0]
        x.append(
            f'    <affiliation type="madhhab" ref="wd:{m["id"]}">'
            f'{escape_xml(madhhab_label)}</affiliation>'
        )

    sufi = d.get("sufi_order", {})
    if sufi.get("name"):
        ref_attr = f' ref="{fr(sufi.get("id",""))}"' if sufi.get("id") else ""
        x.append(
            f'    <affiliation type="sufiOrder"{ref_attr}>'
            f'{escape_xml(sufi["name"])}</affiliation>'
        )


def _build_date_event(elem_name, year_h, cert, note):
    if not year_h:
        return None
    year_g = convert_h_to_g(year_h)
    cert_attr = f' cert="{cert}"' if cert else ""
    when_g_attr = f' when="{year_g}"' if year_g else ""
    if note:
        lang = detect_lang(note)
        return (
            f'    <{elem_name} when-custom="{escape_xml_attr(year_h)}"{when_g_attr}{cert_attr}>\n'
            f'        <note xml:lang="{lang}">{escape_xml(note)}</note>\n'
            f'    </{elem_name}>'
        )
    return f'    <{elem_name} when-custom="{escape_xml_attr(year_h)}"{when_g_attr}{cert_attr}/>'


def build_birth_death(x, d):
    b = _build_date_event("birth", d.get("birth_h",""), d.get("birth_cert",""), d.get("birth_note",""))
    if b: x.append(b)
    de = _build_date_event("death", d.get("death_h",""), d.get("death_cert",""), d.get("death_note",""))
    if de: x.append(de)


def _build_method_field_desc(method_id, field_id, method_dict, field_dict):
    lines = []
    # Method
    if method_id:
        if method_id in method_dict:
            entry = method_dict[method_id]
            label = entry.get("ar") or entry.get("lat") or method_id
            lines.append(
                f'            <desc type="method" ref="{fr(method_id)}">'
                f'{escape_xml(label)}</desc>'
            )
        elif is_id_format(method_id):
            lines.append(
                f'            <desc type="method" ref="{fr(method_id)}"/>'
            )
        else:
            lines.append(
                f'            <desc type="method">{escape_xml(method_id)}</desc>'
            )
    # Field
    if field_id:
        if field_id in field_dict:
            entry = field_dict[field_id]
            label = entry.get("ar") or entry.get("lat") or field_id
            lines.append(
                f'            <desc type="field" ref="{fr(field_id)}">'
                f'{escape_xml(label)}</desc>'
            )
        elif is_id_format(field_id):
            lines.append(
                f'            <desc type="field" ref="{fr(field_id)}"/>'
            )
        else:
            lines.append(
                f'            <desc type="field">{escape_xml(field_id)}</desc>'
            )
    return lines


def _build_teacher_relation(t, aind_id, method_dict, field_dict):
    seq = t.get("seq", "")
    n_attr = f' n="{seq}"' if seq else ""
    lines = [
        f'        <relation type="personal" name="teacher"{n_attr} '
        f'active="{fr(t.get("id",""))}" passive="#{aind_id}">'
    ]
    lines.extend(_build_method_field_desc(
        t.get("method_id", ""), t.get("field_id", ""),
        method_dict, field_dict,
    ))
    if t.get("text_ar") or t.get("text_lat"):
        tid = fr(t.get("text_id", ""))
        ref_attr = f' ref="{tid}"' if tid else ""
        if t.get("text_ar"):
            lines.append(f'            <bibl xml:lang="ar"{ref_attr}>{escape_xml(t["text_ar"])}</bibl>')
        if t.get("text_lat"):
            lines.append(f'            <bibl xml:lang="lat"{ref_attr}>{escape_xml(t["text_lat"])}</bibl>')
    if t.get("learn_date") or t.get("learn_place_ar"):
        da = f' when="{escape_xml_attr(t["learn_date"])}"' if t.get("learn_date") else ""
        pr = f' where="{fr(t.get("learn_place_id",""))}"' if t.get("learn_place_id") else ""
        if t.get("learn_place_ar"):
            lines.append(
                f'            <event type="learning"{da}{pr}>'
                f'<placeName>{escape_xml(t["learn_place_ar"])}</placeName>'
                f'</event>'
            )
        else:
            lines.append(f'            <event type="learning"{da}{pr}/>')
    lines.append('        </relation>')
    return lines


def _build_student_relation(s, aind_id, method_dict, field_dict):
    seq = s.get("seq", "")
    n_attr = f' n="{seq}"' if seq else ""
    lines = [
        f'        <relation type="personal" name="student"{n_attr} '
        f'active="#{aind_id}" passive="{fr(s.get("id",""))}">'
    ]
    lines.extend(_build_method_field_desc(
        s.get("method_id", ""), s.get("field_id", ""),
        method_dict, field_dict,
    ))
    if s.get("text_ar") or s.get("text_lat"):
        tid = fr(s.get("text_id", ""))
        ref_attr = f' ref="{tid}"' if tid else ""
        if s.get("text_ar"):
            lines.append(f'            <bibl xml:lang="ar"{ref_attr}>{escape_xml(s["text_ar"])}</bibl>')
        if s.get("text_lat"):
            lines.append(f'            <bibl xml:lang="lat"{ref_attr}>{escape_xml(s["text_lat"])}</bibl>')
    if s.get("teach_date") or s.get("teach_place_ar"):
        da = f' when="{escape_xml_attr(s["teach_date"])}"' if s.get("teach_date") else ""
        pr = f' where="{fr(s.get("teach_place_id",""))}"' if s.get("teach_place_id") else ""
        if s.get("teach_place_ar"):
            lines.append(
                f'            <event type="teaching"{da}{pr}>'
                f'<placeName>{escape_xml(s["teach_place_ar"])}</placeName>'
                f'</event>'
            )
        else:
            lines.append(f'            <event type="teaching"{da}{pr}/>')
    lines.append('        </relation>')
    return lines


def _build_family_relation(fam, aind_id):
    rel      = fam.get("relation", "other")
    rel_note = fam.get("relation_note", "")
    subtype  = rel_note if (rel == "other" and rel_note) else rel
    fam_ref  = fr(fam.get("id", ""))
    return (
        f'        <relation type="personal" subtype="{escape_xml_attr(subtype)}" '
        f'active="{fam_ref}" passive="#{aind_id}">'
        f'<desc>{escape_xml(fam.get("name",""))}</desc></relation>'
    )


def _build_social_relation(sr, aind_id):
    sr_type = sr.get("type", "")
    if not sr_type:
        return None
    if sr_type == "other" and sr.get("type_other"):
        subtype = sr["type_other"]
    else:
        subtype = sr_type
    person_id  = sr.get("person_id", "")
    person_ref = fr(person_id) if person_id else ""

    inner_parts = []
    if sr.get("person_name"):
        inner_parts.append(f'<desc>{escape_xml(sr["person_name"])}</desc>')
    if sr.get("description"):
        inner_parts.append(
            f'<note xml:lang="{detect_lang(sr["description"])}">'
            f'{escape_xml(sr["description"])}</note>'
        )
    if not inner_parts:
        return None
    return (
        f'        <relation type="personal" subtype="{escape_xml_attr(subtype)}" '
        f'active="{person_ref}" passive="#{aind_id}">'
        + "".join(inner_parts) +
        f'</relation>'
    )


def build_list_relation(x, d, method_dict, field_dict):
    aind_id = d.get("aind_id", "")
    relations = []
    for t in d.get("teachers", []):
        relations.extend(_build_teacher_relation(t, aind_id, method_dict, field_dict))
    for s in d.get("students", []):
        relations.extend(_build_student_relation(s, aind_id, method_dict, field_dict))
    for fam in d.get("family", []):
        relations.append(_build_family_relation(fam, aind_id))
    for sr in d.get("social_relations", []):
        line = _build_social_relation(sr, aind_id)
        if line:
            relations.append(line)
    if relations:
        x.append('    <listRelation>')
        x.extend(relations)
        x.append('    </listRelation>')


def _build_activity(a):
    if not a.get("place_ar"):
        return None
    seq      = a.get("seq", "")
    n_attr   = f' n="{seq}"' if seq else ""
    place_id = a.get("id", "")
    ref_att  = f' ref="{fr(place_id)}"' if place_id else ""
    atype    = a.get("type", "reside")

    date_h    = a.get("date_h", "")
    date_attr = f' when-custom="{escape_xml_attr(date_h)}"' if date_h else ""
    cert      = a.get("date_cert", "")
    cert_attr = f' cert="{cert}"' if cert else ""

    place_inner = f'<placeName{ref_att}>{escape_xml(a["place_ar"])}</placeName>'
    note = a.get("date_note", "")
    note_inner = (
        f'<note xml:lang="{detect_lang(note)}">{escape_xml(note)}</note>'
        if note else ""
    )

    if atype == "born":
        return f'    <event type="birth"{n_attr}{date_attr}{cert_attr}>{place_inner}{note_inner}</event>'
    elif atype == "died":
        return f'    <event type="death"{n_attr}{date_attr}{cert_attr}>{place_inner}{note_inner}</event>'
    elif atype == "buried":
        return f'    <event type="burial"{n_attr}{date_attr}{cert_attr}>{place_inner}{note_inner}</event>'
    elif atype == "hajj":
        return f'    <event type="pilgrimage" subtype="hajj"{n_attr}{date_attr}{cert_attr}>{place_inner}{note_inner}</event>'
    elif atype == "umrah":
        return f'    <event type="pilgrimage" subtype="umrah"{n_attr}{date_attr}{cert_attr}>{place_inner}{note_inner}</event>'
    else:
        # reside / visit / travel / study / other → <residence>
        return (
            f'    <residence{n_attr} type="{atype}"{ref_att}{date_attr}{cert_attr}>'
            f'<placeName>{escape_xml(a["place_ar"])}</placeName>'
            f'{note_inner}'
            f'</residence>'
        )


def build_activities(x, d):
    for a in d.get("activities", []):
        line = _build_activity(a)
        if line:
            x.append(line)


def build_institutions(x, d):
    for inst in d.get("institutions", []):
        na = inst.get("name_ar", inst.get("name", ""))
        nl = inst.get("name_lat", "")
        if not (na or nl):
            continue
        inst_ref = fr(inst.get("id", ""))
        ref_att  = f' ref="{inst_ref}"' if inst_ref else ""
        n_attr   = f' n="{inst.get("seq","")}"' if inst.get("seq") else ""
        x.append(
            f'    <affiliation{n_attr} type="{escape_xml_attr(inst.get("type",""))}"{ref_att}>'
        )
        if na: x.append(f'        <orgName xml:lang="ar">{escape_xml(na)}</orgName>')
        if nl: x.append(f'        <orgName xml:lang="lat">{escape_xml(nl)}</orgName>')
        x.append('    </affiliation>')


def build_offices(x, d):
    for off in d.get("offices", []):
        if not (off.get("name_ar") or off.get("name_lat")):
            continue
        off_ref = fr(off.get("id", ""))
        ref_att = f' ref="{off_ref}"' if off_ref else ""
        n_attr  = f' n="{off.get("seq","")}"' if off.get("seq") else ""
        x.append(f'    <state{n_attr} type="office"{ref_att}>')
        if off.get("name_ar"):
            x.append(f'        <label xml:lang="ar">{escape_xml(off["name_ar"])}</label>')
        if off.get("name_lat"):
            x.append(f'        <label xml:lang="lat">{escape_xml(off["name_lat"])}</label>')
        if off.get("appoint_date"):
            x.append(f'        <date type="appointment" when-custom="{escape_xml_attr(off["appoint_date"])}"/>')
        if off.get("retire_date"):
            x.append(f'        <date type="retirement" when-custom="{escape_xml_attr(off["retire_date"])}"/>')
        if off.get("place_ar") or off.get("place_id"):
            pr = fr(off.get("place_id", ""))
            ref_p = f' ref="{pr}"' if pr else ""
            x.append(f'        <placeName{ref_p}>{escape_xml(off.get("place_ar",""))}</placeName>')
        if off.get("inst_name") or off.get("inst_id"):
            ir = fr(off.get("inst_id", ""))
            ref_i = f' ref="{ir}"' if ir else ""
            x.append(f'        <orgName{ref_i}>{escape_xml(off.get("inst_name",""))}</orgName>')
        x.append('    </state>')


def build_bio_events(x, d):
    for be in d.get("bio_events", []):
        be_type = be.get("type", "")
        if not be_type:
            continue
        if not (be.get("description") or be.get("place_ar")):
            continue

        seq       = be.get("seq", "")
        n_attr    = f' n="{seq}"' if seq else ""
        date_h    = be.get("date_h", "")
        date_attr = f' when-custom="{escape_xml_attr(date_h)}"' if date_h else ""
        cert      = be.get("date_cert", "")
        cert_attr = f' cert="{cert}"' if cert else ""

        inner_lines = []
        if be.get("place_ar"):
            place_id = be.get("place_id", "")
            ref_p    = f' ref="{fr(place_id)}"' if place_id else ""
            inner_lines.append(
                f'        <placeName{ref_p}>{escape_xml(be["place_ar"])}</placeName>'
            )
        if be.get("description"):
            desc_lang = detect_lang(be["description"])
            inner_lines.append(
                f'        <desc xml:lang="{desc_lang}">{escape_xml(be["description"])}</desc>'
            )
        if be.get("date_note"):
            note_lang = detect_lang(be["date_note"])
            inner_lines.append(
                f'        <note xml:lang="{note_lang}">{escape_xml(be["date_note"])}</note>'
            )

        if inner_lines:
            x.append(f'    <event type="{escape_xml_attr(be_type)}"{n_attr}{date_attr}{cert_attr}>')
            x.extend(inner_lines)
            x.append('    </event>')


def build_notes(x, d):
    if d.get("person_notes"):
        x.append(
            f'    <note type="personalia" xml:lang="{detect_lang(d["person_notes"])}">'
            f'{escape_xml(d["person_notes"])}</note>'
        )
    # translation_jp / translation_en は明示的な言語フィールドなので固定
    if d.get("translation_jp"):
        x.append(
            f'    <note type="translation" xml:lang="ja">'
            f'{escape_xml(d["translation_jp"])}</note>'
        )
    if d.get("translation_en"):
        x.append(
            f'    <note type="translation" xml:lang="en">'
            f'{escape_xml(d["translation_en"])}</note>'
        )


def build_xml(d):
    x = []
    method_dict, field_dict = build_method_field_dicts()

    x.append(
        f'<person xml:id="{escape_xml_attr(d.get("aind_id",""))}" '
        f'corresp="#source_{escape_xml_attr(d.get("original_id",""))}">'
    )

    build_persnames(x, d)
    build_sex(x, d)
    build_madhhab_and_sufi(x, d)
    build_birth_death(x, d)
    build_list_relation(x, d, method_dict, field_dict)
    build_activities(x, d)
    build_institutions(x, d)
    build_offices(x, d)
    build_bio_events(x, d)
    build_notes(x, d)

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
# --- Editors' Notes ---
# ===================================================
st.divider()
st.subheader("🗒️ Editors' Notes")
st.caption("判断に困った点・要確認事項・編集上の備考など")
d["editors_notes"] = st.text_area(
    "Editors' Notes",
    value=d.get("editors_notes",""),
    height=120,
    placeholder="例: 生年不詳。師匠の名前が複数の読み方が可能。スプレッドシートのIDと要照合。",
    label_visibility="collapsed"
)

# ===================================================
# --- 10. スプレッドシート書き込み ---
# ===================================================
st.divider()
st.header("4. スプレッドシートに保存")

DATASET_SHEET_ID = "1tCoRH0NEwZpgig2DePCVoldU_PSNAdDW9QKkn2KlNp8"

# 列定義（スプレッドシートのヘッダー順）
# 担当者 | AIND-D-XXXX | 12digitsID | persName(Full Arabic) | persName(Ism/Father/GF) | Birth(H) | Death(H) | Madhhab | Editors' Notes
SHEET_COLUMNS = [
    "担当者",
    "AIND-D-XXXX",
    "12digitsID",
    "persName (Full Arabic)",
    "persName (Ism/Father/GF)",
    "Birth (H)",
    "Death (H)",
    "Madhhab",
    "Editors' Notes",
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
        data.get("editors_notes", ""),     # Editors' Notes
    ]

def find_row_by_id(worksheet, original_id):
    """12digitsID列（4列目）でoriginal_idを検索"""
    try:
        col_values = worksheet.col_values(4)  # 4列目 = 12digitsID（A列に行数追加後）
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

ASSIGNEE_OPTIONS = ["Ito_done", "Kuma_done", "Miura_done", "Ota_done", "Shino_done", "AssistantA_done", "AssistantB_done"]
assignee = st.selectbox("担当者", options=ASSIGNEE_OPTIONS,
    index=ASSIGNEE_OPTIONS.index(st.session_state.get("assignee", "Kuma_done"))
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
                    ws.update(f"B{row_num}:J{row_num}", [row_data])
                    st.success(f"✅ 行 {row_num} を更新しました（12digitsID: {d['original_id']}）")
                else:
                    # 新規行を追加
                    # A列を空にして、B列以降に書く
                    ws.append_row([""] + row_data, value_input_option="USER_ENTERED")
                    st.success(f"✅ 新規行を追加しました（12digitsID: {d['original_id']}）")

            except ImportError as e:
                st.error(f"ライブラリ不足: {e}\nrequirements.txt に gspread と google-auth を追加してください。")
            except Exception as e:
                import traceback
                st.error(f"保存エラー: {type(e).__name__}: {e}")
                st.code(traceback.format_exc())
