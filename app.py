import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import errors as genai_errors
import json
import re
import uuid
import requests
from datetime import date as _date

# アプリのバージョン情報(タイトル横に表示)
APP_VERSION = "v20.11.1"
APP_VERSION_DATE = "2026-07-31"

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
def _safe_get_secret(key, default=None):
    """st.secrets[key] にアクセスする。secrets ファイルが存在しないと
    Streamlit 1.30+ では例外が投げられるため、防御的に None を返す。"""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


api_key = _safe_get_secret("GEMINI_API_KEY")

# 新SDK(google-genai)は Client オブジェクト経由で呼ぶ。
# client.models.generate_content(model=..., contents=...) の形式。
_GENAI_CLIENT = None


def get_genai_client():
    """google-genai の Client をキャッシュして返す。API キーが無ければ None。"""
    global _GENAI_CLIENT
    if _GENAI_CLIENT is not None:
        return _GENAI_CLIENT
    if not api_key:
        return None
    try:
        _GENAI_CLIENT = genai.Client(api_key=api_key)
    except Exception:
        _GENAI_CLIENT = None
    return _GENAI_CLIENT


# 優先モデル(新しい順)。旧 gemini-2.5-flash / 2.0系 / 1.5系は 2026 年に
# シャットダウン済み。参考: https://ai.google.dev/gemini-api/docs/deprecations
PREFERRED_MODELS = [
    'gemini-3.5-flash',        # GA (2026-05-19) / flash-latest 相当
    'gemini-3.1-flash-lite',   # GA (2026-05-07) / 低コスト
    'gemini-flash-latest',     # 最新 flash へのエイリアス(保険)
]


def get_working_model_name():
    """使用する Gemini モデル名(文字列)を返す。新SDKはモデル名を
    generate_content に渡す方式なので、GenerativeModel オブジェクトではなく
    名前を返す。client.models.list() で実在確認し、優先順に選ぶ。"""
    client = get_genai_client()
    if client is None:
        return PREFERRED_MODELS[0]
    try:
        available = []
        for m in client.models.list():
            name = getattr(m, "name", "") or ""
            # "models/gemini-3.5-flash" のような形式 → 末尾名で扱う
            short = name.split("/")[-1]
            actions = getattr(m, "supported_actions", None) or \
                getattr(m, "supported_generation_methods", None) or []
            if actions and "generateContent" not in actions:
                continue
            if any(x in short for x in ("tts", "image", "vision", "embedding")):
                continue
            available.append(short)
        for preferred in PREFERRED_MODELS:
            for m in available:
                if preferred in m:
                    return m
        for m in available:
            if "gemini" in m:
                return m
        if available:
            return available[0]
    except Exception:
        pass
    return PREFERRED_MODELS[0]


def genai_generate_text(prompt, model_name=None):
    """新SDK(google-genai)でテキスト生成し、(text, model_name, error) を返す。
    error は None なら成功。呼び出し側で診断表示・パースを行う。"""
    client = get_genai_client()
    if client is None:
        return None, None, "API キーが未設定です(GEMINI_API_KEY)。"
    name = model_name or get_working_model_name()
    try:
        resp = client.models.generate_content(model=name, contents=prompt)
    except genai_errors.APIError as e:
        return None, name, f"API エラー: {type(e).__name__}: {e}"
    except Exception as e:
        return None, name, f"{type(e).__name__}: {e}"
    text = getattr(resp, "text", None)
    if not text:
        fr = ""
        try:
            fr = str(resp.candidates[0].finish_reason)
        except Exception:
            pass
        return None, name, (
            "モデルが空の応答を返しました"
            + (f"(finish_reason={fr})" if fr else "")
            + "。レート制限・安全フィルタ・モデル名の可能性があります。"
        )
    return text, name, None

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


ORIGINAL_ID_PATTERN = re.compile(r"^\d{12}$")
AIND_ID_PATTERN = re.compile(r"^AIND-D\d{5}$")


def validate_original_id(value):
    """original_id (12 digits ID) が 12 桁の半角数字かどうか判定。
    空欄、12 桁未満/超、英字混入、全角数字等はすべて False。
    """
    if not isinstance(value, str):
        return False
    return bool(ORIGINAL_ID_PATTERN.match(value))


def validate_aind_id(value):
    """aind_id が AIND-D{5桁} 形式かどうか判定。
    """
    if not isinstance(value, str):
        return False
    return bool(AIND_ID_PATTERN.match(value))


def get_xml_id(data):
    """xml:id を取得する。
    形式: AIND-D{5桁}
    aind_id フィールドにテキストから読み取った値を保持する。
    フォーマット違反 / 空欄の場合は None。
    """
    if not isinstance(data, dict):
        return None
    aid = (data.get("aind_id", "") or "").strip()
    if validate_aind_id(aid):
        return aid
    return None



# === スプレッドシート接続(gspread 基盤) ===

DATASET_SHEET_ID = "1tCoRH0NEwZpgig2DePCVoldU_PSNAdDW9QKkn2KlNp8"


def get_gspread_client():
    """st.secretsのService AccountJSONからgspreadクライアントを生成"""
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    sa = _safe_get_secret("gcp_service_account")
    if not sa:
        raise RuntimeError(
            "secrets.toml に [gcp_service_account] セクションがありません。"
            "Streamlit Cloud の Secrets 設定か、ローカルなら "
            ".streamlit/secrets.toml にサービスアカウント JSON を登録してください。"
        )
    creds_dict = dict(sa)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def get_xml_filename(data):
    """XMLファイル名を生成する。
    形式: {AIND-D ID}_{12桁ID}.xml
    例:   AIND-D00001_932540579843.xml

    両方とも揃っていない場合は片方だけ、両方とも欠ければ None。
    """
    if not isinstance(data, dict):
        return None
    aid = (data.get("aind_id", "") or "").strip()
    oid = (data.get("original_id", "") or "").strip()
    aid_ok = validate_aind_id(aid)
    oid_ok = validate_original_id(oid)
    if aid_ok and oid_ok:
        return f"{aid}_{oid}.xml"
    if aid_ok:
        return f"{aid}.xml"
    if oid_ok:
        return f"{oid}.xml"
    return None


def pad_year_attr(s):
    """日付文字列を ISO 8601 風に整形(4桁年・2桁月日のゼロパディング)。
    例: "850" → "0850" / "850-09" → "0850-09" / "850-09-15" → "0850-09-15"
    数値以外のトークンはそのまま残す(防御的)。
    """
    if s is None:
        return ""
    s = str(s).strip()
    if not s:
        return ""
    parts = s.split("-")
    out = []
    for i, p in enumerate(parts):
        ps = p.strip()
        if ps.isdigit():
            width = 4 if i == 0 else 2
            out.append(f"{int(ps):0{width}d}")
        else:
            out.append(p)
    return "-".join(out)

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


# 解析プロンプトは外部ファイル prompt_analyze.txt に分離(app.py 本体の肥大回避)。
# プレースホルダー {{ID_MASTER}} / {{SOURCE_TEXT}} を実データに置換して使う。
# f-string ではなく明示 replace を使う(プロンプト中の JSON 波括弧を壊さないため)。
import os as _os

try:
    _APP_DIR = _os.path.dirname(_os.path.abspath(__file__))
except NameError:
    # 一部の実行形態では __file__ が未定義。カレントディレクトリを使う。
    _APP_DIR = _os.getcwd()

_PROMPT_ANALYZE_PATH = _os.path.join(_APP_DIR, "prompt_analyze.txt")


@st.cache_data(ttl=300)
def _load_analyze_prompt_template():
    """解析プロンプトのテンプレート本文を読み込む(キャッシュ)。
    ファイルが無い場合は None を返し、呼び出し側でエラー表示する。"""
    try:
        with open(_PROMPT_ANALYZE_PATH, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def build_analyze_prompt(id_master_text, source_input):
    """外部テンプレートにID-Masterと史料テキストを差し込んで解析プロンプトを生成。
    テンプレート未読込時は None を返す。"""
    tmpl = _load_analyze_prompt_template()
    if tmpl is None:
        return None
    return (tmpl
            .replace("{{ID_MASTER}}", id_master_text or "")
            .replace("{{SOURCE_TEXT}}", source_input or ""))


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
    "residence", "visit", "travel", "study",
    "hajj", "umrah", "jāwara", "riḥla",
    "legacy",  # 死後イベント(遺産・後世への影響)
    "other",
]
# 注: "buried" は v20.1 で廃止。埋葬地は <death> 内の burial_place_* で管理。

# UI 入力値 → XML 出力(type, subtype) のマッピング。
# subtype が None の場合は subtype 属性を出力しない。
EVENT_TYPE_MAPPING = {
    "hajj":      ("religious", "hajj"),
    "umrah":     ("religious", "umrah"),
    "jāwara":    ("residence", "jāwara"),
    "riḥla":     ("travel",    "riḥla"),
    "residence": ("residence", None),
    "burial":    ("burial",    None),
    "buried":    ("burial",    None),
    "visit":     ("visit",     None),
    "travel":    ("travel",    None),
    "study":     ("study",     None),
    "legacy":    ("legacy",    None),
    "cultural":  ("cultural",  None),
    "political": ("political", None),
    "religious": ("religious", None),
    "other":     ("other",     None),
}


def build_event_attrs(ui_type):
    """UI 入力値から XML の type / subtype 属性文字列を組み立てる。
    マッピング未登録の値は ui_type をそのまま type に使う(防御的)。
    """
    xml_type, xml_subtype = EVENT_TYPE_MAPPING.get(ui_type, (ui_type, None))
    attrs = f'type="{xml_type}"'
    if xml_subtype:
        attrs += f' subtype="{xml_subtype}"'
    return attrs

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

# respStmt の役割選択肢
RESP_ROLE_OPTIONS = [
    "初版作成",
    "修正・追記",
    "校閲",
    "翻訳",
    "ID 照合",
    "その他",
]

# respStmt の作業者名(プルダウン)
RESP_PERSON_OPTIONS = [
    "Takao Ito",
    "Erina Ota",
    "Wakako Kumakura",
    "Tomoaki Shinoda",
    "Toru Miura",
    "Rui Nakagawa",
    "Naoki Umetsu",
    "Saeri Kato",
    "Assistant 4",
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
    # aind_id (AIND-D{5桁}): xml:id として使用、テキストヘッダーから読み取る
    # original_id (12 digits ID): source 属性として使用、テキストヘッダーから読み取る
    "aind_id": "",
    "original_id": "",

    # === 名前 ===
    "full_name": "",
    "name_only": "",
    "full_name_lat": "",

    # === 基本属性 ===
    "sex": "M",
    "certainty": "High",

    # === 生没年・場所 ===
    "birth_h": "",
    "birth_cert": "",
    "birth_note": "",
    "birth_inference_note": "",
    "birth_g": "",
    "birth_place_ar": "",
    "birth_place_lat": "",
    "birth_place_id": "",
    "death_h": "",
    "death_cert": "",
    "death_note": "",
    "death_inference_note": "",
    "death_g": "",
    "death_place_ar": "",
    "death_place_lat": "",
    "death_place_id": "",
    "burial_place_ar": "",
    "burial_place_lat": "",
    "burial_place_id": "",

    # === 法学派(v20.8 で配列化、複数 madhhab 対応) ===
    # 旧 "madhhab"(単一オブジェクト)は migrate で "madhhabs"(配列)に変換される。
    # 各要素: {"seq": 1, "lat": "Shafi'i", "id": "wd:Q82245",
    #          "custom_name": "", "custom_id": "", "ui_id": "..."}
    "madhhabs": [],

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

    # === 作業履歴(respStmt 用) ===
    "resp_stmts": [],

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


_ACTIVITY_TYPE_MIGRATION = {
    "reside": "residence",
    "born":   "other",   # 生没情報は <birth>/<death> へ。残骸は other で温存
    "died":   "other",
}


def migrate_activity(old_item):
    """activities の旧→新変換(date系を追加 + 旧 type 名のリネーム)"""
    new_item = dict(old_item)
    new_item.setdefault("date_h", "")
    new_item.setdefault("date_cert", "")
    new_item.setdefault("date_note", "")
    old_type = new_item.get("type", "")
    if old_type in _ACTIVITY_TYPE_MIGRATION:
        new_item["type"] = _ACTIVITY_TYPE_MIGRATION[old_type]
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
        # aind_id (AIND-D{5桁}) と original_id (12digit) の両方を保持
        "aind_id", "original_id", "full_name", "name_only", "full_name_lat",
        "certainty", "birth_h", "birth_g", "death_h", "death_g",
        "sufi_order", "nisbahs", "laqabs",
        "institutions", "offices", "person_notes", "editors_notes",
        "source_text", "translation_jp", "translation_en",
    ]
    for f in simple_fields:
        if f in old_data:
            new_data[f] = old_data[f]

    # === madhhab → madhhabs(配列)への変換(v20.8 から) ===
    # 旧データ:
    #   "madhhab": {"lat": "Shafi'i", "id": "wd:Q82245", ...}
    # 新データ:
    #   "madhhabs": [{"seq": 1, "lat": "Shafi'i", "id": "wd:Q82245", ...}]
    # 旧 "madhhabs"(既に配列形式)があれば優先、なければ単一 "madhhab" から変換
    if "madhhabs" in old_data and isinstance(old_data["madhhabs"], list):
        new_data["madhhabs"] = old_data["madhhabs"]
    elif "madhhab" in old_data and isinstance(old_data["madhhab"], dict):
        old_m = old_data["madhhab"]
        # 「Unknown / Other」かつ custom_name も空なら、空配列扱い(=未指定)
        lat = old_m.get("lat", "")
        if lat == "Unknown / Other" and not old_m.get("custom_name", "").strip():
            new_data["madhhabs"] = []
        else:
            new_data["madhhabs"] = [{
                "seq": 1,
                "lat": lat or "Unknown / Other",
                "id": old_m.get("id", ""),
                "custom_name": old_m.get("custom_name", ""),
                "custom_id": old_m.get("custom_id", ""),
                "ui_id": str(uuid.uuid4()),
            }]
    else:
        new_data["madhhabs"] = []

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

    # 旧 activities の "buried" タイプを burial_place_* に救済(初出のみ採用)
    # 旧データに buried activity があれば、その place_* を death の burial_place に移す。
    # 移管後、buried activity は activities から削除(重複を避けるため)。
    remaining_activities = []
    burial_moved = False
    for a in new_data["activities"]:
        if a.get("type") == "buried" and not burial_moved:
            if not new_data.get("burial_place_ar") and a.get("place_ar"):
                new_data["burial_place_ar"] = a.get("place_ar", "")
            if not new_data.get("burial_place_lat") and a.get("place_lat"):
                new_data["burial_place_lat"] = a.get("place_lat", "")
            if not new_data.get("burial_place_id") and a.get("id"):
                new_data["burial_place_id"] = a.get("id", "")
            burial_moved = True
            # この buried activity は捨てる(burial_place に移管したため)
            continue
        # buried 以外、または 2 つ目以降の buried(レアケース)はそのまま残す
        remaining_activities.append(a)
    new_data["activities"] = remaining_activities

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


