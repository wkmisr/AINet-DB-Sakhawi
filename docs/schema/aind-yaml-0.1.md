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
| `birth` / `death` | `date`（`ah`・`notBefore`・`notAfter`・`cert`）、`places[]`（埋葬地は `role: burial`、葬儀の礼拝の場所は `role: funeral`）、`persons[]`（`role: funeral_prayer`・`funeral_attendee`・`buried_near`）、`quote`、`note` | `b` / `d` |
| `persons[]` | 本文に出てくる（または含意される）が ID で同定できない人物：`label`（TEI の desc）、`for`（その人物が現れる項目）、`name_element`（名のない父・祖父は見出しの1番目・2番目の nasab、`by: rule`）。参照は `<レコードID>#pN` | `p1`… |
| `relations[]` | `type`（subtype から機械的に決める：kin・scholarly＝teacher・identity＝possible_identity・social）・`subtype`・`active`・`passive`（規則15：subtype は「active が passive の何にあたるか」。本項主かどうかは関係しない）、`methods[]`（TMP-S）、`context[]`（日付・場所）、`works[]`、`cert`、`quote`、`note` | `r1`… |
| `states[]` | 官職・身分：`type`（office・status…）、`subtype`（deputy）、`ref`（なければ `label`）、`places[]`・`orgs[]`・`dates[]`、`cert`、`quote`、`note` | `s1`… |
| `affiliations[]` | 所属：`type`、`ref`（なければ `label`）、`cert`、`note` | `a1`… |
| `events[]` | 出来事：`type`・`subtype`、`date`、`methods[]`（学習の方法 TMP-S、relation と同じ）、`persons[]`・`places[]`・`orgs[]`・`works[]`、`quote`（出来事の**中心語1語**）、`summary`（英語などの言い換え）、`cert`、`note`。規則で中心語を付けたものは `trigger: rule` | `e1`… |
| `assessments[]` | 人物評（Waka 決定 2026-11-26）：伝記作者による人物の評価（«وهو من الصلحاء»、«كان خيرا دينا»）。官職・身分・出来事のどれでもない。`quote`（本文の語。なければ `label`）・`norm`・`terms[]`（統制語彙：صالح・خير・دين・فاضل・ثقة・زاهد・عابد・متعبد・ورع・متواضع・معتقد・عفيف・ساكن）・`by: rule`（定型句 كان／وهو〔من〕＋評価語 から規則で拾ったもの。ビューアーで確認）・`assessor`（評した人。なければサハーウィー）・`cert`・`note`。TEI で state type="status" に ID なしで入っていた人物評は変換時にここへ移す（state の識別子は振り直さない）。mARkdown のタグは `@V01[assessment\|v1]` | `v1`… |
| `sources[]` | 典拠への言及（Waka 決定 2026-11-26）：«ذكره／أرخه／قال فلان» など、本人の生涯の出来事ではなく「誰がどの書で記録したか」。`persons[]`（記録した人）・`works[]`（書名）・`quote`（中心語）・`norm`・`summary`・`cert`・`note`。TEI では今も event type="cultural" subtype="mention" で、変換時にここへ移す。出来事の識別子は振り直さない（欠番が出る）。mARkdown のタグは `@C01[mention\|c1]` | `c1`… |
| `notes[]` | 項目に属さない注記 | |
| `translation` | `ja`・`en` | |
| `provenance` | `app`・`generated_at`・`model_requested`・`model_resolved`（記録がなければ `model_era` と推定の根拠）・`created_by` | |

- 参照の中（`places[]` など）は `{ref, quote, role, cert}`。
- **`quote` と `norm`（2026-11-23、ロマノフの助言・Waka 決定）**：`quote` は本文のままの語（前接辞 ب・و・ف・ك・ل も含む）。`norm` は標準化した形で、`quote` と違うときだけ書く。標準化は (1) 前接辞を外す（mARkdown のタグが数える前接辞の字数による。出来事の中心語は頭の و・ف を規則で外す）、(2) 名前要素の単位で格の形をそろえる（語句の頭の أبي・أبا→أبو、أخي・أخا→أخو、ذي・ذا→ذو、بني→بنو。後ろに語が続くときだけ。«ابن أبي اليمن» のように句の中にあるものはそのまま）、(3) OpenITI の `normalize_ara_light`（أ・إ・آ・ٱ→ا、ى→ي、台座つきハムザ→ء ほか。MIT ライセンスの関数を変換スクリプトに写した）。
- `quote: null` は「本文で位置が決まっていない」の意味。ビューアーでは「未」として出る。本文に出てこないと人が判断したものは「本文になし」（今後 YAML に `attested: false` として持たせる）。

