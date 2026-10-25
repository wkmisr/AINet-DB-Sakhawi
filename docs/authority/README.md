# 典拠台帳(Wikidata / GeoNames)

AINet-DB で使っている `wd:Q…` と `gn:…` を全件抜き出し、Wikidata と GeoNames から中身(ラベル・種別・生没年・座標など)を取ってきて、手元で引ける台帳にしたものです。目的は次の3つです。

1. **毒wd/gn を機械的に見つける**:存在しない番号、統合済み(リダイレクト)の番号、生物の分類群、人物の位置に地名や著作が入っているもの、近現代の人物、没年が大きくずれる `person/@corresp` などを検出します。
2. **照合を速くする**:`要照合wd/gn` に、その番号が実際に何を指しているかが併記されます。Wikidata を開く前に見当がつきます。
3. **判定を記録する**:人が照合した結果を `verified.tsv` に残します。OK 判定済みのものは、次回から「要照合」に出ません。これが「登録済み・確認済みの ID だけを通す」仕組みの土台になります。

> 台帳の中身は**照合の材料**であって「確認済み」ではありません。確認済みかどうかは `verified.tsv` だけが決めます。

## 更新のしかた(Mac のターミナルで)

```
cd ~/Desktop/AINet-DB-Sakhawi
python3 docs/authority/update_authority.py
```

- 初回は数分かかります(Wikidata 約180件、GeoNames 約70件。GeoNames は1件1秒ずつ間を空けます)。2回目以降は、取得から30日以内のものを飛ばすので速く終わります。
- Claude の作業環境からは両サイトに接続できないため、取得だけは Mac で実行します。抽出・照合表づくりはネット不要です(`--extract-only`)。
- 校閲前のバッチも対象に含めるとき:`--extra-xml docs/_work/B129-133_incoming`
- GeoNames はアカウントなしで取れる RDF 版を使います。取得に失敗した行は `status=error:…` になり、次回の実行で自動的に取り直します。失敗が続くときは GeoNames の無料アカウント(geonames.org で登録し、アカウント設定で Web サービスを有効化)を作り、`--gn-user アカウント名` を付けて実行すると公式 API で取れます。

## ファイル

| ファイル | 中身 | git |
|---|---|---|
| `used_uris.tsv` | 使用中 URI と、XML・ID-Master・precheck での使われ方(参照数・位置・記載名・期待種別) | 管理 |
| `wd_entities.tsv` | Wikidata:ラベル ar/en/ja、別名、説明、P31、種別、生没年(末尾 J=ユリウス暦で記録)、座標、GeoNames ID、国、Wikipedia 記事名、取得日 | 管理 |
| `gn_entities.tsv` | GeoNames:名称、アラビア語名・日本語名、地物種別(P.PPLC など)、国、座標、対応する wd、取得日 | 管理 |
| `wd_class_labels.tsv` | P31 などに出てくるクラスの名前 | 管理 |
| `review_queue.tsv` | **照合用の一覧**。自動フラグの重い順(毒 → 毒疑い → 要修正 → 要確認 → 参考 → フラグなし → 判定済み)。Numbers / Excel で開く | 管理 |
| `verified.tsv` | **人の判定**(OK / 毒 / 付替 / 保留)。手で追記する | 管理 |
| `cache/` | 取得した生データ | 管理外 |

## 照合の手順

1. `review_queue.tsv` を開き、上から見ます。`label_ar / label_en / description / type / life_or_coord` が Wikidata・GeoNames 側の実際の中身、`names_in_xml / idmaster` がこちら側の使われ方です。`url` 列から本体を開けます。
2. 判断したら `verified.tsv` に1行追記します(タブ区切り。同じ URI は後の行が優先されます)。

   | 列 | 書き方 |
   |---|---|
   | uri | `wd:Q1239` / `gn:360630` |
   | verdict | `OK`(正しい)/ `毒`(誤り)/ `付替`(リダイレクト等で別番号へ移す)/ `保留` |
   | seen_label | 確認したときのラベル |
   | checked_by / date | 確認者と日付 |
   | note | 正しい番号・根拠など |

