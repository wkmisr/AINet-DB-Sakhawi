# 統制語彙外の relation subtype（2026-11-22 洗い出し）

Individuals 4,295 ファイルの relation 7671 件のうち、統制語彙（app.py の FAMILY_RELATIONS・SOCIAL_RELATION_TYPES に teacher・possible_identity・killer・maternal_*・paternal_uncle を加えたもの）にない subtype は **151 件（140 ファイル）**。明細は `out_of_vocab.tsv`。

| 群 | 件数 | 主な subtype | 処置案 |
|---|---|---|---|
| A 言及・典拠 | 24 | biographer・mentioned by・praised by・chronicler・composed for・author/compiler ほか | 人的関係ではない。Pattern A（cultural/mention の event＋persName）に移す。先例 D01824（praise）・D05997 |
| B 同行・面識 | 37 | companion 17・met 11・met_or_known_by・travel companion・associate・acquaintance ほか | (a) 統制語彙に `companion`（صحبة・同行）を新設し、companion 系はここへ。met 系（لقيته 等の面会）は規則（学習を伴わない「لقيته」＝event、2026-10-27）どおり event に移す (b) すべて friend／other に寄せる |
| C 代理 | 18 | deputy | (a) 統制語彙に `deputy`（active＝代理、passive＝本務者）を新設 (b) other＋note |
| D 主従・上下 | 18 | employer・servant・sovereign・military_superior・servant/master・appointer・advisor/tutor ほか | 規則51（仕えた・重用された＝patron）どおり patron／client に。appointer は任官の event の persName（role="appointer"）に |
| E 親族の表記ゆれ | 17 | nephew・child・granduncle・paternal_grandfather・relative_by_marriage・co-father-in-law・daughter-in-law ほか | 既存語へ：nephew→siblings_child、child→son／daughter、paternal_grandfather→grandfather。姻戚は規則52（向きが決まれば son-in-law 等、決まらなければ relative）。granduncle は relative＋note（または新設） |
| F 出来事にあたるもの | 24 | killed together with・captor・jailer・funeral・witness・executor of will・host・mediator・reciter ほか | relation から出来事の persName（@role）に移す（★9 と同じ扱い）。killer は既存の例外どおり relation のまま |
| G 同郷・近隣 | 9 | neighbor 6・townsman・compatriot | 人的関係としては弱い。other＋note か、本文の語を note に残して relation を外す |
| H その他 | 4 | spiritual relationship・believer/admirer・type="professional" の predecessor ほか | 個別に判断（believer/admirer は「له فيه اعتقاد」型で、mention か other） |

## 反映（2026-11-22、Waka 裁定：A〜G 推奨どおり、B・C は (a)）
- 適用スクリプト `apply_fixes.py`（`out_of_vocab.tsv` を入力）。誤りの型の ★1〜★11（`docs/accuracy/yaml_patterns_20261122/rulings_draft.md`）も同じスクリプトで反映。
- 変更 144 ファイル。各ファイルに respStmt（`claude-opus-5-5-vocab-20261122`）を1つ追記し、変更内容を note に列挙。
- 反映後、統制語彙外の relation は 0 件（companion・deputy を統制語彙に追加した前提）。
- deputy は既存 18 件がすべて active＝本務者だったので、規則15 の読み（active が passive の何にあたるか）に合わせて active＝代理（本項主）・passive＝本務者に入れ替えた（educator と同じ本項主 active の例外）。
- 葬儀・埋葬の relation（funeral・funeral_attendee・led funeral prayer for・neighbor in burial）は、葬儀を bio_event にしない規則により <death> の persName（role=funeral_prayer／buried_near）に移した。
- 「له ذكر في」型（mentioned_in・mentioned in biography・mentioned in connection with・cross-reference、D03182 の met）は note type="cross-reference" に。
- H：D01864・D04661 の predecessor は type を professional→personal に。D02211・D02327 の اعتقاد 型は other＋note。D03206 sovereign は other＋note。D00311 chief / head は同じ相手の teacher と重複のため除去。D00524 appointer は deputy（本項主が代理）。D01702 advisor/tutor は client（本項主がバルクークの主人）。
- precheck（v12）を変更前後で比較：検出 194→191 件、新しい種類の指摘なし（減ったのは長い句を persName の記載名にしていた名前不一致）。

## app.py に積んでおく修正（一括修正の候補）
- SOCIAL_RELATION_TYPES に companion・deputy を追加（deputy は active＝本項主で出力）。
- event の placeName に role（origin・destination・alternative）、event の persName に role（companion・killer・co-victim・appointer など）、note type="frequency" を出せるようにする。
- docs/browser の表示：上記 role と companion・deputy のラベル。