_PLACEHOLDER_RE = re.compile(r"^TMP-[A-Z]-0+$")


def is_placeholder_id(id_str):
    """TMP-X-00000 / TMP-X-000000 のようなプレースホルダーか判定。
    空文字も「採番されていない」扱いで True を返す。
    """
    if not id_str:
        return True
    return bool(_PLACEHOLDER_RE.match(str(id_str).strip()))


# 自動採番の対象フィールド: (section, field, prefix, pair_name_field)
# pair_name_field: 採番するか判定するための「名前」フィールド名。
#                  この名前フィールドが空欄の場合、ID も採番しない
#                  (Gemini がテンプレートのプレースホルダーを誤って返した場合の防御)。
#                  None なら名前チェックなし(常に採番)。
TMP_FIELDS_BY_PREFIX = [
    ("nisbahs",          "id",              "TMP-N-",  "ar"),
    ("teachers",         "id",              "TMP-P-",  "name"),
    ("teachers",         "text_id",         "TMP-T-",  "text_ar"),
    ("teachers",         "learn_place_id",  "TMP-L-",  "learn_place_ar"),
    ("students",         "id",              "TMP-P-",  "name"),
    ("students",         "text_id",         "TMP-T-",  "text_ar"),
    ("students",         "teach_place_id",  "TMP-L-",  "teach_place_ar"),
    ("activities",       "id",              "TMP-L-",  "place_ar"),
    ("institutions",     "id",              "TMP-I-",  "name_ar"),
    ("offices",          "id",              "TMP-O-",  "name_ar"),
    ("offices",          "place_id",        "TMP-L-",  "place_ar"),
    ("offices",          "inst_id",         "TMP-I-",  "inst_name"),
    ("family",           "id",              "TMP-P-",  "name"),
    ("bio_events",       "place_id",        "TMP-L-",  "place_ar"),
    ("social_relations", "person_id",       "TMP-P-",  "person_name"),
]


# === ID-Master ポストプロセス照合(Task 3-1) ===

# アラビア文字の正規化テーブル(完全一致照合用)。
# ハムザのバリエーション・ターマールブータ・アリフマクスーラを統一し、
# 末尾のダイアクリティクス(タンウィーン等)を除去する。
_ARABIC_NORMALIZE_TR = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي",
    "ة": "ه",
    "ؤ": "و",
    "ئ": "ي",
})
# 削除する文字: シャッダ・スクーン・各種ハラカ・タンウィーン
_ARABIC_DIACRITICS = re.compile(r"[ً-ٰٟ]")


def normalize_arabic(s):
    """アラビア語テキストを完全一致照合用に正規化。
    ハムザ統一、ヤー/タ・マルブータ統一、ダイアクリティクス削除、
    空白の整理を行う。
    """
    if not s:
        return ""
    s = str(s).strip()
    s = s.translate(_ARABIC_NORMALIZE_TR)
    s = _ARABIC_DIACRITICS.sub("", s)
    s = re.sub(r"\s+", " ", s)
    return s


# 照合対象: (section, name_field, id_field, expected_id_master_category)
# expected_category は ID-Master の Category 列との一致判定に使う。
# 空文字なら Category チェックを省略(全カテゴリ対象)。
ID_MATCH_FIELDS = [
    ("teachers",         "name",           "id",              "Person"),
    ("teachers",         "text_ar",        "text_id",         "Text"),
    ("teachers",         "learn_place_ar", "learn_place_id",  "Place"),
    ("students",         "name",           "id",              "Person"),
    ("students",         "text_ar",        "text_id",         "Text"),
    ("students",         "teach_place_ar", "teach_place_id",  "Place"),
    ("family",           "name",           "id",              "Person"),
    ("nisbahs",          "ar",             "id",              "Nisbah"),
    ("activities",       "place_ar",       "id",              "Place"),
    ("institutions",     "name_ar",        "id",              "Institution"),
    ("offices",          "name_ar",        "id",              "Office"),
    ("offices",          "place_ar",       "place_id",        "Place"),
    ("offices",          "inst_name",      "inst_id",         "Institution"),
    ("bio_events",       "place_ar",       "place_id",        "Place"),
    ("social_relations", "person_name",    "person_id",       "Person"),
]


def _build_id_master_index(records):
    """ID-Master を {(category, normalized_arabic): id_value} の辞書に変換。
    Category 不明エントリは ("", normalized_arabic) でも引けるよう両方登録。
    """
    index = {}
    for r in records:
        id_val = (r.get("ID", "") or "").strip()
        cat = (r.get("Category", "") or "").strip()
        if not id_val:
            continue
        # 「الأزهر | جامع الأزهر」「التقي بن فهد| ابن فهد」のような
        # | 区切りの別名も個別キーとして登録する(v20.11)。
        # これをしないと別名側の表記で照合失敗→取りこぼし/誤検疫が起きる。
        for _alt in str(r.get("Arabic", "") or "").split("|"):
            ar = normalize_arabic(_alt)
            if not ar:
                continue
            index.setdefault((cat, ar), id_val)
            index.setdefault(("", ar), id_val)  # Category 不問のフォールバック
    return index


def _is_confirmed_id(id_str):
    """既に確定した ID(Wikidata Q-ID, GeoNames 数字, 確定 TMP-, id_)かを判定。
    プレースホルダー(TMP-X-0...0)や空欄は False。

    注意: この関数は「形式として確定 ID か」だけを見る。TMP- 番号が
    ID-Master に実在するか・名前が一致するかは検証しない。生成モデルが
    埋めた偽 TMP 番号の検疫は verify_and_quarantine_tmp_ids() で別途行う。
    """
    s = (id_str or "").strip()
    if not s:
        return False
    if is_placeholder_id(s):
        return False
    return True


# === 幻番号(phantom TMP)検疫 — Task: 幻番号の検出・遮断 ===
#
# 背景: 生成モデル(Gemini 等)は、未知の人物・地名などに対して
# ID-Master に実在する既存 TMP 番号(例 TMP-P-000066)を勝手に流用して
# 返すことがある。これらは全桁ゼロのプレースホルダーではないため
# is_placeholder_id() では捕捉できず、_is_confirmed_id() が True を返して
# しまい、名前照合も再採番もスキップされてそのまま確定 ID として残る。
# これが校閲工数の最頻出エラー(HANDOVER: phantom number contamination)。
#
# 対策: 採番パイプラインの最初に本関数を通し、生成モデルが埋めた TMP 番号を
#   (a) ID-Master に実在し
#   (b) 同じ行の名前が正規化一致する
# ときだけ確定として残す。それ以外(未登録番号・別人流用)は
# プレースホルダー "TMP-X-000000" に差し戻し、正規の照合→追記採番ルートに
# 載せる。差し戻した内容は呼び出し側に返し、UI で可視化する。

# TMP プレフィックス → ID-Master の Category 名
_PREFIX_TO_CATEGORY = {
    "TMP-P-": "Person",
    "TMP-N-": "Nisbah",
    "TMP-L-": "Place",
    "TMP-I-": "Institution",
    "TMP-O-": "Office",
    "TMP-T-": "Text",
    "TMP-S-": "Subject",
}


def _build_id_to_master_row(records):
    """ID-Master を {id_value: {"ar_norm": 正規化アラビア名, "raw": 元行}} に変換。
    同一 ID が複数行にある場合は最初の行を採用。"""
    idmap = {}
    for r in records:
        id_val = (r.get("ID", "") or "").strip()
        if not id_val:
            continue
        if id_val not in idmap:
            _ar_raw = str(r.get("Arabic", "") or "")
            _alts = [normalize_arabic(a) for a in _ar_raw.split("|")]
            _alts = [a for a in _alts if a]
            idmap[id_val] = {
                "ar_norm": normalize_arabic(_ar_raw),
                "ar_norms": _alts,  # | 区切り別名(v20.11)
                "latin": (r.get("Latin", "") or "").strip(),
                "category": (r.get("Category", "") or "").strip(),
            }
    return idmap


def verify_and_quarantine_tmp_ids(d, records=None, silent=False):
    """生成モデルが埋めた TMP 番号を ID-Master 実在＋名前一致で検証し、
    不正なものをプレースホルダーに差し戻す。

    Returns: 差し戻した項目のリスト
        [{"section","field","name","bad_id","reason","master_name"}...]
    reason は "unregistered"(番号未登録) / "name_mismatch"(別人流用)。
    """
    if records is None:
        records = load_id_master()
    if not records:
        return []

    idmap = _build_id_to_master_row(records)
    quarantined = []

    def check_one(container, name_field, id_field, prefix):
        current = str(container.get(id_field, "") or "").strip()
        if not current.startswith(prefix):
            return
        if is_placeholder_id(current):
            return  # 既にプレースホルダー → 正規ルートで処理
        name_raw = str(container.get(name_field, "") or "").strip()
        name_norm = normalize_arabic(name_raw)
        digits = TMP_ID_PREFIXES[prefix][1]
        placeholder = f"{prefix}{0:0{digits}d}"

        row = idmap.get(current)
        if row is None:
            # ID-Master に存在しない番号 → 生成モデルの捏造
            container[id_field] = placeholder
            quarantined.append({
                "section": "", "field": id_field, "name": name_raw,
                "bad_id": current, "reason": "unregistered", "master_name": "",
            })
            return
        # 番号は実在する。名前が一致するか(正規化完全一致。| 区切り別名も許容)。
        _alts = row.get("ar_norms") or ([row["ar_norm"]] if row.get("ar_norm") else [])
        if name_norm and _alts and name_norm not in _alts:
            container[id_field] = placeholder
            quarantined.append({
                "section": "", "field": id_field, "name": name_raw,
                "bad_id": current, "reason": "name_mismatch",
                "master_name": row["ar_norm"],
            })
        # 名前一致、あるいは名前空欄(照合不能)なら現状維持。
        # 名前空欄の TMP は後続の auto_assign 側でクリアされる。

    for section, field, prefix, pair_name_field in TMP_FIELDS_BY_PREFIX:
        for item in d.get(section, []) or []:
            before = str(item.get(field, "") or "").strip()
            check_one(item, pair_name_field, field, prefix)
            if item.get(field, "") != before and quarantined:
                quarantined[-1]["section"] = section

    # トップレベル birth/death/burial place_id
    for field in ("birth_place_id", "death_place_id", "burial_place_id"):
        pair_field = field.replace("_id", "_ar")
        before = str(d.get(field, "") or "").strip()
        check_one(d, pair_field, field, "TMP-L-")
        if str(d.get(field, "") or "").strip() != before and quarantined:
            quarantined[-1]["section"] = field

    if not silent and quarantined:
        st.warning(
            f"⚠️ 生成モデルが返した {len(quarantined)} 件の TMP 番号を検疫しました"
            "(ID-Master 実在・名前一致の検証で不合格)。下記を確認してください。"
        )
        for q in quarantined:
            reason_ja = {
                "unregistered": "未登録番号",
                "name_mismatch": f"別人流用(Master名: {q['master_name']})",
            }.get(q["reason"], q["reason"])
            st.caption(
                f"　• [{q['section']}.{q['field']}] "
                f"「{q['name'] or '(名前空欄)'}」← {q['bad_id']} を差し戻し（{reason_ja}）"
            )

    try:
        st.session_state.setdefault("_last_reports", {})["tmp_quarantine"] = quarantined
    except Exception:
        pass

    return quarantined


# === wd/gn 毒ID検疫・汎称語フィルタ・立項番号ガード (v20.11 追加) ===
#
# 背景(校閲バッチ B14–B19 で確定した生成モデルの系統的エラー):
#  (1) Wikidata Q-ID の実item別物流用。例: Q208507=The Chemical Brothers を
#      صحيح البخاري に、Q561280=César-François Cassini(18世紀仏天文学者)を
#      الأشرف قايتباي に付与。TMP検疫(verify_and_quarantine_tmp_ids)は
#      wd:/gn: を素通しするため、ここで別途検疫する。
#  (2) 汎称語の幻person化。「سمع على جماعة منهم فلان」の جماعة(一団)を
#      person 化して ID-Master の TMP-P-000004(جماعة) 等に照合させてしまう。
#      ※「ابن جماعة」は実在の家名なので保護する。
#  (3) 立項番号の誤読。corpus 行頭の裸数字(刊本の立項連番)を没年に転記
#      (例 B19 D01856「831年没」)・訳文冒頭に混入(833/837)。

