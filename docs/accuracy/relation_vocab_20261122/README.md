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
