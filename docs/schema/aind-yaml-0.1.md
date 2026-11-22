# aind-yaml 0.1 ── YAML と mARkdown の書き方（案、2026-11-22）

試行段階。移行を決めるまでは `Individuals/` の TEI が正本で、`data_v01/` は `tools/viewer/` のスクリプトで TEI から作り直せる。

## 基本の考え方
- **YAML は判断（assertion）の正本、mARkdown は本文と位置の正本。** 両者は項目の識別子（`r1`・`s1`・`e1` など）で結ぶ。
- **典拠の名前は ID-Master にだけ置く。** レコードには `ref` だけを書き、正式名・転写・訳語は写さない（典拠コントロール／正規化）。
- **`quote` は本文どおりの文字列。** corpus の本文から抜いたままを書く（正規化しない）。位置は mARkdown のタグが持つ。
  - 根拠：W3C Web Annotation の TextQuoteSelector（exact）、TEI の「要素の中身は史料どおり、正規化は @ref」、ファクトイド型人名録モデル。
- **ID のない値だけ `label`**（ID を持たない官職名、名前要素など）。
- **西暦は保存しない。** ヒジュラ暦から計算する。
- **変更履歴は git と凍結した TEI（tag `tei-final`）に任せる。** レコードには `provenance` の要約だけを置く。
- **識別子 `wd:`・`gn:` は W3C CURIE の書き方のまま。**

## ファイル
- `data_v01/meta/<ID>.yml`：判断（この文書の形式）
- `data_v01/text/<ID>.md`：mARkdown 本文。1行目 `### $ <ID>`、2行目に本文（タグ付き）

## YAML の項目

| 項目 | 内容 | 識別子 |
|---|---|---|
| `schema` | `aind-yaml/0.1` | |
| `id` / `source.uid` / `sex` | 見出しの ID、原典の12桁 ID、性別 | |
| `name.full` | 見出しの名前（本文どおり） | |
| `name.elements[]` | 名前要素：`type`（ism・nasab・nisbah・laqab・kunyah・shuhrah・honorific・madhhab）、`ref`、`quote`。規則で付けたものは `by: rule` | `n1`… |
| `birth` / `death` | `date`（`ah`・`notBefore`・`notAfter`・`cert`）、`places[]`、`quote`、`note` | `b` / `d` |
| `relations[]` | `type`・`subtype`・`active`・`passive`（規則15：subtype は「active が passive の何にあたるか」）、`methods[]`（TMP-S）、`context[]`（日付・場所）、`works[]`、`cert`、`quote`、`note` | `r1`… |
| `states[]` | 官職・身分：`type`（office・status…）、`subtype`（deputy）、`ref`（なければ `label`）、`places[]`・`orgs[]`・`dates[]`、`cert`、`quote`、`note` | `s1`… |
| `affiliations[]` | 所属：`type`、`ref`（なければ `label`）、`cert`、`note` | `a1`… |
| `events[]` | 出来事：`type`・`subtype`、`date`、`persons[]`・`places[]`・`orgs[]`・`works[]`、`quote`（出来事の**中心語1語**）、`summary`（英語などの言い換え）、`cert`、`note`。規則で中心語を付けたものは `trigger: rule` | `e1`… |
| `notes[]` | 項目に属さない注記 | |
| `translation` | `ja`・`en` | |
| `provenance` | `app`・`generated_at`・`model_requested`・`model_resolved`（記録がなければ `model_era` と推定の根拠）・`created_by` | |

- 参照の中（`places[]` など）は `{ref, quote, role, cert}`。`role` の例：origin・destination（移動の出発地・到着地）、companion（同行者）。
- `quote: null` は「本文で位置が決まっていない」の意味。ビューアーでは「未」として出る。本文に出てこないと人が判断したものは「本文になし」（今後 YAML に `attested: false` として持たせる）。

## 日付の規則
- 幅のある年は `notBefore`・`notAfter` で書く（単一の年に cert low を付ける書き方はしない）。
- **「بضع」は1〜9として扱う**（Waka 裁定 2026-11-22。辞書の定義の揺れ（3〜9／1〜9）に対して、真の値を外さない安全側を採る）。「بضع وعشرين」＝821〜829、「بضع عشرة」＝811〜819（百の位は文脈から）。
  - XML の30件（3〜9 型20件、1〜9 型6件、820＋cert low 4件：D00003・D01780・D05686・D10176b）は変換時にこの幅にそろえ、note に裁定を記録。

## mARkdown のタグ
- 既存の形に `|識別子` を足す：`@P12[father:AIND-D00280|r1] بابن سابق`、`@O01[office:wd:Q125482|s3] إمامتها`、`@S01[nisbah:TMP-N-00010|n1] القاهري`
- 出来事：**中心語（トリガー）1語**に付ける。句の範囲は持たない。`@E01[種類|eK]`。例：`@E01[hajj|e2] وحج`、`@E01[cultural|e3] وحفظ`
  - 根拠：情報抽出の出来事注釈（ACE 2005、TimeML の EVENT）は、出来事を句ではなく中心語で示す。範囲の判断の揺れを避けられる。
  - 誰が・どこで・いつは、出来事の `persons[]`・`places[]`・`date` と、それぞれのタグで結ばれる。
  - ビューアー（試作）では `@E01[種類:eK]` と書いている。変換時に `|eK` の形に直す。
- 幅のある年：`@YD821-829[3]`。官職：`@O`。出来事：`@E`。いずれも OpenITI にはない、こちらで足した書き方。

## 変換の試行（4,295件）
- 変換スクリプト：`tools/viewer/`（手順は `tools/viewer/README.md`）。出力は `data_v01/`。
- 出力：meta 13.2MB、text 2.1MB。規則で付けた ism・nasab が名前要素として新たに入った。
- 本文と結べた項目：人物 5,957、名前要素 21,733、官職 1,791、年 2,297、出来事 2,187。位置のないもの（`quote: null`）：関係 2,781、官職 765、出来事 1,096、名前要素 282。
- 出来事の中心語（2026-11-22）：出来事 3,704 件のうち 2,187 件に規則で付与（種類・下位種類ごとの動詞と、英語の要約の語から引く）。ビューアーでは「推定」と表示し、CHECKED で確定。残りはビューアーで AI（Opus）に推定させるか、人がドラッグで付ける。

## 公開（Zenodo）と履歴
- 版ごとに DOI を付けて公開する（Zenodo の版管理）。TEI の最終版を一つの版として先に公開すれば、TEI 時代の変更履歴（respStmt）はその版の中に残る。
- YAML 版では、レコードごとの来歴は `provenance` の要約、データ全体の作り方と版ごとの変更は README と CHANGELOG に書く（FAIR 原則 R1.2「詳しい来歴」に対応）。

## 未決
- `quote` に前置詞（ب・و など）を含めるか。現状は人物・地名などは mARkdown の前接辞の字数を除いた形、出来事の中心語は語全体（例：وحج）。
- `attested: false`（本文になし）と CHECKED を YAML のどこに持つか（`provenance` か各項目か）。
- 関係の向き：`active`/`passive` のまま（規則15）にするか、`partner` と `role` に直すか。
- 出来事の繰り返し（「يكثر」など）：`repeated: true` を足すか（TimeML の頻度属性に相当）。