# 過去バッチで「実item別物/照合不可」と確定した Q-ID(見たら即検疫)
WD_GN_DENYLIST = {
    "Q208507",   # The Chemical Brothers — صحيح البخاري ではない
    "Q193272",   # ECOWAS(西アフリカ諸国経済共同体) — صحيح مسلم ではない
    "Q1248893",  # Rhipsalis paradoxa subsp.(サボテン) — جامع الترمذي ではない
    "Q593290",   # 照合不可 — سنن أبي داود ではない
    "Q1140365",  # The Calamari Wrestler(映画) — سنن النسائي ではない
    "Q940817",   # 1988年五輪トーゴ選手団 — سنن ابن ماجه ではない
    "Q900871",   # 大川藍(タレント) — الموطأ ではない
    "Q561280",   # César-François Cassini de Thury — قايتباي ではない(B19)
    "Q259",      # Azerbaijan 非該当(現国家=Q227/歴史地域=Q12836408)(B19)
    "Q285077",   # Serri(伊の町) — برقوق ではない(B18)
    "Q470381",   # Heliangelus(ハチドリ) — المؤيد شيخ ではない(B18)
    "Q287515",   # Neumühle(独) — جقمق ではない(B18)
    "Q802521",   # B18破棄
    "Q23975569", # Barsbay madrasa 誤指し
    "Q6835017",  # ḥājib 照合不可
    "Q282218",   # ABC motorcycles — المؤيد شيخ ではない(B28)
    "Q412004",   # "D7" — الأشرف قايتباي ではない(B28)
    "Q368154",   # Sigismund Báthory — الأزهر ではない(B26発覚。ID-Master「الأزهر」行が
                 # 未清掃のため、マスタ照合(step3)より先に必ずここで捕捉する)
}

# 検疫時に校閲者へ提示する「正」候補(自動置換はしない。確認の上で採用)
WD_GN_SUGGESTIONS = {
    "Q208507":  "Q1023470 (Ṣaḥīḥ al-Bukhārī)",
    "Q193272":  "Q886659 (Ṣaḥīḥ Muslim)",
    "Q1248893": "Q2998769 (Jāmiʿ al-Tirmidhī)",
    "Q593290":  "Q947278 (Sunan Abī Dāwūd)",
    "Q1140365": "Q2175237 (Sunan al-Nasāʾī / al-Sunan al-Ṣughrā)",
    "Q940817":  "Q1187931 (Sunan Ibn Mājah)",
    "Q900871":  "Q1050556 (al-Muwaṭṭaʾ)",
    "Q561280":  "AIND-D06305 + corresp=wd:Q557847 (Qāytbāy。D-3裁定=AIND優先)",
    "Q282218":  "AIND-D03345 (al-Muʾayyad Shaykh)",
    "Q412004":  "AIND-D06305 + corresp=wd:Q557847 (al-Ashraf Qāytbāy)",
    "Q368154":  "Q312342 (al-Azhar)",
    "Q259":     "Q12836408 (Azerbaijan region)",
    "Q285077":  "AIND-D02178 (al-Ẓāhir Barqūq)",
    "Q470381":  "AIND-D03345 (al-Muʾayyad Shaykh)",
    "Q287515":  "AIND-D02423 (al-Ẓāhir Jaqmaq)",
}

# プロジェクトで実item照合済みの Q-ID(handover v13.0 確定リスト+今回照合分)
WD_ALLOWLIST = {
    "Q4120128", "Q471116", "Q1023470", "Q886659", "Q2998769", "Q947278",
    "Q2175237", "Q1187931", "Q1050556", "Q12217063",
    "Q557847", "Q248996", "Q698037", "Q730299",
    "Q293604", "Q4664581", "Q4725309", "Q257745", "Q6798541", "Q12198099",
    "Q486080", "Q428858", "Q8462", "Q12836408",
    "Q82245", "Q160851", "Q191314", "Q48221",
    "Q217029", "Q484181", "Q12227702", "Q1817983", "Q1866303",
    # Q368154 は毒(Sigismund Báthory)と判明したため allowlist から denylist へ移動(v20.11.1)
}

# 照合済み GeoNames(handover 確定+B19照合分)
GN_ALLOWLIST = {
    "360630",   # القاهرة Cairo
    "109223",   # المدينة Medina
    "104515",   # مكة Mecca
    "170063",   # حلب Aleppo
    "170654",   # دمشق Damascus
    "358048",   # دمياط Damietta
    "266826",   # طرابلس Tripoli (Lebanon)
    "2464915",  # سوسة Sousse
}

# (名前に含まれる語, gn) の既知誤指しペア(gn自体は実在地名なので全面denyしない)
GN_PAIR_DENY = [
    ("سواكن", "105299"),   # Suakin に Jizan の gn を誤付与するパターン
    ("سوسه",  "2464917"),  # Sousse に別idを誤付与するパターン(正: 2464915)
]

# wd で来ても AIND を正とする人物(B28 D-3裁定 2026-07-31: قايتباي)。
# 検疫時に ID を AIND へ差替え、XML 出力時に corresp="wd:..." を自動付与する。
WD_TO_AIND_REDIRECT = {
    "Q557847": "AIND-D06305",   # al-Ashraf Qāytbāy(本伝同定=B28)
}
AIND_CORRESP = {
    "AIND-D06305": "wd:Q557847",
}

_WD_ID_FORM_RE = re.compile(r"^(?:wd:)?(Q\d+)$")
_GN_ID_FORM_RE = re.compile(r"^(?:gn:)?(\d+)$")


def verify_and_quarantine_wd_gn_ids(d, records=None, silent=False):
    """Wikidata Q-ID / GeoNames ID を検疫する。

    - WD_GN_DENYLIST の Q-ID → NEEDID に差し戻し(過去バッチで実item別物と確定)
    - ID-Master 登録済みの Q/gn → 登録名(| 区切り別名含む)と不一致なら NEEDID
    - WD_ALLOWLIST / GN_ALLOWLIST / ID-Master 名前一致 → そのまま(確定扱い)
    - それ以外の未知 wd/gn → 値は保持し「要 WebSearch 実item照合」として報告のみ
      (生成モデルが正しい Q-ID を知っている場合を壊さないため破棄しない)

    Returns: (quarantined, review)
    """
    if records is None:
        records = load_id_master()
    idmap = _build_id_to_master_row(records) if records else {}
    quarantined = []
    review = []

    fields = list(ID_MATCH_FIELDS) + [
        ("(top)", "birth_place_ar",  "birth_place_id",  "Place"),
        ("(top)", "death_place_ar",  "death_place_id",  "Place"),
        ("(top)", "burial_place_ar", "burial_place_id", "Place"),
    ]

    def check(container, section, name_field, id_field):
        raw = str(container.get(id_field, "") or "").strip()
        if not raw or raw == NEEDID_MARKER or raw.startswith(("TMP-", "AIND-", "#")):
            return
        mq = _WD_ID_FORM_RE.match(raw)
        mg = _GN_ID_FORM_RE.match(raw) if not mq else None
        if not mq and not mg:
            return
        key = mq.group(1) if mq else mg.group(1)
        name_raw = str(container.get(name_field, "") or "").strip()
        name_norm = normalize_arabic(name_raw)

        # (1) 確定毒 Q-ID
        if mq and key in WD_GN_DENYLIST:
            container[id_field] = NEEDID_MARKER
            quarantined.append({
                "section": section, "field": id_field, "name": name_raw,
                "bad_id": raw, "reason": "wd実item別物/照合不可(確定毒)",
                "suggest": WD_GN_SUGGESTIONS.get(key, ""),
            })
            return
        # (1.6) AIND 優先人物への差替(D-3裁定)。corresp は build_xml が付与する
        if mq and key in WD_TO_AIND_REDIRECT:
            container[id_field] = WD_TO_AIND_REDIRECT[key]
            review.append({
                "section": section, "field": id_field, "name": name_raw,
                "id": f"{raw} → {WD_TO_AIND_REDIRECT[key]}(+corresp {raw}。D-3裁定による自動差替)",
            })
            return
        # (2) geonames 既知誤指しペア
        if mg:
            for word, bad_gn in GN_PAIR_DENY:
                if key == bad_gn and word in name_norm:
                    container[id_field] = NEEDID_MARKER
                    quarantined.append({
                        "section": section, "field": id_field, "name": name_raw,
                        "bad_id": raw, "reason": "geonames 既知の誤指しペア",
                        "suggest": "",
                    })
                    return
        # (3) ID-Master 登録済み → 登録名との一致検証(| 別名許容)
        row = idmap.get(key)
        if row is not None:
            alts = row.get("ar_norms") or []
            if name_norm and alts and name_norm not in alts:
                container[id_field] = NEEDID_MARKER
                quarantined.append({
                    "section": section, "field": id_field, "name": name_raw,
                    "bad_id": raw,
                    "reason": f"ID-Master 登録名と不一致(登録: {row.get('ar_norm', '')})",
                    "suggest": "",
                })
            return
        # (4) プロジェクト照合済み → 素通し
        if (mq and key in WD_ALLOWLIST) or (mg and key in GN_ALLOWLIST):
            return
        # (5) 未知 → 保持して要照合レポート
        review.append({
            "section": section, "field": id_field, "name": name_raw, "id": raw,
        })

    for section, name_field, id_field, _cat in fields:
        if section == "(top)":
            check(d, section, name_field, id_field)
        else:
            for item in d.get(section, []) or []:
                if isinstance(item, dict):
                    check(item, section, name_field, id_field)

    try:
        _r = st.session_state.setdefault("_last_reports", {})
        _r["wd_quarantine"] = quarantined
        _r["wd_review"] = review
    except Exception:
        pass

    if not silent:
        if quarantined:
            st.warning(
                f"⚠️ Wikidata/GeoNames の毒ID・別item流用 {len(quarantined)} 件を"
                "検疫しました(NEEDID に差し戻し)。"
            )
            for q in quarantined:
                sug = f" → 候補: {q['suggest']}" if q.get("suggest") else ""
                st.caption(
                    f"　• [{q['section']}.{q['field']}] 「{q['name'] or '(名前空欄)'}」"
                    f"← {q['bad_id']} を差し戻し({q['reason']}){sug}"
                )
        if review:
            st.info(
                f"ℹ️ 未照合の Wikidata/GeoNames ID が {len(review)} 件あります。"
                "校閲時に WebSearch で実item名を照合してください(値は保持)。"
            )
            for r in review:
                st.caption(f"　• [{r['section']}.{r['field']}] 「{r['name']}」= {r['id']}(要照合)")

    return quarantined, review


# 汎称語(集合名詞)。正規化後の完全一致で判定。
# 注意: ة→ه 正規化後の綴りで書くこと(جماعة→جماعه)。
_GENERIC_COLLECTIVE_RE = re.compile(
    r"^(?:"
    r"جماعه(?: من .{0,60})?"
    r"|(?:و)?غيره(?:م|ما|ن)?"
    r"|(?:و)?اخرون"
    r"|غير واحد(?:ه)?"
    r"|جمع(?: من .{0,60})?"
    r"|خلق(?: كثير)?"
    r"|الناس"
    r")$"
)


def drop_generic_collective_entries(d, silent=False):
    """جماعة/آخرون/غيره 等の集合汎称が person 化されたエントリを除去する。

    プロンプト§18は skip を指示しているが生成モデルは守らないことがある
    (B19 D02075: جماعة を teacher 化し TMP-P-000004 を付与)。
    保護: 「ابن جماعة」「... بن جماعة」等の実在家名は名前に بن/ابن を
    含むため除去対象にしない。
    """
    targets = [
        ("teachers", "name"),
        ("students", "name"),
        ("family", "name"),
        ("social_relations", "person_name"),
    ]
    dropped = []
    for section, name_field in targets:
        items = d.get(section, []) or []
        kept = []
        for it in items:
            if not isinstance(it, dict):
                kept.append(it)
                continue
            nm = normalize_arabic(str(it.get(name_field, "") or ""))
            protected = (
                (" بن " in f" {nm} ") or nm.startswith("ابن ") or nm.startswith("بن ")
            )
            if nm and not protected and _GENERIC_COLLECTIVE_RE.match(nm):
                dropped.append({"section": section, "name": it.get(name_field, "")})
                continue
            kept.append(it)
        d[section] = kept

    try:
        st.session_state.setdefault("_last_reports", {})["generics"] = dropped
    except Exception:
        pass

    if not silent and dropped:
        st.warning(
            f"⚠️ 集合汎称(جماعة/غيره 等)が person 化された {len(dropped)} 件を"
            "除去しました(プロンプト§18違反の是正)。"
        )
        for q in dropped:
            st.caption(f"　• [{q['section']}] 「{q['name']}」を除去")

    return dropped


# corpus マーカー「$# $ 831 ...」/「$# $$ 162 ...」の直後の裸数字=刊本の立項連番
_ENTRY_SERIAL_RE = re.compile(r"\$#\s*\${1,3}\s+(\d{1,4})(?=\s)")


def scrub_entry_serial_artifacts(d, silent=False):
    """刊本の立項連番(行頭裸数字)の誤読アーティファクトを検出・除去する。

    - 訳文(ja/en)冒頭の裸連番 → 除去(訳が裸番号で始まる正当な場合はない)
    - death_h / birth_h が連番と一致 → 自動削除はせず cert=low 化+note警告
      (偶然、実際の没年と一致する可能性があるため。最終判断は校閲者)
    - 訳文冒頭が「<連番>年」「In <連番>」で始まる場合 → 警告のみ
    """
    src = str(d.get("source_text", "") or "")
    m = _ENTRY_SERIAL_RE.search(src)
    if not m:
        return []
    serial = m.group(1)
    issues = []

    # 訳頭の裸連番(直後が区切り文字のときだけ剥がす。「831年」は剥がさない)
    _sep = r"[\s　、。,.:：]"
    strip_re = re.compile(r"^\s*0*" + re.escape(serial) + r"(?![0-9])(?=" + _sep + r")" + _sep + r"+")
    for fld in ("translation_jp", "translation_en"):
        t = str(d.get(fld, "") or "")
        m2 = strip_re.match(t)
        if m2 and m2.end() < len(t):
            d[fld] = t[m2.end():]
            issues.append({"field": fld, "msg": f"訳冒頭の立項番号 {serial} を除去しました"})
            continue
        # 「831年…」「In 837, …」型は警告のみ(実年の可能性があるため)
        if re.match(r"^\s*0*" + re.escape(serial) + r"年", t) or \
           re.match(r"^\s*In\s+0*" + re.escape(serial) + r"\b", t):
            issues.append({
                "field": fld,
                "msg": f"訳冒頭に立項番号と同値の年({serial})— 原文に年の記載があるか要確認",
            })

    # 生没年が連番と一致 → 要確認フラグ
    for fld in ("death_h", "birth_h"):
        y = str(d.get(fld, "") or "").strip()
        if y and y.split("-")[0].lstrip("0") == serial.lstrip("0"):
            note_f = fld.replace("_h", "_note")
            marker = f"CHECK: {fld}={y} equals the edition's entry serial number {serial}"
            cur_note = str(d.get(note_f, "") or "")
            if marker not in cur_note:
                d[note_f] = (cur_note.strip() + (" " if cur_note.strip() else "") +
                             "⚠ " + marker +
                             " — verify the year is actually stated in the source text.").strip()
            cert_f = fld.replace("_h", "_cert")
            if (d.get(cert_f, "") or "") in ("", "high", "medium"):
                d[cert_f] = "low"
            issues.append({
                "field": fld,
                "msg": f"{fld}={y} が立項番号 {serial} と一致(cert=low 化・note に要確認を追記)",
            })

    try:
        st.session_state.setdefault("_last_reports", {})["serial"] = issues
    except Exception:
        pass

    if not silent and issues:
        st.warning(f"⚠️ 立項番号アーティファクトを {len(issues)} 件処理しました。")
        for q in issues:
            st.caption(f"　• [{q['field']}] {q['msg']}")

    return issues


