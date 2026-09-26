# cert 運用の実装仕様（要判断§I 裁定 2026-08-21・3段階案）

## ご質問への回答: **はい、pyファイルも書き換えが必要です。しかも3ファイルです。**

現状を調べたところ、**cert を relation / state に付ける枠組みがそもそも存在しません**。

| ファイル | 現状 | 必要な作業 |
|---|---|---|
| **`prompt_analyze.txt`** | `cert` の語は9箇所あるが**すべて日付専用**（`birth_cert` / `death_cert` / `date_cert`）。relation・state用のcertフィールドは**なし**。マーカー語（`زعم`/`بلغني`/`قال أنه`/`يحرر`）への言及も**0件** | **★最重要**。JSONスキーマにフィールド追加＋判定ルールの新セクション |
| **`app.py`** | 同上（マーカー語0件）。JSONに`cert`が来ても**XMLの`@cert`に落とす経路がない** | JSON→XML変換に`@cert`出力を追加 |
| **`docs/precheck_aind_v11.py`** | `cert` の語が**0件**＝一切検査していない | v12でマーカー検出ルールを追加 |

**`prompt_analyze.txt` を直さないかぎり、生成側は永久に cert を出しません。** 今回のように毎バッチ校閲側で手作業補填することになります。上流を直すのが本筋です。

---

# 1. `prompt_analyze.txt`

## 1-A. 新セクションの追加（貼り付け用）

既存の **【18b. FORWARD/BACKWARD REFERENCE MARKERS】の直前**（772行目付近）に挿入するのが構成上自然です。同セクションが「原文のマーカー語をどう扱うか」を扱っており、性格が揃うためです。

```
============================================================
【18a. EPISTEMIC MARKERS — WHO IS ASSERTING THIS?】
============================================================
al-Sakhāwī distinguishes between what HE states directly and what he
merely REPORTS from others. This distinction MUST be preserved.

When a statement is introduced by one of the markers below, set the
"cert" field of the affected record (teacher / student / activity /
office / event / relation) accordingly.

  MARKER                        MEANING                        cert
  ----------------------------------------------------------------
  (no marker)                   al-Sakhāwī's own statement     ""  (omit)
  قال أنه / ذكر أنه              the SUBJECT's own claim,       "medium"
                                neutrally reported
  بلغني / أُخبرت                 hearsay reaching al-Sakhāwī,   "medium"
                                source not named
  زعم                           a THIRD PARTY's claim, with    "low"
                                al-Sakhāwī's implicit reserve
  يحرر                          al-Sakhāwī himself flags it    "low"
                                as unverified                  + see below

IMPORTANT — why زعم is one level lower:
  قال and بلغني are neutral verbs of report. زعم carries a note of
  doubt ("claimed, allegedly"). al-Sakhāwī's CHOICE of زعم over قال is
  itself an evaluative act. Do NOT flatten them to the same level.

SCOPE: the marker governs everything up to the end of that clause.
  e.g. "وقال أنه سمع البخاري على X وبعض مسلم على Y والشفا على Z"
       → ALL THREE teacher records get cert="medium", not just the first.

ALWAYS also record the marker word itself, so the basis is traceable:
  "cert_note_ar": "زعم"

يحرر — SPECIAL HANDLING:
  When al-Sakhāwī writes يحرر ("to be verified"), he is questioning
  whether the material belongs to this biography at all. In addition to
  cert="low", emit a possible_identity flag:
      "possible_identity": true,
      "cert_note_ar": "يحرر أهو من ترجمة هذا"

DO NOT confuse these with رأيته / رأيت خطه / اجتمع بي — those are
al-Sakhāwī's OWN direct observation and take NO cert.
```

## 1-B. JSONスキーマへのフィールド追加（【20. OUTPUT FORMAT】）

**`teachers` / `students` / `activities` / `offices` / `events` / `relations` の各要素に2フィールドを追加**してください。

```json
  "teachers": [
    {
      "seq": 1,
      "name": "", "id": "",
      "method_id": "",
      "field_id": "",
      "text_ar": "", "text_lat": "", "text_id": "",
      "learn_date": "",
      "learn_place_ar": "", "learn_place_lat": "", "learn_place_id": "",
      "cert": "",                              ← 追加
      "cert_note_ar": ""                       ← 追加
    }
  ],
```

`activities` には既に `date_cert` がありますが、これは**日付の確度**であって**事実そのものの確度**とは別物です。混同を避けるため、フィールド名は `cert` と分けてください。

## 1-C. 【19. FINAL CHECKLIST】への追加

```
□ If the source text contains زعم / بلغني / قال أنه / ذكر أنه / يحرر,
  did every record governed by that clause receive a "cert" value?
```

