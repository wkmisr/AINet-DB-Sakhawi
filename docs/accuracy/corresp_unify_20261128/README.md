# 外部 ID の一本化：レコードの corresp を外し、典拠表の same_as に持つ（2026-11-28）

WK 裁定 2026-11-28。作業は Claude Fable 5.2。

## 裁定

人物と外部 ID（Wikidata 番号）の対応は、典拠表 `authority/persons_registry.tsv` の same_as 欄にだけ持つ。レコード（XML）の corresp 属性は使わない。

理由は定義。TEI の `@corresp` は「この要素が、指した先と何らかの形で対応する」というゆるい属性で、付いている要素自身について述べる。relation や persName に付けても「この人物は Wikidata のこの項目と同一」という主張にはならない。同一性は人物について1回だけ言うもので、その置き場所が same_as 欄。言及の側は ref・active・passive で「誰を指すか」だけを言う。

これにより、8月の「D-3形式」（AIND 番号＋corresp に Wikidata 番号）、10月の العيني の参照形の統一（B129-133 ★3）、本日の「same_as 欄、レコードでは corresp」は改まる。AIND 番号を正とする点は変わらない。

## 変えたもの

| 対象 | 数 | 内容 |
|---|---|---|
| corresp に Wikidata 番号（relation・persName） | 84か所 | 属性を外した。うち 64か所は العيني（wd:Q257745） |
| corresp に Wikidata 番号（person 要素） | 3か所 | 属性を外した（AIND-D00401・D01845・D02400。番号は same_as に既にあった） |
| corresp に AIND 番号（ref・active と同じ番号の重ね書き） | 43か所 | 属性を外した。スルタン級の 6人への参照 |
| 計 | 130か所・118 レコード | 各レコードに respStmt を足した |
| 典拠表の same_as | 8行 | レコードにしかなかった番号を入れた（下の表） |

一覧は `changes.tsv`（レコード・要素・人物・外した値）。

引き継ぎ文書（2026-11-28）は corresp に AIND 番号がある箇所を「44か所」としていた。1か所は AIND-D03674 の注の文章（「… ＋ corresp="#AIND-D06305"」という校閲の記録）で、属性ではない。属性は 43か所。注の文章は履歴なので変えていない。

### same_as に入れた 8行

| 人物 | AIND | 番号 | 確かめたもの |
|---|---|---|---|
| جقمق | AIND-D02423 | wd:Q647942 | 引き継ぎ v13.15 の D-3形式の記録、台帳 |
| برسباي | AIND-D02168 | wd:Q557812 | 引き継ぎ v13.18、AIND-D02158 の注、台帳 |
| شاه رخ | AIND-D03298 | wd:Q553204 | 引き継ぎ v13.15、台帳 |
| فرج بن برقوق | AIND-D06160 | wd:Q698037 | 台帳だけ（引き継ぎに D-3形式の記録はない）。corpus の本伝は「فرج بن برقوق بن أنس الناصر … ولد في سنة إحدى وتسعين وسبعمائة」 |
| ابن قاضي شهبة（التقي أبو بكر） | AIND-D10669 | wd:Q85461758 | レコード 2か所の corresp、corpus の本伝（ويعرف كسلفه بابن قاضي شهبة）、台帳（1377–1448） |
| الشمس البساطي | AIND-D06729 | wd:Q12219083 | レコード 1か所の corresp、corpus の本伝（ولد في سنة ستين）、台帳（1359 生） |
| ابن ناصر الدين | AIND-D07808 | wd:Q6537956 | レコード 1か所の corresp、corpus の本伝（ولد … سنة سبع وسبعين وسبعمائة）、台帳（1375 生） |
| السراج البلقيني | AIND-D05849 | wd:Q6798541 | レコード 3か所の corresp、corpus の本伝（ولد … سنة أربع وعشرين وسبعمائة）、台帳（1324 生） |

「台帳」は `docs/authority/wd_entities.tsv`（Wikidata から取得した項目の内容）。上の 4人（スルタン）の番号は、レコードには入っていなかった（corresp に AIND 番号が重ねて入っていたため）。

فرج の生年は台帳で 1386、corpus で 791年（1389年）。同じ人物であることは在位（1399–1412）と名前で明らか。

## 道具

- `tools/authority/build_authority.py`
  - ref・active・passive をタグの中だけから読む。注の文章が昔の属性を引用している箇所（`ref="#TMP-I-00000"`、`active="#NEEDED"`、`active="#TMP-P-000087"`）を参照として拾い、「典拠表にない参照」として 3件報告していた。3 → 0。
  - `check` に検査を足した：レコードに corresp 属性がないこと。
- `docs/authority/authority_lib.py`：台帳の「使用中の番号」に、両方の典拠表の same_as 欄を数える。レコードから外した番号が台帳から落ちないようにするため。
- `app.py`：出力のときに `corresp="wd:…"` を付ける処理を外した（付けると `check` に落ちる）。校閲者に見せる「正」候補（`WD_GN_SUGGESTIONS`）からも「+ corresp=…」を外した。
- `docs/lod_prototype/xml2ttl.py`：owl:sameAs を person の corresp からでなく、典拠表の same_as 欄から出す。

## 独立校閲のあとの手当て（WK 裁定 2026-11-28「いずれも推奨通り」）

- 典拠表の履歴：スルタン 4人（AIND-D02423・D02168・D03298・D06160）の「レコードの corresp から移した」を、番号の出どころ（引き継ぎ文書と台帳、فرج は台帳だけ）に直した。この 4人の番号はレコードにはなかった。
- この README の العيني の数を 62 → 64 に。
- `app.py` の候補とコメント、`xml2ttl.py`、`build_authority.py` の corresp 検査（空白＋二重引用符の形だけでなく、改行・タブのあとや単引用符も拾う）。
- 校閲結果は Project doc「外部ID一本化PR132_校閲結果_20261128」。

## 確かめたこと

- 118 レコードすべてで、変更前後の要素・属性・本文を比べ、違いは corresp 属性と末尾の respStmt だけ。
- corresp に Wikidata 番号があった要素は、どれも ref・active・passive に対応する人物の AIND 番号を持つ（`apply.py` の assert）。
- 典拠表の変更は 8行の same_as と history だけ。
- `build_authority.py check` は終了コード 0。

## 手を付けていないもの

- `docs/authority/used_uris.tsv`・`review_queue.tsv` の作り直し。ID-Master の書き出しが要るので、Mac で `python3 docs/authority/update_authority.py` を実行する。
- `docs/tools/precheck_aind_v12.py`：メッセージに「#AIND-… + corresp="wd:…" 形式へ」が残っている。また「person/@corresp の没年と Wikidata の没年の差」の検査は、見る対象がなくなった。XML のバッチ処理は止めているので、パイプライン再設計のなかで扱う。
- `docs/tools/quarantine_wd_gn_xml.py`：レコードに `corresp="wd:…"` を書き足す処理（1.6 と AIND_FIRST）が残っている。動かすと corresp が戻る（`check` で止まる）。precheck と同じく、パイプライン再設計のなかで扱う。
- `docs/authority/authority_lib.py` の person/@corresp の種別判定（害はない。再設計のときに外す）。
- 過去の校閲ブリーフ・検証報告・引き継ぎ文書にある D-3形式・العيني の参照形の記述（履歴）。
- レコードの注の文章にある「corresp=…」の記述（履歴）。