def apply_id_master_matching(d, silent=False):
    """ID-Master と完全一致で照合し、未確定の ID 欄に自動で値を入れる。

    対象: 各セクションの (アラビア名, ID) ペア(ID_MATCH_FIELDS 参照)
    既に確定 ID が入っている欄は触らない。プレースホルダー / 空欄のみ更新。
    """
    records = load_id_master()
    if not records:
        if not silent:
            st.warning("ID-Master を読み込めませんでした。")
        return 0

    index = _build_id_master_index(records)
    filled = 0
    skipped = 0

    for section, name_field, id_field, category in ID_MATCH_FIELDS:
        for item in d.get(section, []) or []:
            current_id = str(item.get(id_field, "") or "").strip()
            if _is_confirmed_id(current_id):
                # 既に確定 ID あり → 触らない
                continue
            name_raw = str(item.get(name_field, "") or "").strip()
            if not name_raw:
                continue
            key_norm = normalize_arabic(name_raw)
            matched_id = index.get((category, key_norm)) or index.get(("", key_norm))
            if matched_id:
                item[id_field] = matched_id
                filled += 1
            else:
                skipped += 1

    if not silent:
        if filled:
            st.success(f"ID-Master 照合: {filled} 件に ID を自動付与しました(未照合 {skipped} 件)。")
        else:
            st.info(f"ID-Master 照合: 自動付与の対象はありませんでした(候補 {skipped} 件)。")
    return filled


NEEDID_MARKER = "NEEDID"


def mark_unresolved_ids_in_data(d, silent=False):
    """照合で埋まらなかった ID 欄を扱う。番号は生成しない。

    方針(2026-07-03 Waka 指示):
    - アプリ側は新規 TMP 番号を一切採番しない。発番は校閲工程(Claude)に一元化。
    - 「同じ行の名前欄に値があるのに ID が未確定」の欄にだけ NEEDID マーカーを入れ、
      校閲時に AIND 同定 or 新規 TMP 付与すべき箇所を一目で分かるようにする。
    - 名前欄が空の欄(原文に当該情報がない = 該当なし)は空欄のまま。マーカーも入れない。
      生成モデルがそこにプレースホルダーや偽番号を入れていた場合はクリアする。

    「未確定」= 空欄 / プレースホルダー(TMP-X-0...0) / 検疫で差し戻された欄。
    既に確定した ID(AIND-, Q-ID, GeoNames 数字, ID-Master 実在 TMP 等)は触らない。
    NEEDID が既に入っている欄も維持する。
    """
    marked = 0
    cleared = 0

    def is_unresolved(current, prefix):
        """current が未確定(空 or プレースホルダー)か。"""
        if not current:
            return True
        if current == NEEDID_MARKER:
            return True  # 既にマーカー → 未確定扱い(維持)
        if is_placeholder_id(current) and current.startswith(prefix):
            return True
        return False

    def handle(container, name_field, id_field, prefix):
        nonlocal marked, cleared
        current = str(container.get(id_field, "") or "").strip()
        name_val = str(container.get(name_field, "") or "").strip() if name_field else ""

        # 名前が空 = 原文に該当情報なし。ID は必ず空欄にする。
        # (生成モデルが空欄ペアに入れた偽番号・プレースホルダー・NEEDID を除去。
        #  確定 ID であっても、名前が無ければその ID の根拠が無いのでクリアする。)
        if name_field and not name_val:
            if current:
                container[id_field] = ""
                cleared += 1
            return

        # 名前あり: 確定 ID(NEEDID 以外の実 ID・プレースホルダー以外)はそのまま。
        if current and current != NEEDID_MARKER and not (
            is_placeholder_id(current) and current.startswith(prefix)
        ):
            return

        # 名前あり & 未確定(空 / プレースホルダー / NEEDID) → NEEDID マーカー付与
        if is_unresolved(current, prefix):
            if container.get(id_field, "") != NEEDID_MARKER:
                container[id_field] = NEEDID_MARKER
                marked += 1

    for section, field, prefix, pair_name_field in TMP_FIELDS_BY_PREFIX:
        for item in d.get(section, []) or []:
            handle(item, pair_name_field, field, prefix)

    # トップレベル birth/death/burial place_id
    for field in ("birth_place_id", "death_place_id", "burial_place_id"):
        handle(d, field.replace("_id", "_ar"), field, "TMP-L-")

    if not silent:
        msgs = []
        if marked:
            msgs.append(f"{marked} 個の欄に {NEEDID_MARKER} を付与しました(校閲で ID 付与)。")
        if cleared:
            msgs.append(f"{cleared} 個の欄をクリアしました(名前が空欄のため)。")
        if msgs:
            st.success(" / ".join(msgs))
        else:
            st.info("ID 付与が必要な欄はありません。")
        st.rerun()

    return marked, cleared


def auto_assign_tmp_ids_in_data(d, silent=False):
    """【廃止】旧・自動採番関数。2026-07-03 の方針変更で番号生成を廃止し、
    mark_unresolved_ids_in_data(NEEDID 付与)に置き換えた。後方互換のため
    名前だけ残し、新関数へ委譲する。"""
    return mark_unresolved_ids_in_data(d, silent=silent)


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