3. 次に precheck を回すと、`毒` は `[台帳:毒]`、`付替` は `[台帳:要修正]` として報告されます。`OK` は「要照合」から外れます。

`verified.tsv` には、これまでに Waka さんが実照合した番号(2026-09〜10)と、ID-Master の Note に毒と記録された番号を最初から入れてあります。

## precheck との連携

`docs/precheck_aind_v12.py` は、`docs/authority/` に台帳があれば自動で読み込みます(使わないときは `--no-authority`)。追加される報告は次のとおりです。

| 区分 | 内容 |
|---|---|
| `台帳:毒` | Wikidata/GeoNames に存在しない番号、生物分類群、`verified.tsv` で毒判定 |
| `台帳:毒疑い` | 位置と種別の不一致(人物位置に地名・著作など、非人物位置に人物)、近現代の人物(没年 > 1700 または生年 > 1650)、`person/@corresp` の没年と P570 の差が5年を超える |
| `台帳:要修正` | リダイレクト(統合済み番号)、`verified.tsv` で付替指示 |
| `台帳:要確認` | 台帳にまだない番号(新しく出てきた番号。update を再実行)、種別を判定できないもの |

期待種別は XML 上の位置で決まります(`relation/@active・passive`・`persName` → 人物、`placeName` → 地名(death/event 直下は施設も可)、`affiliation`・`orgName` → 施設・組織、`state` → 職・称号、`bibl` → 著作、`desc` → 分野)。種別は Wikidata の P31/P279 をたどって、human / place / structure / org / work / position / group / belief / discipline / taxon / event のどれに属するかで判定します。

## ローカル検索

```
python3 docs/authority/lookup.py Q1283          # 番号の中身と、こちらでの使われ方・自動フラグ
python3 docs/authority/lookup.py gn:360630
python3 docs/authority/lookup.py القاهرة        # ラベル・別名・XML 記載名から検索
python3 docs/authority/lookup.py --flags        # 未判定で、毒・毒疑い・要修正のもの
python3 docs/authority/lookup.py --flags --all  # 要確認・参考も含める
```

## ライセンス

- Wikidata:CC0。
- GeoNames:CC BY 4.0。公開サイトや論文で GeoNames 由来の名称・座標を示すときは「GeoNames (geonames.org), CC BY 4.0」と出典を表示します。

## 今後(②照合用の候補プール)

使用中の番号の台帳(①)とは別に、まだ使っていない候補を手元で引くためのプールを作る予定です。Wikidata は SPARQL で対象範囲(没年 AH700〜950 頃の人物、エジプト・シリア・ヒジャーズ・イエメンの地名・施設、アラビア語著作など)をまとめて取得し、GeoNames は国別ダンプとアラビア語別名を使います。サイズが大きいので git 管理外に置き、SQLite で検索できるようにします。対象範囲を決めてから着手します。

## 生成側の方針(2026-10-26 Waka 裁定)

- `prompt_analyze.txt` RULE 0b: Gemini は wd/gn を記憶から書かない。書いてよいのは ID-Master にある番号(名前一致)と、プロンプトに印字した固定番号(分野リスト、ハディース8書、イブン・ハジャル Q471116、サハーウィー本人 Q4120128)だけ。それ以外は TMP の全零プレースホルダー
- `app.py` v20.12: それでも出てきた未照合の wd/gn は保持せず NEEDID に差し戻し、名前で ID-Master と再照合する(例: منى → TMP-L-00201)。`verified.tsv` の OK は通し、毒・付替は差し戻す
- 正しい wd/gn は校閲時に、この台帳(`lookup.py`・`review_queue.tsv`)で照合して付ける