## トリプル書き出しの前提（2026-11-22）
YAML はそのままではトリプルではないが、欠けなく機械的に変換できるように次を守る。書き出し（TSV／Turtle）は YAML から毎回作り、正本は YAML と mARkdown だけにする。

- **ノードの住所**：レコードは `AIND-D…`、項目は `<レコードID>#<項目の識別子>`（例 `AIND-D00008#e2`）。関係・官職・出来事は一つのノードになり、確度・本文の語句・日付・場所はそのノードに付く。
- **識別子は変えない**：YAML を正本にした後は、一度付けた識別子（`r1`・`e1`・`p1` など）を振り直さない。項目を消しても番号を詰めない。移行までは TEI から作り直すが、同じ TEI からは同じ番号が出る（決定的）。
- **同定できない人物**：TEI では `#NEEDID`（作業上の印）のまま。YAML では一人ずつ `persons[]` に立て、`<レコードID>#pN` で参照する。同じレコードの中の二つの #NEEDID が同じ人かどうかは判断せず、分けておく（後で同定したら ID に置き換える）。人物以外の #NEEDID（場所・官職など）は `ref` を持たず `label` だけにする。
- **関係の向き**：述語の意味だけで決まる（規則15、2026-11-22 改訂）。逆向きと対称の語は下の表のとおり。両方のレコードに書かれた同じ関係（2026-11-22 時点で 182 組、矛盾 0）は、書き出しで一本にまとめる。

  | 述語（active が passive の何か） | 逆向きの読み | 
  |---|---|
  | teacher | student（データには書かない） |
  | father・mother | son・daughter（子） |
  | son・daughter | father・mother（親） |
  | grandfather・maternal_grandfather・grandmother | grandson（孫） |
  | ancestor | descendant |
  | uncle・paternal_uncle・maternal_uncle・maternal_aunt | siblings_child |
  | siblings_child | uncle・aunt（親の兄弟姉妹） |
  | father-in-law | son-in-law（逆も同じ） |
  | patron | client（逆も同じ） |
  | predecessor | successor（逆も同じ） |
  | deputy | principal（本務者。データには書かない） |
  | educator | ward（被養育者。データには書かない） |
  | killer | victim（データには書かない） |
  | 対称（向きなし） | brother・sister・spouse・cousin・relative・brother-in-law・colleague・rival・companion・friend・correspondent・possible_identity・other |
- **確度**：`cert` がない項目は「本文に疑いの表現がない」を意味する。
- **TMP の ID**：統合で消える TMP は、ID-Master に「旧 ID→新 ID」を残し、書き出しで置き換え関係（`dct:isReplacedBy` 相当）を出す。公開したリンクを切らないため。
- **出来事の人物**：`role` がなければ「参加者」として書き出す。
- 試作（`docs/lod_prototype/xml2ttl.py`、TEI から直接）は #NEEDID の人物を捨て、項目を並び順で番号付けしていた。YAML からの書き出しで置き換える。

## 日付の規則
- 幅のある年は `notBefore`・`notAfter` で書く（単一の年に cert low を付ける書き方はしない）。
- **「بضع」は1〜9として扱う**（Waka 裁定 2026-11-22。辞書の定義の揺れ（3〜9／1〜9）に対して、真の値を外さない安全側を採る）。「بضع وعشرين」＝821〜829、「بضع عشرة」＝811〜819（百の位は文脈から）。
  - TEI の側を直した（PR #118、2026-11-22）：X3〜X9 と書いた幅は X1〜X9 に、単一の年＋cert low の4件（D00003・D01780・D05686・D10176b）は幅に。変換は TEI の値をそのまま使う（以前は変換時に幅を上書きしていたが、百の位を誤る場合があった：D07146 の生年）。

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
- ~~関係の向き~~：`active`/`passive` のまま、向きは述語の意味だけで決める（Waka 裁定 2026-11-22、案 (a)）。
- 出来事の繰り返し（「يكثر」など）：`repeated: true` を足すか（TimeML の頻度属性に相当）。