# トップレベル(person 直下、リストでない)翻字欄。
# (ar_field, lat_field)。full_name は ar 相当の生名から翻字を作る。
TOP_LEVEL_TRANSLITERATE_PAIRS = [
    ("full_name",       "full_name_lat"),
    ("birth_place_ar",  "birth_place_lat"),
    ("death_place_ar",  "death_place_lat"),
    ("burial_place_ar", "burial_place_lat"),
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

    # トップレベル(リストでない)翻字欄も対象に含める。
    # path の section を "__top__" とし、idx に None を入れて区別する。
    for ar_field, lat_field in TOP_LEVEL_TRANSLITERATE_PAIRS:
        ar_val = (d.get(ar_field, "") or "").strip()
        lat_val = (d.get(lat_field, "") or "").strip()
        if ar_val and not lat_val:
            targets.append((("__top__", None, lat_field), ar_val))

    return targets


def apply_transliterations(d, targets, results):
    """翻字結果を空欄に書き戻す。再確認込みで既存値は絶対に上書きしない。"""
    for (path, _), result in zip(targets, results):
        section, idx, field = path
        if not isinstance(result, str):
            continue
        if section == "__top__":
            # トップレベル欄
            if not (d.get(field, "") or "").strip():
                d[field] = result.strip()
        else:
            if not (d[section][idx].get(field, "") or "").strip():
                d[section][idx][field] = result.strip()


def transliterate_empty_latin_fields(d):
    """メイン関数: 空のラテン欄を IJMES 翻字で一括補完。"""
    targets = collect_empty_latin_fields(d)
    if not targets:
        st.info(
            "補完すべき空欄がありません。"
            "(アラビア語欄が入力済みで、対応するラテン欄が空の項目が対象です)"
        )
        return

    st.caption(f"🔧 翻字対象: {len(targets)} 件を検出しました。")
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
            _raw_text, _model_name, _err = genai_generate_text(prompt)
            st.caption(f"🔧 使用モデル: {_model_name or '(未取得)'}")
            if _err:
                st.error(f"翻字エラー: {_err}")
                return

            raw = re.sub(r"```json|```", "", _raw_text).strip()
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
        except json.JSONDecodeError as e:
            st.error(f"翻字エラー: 応答をJSONとして解析できません: {e}")
        except Exception as e:
            st.error(f"翻字エラー: {type(e).__name__}: {e}")


def apply_prompt_madhhab(data, madhhab_value):
    """プロンプトの madhhab 値(文字列 or リスト)を data.madhhabs に展開。

    Gemini からの返り値の形式:
      - 文字列: "Hanafi" → 単一エントリの配列に変換
      - リスト: ["Shafi'i", "Hanbali"] → 順番付き配列に変換(時系列順)
      - リスト(辞書): [{"name": "Shafi'i"}, ...] にも対応(柔軟性確保)
    既存の madhhabs があれば上書き。
    """
    # 入力を正規化してリスト of 文字列にする
    names = []
    if isinstance(madhhab_value, str):
        if madhhab_value.strip():
            names = [madhhab_value.strip()]
    elif isinstance(madhhab_value, list):
        for item in madhhab_value:
            if isinstance(item, str) and item.strip():
                names.append(item.strip())
            elif isinstance(item, dict):
                # {"name": "..."} 形式にも対応
                n = (item.get("name", "") or item.get("lat", "") or "").strip()
                if n:
                    names.append(n)

    if not names:
        return

    new_madhhabs = []
    for i, name in enumerate(names, start=1):
        entry = {
            "seq": i,
            "lat": "Unknown / Other",
            "id": "",
            "custom_name": "",
            "custom_id": "",
            "ui_id": str(uuid.uuid4()),
        }
        # 標準4派にマッチするか確認
        matched = False
        for key, qid in MADHHAB_DATA.items():
            latin_part = key.split(" ")[0]  # 例: "Hanafi"
            if name.lower() == latin_part.lower() or name == key:
                entry["lat"] = key
                entry["id"] = qid
                matched = True
                break
        if not matched:
            # 標準4派にマッチしない場合は custom 扱い
            entry["custom_name"] = name
        new_madhhabs.append(entry)

    data["madhhabs"] = new_madhhabs


def apply_prompt_result(data, prompt_result):
    """Gemini の返り値を data_v19 に最大限自動反映する。"""

    simple_fields = [
        "aind_id", "original_id", "full_name", "name_only", "full_name_lat",
        "translation_jp", "translation_en",
    ]
    for f in simple_fields:
        if f in prompt_result:
            data[f] = prompt_result[f]

    # original_id のバリデーション: 12 桁数字でなければ警告を表示。
    # データ自体は保持(ユーザーが手で修正できるように)。
    oid = (data.get("original_id", "") or "").strip()
    if oid and not validate_original_id(oid):
        st.warning(
            f"original_id (12 digits ID) が 12 桁の半角数字ではありません: {oid!r}。"
            "入力欄で修正してください。"
        )

    # aind_id のバリデーション: AIND-D{5桁} 形式でなければ警告
    aid = (data.get("aind_id", "") or "").strip()
    if aid and not validate_aind_id(aid):
        st.warning(
            f"aind_id (AIND-D ID) が AIND-DXXXXX 形式ではありません: {aid!r}。"
            "xml:id として使用されないため、入力欄で修正してください。"
        )

    # sex
    sex = prompt_result.get("sex", "U")
    data["sex"] = sex if sex in ("M", "F", "U") else "U"

    # 生没年(年・確実性・注記・場所)
    for prefix in ("birth", "death"):
        for suffix in ("h", "cert", "note"):
            key = f"{prefix}_{suffix}"
            if key in prompt_result:
                data[key] = prompt_result[key]
        # 場所(ar / lat / id)
        for suffix in ("place_ar", "place_lat", "place_id"):
            key = f"{prefix}_{suffix}"
            if key in prompt_result:
                data[key] = prompt_result[key]
        # G暦は H から自動計算
        data[f"{prefix}_g"] = convert_h_to_g(data[f"{prefix}_h"])

    # 埋葬地(ar / lat / id)
    for suffix in ("place_ar", "place_lat", "place_id"):
        key = f"burial_{suffix}"
        if key in prompt_result:
            data[key] = prompt_result[key]

    # === _lat 欄の不正値の自動クリア(Gemini が時々座標や ID を入れるバグ対策) ===
    # 全ての _lat 欄(トップレベル + 配列内)を再帰的にチェック。
    # 不正パターン: 座標(小数点付き数値)/ Q-ID / 純粋数字 / TMP- / アラビア文字
    import re as _re
    _coord_pattern = _re.compile(r"^-?\d+\.\d+$")              # 21.43, -33.5 等
    _qid_pattern = _re.compile(r"^Q\d+$")                       # Q42004
    _tmp_pattern = _re.compile(r"^TMP-")                        # TMP-L-00001 等
    _digits_only = _re.compile(r"^\d+$")                        # 104515 等
    _arabic_pattern = _re.compile(r"[\u0600-\u06FF]")           # アラビア文字含む

    def _is_invalid_lat(val):
        if not val:
            return False
        v = val.strip()
        if not v:
            return False
        return bool(
            _coord_pattern.match(v) or
            _qid_pattern.match(v) or
            _tmp_pattern.match(v) or
            _digits_only.match(v) or
            _arabic_pattern.search(v)
        )

    cleared_lats = []

    # トップレベルの _lat 欄
    for fld in ("birth_place_lat", "death_place_lat", "burial_place_lat",
                "full_name_lat"):
        val = (data.get(fld, "") or "").strip()
        if _is_invalid_lat(val):
            cleared_lats.append((fld, val))
            data[fld] = ""

    # 配列内の _lat 欄
    array_lat_fields = {
        "teachers":     ["text_lat", "learn_place_lat"],
        "students":     ["text_lat", "teach_place_lat"],
        "activities":   ["place_lat"],
        "institutions": ["name_lat", "place_lat"],
        "offices":      ["name_lat", "place_lat"],
        "bio_events":   ["place_lat"],
        "nisbahs":      ["lat"],
        "laqabs":       ["lat"],
    }
    for section, fields in array_lat_fields.items():
        for idx, item in enumerate(data.get(section, []) or []):
            if not isinstance(item, dict):
                continue
            for fld in fields:
                val = (item.get(fld, "") or "").strip()
                if _is_invalid_lat(val):
                    cleared_lats.append((f"{section}[{idx}].{fld}", val))
                    item[fld] = ""

    if cleared_lats:
        msg = "翻字欄(_lat)に座標/ID/アラビア文字が入っていたため自動クリアしました:\n" + \
              "\n".join(f"  • {f} = {v!r} → 空欄" for f, v in cleared_lats[:10])
        if len(cleared_lats) > 10:
            msg += f"\n  …他 {len(cleared_lats) - 10} 件"
        st.warning(msg)

    # 法学派
    # 法学派(配列対応 v20.8)
    # Gemini が "madhhabs"(配列)または "madhhab_name"(文字列、旧仕様互換)を返す
    if "madhhabs" in prompt_result:
        apply_prompt_madhhab(data, prompt_result.get("madhhabs"))
    else:
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

    # 幻番号検疫 → ID-Master 照合 → TMP- プレースホルダー採番 の順で実行。
    # (1) 生成モデルが埋めた偽 TMP 番号をプレースホルダーに差し戻す。
    #     これをしないと _is_confirmed_id() が偽番号を確定扱いし、
    #     以降の照合・採番がスキップされてしまう(幻番号汚染の主因)。
    # (2) 差し戻した欄も含め、名前で ID-Master と正しく再照合。
    # (3) 残ったプレースホルダーに追記式で採番。
    # (0) 立項番号アーティファクト(訳頭の裸番号・連番=生没年)を先に処理(v20.11)
    scrub_entry_serial_artifacts(data, silent=True)
    # (0.5) جماعة 等の集合汎称エントリを除去(v20.11)
    drop_generic_collective_entries(data, silent=True)
    _quar = verify_and_quarantine_tmp_ids(data, silent=True)
    # (1.5) wd:Q / gn: の毒ID・別item流用を検疫(v20.11)
    verify_and_quarantine_wd_gn_ids(data, silent=True)
    try:
        st.session_state["_last_quarantine"] = _quar
    except Exception:
        pass
    apply_id_master_matching(data, silent=True)
    mark_unresolved_ids_in_data(data, silent=True)

    # === Streamlit session_state の同期 ===
    # text_input に key を指定している場合、Streamlit は session_state を
    # 「正」として表示する。data を更新しただけでは UI に反映されないため、
    # session_state にも同じ値を直接代入する。
    # (del だと再描画時に value 引数が使われない場合があるため、直接代入が確実)
    ui_keys_to_sync = {
        "birth_place_ar_input":  data.get("birth_place_ar", ""),
        "birth_place_lat_input": data.get("birth_place_lat", ""),
        "birth_place_id_input":  data.get("birth_place_id", ""),
        "death_place_ar_input":  data.get("death_place_ar", ""),
        "death_place_lat_input": data.get("death_place_lat", ""),
        "death_place_id_input":  data.get("death_place_id", ""),
        "burial_place_ar_input":  data.get("burial_place_ar", ""),
        "burial_place_lat_input": data.get("burial_place_lat", ""),
        "burial_place_id_input":  data.get("burial_place_id", ""),
    }
    for k, v in ui_keys_to_sync.items():
        st.session_state[k] = v


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

                    prompt = build_analyze_prompt(id_master_text, source_input)
                    if prompt is None:
                        st.error("解析プロンプト(prompt_analyze.txt)を読み込めません。app.py と同じディレクトリに配置してください。")
                        st.stop()
                    _resp_text, _model_name, _err = genai_generate_text(prompt)
                    if _err:
                        st.error(f"解析エラー: {_err}(モデル: {_model_name or '未取得'})")
                        st.stop()
                    raw = re.sub(r"```json|```", "", _resp_text).strip()
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

                        _q = st.session_state.get("_last_quarantine", [])
                        if _q:
                            st.warning(
                                f"⚠️ 生成モデルが返した {len(_q)} 件の TMP 番号を"
                                "検疫しました(ID-Master 未登録または別人流用)。"
                                "解析結果内で該当欄を確認してください。"
                            )
                        st.success("解析完了")
                        st.rerun()
                    else:
                        st.error("JSON抽出失敗")
                        st.text((_resp_text or "")[:400])
                except Exception as e:
                    st.error(f"エラー: {e}")
        else:
            st.warning("テキストを入力してください。")

    # ID 候補検索ツール(Task 3-2)
    with st.expander("🔎 ID 候補検索", expanded=False):
        st.caption(
            "アラビア語またはローマ字を入力すると、ID-Master から候補が"
            "表示されます。表示された ID をコピーして該当の入力欄に貼り付けてください。"
        )
        _lookup_records = load_id_master()
        lookup_q = st.text_input(
            "検索クエリ(2 文字以上)",
            value="",
            key="id_lookup_query",
            placeholder="例: ابن حجر / Ibn Ḥajar / القاهرة",
        )
        _lookup_cat = st.selectbox(
            "カテゴリで絞り込み(任意)",
            ["(すべて)", "Person", "Place", "Nisbah", "Institution",
             "Office", "Text", "Subject"],
            key="id_lookup_cat",
        )
        if lookup_q and len(lookup_q.strip()) >= 2 and _lookup_records:
            q_norm = normalize_arabic(lookup_q.strip())
            q_lower = lookup_q.strip().lower()
            cat_filter = "" if _lookup_cat == "(すべて)" else _lookup_cat
            matches = []
            for r in _lookup_records:
                if cat_filter and (r.get("Category", "") or "").strip() != cat_filter:
                    continue
                ar_norm = normalize_arabic(r.get("Arabic", ""))
                lat = (r.get("Latin", "") or "").lower()
                if q_norm and q_norm in ar_norm:
                    matches.append(r)
                elif q_lower and q_lower in lat:
                    matches.append(r)
                if len(matches) >= 20:
                    break
            if matches:
                st.markdown(f"**{len(matches)} 件ヒット(上位 20 件)**")
                for r in matches:
                    ar = r.get("Arabic", "")
                    lat = r.get("Latin", "")
                    id_val = r.get("ID", "")
                    cat = r.get("Category", "")
                    note = r.get("Note", "")
                    label = f"`{id_val}` — {ar}"
                    if lat:
                        label += f" ({lat})"
                    if cat:
                        label += f"  [{cat}]"
                    if note:
                        label += f" — {note}"
                    st.markdown(label)
            else:
                st.info("該当する候補がありません。")

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
_title_col, _ver_col = st.columns([4, 1])
_title_col.title("🌙 AINet-DB Researcher Pro")
_ver_col.markdown(
    f"<div style='text-align:right; padding-top:1.6rem;'>"
    f"<span style='font-size:0.9rem; color:#888;'>"
    f"{APP_VERSION} &nbsp; <span style='color:#aaa;'>{APP_VERSION_DATE}</span>"
    f"</span></div>",
    unsafe_allow_html=True,
)

# === ツールバー(翻字補完 / ID 照合 / 採番更新 / クリア) ===
clr_c1, clr_c2, clr_c3, clr_c5 = st.columns([0.40, 0.20, 0.20, 0.20])
with clr_c2:
    if st.button("↗ 翻字を一括補完", use_container_width=True,
                 help="空のラテン欄を IJMES 翻字で一括補完(既存の入力は保持)"):
        transliterate_empty_latin_fields(d)
with clr_c3:
    if st.button("🔄 ID再チェック", use_container_width=True,
                 help="幻番号を検疫 → ID-Master 照合 → 未確定欄(名前あり)に NEEDID 付与。"
                      "解析後に手でエントリを足したときに実行してください"):
        scrub_entry_serial_artifacts(d)     # 立項番号の混入を検出(v20.11)
        drop_generic_collective_entries(d)  # جماعة等の汎称エントリを除去(v20.11)
        verify_and_quarantine_tmp_ids(d)    # 幻番号を差し戻す
        verify_and_quarantine_wd_gn_ids(d)  # wd/gn 毒IDを検疫(v20.11)
        apply_id_master_matching(d)         # 名前一致で既存IDを付与
        mark_unresolved_ids_in_data(d)      # 残りにNEEDID(末尾でst.rerun)
with clr_c5:
    if st.button("🗑️ 入力をクリア", use_container_width=True,
                 help="入力した全データをクリアします"):
        st.session_state["_show_clear_confirm"] = True

# === 検疫レポート(直近の解析/ID再チェック。st.rerun 後も session_state から表示) v20.11 ===
_reports = st.session_state.get("_last_reports") or {}
_rep_counts = {
    "立項番号": len(_reports.get("serial") or []),
    "汎称語除去": len(_reports.get("generics") or []),
    "TMP検疫": len(_reports.get("tmp_quarantine") or []),
    "wd/gn検疫": len(_reports.get("wd_quarantine") or []),
    "wd/gn要照合": len(_reports.get("wd_review") or []),
}
if any(_rep_counts.values()):
    _summary = " / ".join(f"{k}: {v}件" for k, v in _rep_counts.items() if v)
    with st.expander(f"🛡️ 検疫レポート — {_summary}", expanded=True):
        for q in _reports.get("serial") or []:
            st.caption(f"• [立項番号] [{q.get('field')}] {q.get('msg')}")
        for q in _reports.get("generics") or []:
            st.caption(f"• [汎称語] [{q.get('section')}] 「{q.get('name')}」を除去")
        for q in _reports.get("tmp_quarantine") or []:
            st.caption(
                f"• [TMP検疫] [{q.get('section')}.{q.get('field')}] "
                f"「{q.get('name') or '(名前空欄)'}」← {q.get('bad_id')} を NEEDID/プレースホルダーに差し戻し"
            )
        for q in _reports.get("wd_quarantine") or []:
            _sug = f" → 候補: {q.get('suggest')}" if q.get("suggest") else ""
            st.caption(
                f"• [wd/gn検疫] [{q.get('section')}.{q.get('field')}] "
                f"「{q.get('name') or '(名前空欄)'}」← {q.get('bad_id')}({q.get('reason')}){_sug}"
            )
        for q in _reports.get("wd_review") or []:
            st.caption(
                f"• [要照合] [{q.get('section')}.{q.get('field')}] "
                f"「{q.get('name')}」= {q.get('id')} — WebSearch で実item名を照合してください"
            )
        if st.button("レポートを確認済みにする", key="_dismiss_reports"):
            st.session_state["_last_reports"] = {}
            st.rerun()

if st.session_state.get("_show_clear_confirm"):
    st.warning("⚠️ 全ての入力データがクリアされます。本当によろしいですか?")
    cc1, cc2, cc3 = st.columns([1, 1, 4])
    if cc1.button("✅ クリアする", type="primary"):
        st.session_state.data_v19 = json.loads(json.dumps(DEFAULT_DATA_V19))
        # UI 用の session_state キーも空文字列に同期(クリア)
        _ui_keys_to_clear = [
            "birth_place_ar_input", "birth_place_lat_input", "birth_place_id_input",
            "death_place_ar_input", "death_place_lat_input", "death_place_id_input",
            "burial_place_ar_input", "burial_place_lat_input", "burial_place_id_input",
        ]
        for _k in _ui_keys_to_clear:
            st.session_state[_k] = ""
        st.session_state["_show_clear_confirm"] = False
        st.rerun()
    if cc2.button("キャンセル"):
        st.session_state["_show_clear_confirm"] = False
        st.rerun()

st.header("2. Metadata Editor")

# --- 基本情報 ---
# AIND-D ID と 12 digits ID と Sex を同じ行に並べる
basic_c1, basic_c2, basic_c3 = st.columns([1, 1, 1])
d["aind_id"] = basic_c1.text_input(
    "AIND-D ID (xml:id)",
    d.get("aind_id", ""),
    placeholder="例: AIND-D00001",
    help="AIND-D{5桁}形式。テキストヘッダーから自動抽出されます。XMLでは xml:id として使用。",
)
d["original_id"] = basic_c2.text_input(
    "12 digits ID (@source)",
    d.get("original_id", ""),
    placeholder="例: 932540579843",
    help="12 桁の半角数字。テキストヘッダーから自動抽出されます。XMLでは source 属性として使用。",
)
sex_keys   = [s[0] for s in SEX_OPTIONS]
sex_labels = {s[0]: s[1] for s in SEX_OPTIONS}
cur_sex = d.get("sex", "M")
if cur_sex not in sex_keys:
    cur_sex = "M"
d["sex"] = basic_c3.selectbox(
    "Sex",
    sex_keys,
    format_func=lambda x: sex_labels[x],
    index=sex_keys.index(cur_sex),
    key="sex_select",
)

# 形式チェック警告
_warnings = []
if d.get("aind_id") and not validate_aind_id(d["aind_id"]):
    _warnings.append(
        f"AIND-D ID は AIND-DXXXXX 形式である必要があります(現在: {d['aind_id']!r})"
    )
if d.get("original_id") and not validate_original_id(d["original_id"]):
    _warnings.append(
        f"12 digits ID は 12 桁の半角数字である必要があります(現在: {d['original_id']!r})"
    )
for w in _warnings:
    st.warning(w)

d["full_name"]   = st.text_input("persName (Full Arabic)", d["full_name"])
d["name_only"]   = st.text_input("persName (Ism/Father/GF)", d["name_only"])

# ===================================================
# --- Nisbahs ---
# ===================================================
st.divider()
st.subheader("🏷️ Nisbahs")
nh = st.columns([1,1,1,0.3])
nh[0].caption("Arabic"); nh[1].caption("Latinized"); nh[2].caption("ID (TMP-N-)"); nh[3].caption("Del")
for i, item in enumerate(d.get("nisbahs",[])):
    if "ui_id" not in item: item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    r = st.columns([1,1,1,0.3])
    item["ar"]  = r[0].text_input("ar",  item.get("ar",""),  key=f"n_a_{uid}", label_visibility="collapsed")
    item["lat"] = r[1].text_input("lat", item.get("lat",""), key=f"n_l_{uid}", label_visibility="collapsed")
    item["id"]  = r[2].text_input("id",  item.get("id",""),  key=f"n_i_{uid}", label_visibility="collapsed", placeholder="TMP-N-00001")
    if r[3].button("❌", key=f"n_del_{uid}"):
        d["nisbahs"].pop(i); st.rerun()
if st.button("＋ add nisbah"):
    d["nisbahs"].append({"ui_id":str(uuid.uuid4()),"ar":"","lat":"","id":"TMP-N-00000"}); st.rerun()

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
st.subheader("📅 Birth / Death")

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
    d["birth_inference_note"] = st.text_input(
        "Birth Inference Note (推論根拠 / 英語推奨)",
        d.get("birth_inference_note", ""),
        placeholder='例: Inferred from "died at 50 in 900H".',
        help="原文に明示が無く文脈推論で記入した場合、その根拠を英語で記述。"
             '出力 XML には <note type="inference" xml:lang="en"> として現れる。',
    )
    # Birth Place
    bpc1, bpc2, bpc3 = st.columns([1, 1, 1])
    bpc1.caption("📍 Birth Place (Arabic)")
    bpc2.caption("Birth Place (Latin)")
    bpc3.caption("Birth Place ID (GeoNames / TMP-L-)")
    d["birth_place_ar"] = bpc1.text_input(
        "bpar", d.get("birth_place_ar", ""),
        key="birth_place_ar_input", label_visibility="collapsed",
        placeholder="例: مكة",
    )
    d["birth_place_lat"] = bpc2.text_input(
        "bplat", d.get("birth_place_lat", ""),
        key="birth_place_lat_input", label_visibility="collapsed",
        placeholder="例: Makka",
    )
    d["birth_place_id"] = bpc3.text_input(
        "bpid", d.get("birth_place_id", ""),
        key="birth_place_id_input", label_visibility="collapsed",
        placeholder="例: 104515 / TMP-L-00001",
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
    d["death_inference_note"] = st.text_input(
        "Death Inference Note (推論根拠 / 英語推奨)",
        d.get("death_inference_note", ""),
        placeholder='例: Inferred from "his son inherited his post in 905H".',
        help='出力 XML には <note type="inference" xml:lang="en"> として現れる。',
    )
    # Death Place(没地)
    dpc1, dpc2, dpc3 = st.columns([1, 1, 1])
    dpc1.caption("📍 Death Place (Arabic) — 没地")
    dpc2.caption("Death Place (Latin)")
    dpc3.caption("Death Place ID (GeoNames / TMP-L-)")
    d["death_place_ar"] = dpc1.text_input(
        "dpar", d.get("death_place_ar", ""),
        key="death_place_ar_input", label_visibility="collapsed",
        placeholder="例: القاهرة",
    )
    d["death_place_lat"] = dpc2.text_input(
        "dplat", d.get("death_place_lat", ""),
        key="death_place_lat_input", label_visibility="collapsed",
        placeholder="例: al-Qāhira",
    )
    d["death_place_id"] = dpc3.text_input(
        "dpid", d.get("death_place_id", ""),
        key="death_place_id_input", label_visibility="collapsed",
        placeholder="例: 360630 / TMP-L-00001",
    )
    # Burial Place(埋葬地)
    bupc1, bupc2, bupc3 = st.columns([1, 1, 1])
    bupc1.caption("⚰️ Burial Place (Arabic) — 埋葬地")
    bupc2.caption("Burial Place (Latin)")
    bupc3.caption("Burial Place ID (GeoNames / TMP-L-)")
    d["burial_place_ar"] = bupc1.text_input(
        "bupar", d.get("burial_place_ar", ""),
        key="burial_place_ar_input", label_visibility="collapsed",
        placeholder="例: تربة باب الوزير",
    )
    d["burial_place_lat"] = bupc2.text_input(
        "buplat", d.get("burial_place_lat", ""),
        key="burial_place_lat_input", label_visibility="collapsed",
        placeholder="例: Turbat Bāb al-Wazīr",
    )
    d["burial_place_id"] = bupc3.text_input(
        "bupid", d.get("burial_place_id", ""),
        key="burial_place_id_input", label_visibility="collapsed",
        placeholder="例: TMP-L-00001",
    )

# ===================================================
# --- Madhhab(複数対応 v20.8)---
# ===================================================
st.divider()
st.subheader("⚖️ Madhhab")
st.caption("法学派を時系列順に記録できます(最大 3 つ、転向した場合などに対応)。")

madhhab_keys = list(MADHHAB_DATA.keys())
madhhabs = d.get("madhhabs", [])

# 既存エントリ表示
for i, mitem in enumerate(madhhabs):
    if "ui_id" not in mitem:
        mitem["ui_id"] = str(uuid.uuid4())
    uid = mitem["ui_id"]

    # 順番セレクト + Madhhab + Wikidata ID + 削除ボタン
    mc_seq, mc_lat, mc_wid, mc_del = st.columns([1, 3, 3, 1])
    mc_seq.caption("Seq")
    mc_lat.caption("Madhhab")
    mc_wid.caption("Wikidata ID")
    mc_del.caption(" ")

    cur_seq = mitem.get("seq", i + 1)
    if cur_seq not in (1, 2, 3):
        cur_seq = i + 1 if (i + 1) in (1, 2, 3) else 1
    mitem["seq"] = mc_seq.selectbox(
        "seq", [1, 2, 3],
        index=[1, 2, 3].index(cur_seq),
        key=f"madhhab_seq_{uid}",
        label_visibility="collapsed",
    )

    cur_lat = mitem.get("lat", "Unknown / Other")
    def_idx = madhhab_keys.index(cur_lat) if cur_lat in madhhab_keys else madhhab_keys.index("Unknown / Other")
    selected_m = mc_lat.selectbox(
        "Madhhab", options=madhhab_keys, index=def_idx,
        key=f"madhhab_lat_{uid}", label_visibility="collapsed",
    )
    wikidata_id = MADHHAB_DATA[selected_m]
    mc_wid.text_input(
        "Wikidata ID", value=wikidata_id, disabled=True,
        key=f"madhhab_wid_{uid}", label_visibility="collapsed",
    )

    # 削除ボタン
    if mc_del.button("❌", key=f"madhhab_del_{uid}"):
        d["madhhabs"].pop(i)
        st.rerun()

    # Custom 入力(Unknown / Other のとき)
    if selected_m == "Unknown / Other":
        uo1, uo2 = st.columns(2)
        custom_name = uo1.text_input(
            "Madhhab name (free text)",
            value=mitem.get("custom_name", ""),
            key=f"madhhab_custom_name_{uid}",
        )
        custom_id = uo2.text_input(
            "Madhhab ID (Q / TMP-)",
            value=mitem.get("custom_id", ""),
            key=f"madhhab_custom_id_{uid}",
        )
        mitem.update({
            "lat": selected_m, "id": "",
            "custom_name": custom_name, "custom_id": custom_id,
        })
    else:
        mitem.update({
            "lat": selected_m, "id": wikidata_id,
            "custom_name": "", "custom_id": "",
        })

# 追加ボタン(最大 3 つまで)
if len(madhhabs) < 3:
    if st.button("＋ Madhhab を追加", key="add_madhhab"):
        # 次のseq番号を計算
        used_seqs = {m.get("seq", 0) for m in d.get("madhhabs", [])}
        next_seq = 1
        for n in (1, 2, 3):
            if n not in used_seqs:
                next_seq = n
                break
        d.setdefault("madhhabs", []).append({
            "seq": next_seq,
            "lat": "Unknown / Other",
            "id": "",
            "custom_name": "",
            "custom_id": "",
            "ui_id": str(uuid.uuid4()),
        })
        st.rerun()
else:
    st.caption("(Madhhab は最大 3 つまでです)")

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
        ct = item.get("type","residence")
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
        item["inference_note"] = st.text_input(
            "Inference Note (推論根拠 / 英語推奨)",
            item.get("inference_note", ""),
            key=f"a_inf_{uid}",
            placeholder='例: Inferred from "تربة أبيهما" within the Khānqāh of Faraj b. Barqūq.',
            help='出力 XML には <note type="inference" xml:lang="en"> として現れる。',
        )
    st.markdown("---")
if st.button("＋ add activity"):
    d["activities"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["activities"])+1,
        "place_ar":"","place_lat":"","type":"residence","id":"",
        "date_h":"","date_cert":"","date_note":"",
        "inference_note":""}); st.rerun()

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
        item["inference_note"] = st.text_input(
            "Inference Note (推論根拠 / 英語推奨)",
            item.get("inference_note", ""),
            key=f"o_inf_{uid}",
            placeholder="例: Inferred from a colophon referring to him as nāʾib al-qāḍī.",
            help='出力 XML には <note type="inference" xml:lang="en"> として現れる。',
        )
    st.markdown("---")