---

# 2. `app.py`

JSON→XML変換部で、`cert` が空でなければ**該当要素に `@cert` を出力**してください。

```python
# teachers / students / activities / offices / events / relations 共通
cert = (rec.get("cert") or "").strip()
attrs = {...}                       # 既存の属性組み立て
if cert in ("high", "medium", "low"):
    attrs["cert"] = cert

# cert_note_ar は <note xml:lang="ar"> として子要素に
note_ar = (rec.get("cert_note_ar") or "").strip()
if note_ar:
    el.append(make_note(note_ar, lang="ar"))

# possible_identity フラグ → relation 生成
if rec.get("possible_identity"):
    emit_relation(subtype="possible_identity", cert="low", ...)
```

**注意**: `@cert` は TEI の標準属性なので、要素名を問わず付与できます。既存の `birth_cert` / `death_cert` は `<birth>` / `<death>` の `@cert` に落ちているはずなので、**同じ経路を relation / state / event にも広げる**形になります。

---

# 3. `docs/precheck_aind_v11.py` → **v12**

corpus本文にマーカーがあるのに、対応要素に `cert` がない場合を警告します。**現状 `cert` の語が0件＝完全に無検査**です。

```python
# --- v12 追加: 認識論的マーカーと cert の整合チェック ---
EPISTEMIC = {
    "زعم":       "low",
    "بلغني":     "medium",
    "قال أنه":   "medium",
    "ذكر أنه":   "medium",
    "يحرر":      "low",
}
CERT_BEARING = ("relation", "state", "event", "affiliation")

def check_epistemic(root, corpus_text, findings, loc_prefix):
    """corpus本文にマーカーがあるのに cert 無しの要素が残っていれば警告"""
    hits = [(m, c) for m, c in EPISTEMIC.items() if norm_ar(m) in norm_ar(corpus_text)]
    if not hits:
        return
    markers = " / ".join(m for m, _ in hits)
    expected = min((c for _, c in hits), key=lambda x: ["low", "medium", "high"].index(x))
    for el in root.iter():
        if el.tag not in CERT_BEARING:
            continue
        if el.get("cert"):
            continue
        findings.append((
            "cert欠落",
            f"{loc_prefix}{el.tag} — corpus本文に認識論的マーカー「{markers}」があるが "
            f"@cert が未設定(期待値: {expected} 以下)"
        ))
```

### 併せて v12 に入れていただきたい検査（B54で判明したもの）

| # | 検査 | 根拠 |
|---|---|---|
| 1 | **XMLパース失敗ファイルを一覧出力** | 破損13件が**precheckから黙って除外**されていた。可視化しないと再発する |
| 2 | **`@when` にヒジュラ暦形式（`0\d{3}`）が入っていないか** | B54で8件。v20.11.1でも継続 |
| 3 | **`when-custom` から西暦を機械計算し `@when` と±1年超乖離** | B54で7件（後半月の年繰り上がり取りこぼし） |
| 4 | **言及者の没年 < 被言及者の没年** | §D-1。corpus全体で「أرخه ابن فهد」436項が対象 |
| 5 | **`subtype` 属性値に空白が含まれる** | B54で9種類の統制語彙違反 |
| 6 | **同一IDが異カテゴリ位置で使用**（ニスバ番号のperson位置流用等） | B54で5箇所 |
| 7 | **CSV/TSV自動判別** | `load_idmaster` が `delimiter="\t"` 固定のため、CSVを渡すと**全参照が偽陽性化**（288件→22件） |

---

# 4. 適用済みの4ファイル（参考実装）

上記仕様に沿って、B54の該当4件には**手作業で適用済**です。生成側実装時の期待出力例としてご参照ください。

| ファイル | マーカー | 適用 |
|---|---|---|
| `D05666` | `زعم` | teacher relation n=2 に `cert="low"` ＋ `<note xml:lang="ar">زعم</note>` |
| `D05704` | `بلغني` | state×2（مدرس / الشهادة）＋ event(hajj) に `cert="medium"`。※イジャーザ証人署名の event はサハーウィー直接叙述のため cert なし |
| `D05705` | `وقال أنه` | teacher relation **4件すべて**に `cert="medium"`（1つのقالが3つの聴聞すべてを支配） |
| `D05634` | `يحرر` | `possible_identity` relation を新設し `cert="low"` ＋ マーカー語を注記 |

`D05704` の扱いが**スコープ規則の実例**になっています。同一項の中でも、**伝聞に基づく部分（教職・公証人職・ハッジ）にのみ cert を付け、サハーウィー自身が見た部分（イジャーザへの証人署名）には付けていません**。マーカーは項全体ではなく**節を支配する**、という点が実装上の要点です。