if st.button("＋ add office"):
    d["offices"].append({"ui_id":str(uuid.uuid4()),"seq":len(d["offices"])+1,
        "name_ar":"","name_lat":"","id":"TMP-O-00000",
        "place_ar":"","place_lat":"","place_id":"",
        "inst_name":"","inst_id":"","appoint_date":"","retire_date":"",
        "inference_note":""}); st.rerun()

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

        # 4行目: Inference Note(推論根拠)
        item["inference_note"] = st.text_input(
            "Inference Note (推論根拠 / 英語推奨)",
            item.get("inference_note", ""),
            key=f"be_inf_{uid}",
            placeholder="例: Inferred from cross-reference to his student's biography.",
            help='出力 XML には <note type="inference" xml:lang="en"> として現れる。',
        )

    st.markdown("---")

if st.button("＋ add biographical event"):
    d["bio_events"].append({
        "ui_id":          str(uuid.uuid4()),
        "seq":            len(d["bio_events"]) + 1,
        "type":           "",
        "date_h":         "",
        "date_cert":      "",
        "date_note":      "",
        "place_ar":       "",
        "place_lat":      "",
        "place_id":       "",
        "description":    "",
        "inference_note": "",
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
# --- 作業者情報 (respStmt) ---
# ===================================================
st.divider()
st.subheader("🖊️ 作業者情報 (respStmt)")
st.caption("この person 要素の編集に関わった担当者を記録します。複数の作業履歴を並列で記録可能。")

resp_stmts = d.get("resp_stmts", [])
for i, item in enumerate(resp_stmts):
    if "ui_id" not in item:
        item["ui_id"] = str(uuid.uuid4())
    uid = item["ui_id"]
    with st.container():
        rc = st.columns([1.2, 1.5, 1, 0.3])
        rc[0].caption("役割")
        rc[1].caption("作業者名")
        rc[2].caption("日付 (YYYY-MM-DD)")

        cur_role = item.get("role", "初版作成")
        if cur_role not in RESP_ROLE_OPTIONS:
            cur_role = "その他"
        item["role"] = rc[0].selectbox(
            "role", RESP_ROLE_OPTIONS,
            index=RESP_ROLE_OPTIONS.index(cur_role),
            key=f"rs_role_{uid}", label_visibility="collapsed",
        )
        # 既存値が選択肢に無ければ末尾に追加(レガシーデータ保持)
        cur_name = item.get("name", "")
        _person_opts = list(RESP_PERSON_OPTIONS)
        if cur_name and cur_name not in _person_opts:
            _person_opts.append(cur_name)
        _idx = _person_opts.index(cur_name) if cur_name in _person_opts else 0
        item["name"] = rc[1].selectbox(
            "name", _person_opts,
            index=_idx,
            key=f"rs_name_{uid}", label_visibility="collapsed",
        )
        item["date"] = rc[2].text_input(
            "date", item.get("date", _date.today().isoformat()),
            key=f"rs_date_{uid}", label_visibility="collapsed",
            placeholder="YYYY-MM-DD",
        )
        if rc[3].button("❌", key=f"rs_del_{uid}"):
            d["resp_stmts"].pop(i); st.rerun()
    st.markdown("---")

if st.button("＋ add respStmt"):
    d["resp_stmts"].append({
        "ui_id": str(uuid.uuid4()),
        "role":  "初版作成",
        "name":  RESP_PERSON_OPTIONS[0],
        "date":  _date.today().isoformat(),
    })
    st.rerun()

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
    """法学派(複数対応)とスーフィー教団を出力する。

    madhhabs 配列を seq 順にソートして <affiliation type="madhhab" n="..."> を生成。
    旧 madhhab(単一)もフォールバック対応(migrate 前のデータ用)。
    """
    # 新形式: madhhabs(配列)
    madhhabs = d.get("madhhabs", [])
    # 旧形式: madhhab(単一)へのフォールバック(migrate 前データ用)
    if not madhhabs and isinstance(d.get("madhhab"), dict):
        old_m = d["madhhab"]
        lat = old_m.get("lat", "")
        if lat and not (lat == "Unknown / Other" and not old_m.get("custom_name", "").strip()):
            madhhabs = [{
                "seq": 1, "lat": lat,
                "id": old_m.get("id", ""),
                "custom_name": old_m.get("custom_name", ""),
                "custom_id": old_m.get("custom_id", ""),
            }]

    # seq 順にソート
    sorted_madhhabs = sorted(madhhabs, key=lambda m: m.get("seq", 99))

    for m in sorted_madhhabs:
        if not isinstance(m, dict):
            continue
        lat = m.get("lat", "")
        seq = m.get("seq", 1)
        n_attr = f' n="{seq}"' if len(sorted_madhhabs) > 1 else ""

        if lat == "Unknown / Other":
            cn = m.get("custom_name", "")
            ci = m.get("custom_id", "")
            if cn or ci:
                ref_attr = f' ref="{fr(ci)}"' if ci else ""
                x.append(
                    f'    <affiliation type="madhhab"{n_attr}{ref_attr}>'
                    f'{escape_xml(cn)}</affiliation>'
                )
        elif m.get("id"):
            # "Shafi'i (シャーフィイー派)" → "Shafi'i"(日本語注釈は除去)
            madhhab_label = lat.split(" (")[0]
            # id は既に "wd:Q..." 形式 or "Q..." 形式の両方をサポート
            id_val = m["id"]
            ref_val = id_val if id_val.startswith("wd:") else f"wd:{id_val}"
            x.append(
                f'    <affiliation type="madhhab"{n_attr} ref="{ref_val}">'
                f'{escape_xml(madhhab_label)}</affiliation>'
            )

    sufi = d.get("sufi_order", {})
    if sufi.get("name"):
        ref_attr = f' ref="{fr(sufi.get("id",""))}"' if sufi.get("id") else ""
        x.append(
            f'    <affiliation type="sufiOrder"{ref_attr}>'
            f'{escape_xml(sufi["name"])}</affiliation>'
        )


def _build_placename_lines(place_ar, place_lat, place_id, place_type=None):
    """<placeName> 行を生成。place_type を指定すると type 属性を付与。
    地名(ar)・翻字(lat)・ID のいずれかが揃っていれば出力。両方空なら空リスト。
    """
    lines = []
    has_any = bool((place_ar or "").strip() or (place_lat or "").strip() or (place_id or "").strip())
    if not has_any:
        return lines

    type_attr = f' type="{place_type}"' if place_type else ""
    ref_attr = f' ref="{fr(place_id)}"' if (place_id or "").strip() else ""

    if (place_ar or "").strip():
        lines.append(
            f'        <placeName xml:lang="ar"{type_attr}{ref_attr}>'
            f'{escape_xml(place_ar)}</placeName>'
        )
    if (place_lat or "").strip():
        lines.append(
            f'        <placeName xml:lang="ar-Latn"{type_attr}{ref_attr}>'
            f'{escape_xml(place_lat)}</placeName>'
        )
    # ar も lat も空で ID だけある場合、空 placeName で ID を保持
    if not (place_ar or "").strip() and not (place_lat or "").strip() and (place_id or "").strip():
        lines.append(
            f'        <placeName{type_attr}{ref_attr}/>'
        )
    return lines


def _build_date_event(elem_name, year_h, cert, note, inference_note="",
                     place_ar="", place_lat="", place_id="",
                     burial_place_ar="", burial_place_lat="", burial_place_id=""):
    """生没年・場所・埋葬地を一括して <birth>/<death> 要素に出力する。
    日付がなくても、場所情報があれば要素を出力する。
    burial_place_* は death の場合のみ意味を持つ。
    """
    has_year = bool((year_h or "").strip())
    has_place = bool((place_ar or "").strip() or (place_lat or "").strip() or (place_id or "").strip())
    has_burial = bool(
        (burial_place_ar or "").strip()
        or (burial_place_lat or "").strip()
        or (burial_place_id or "").strip()
    )
    if not has_year and not has_place and not has_burial:
        return None

    # 属性: when-custom / when / cert
    attrs = ""
    if has_year:
        year_h_padded = pad_year_attr(year_h)
        year_g = convert_h_to_g(year_h)
        attrs += f' when-custom="{escape_xml_attr(year_h_padded)}"'
        if year_g:
            attrs += f' when="{year_g}"'
        if cert:
            attrs += f' cert="{cert}"'

    # 子要素: placeName(死亡地・出生地) / placeName(埋葬地、type="burial") / note / inference_note
    inner_lines = []

    # 1. 場所(death の場合は没地、birth の場合は出生地)→ type は付けない(birth/death要素自体で文脈が明確)
    inner_lines.extend(
        _build_placename_lines(place_ar, place_lat, place_id, place_type=None)
    )
    # 2. 埋葬地(death のみ)
    if has_burial:
        inner_lines.extend(
            _build_placename_lines(
                burial_place_ar, burial_place_lat, burial_place_id,
                place_type="burial",
            )
        )
    # 3. note
    if note:
        inner_lines.append(
            f'        <note xml:lang="{detect_lang(note)}">{escape_xml(note)}</note>'
        )
    # 4. inference_note
    if inference_note:
        inner_lines.append(
            f'        <note type="inference" xml:lang="{detect_lang(inference_note)}">'
            f'{escape_xml(inference_note)}</note>'
        )

    if inner_lines:
        return (
            f'    <{elem_name}{attrs}>\n'
            + "\n".join(inner_lines) + "\n"
            f'    </{elem_name}>'
        )
    # 子要素がなく、属性だけある場合は自己閉じタグ
    return f'    <{elem_name}{attrs}/>'


def build_birth_death(x, d):
    b = _build_date_event(
        "birth",
        d.get("birth_h", ""), d.get("birth_cert", ""),
        d.get("birth_note", ""), d.get("birth_inference_note", ""),
        place_ar=d.get("birth_place_ar", ""),
        place_lat=d.get("birth_place_lat", ""),
        place_id=d.get("birth_place_id", ""),
    )
    if b:
        x.append(b)
    de = _build_date_event(
        "death",
        d.get("death_h", ""), d.get("death_cert", ""),
        d.get("death_note", ""), d.get("death_inference_note", ""),
        place_ar=d.get("death_place_ar", ""),
        place_lat=d.get("death_place_lat", ""),
        place_id=d.get("death_place_id", ""),
        burial_place_ar=d.get("burial_place_ar", ""),
        burial_place_lat=d.get("burial_place_lat", ""),
        burial_place_id=d.get("burial_place_id", ""),
    )
    if de:
        x.append(de)


def _method_field_label_lang(entry):
    """ID-Master エントリから使用するラベルと xml:lang を決定。
    Arabic があれば ar、なければ Latin → ar-Latn、それも無ければ ja。"""
    if entry.get("ar"):
        return entry["ar"], "ar"
    if entry.get("lat"):
        return entry["lat"], "ar-Latn"
    if entry.get("ja"):
        return entry["ja"], "ja"
    return "", "ar"


_FAMILY_RELATION_SUBTYPES = {
    "father", "mother", "son", "daughter", "brother", "sister",
    "spouse", "grandfather", "grandmother",
    "uncle", "aunt", "cousin", "siblings_child",
    "ancestor", "descendant",
}


def assign_n_attribute(relation_subtype, idx):
    """relation の n属性を分野別に振る:
    - teacher / student: 連番(必ず n を付ける)
    - 親族関係: n属性なし
    - 社会的関係: idx が真であれば n を付ける(必要に応じて)
    """
    if relation_subtype in ("teacher", "student"):
        return f' n="{idx}"' if idx else ""
    if relation_subtype in _FAMILY_RELATION_SUBTYPES:
        return ""
    # 社会的関係 / その他
    return f' n="{idx}"' if idx else ""


def _build_method_field_desc(method_id, field_id, method_dict, field_dict):
    lines = []
    for kind, val, dct in [("method", method_id, method_dict),
                            ("field",  field_id,  field_dict)]:
        if not val:
            continue
        if val in dct:
            label, lang = _method_field_label_lang(dct[val])
            if label:
                lines.append(
                    f'            <desc type="{kind}" ref="{fr(val)}" xml:lang="{lang}">'
                    f'{escape_xml(label)}</desc>'
                )
            else:
                # ラベル空 — ref のみの空要素にも xml:lang を付与
                lines.append(
                    f'            <desc type="{kind}" ref="{fr(val)}" xml:lang="ar"/>'
                )
        elif is_id_format(val):
            # ID 形式だが辞書に無い(古い ID 等)→ ref のみ・xml:lang="ar"
            lines.append(
                f'            <desc type="{kind}" ref="{fr(val)}" xml:lang="ar"/>'
            )
        else:
            # 自由記述 → 言語を推定して付与
            lines.append(
                f'            <desc type="{kind}" xml:lang="{detect_lang(val)}">'
                f'{escape_xml(val)}</desc>'
            )
    return lines


def _build_teacher_relation(t, aind_id, method_dict, field_dict):
    n_attr = assign_n_attribute("teacher", t.get("seq", ""))
    lines = [
        f'        <relation type="personal" subtype="teacher"{n_attr} '
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
            lines.append(f'            <bibl xml:lang="ar-Latn"{ref_attr}>{escape_xml(t["text_lat"])}</bibl>')
    if t.get("learn_date") or t.get("learn_place_ar"):
        da = f' when="{escape_xml_attr(pad_year_attr(t["learn_date"]))}"' if t.get("learn_date") else ""
        place_ref = fr(t.get("learn_place_id", ""))
        place_ref_attr = f' ref="{place_ref}"' if place_ref else ""
        if t.get("learn_place_ar"):
            lines.append(
                f'            <event type="learning"{da}>'
                f'<placeName{place_ref_attr}>{escape_xml(t["learn_place_ar"])}</placeName>'
                f'</event>'
            )
        elif place_ref:
            # 地名表記なし・参照のみ → 空の placeName で ref を保持
            lines.append(
                f'            <event type="learning"{da}>'
                f'<placeName{place_ref_attr}/>'
                f'</event>'
            )
        else:
            lines.append(f'            <event type="learning"{da}/>')
    lines.append('        </relation>')
    return lines


def _build_student_relation(s, aind_id, method_dict, field_dict):
    n_attr = assign_n_attribute("student", s.get("seq", ""))
    lines = [
        f'        <relation type="personal" subtype="student"{n_attr} '
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
            lines.append(f'            <bibl xml:lang="ar-Latn"{ref_attr}>{escape_xml(s["text_lat"])}</bibl>')
    if s.get("teach_date") or s.get("teach_place_ar"):
        da = f' when="{escape_xml_attr(pad_year_attr(s["teach_date"]))}"' if s.get("teach_date") else ""
        place_ref = fr(s.get("teach_place_id", ""))
        place_ref_attr = f' ref="{place_ref}"' if place_ref else ""
        if s.get("teach_place_ar"):
            lines.append(
                f'            <event type="teaching"{da}>'
                f'<placeName{place_ref_attr}>{escape_xml(s["teach_place_ar"])}</placeName>'
                f'</event>'
            )
        elif place_ref:
            lines.append(
                f'            <event type="teaching"{da}>'
                f'<placeName{place_ref_attr}/>'
                f'</event>'
            )
        else:
            lines.append(f'            <event type="teaching"{da}/>')
    lines.append('        </relation>')
    return lines


def _build_family_relation(fam, aind_id):
    rel      = fam.get("relation", "other")
    rel_note = (fam.get("relation_note", "") or "").strip()
    fam_ref  = fr(fam.get("id", ""))
    fam_name = fam.get("name", "")
    fam_lang = detect_lang(fam_name) if fam_name else "ar"

    # 非標準の家族関係: subtype="other" + <desc type="relationship_type"> 構造
    # 標準: subtype は relation 値そのまま
    if rel == "other" and rel_note:
        inner = (
            f'<desc type="relationship_type" xml:lang="{detect_lang(rel_note)}">'
            f'{escape_xml(rel_note)}</desc>'
            f'<desc xml:lang="{fam_lang}">{escape_xml(fam_name)}</desc>'
        )
        subtype_value = "other"
    else:
        inner = f'<desc xml:lang="{fam_lang}">{escape_xml(fam_name)}</desc>'
        subtype_value = rel

    # 親族関係は subtype を問わず n 属性なし(spec 1-12)
    return (
        f'        <relation type="personal" subtype="{escape_xml_attr(subtype_value)}" '
        f'active="{fam_ref}" passive="#{aind_id}">'
        f'{inner}</relation>'
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
        inner_parts.append(
            f'<desc xml:lang="{detect_lang(sr["person_name"])}">'
            f'{escape_xml(sr["person_name"])}</desc>'
        )
    if sr.get("description"):
        inner_parts.append(
            f'<note xml:lang="{detect_lang(sr["description"])}">'
            f'{escape_xml(sr["description"])}</note>'
        )
    if not inner_parts:
        return None
    n_attr = assign_n_attribute(subtype, sr.get("seq", ""))
    return (
        f'        <relation type="personal" subtype="{escape_xml_attr(subtype)}"{n_attr} '
        f'active="{person_ref}" passive="#{aind_id}">'
        + "".join(inner_parts) +
        f'</relation>'
    )


def build_list_relation(x, d, method_dict, field_dict):
    # 関係の active/passive 参照には派生 xml:id を使う。
    # original_id が 12 桁でない場合は空欄(プレビュー時の暫定状態)。
    aind_id = get_xml_id(d) or ""
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
    date_attr = f' when-custom="{escape_xml_attr(pad_year_attr(date_h))}"' if date_h else ""
    cert      = a.get("date_cert", "")
    cert_attr = f' cert="{cert}"' if cert else ""

    place_inner = f'<placeName{ref_att}>{escape_xml(a["place_ar"])}</placeName>'
    note = a.get("date_note", "")
    note_inner = (
        f'<note xml:lang="{detect_lang(note)}">{escape_xml(note)}</note>'
        if note else ""
    )
    inf = a.get("inference_note", "")
    inf_inner = (
        f'<note type="inference" xml:lang="{detect_lang(inf)}">{escape_xml(inf)}</note>'
        if inf else ""
    )

    # 生没情報は <birth>/<death> 要素で記録するため、activity の born/died は
    # 廃止済み(migrate_activity で other に変換)。
    # 旧 "reside" は migrate_activity で "residence" にリネーム済み。
    type_attrs = build_event_attrs(atype)
    return (
        f'    <event {type_attrs}{n_attr}{date_attr}{cert_attr}>'
        f'{place_inner}'
        f'{note_inner}'
        f'{inf_inner}'
        f'</event>'
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
        if nl: x.append(f'        <orgName xml:lang="ar-Latn">{escape_xml(nl)}</orgName>')
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
            x.append(f'        <label xml:lang="ar-Latn">{escape_xml(off["name_lat"])}</label>')
        if off.get("appoint_date"):
            x.append(f'        <date type="appointment" when-custom="{escape_xml_attr(pad_year_attr(off["appoint_date"]))}"/>')
        if off.get("retire_date"):
            x.append(f'        <date type="retirement" when-custom="{escape_xml_attr(pad_year_attr(off["retire_date"]))}"/>')
        if off.get("place_ar") or off.get("place_id"):
            pr = fr(off.get("place_id", ""))
            ref_p = f' ref="{pr}"' if pr else ""
            x.append(f'        <placeName{ref_p}>{escape_xml(off.get("place_ar",""))}</placeName>')
        if off.get("inst_name") or off.get("inst_id"):
            ir = fr(off.get("inst_id", ""))
            ref_i = f' ref="{ir}"' if ir else ""
            x.append(f'        <orgName{ref_i}>{escape_xml(off.get("inst_name",""))}</orgName>')
        if off.get("inference_note"):
            inf = off["inference_note"]
            x.append(
                f'        <note type="inference" xml:lang="{detect_lang(inf)}">'
                f'{escape_xml(inf)}</note>'
            )
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
        date_attr = f' when-custom="{escape_xml_attr(pad_year_attr(date_h))}"' if date_h else ""
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
        if be.get("inference_note"):
            inf = be["inference_note"]
            inner_lines.append(
                f'        <note type="inference" xml:lang="{detect_lang(inf)}">'
                f'{escape_xml(inf)}</note>'
            )

        if inner_lines:
            type_attrs = build_event_attrs(be_type)
            x.append(f'    <event {type_attrs}{n_attr}{date_attr}{cert_attr}>')
            x.extend(inner_lines)
            x.append('    </event>')


def build_resp_stmts(x, d):
    """<respStmt> を末尾に並列配置(複数可)。空欄エントリはスキップ。"""
    for r in d.get("resp_stmts", []):
        role = (r.get("role", "") or "").strip()
        name = (r.get("name", "") or "").strip()
        date_str = (r.get("date", "") or "").strip()
        if not (role or name or date_str):
            continue
        x.append('    <respStmt>')
        if role:
            x.append(f'        <resp xml:lang="ja">{escape_xml(role)}</resp>')
        if name:
            x.append(f'        <persName>{escape_xml(name)}</persName>')
        if date_str:
            x.append(f'        <date when="{escape_xml_attr(date_str)}"/>')
        x.append('    </respStmt>')


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

    xml_id = get_xml_id(d) or ""
    source_id = (d.get("original_id", "") or "").strip()
    source_attr = f' source="{escape_xml_attr(source_id)}"' if source_id else ""
    x.append(
        f'<person xml:id="{escape_xml_attr(xml_id)}"{source_attr}>'
    )
    # アプリのバージョン情報を XML コメントとして埋め込む
    # (TEI 仕様を壊さず、データ生成元が追跡可能)
    from datetime import datetime as _dt, timezone as _tz
    _generated_at = _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    x.append(
        f'    <!-- generated by AINet-DB Researcher Pro '
        f'{APP_VERSION} ({APP_VERSION_DATE}) at {_generated_at} -->'
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
    build_resp_stmts(x, d)

    x.append("</person>")
    xml_out = "\n".join(x)
    # D-3裁定(2026-07-31): AIND 優先人物の参照に corresp="wd:..." を自動付与
    for _aind, _wd in AIND_CORRESP.items():
        for _attr in ("active", "passive", "ref"):
            xml_out = xml_out.replace(
                f'{_attr}="#{_aind}"',
                f'{_attr}="#{_aind}" corresp="{_wd}"',
            )
    return xml_out

xml_str = build_xml(d)

# NEEDID 残留チェック: 校閲での ID 付与が未完の欄があれば警告。
_needid_count = xml_str.count(NEEDID_MARKER)
if _needid_count:
    st.warning(
        f"⚠️ この XML には未付与の ID マーカー（{NEEDID_MARKER}）が {_needid_count} 件残っています。"
        "校閲工程で AIND 同定または新規 TMP 付与を行ってください（`grep NEEDID` で該当箇所を確認できます）。"
    )

st.code(xml_str, language="xml")

# === ダウンロード / コピー ボタン ===
# ファイル名は AIND-D ID と 12 digits ID から生成: AIND-D{5桁}_{12桁}.xml
# どちらか欠けている場合は片方だけ、両方欠ければボタン無効。
# {12桁}.xml にフォールバック。
_download_filename = get_xml_filename(d)
btn_col1, btn_col2 = st.columns([1, 1])

with btn_col1:
    if _download_filename:
        st.download_button(
            label=f"📥 XMLをダウンロード ({_download_filename})",
            data=xml_str,
            file_name=_download_filename,
            mime="application/xml",
            use_container_width=True,
            help="現在の人物の XML をファイルとしてダウンロードします。"
                 "ファイル名は AIND-D ID + 12桁ID から生成されます。",
        )
    else:
        st.button(
            "📥 XMLをダウンロード",
            use_container_width=True,
            disabled=True,
            help="ダウンロードには 12桁の Source ID が必要です。",
        )

with btn_col2:
    # クリップボードコピーボタン(JavaScriptで実装)
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
        font-size:1rem; cursor:pointer; width:100%;
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

# DATASET_SHEET_ID と get_gspread_client は load_progress_label_mapping より前に
# 定義する必要があるため、ファイル上部に移動済み(行 192 付近)。

# === スプレッドシートの実際の列構成 ===
# A: 行数(触らない / 関数式が入っているかもしれない)
# B: 担当者(アプリが書き込む)
# C: AIND-D ID(触らない / 手動記入領域)
# D: 12digitsID(触らない / 手動記入領域・検索キー)
# E: persName (Full Arabic)(アプリが書き込む)
# F: persName (Ism/Father/GF)(アプリが書き込む)
# G: Birth (H)(アプリが書き込む)
# H: Death (H)(アプリが書き込む)
# I: Madhhab(アプリが書き込む)
# J: Editors' Notes(アプリが書き込む)

# 表示用ヘッダー(プレビュー表で使用)
SHEET_COLUMNS = [
    "担当者",                       # B列
    "persName (Full Arabic)",       # E列
    "persName (Ism/Father/GF)",     # F列
    "Birth (H)",                    # G列
    "Death (H)",                    # H列
    "Madhhab",                      # I列
    "Editors' Notes",               # J列
]

# 列番号(1-indexed)とプレビュー上の対応
SHEET_COL_ID12 = 4   # D列: 12digitsID(検索キー)
SHEET_COL_AIND_ID = 3  # C列: AIND-D ID(触らない)
SHEET_COL_ASSIGNEE = 2  # B列: 担当者


def build_row_b(data, assignee):
    """B列(担当者)に書き込む 1セル分のデータを返す"""
    return [assignee]


def build_row_ej(data):
    """E〜J列(persName以降)に書き込む 6セル分のデータを返す。
    C列(AIND-D ID)と D列(12 digits ID)は触らないため含めない。
    """
    # Madhhab表示文字列(複数 madhhab に対応 v20.8)
    # 配列 madhhabs を seq 順にソートして "Shafi'i → Hanbali" のように連結
    madhhab_strs = []
    madhhabs = data.get("madhhabs", [])
    # 旧形式 madhhab フォールバック
    if not madhhabs and isinstance(data.get("madhhab"), dict):
        old_m = data["madhhab"]
        if old_m.get("lat") and old_m.get("lat") != "Unknown / Other":
            madhhabs = [{"seq": 1, "lat": old_m["lat"], "custom_name": old_m.get("custom_name", "")}]
        elif old_m.get("custom_name", "").strip():
            madhhabs = [{"seq": 1, "lat": "Unknown / Other", "custom_name": old_m["custom_name"]}]

    for m in sorted(madhhabs, key=lambda x: x.get("seq", 99)):
        if not isinstance(m, dict):
            continue
        if m.get("lat") == "Unknown / Other":
            name = m.get("custom_name", "")
        else:
            # "Shafi'i (シャーフィイー派)" → "Shafi'i"
            name = (m.get("lat", "") or "").split(" (")[0]
        if name:
            madhhab_strs.append(name)
    madhhab_str = " → ".join(madhhab_strs)  # 時系列順なので "→" で繋ぐ

    return [
        data.get("full_name", ""),         # E: persName (Full Arabic)
        data.get("name_only", ""),         # F: persName (Ism/Father/GF)
        data.get("birth_h", ""),           # G: Birth (H)
        data.get("death_h", ""),           # H: Death (H)
        madhhab_str,                       # I: Madhhab
        data.get("editors_notes", ""),     # J: Editors' Notes
    ]


def build_preview_row(data, assignee):
    """プレビュー表示用: B列と E〜J列のデータを1行にまとめる"""
    return build_row_b(data, assignee) + build_row_ej(data)


def find_row_by_id(worksheet, original_id):
    """D列(12digitsID)で original_id を検索し、行番号を返す。
    見つからなければ None。
    """
    try:
        col_values = worksheet.col_values(SHEET_COL_ID12)  # D列
        for idx, val in enumerate(col_values):
            if val.strip() == str(original_id).strip():
                return idx + 1  # gspreadは1-indexed
        return None
    except Exception:
        return None


def find_first_empty_row(worksheet):
    """D列(12digitsID)が空で、かつそれより上のどこかにデータがある行を探して
    その行番号を返す(=末尾の空行ではなく、最初の空き行)。
    シート全体が空ならヘッダーの次行(2)を返す。
    """
    try:
        col_values = worksheet.col_values(SHEET_COL_ID12)
        # 1行目はヘッダー
        for idx, val in enumerate(col_values[1:], start=2):
            if not val.strip():
                return idx
        # 全行に値があれば、シートの次の行
        return len(col_values) + 1
    except Exception:
        return None


# --- UI ---
st.caption(
    "スプレッドシートに書き込むには、Streamlit Cloud の Secrets に "
    "`[gcp_service_account]` セクションでService AccountのJSONを登録し、"
    "スプレッドシートをそのアカウントのメールアドレスに共有してください。"
)

# respStmt の最初のエントリの作業者名を「初版作成者」として使用
# (B列に書き込む担当者名)
def get_assignee_from_resp_stmts(data):
    """resp_stmts の最初のエントリの作業者名(name)を返す。
    空 or 未設定なら空文字列。
    """
    resp_stmts = data.get("resp_stmts", []) or []
    if not resp_stmts:
        return ""
    first = resp_stmts[0]
    if not isinstance(first, dict):
        return ""
    return (first.get("name", "") or "").strip()

assignee = get_assignee_from_resp_stmts(d)

# 担当者の表示(編集不可、respStmt から自動取得)
if assignee:
    st.success(
        f"📌 **担当者(初版作成者): `{assignee}`** "
        f"(respStmt セクションの最初のエントリより自動取得)"
    )
else:
    st.warning(
        "⚠️ respStmt セクションが空です。"
        "スプレッドシート保存には、respStmt セクション(画面下部)で"
        "「初版作成」の担当者を追加してください。"
    )

col_prev, col_save = st.columns([2, 1])

# プレビュー
with col_prev:
    st.markdown("**書き込み内容プレビュー(B列 + E〜J列)**")
    preview_row = build_preview_row(d, assignee)
    preview_df  = dict(zip(SHEET_COLUMNS, preview_row))
    st.table(preview_df)
    st.caption("※ C列(AIND-D ID)と D列(12 digits ID)は変更されません。")

# 保存ボタン
with col_save:
    st.markdown("&nbsp;", unsafe_allow_html=True)  # 縦位置調整
    if st.button("📤 スプレッドシートに保存", use_container_width=True, type="primary"):
        if not assignee:
            st.error(
                "respStmt セクション(画面下部)で担当者(初版作成者)を"
                "追加してから保存してください。"
            )
        elif not d.get("original_id"):
            st.error("Source ID (12digitsID) が空です。入力してから保存してください。")
        else:
            try:
                gc = get_gspread_client()
                sh = gc.open_by_key(DATASET_SHEET_ID)
                ws = sh.get_worksheet(0)  # 最初のシート

                row_b  = build_row_b(d, assignee)   # 担当者(B列)
                row_ej = build_row_ej(d)            # persName 以降(E〜J列)

                row_num = find_row_by_id(ws, d["original_id"])

                if row_num:
                    # 既存行を更新: B列と E〜J列のみ
                    # AIND-D ID(C列)と 12 digits ID(D列)は触らない
                    # RAW にしておくと先頭ゼロや AIND-D 形式の文字列が
                    # 数値に勝手変換されない(これらは触らないが念のため)
                    ws.update(
                        f"B{row_num}",
                        [row_b],
                        value_input_option="RAW",
                    )
                    ws.update(
                        f"E{row_num}:J{row_num}",
                        [row_ej],
                        value_input_option="RAW",
                    )
                    st.success(
                        f"✅ 行 {row_num} を更新しました"
                        f"(12digitsID: {d['original_id']})"
                    )
                else:
                    # 新規行: B列に担当者、E〜J列にデータのみ書き込み
                    # C列(AIND-D ID)とD列(12 digits ID)は手動記入領域として触らない
                    # 一番下の空き行ではなく、D列が空の最初の行を探す
                    empty_row = find_first_empty_row(ws)
                    if empty_row is None:
                        st.error("空き行を特定できませんでした。シートを確認してください。")
                    else:
                        # B列に担当者
                        ws.update(
                            f"B{empty_row}",
                            [row_b],
                            value_input_option="RAW",
                        )
                        # E〜J列にデータ
                        ws.update(
                            f"E{empty_row}:J{empty_row}",
                            [row_ej],
                            value_input_option="RAW",
                        )
                        st.success(
                            f"✅ 新規行(行 {empty_row})の B列・E〜J列に書き込みました。"
                            f"\n\n"
                            f"⚠️ **C列(AIND-D ID)と D列(12 digits ID)は触っていません。**"
                            f"手動で記入してください: "
                            f"AIND-D ID = `{d.get('aind_id', '')}`、"
                            f"12 digits ID = `{d.get('original_id', '')}`"
                        )

            except ImportError as e:
                st.error(f"ライブラリ不足: {e}\nrequirements.txt に gspread と google-auth を追加してください。")
            except Exception as e:
                import traceback
                st.error(f"保存エラー: {type(e).__name__}: {e}")
                st.code(traceback.format_exc())
