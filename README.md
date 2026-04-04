# Arab-Islam Network DB Project (AINet-DB)

本リポジトリは、アル＝サハウィーの『輝く光（al-Daw' al-Lami'）』を構造化し、マムルーク朝期の知識グラフを構築するためのプロジェクトです。

## プロジェクトの概要
* **対象**: 9世紀ヒジュラ暦の人物録（約13,000名）
* **手法**: 生成AI（Claude/Gemini）による抽出 ＋ 専門家による校閲
* **目標**: TEI形式による構造化および外部DB（Wikidata等）との連携

## プロジェクトのデータセット
* https://drive.google.com/drive/folders/1rEAbyK3-rEhrNPX30wWJDntCs-hKiyLu?usp=sharing

* | ファイル・シート名 | 種類 | 説明 |
|---|---|---|
| **DawForAIND.txt** | テキストファイル | シャハーウィー著『輝く光（al-Ḍawʾ al-Lāmiʿ）』のデジタルテキスト。解析ツールへの入力にはこちらを使用します。 |
| **ID-Master** | Googleスプレッドシート | 地名・機関・人物・書物などのIDを一元的に蓄積・管理するマスターリストです。解析時にAIが自動参照します。 |
| **Sakhawi_PersonList** | Googleスプレッドシート | 『輝く光』に立項されている人物の一覧です。解析ツールで抽出したデータが自動的に反映されます。 |
 

# AINet-DB Researcher Pro 使い方ガイド

**対象：** デジタルツールに不慣れな人文学研究者の方へ  
**目的：** イスラーム伝記史料から人物データを抽出し、データベース用のXMLファイルを作成する

---

## このツールでできること

アラビア語の人名録（伝記史料）のテキストを貼り付けると、AIが自動的に人物情報を読み取り、整理してくれます。研究者はその結果を確認・修正しながら、学術データベース用のフォーマット（TEI-XML）を作成できます。また、作成したデータは共有のスプレッドシートに保存することができます。

---

## 画面の構成

画面は大きく **左側（サイドバー）** と **右側（メインエリア）** に分かれています。

- **左側**：史料テキストの入力・解析・翻訳の表示
- **右側**：AIが抽出したデータの確認・修正・XML出力・保存

---

## 作業の流れ

<details>
<summary>▶ ステップ 1：史料テキストを入力する</summary>

<br>

画面左側の「**史料テキスト (Arabic)**」という欄に、アラビア語の伝記テキストを貼り付けます。

テキストは人物一人分ずつ入力してください。複数人をまとめて入力すると、AIが混乱する場合があります。

</details>

---

<details>
<summary>▶ ステップ 2：解析する</summary>

<br>

「**🔍 解析する**」ボタンを押します。

AIが数秒〜十数秒かけてテキストを読み取り、以下の情報を自動的に抽出します。

- 人物名（フルネーム・略称）
- ニスバ（出身地・所属を示す名前の一部）
- ラカブ（号）・クンヤ（父称）・通称
- 生没年（ヒジュラ暦・西暦換算）
- 法学派・スーフィー教団
- 師匠・弟子とその学習内容
- 活動地・所属機関・官職
- 家族関係
- 日本語訳・英語訳

解析が終わると「**解析完了**」と表示され、右側の各欄にデータが自動入力されます。

> **注意：** AIは便利ですが、完璧ではありません。必ず内容を確認し、誤りがあれば手動で修正してください。

</details>

---

<details>
<summary>▶ ステップ 3：データを確認・修正する</summary>

<br>

右側の「**2. Metadata Editor**」エリアで、AIが抽出したデータを上から順に確認します。
各セクションの内容は以下の通りです。クリックして詳細を確認してください。

<details>
<summary>　　📋 基本情報</summary>

<br>

| 欄 | 内容 |
|---|---|
| @xml:id | このデータベース内でのID（例：AIND-D0001） |
| @source | 史料テキストの番号（例：932540579843） |
| persName (Full Arabic) | フルネーム（アラビア語） |
| persName (Ism/Father/GF) | イスム・父名・祖父名のみ |

</details>

<details>
<summary>　　🏷️ Nisbahs（ニスバ）</summary>

<br>

出身地や所属を示す名前の部分（例：الجبرتي）です。アラビア語・ラテン文字転写・IDを入力します。

</details>

<details>
<summary>　　🔤 Laqab / Shuhrah / Kunyah（号・通称・クンヤ）</summary>

<br>

- **laqab（号）**：敬称・名誉称（例：زين الدين）
- **shuhrah（通称）**：世間に広く知られた呼び名
- **kunyah（クンヤ）**：「〜の父（أبو）」「〜の母（أم）」で始まる称号

</details>

<details>
<summary>　　📅 生没年</summary>

<br>

ヒジュラ暦で入力すると、西暦への換算が自動で行われます。

</details>

<details>
<summary>　　⚖️ Madhhab（法学派）</summary>

<br>

プルダウンから選択します。一覧にない場合は「Unknown / Other」を選ぶと自由記入欄が表示されます。

</details>

<details>
<summary>　　☪️ Sufi Order（スーフィー教団）</summary>

<br>

所属していた場合に記入します。

</details>

<details>
<summary>　　🎓 Teachers & Subjects（師匠と学習内容）</summary>

<br>

誰から何を学んだかを記録します。典籍名・学習した日時・場所も入力できます。

**＋ add teacher** ボタンで行を追加できます。不要な行は **❌** ボタンで削除できます。

</details>

<details>
<summary>　　🧑‍🎓 Students & Subjects（弟子と教授内容）</summary>

<br>

誰に何を教えたかを記録します。Teachers と同じ構成です。

</details>

<details>
<summary>　　📍 Activities / Places（活動地）</summary>

<br>

機関名を伴わない地理的な移動・滞在・出生・死亡・埋葬などを記録します。  
▲▼ボタンで順番を入れ替えられます。

> **Institutions との使い分け：** 「メッカに滞在した」→ Activities。「アズハルで学んだ」→ Institutions。

</details>

<details>
<summary>　　🏛️ Institutions（所属機関）</summary>

<br>

マドラサ・モスク・図書館など、名前のある機関との関わりを記録します。  
▲▼ボタンで順番を入れ替えられます。

</details>

<details>
<summary>　　🏅 Offices / Positions（官職）</summary>

<br>

カーディー（裁判官）などの官職を保有した順に記録します。就任・退任の日時、勤務地、所属機関も入力できます。  
▲▼ボタンで順番を入れ替えられます。

</details>

<details>
<summary>　　👨‍👩‍👧 Family Relations（家族関係）</summary>

<br>

父・母・息子・娘・兄弟など、プルダウンから関係を選択します。「Other」を選ぶと自由記入欄が表示されます。

</details>

<details>
<summary>　　📝 Person Notes（人物メモ）</summary>

<br>

性格・評判・特筆すべき成果・日常生活の様子など、XMLには含まれない人物に関する自由なメモを書けます。

</details>

<details>
<summary>　　🗒️ Editors' Notes（編集メモ）</summary>

<br>

判断に困った点、要確認事項、編集上の備考などを書きます。この内容はスプレッドシートにも保存されます。

</details>

</details>

---

<details>
<summary>▶ ステップ 4：XMLを確認・コピーする</summary>

<br>

「**3. TEI-XML Export**」セクションに、入力内容をもとに生成されたXMLが表示されます。

TEI-XMLテキストの右上にカーソルを置くと現れる**コピー**ボタンを押すと、テキスト全体がコピーされます。コピーしたXMLは、テキストエディタやメモ帳などに貼り付けて保存してください。

</details>

---

<details>
<summary>▶ ステップ 5：スプレッドシートに保存する</summary>

<br>

「**4. スプレッドシートに保存**」セクションで作業します。

1. 「**担当者**」プルダウンから自分の名前を選ぶ
2. 「**書き込み内容プレビュー**」で内容を確認する
3. 「**📤 スプレッドシートに保存**」ボタンを押す

同じ人物（同じ12digitsID）のデータが既にスプレッドシートにある場合は**上書き更新**されます。新しい人物の場合は**末尾に追記**されます。

</details>

---

## IDについて

このツールでは、人物・地名・機関などに外部データベースのIDを付与します。IDの種類は以下の通りです。

| 種類 | 用途 | 例 |
|---|---|---|
| **GeoNames ID**（数字のみ） | 地名 | `104515`（メッカ） |
| **Wikidata ID**（Qから始まる） | 概念・組織・人物 | `Q160851`（ハナフィー派） |
| **TMP-（仮ID）** | まだ外部IDが見つかっていない項目 | `TMP-P-00001` |

TMP-（仮ID）は後から正式なIDに差し替えることができます。

---

## ID Masterについて

画面左側の「**📋 ID Master 状態**」を開くと、研究グループが共有しているIDリストを確認できます。

このリストに登録されている地名・機関・人物は、解析時にAIが自動的に正しいIDを割り当てます。

### ID Masterに新規IDを登録する方法

史料を読んでいると、まだID Masterに登録されていない地名・機関・人物・書物などが出てきます。そのような場合、外部データベースでIDを調べてID Masterに追加します。

<details>
<summary>▶ ① 地名の場合 → GeoNames で調べる</summary>

<br>

地名には **GeoNames**（地名データベース）のIDを使います。

**手順**

1. ブラウザで [https://www.geonames.org/](https://www.geonames.org/) を開く
2. 画面上部の検索欄に地名を入力する（ラテン文字またはアラビア語で入力可）  
   例：`Mecca`、`Cairo`、`مكة`
3. 検索結果の一覧から、該当する地名をクリックする
4. 詳細ページのURLに含まれる数字がIDです  
   例：`https://www.geonames.org/`**`104515`**`/mecca.html` → IDは `104515`

> **注意：** 同名の地名が複数表示される場合があります。国・地域・現在の名称などを手がかりに、正しい場所を選んでください。

**ID Masterへの記入例**

| Category | Arabic | Latin | ID | Note |
|---|---|---|---|---|
| Place | مكة | Mecca | 104515 | |
| Place | القاهرة | Cairo | 360630 | |

</details>

<details>
<summary>▶ ② 機関・概念・法学派・スーフィー教団の場合 → Wikidata で調べる</summary>

<br>

機関や概念には **Wikidata**（知識データベース）のIDを使います。IDは「Q」で始まる番号です。

**手順**

1. ブラウザで [https://www.wikidata.org/](https://www.wikidata.org/) を開く
2. 画面上部の検索欄に名前を入力する（英語・アラビア語どちらでも可）  
   例：`Al-Azhar`、`Hanafi`、`Qadiriyya`
3. 検索結果から該当する項目をクリックする
4. ページタイトルの横にある「Q〇〇〇〇」がIDです  
   例：`Q123552`（アズハル大学）

> **ヒント：** Wikidataのページは多言語に対応しています。英語で検索してもアラビア語の表記が確認できます。

**ID Masterへの記入例**

| Category | Arabic | Latin | ID | Note |
|---|---|---|---|---|
| Institution | الأزهر | al-Azhar | Q123552 | |
| Madhhab | حنفي | Hanafi | Q160851 | |
| SufiOrder | القادرية | Qadiriyya | Q193458 | |

</details>

<details>
<summary>▶ ③ 人物の場合 → Wikidata で調べる</summary>

<br>

著名な学者や歴史的人物は Wikidata に登録されている場合があります。

**手順**

1. [https://www.wikidata.org/](https://www.wikidata.org/) で人物名を検索する  
   例：`Ibn Hajar al-Asqalani`、`al-Sakhawi`
2. 該当する人物のページを開き、「Q〇〇〇〇」のIDを確認する

> **注意：** 人物はWikidataに登録されていない場合も多いです。見つからない場合は仮ID（TMP-P-XXXXX）のままにしておき、後から追加できます。

</details>

<details>
<summary>▶ ④ 書物・典籍の場合 → Wikidata で調べる</summary>

<br>

著名な書物も Wikidata で検索できます。

**手順**

1. [https://www.wikidata.org/](https://www.wikidata.org/) で書名を検索する  
   例：`Sahih al-Bukhari`、`Muqaddima`
2. 該当する書物のページを開き、「Q〇〇〇〇」のIDを確認する

</details>

<details>
<summary>▶ ⑤ 見つからない場合は仮IDのままでよい</summary>

<br>

GeoNamesにもWikidataにも該当する項目がない場合は、**仮ID（TMP-）のまま**にしておいて構いません。仮IDは後から正式なIDに差し替えることができます。

| 仮IDの種類 | 用途 |
|---|---|
| TMP-P-XXXXX | 人物（Person） |
| TMP-L-XXXXX | 地名（Location） |
| TMP-I-XXXXX | 機関（Institution） |
| TMP-O-XXXXX | 官職（Office） |
| TMP-T-XXXXX | 書物・典籍（Text） |
| TMP-S-XXXXX | 学問分野（Subject） |

</details>

<details>
<summary>▶ ⑥ ID MasterスプレッドシートへのIDの追加方法</summary>

<br>

IDが確定したら、共有スプレッドシート「**ID Master**」に追加します。

**スプレッドシートの列構成**

| 列名 | 内容 | 記入例 |
|---|---|---|
| Category | 種類 | Place / Institution / Person / Text / SufiOrder / Madhhab |
| Arabic | アラビア語表記 | مكة |
| Latin | ラテン文字転写 | Mecca |
| ID | GeoNames数字またはWikidata Q番号 | 104515 / Q160851 |
| Note | 補足（任意） | 聖地、現サウジアラビア |

**記入上の注意**

- **Category** は半角英語で統一してください（大文字・小文字を区別します）
- **Arabic** 欄は右から左に書くアラビア語でも問題ありません
- **Latin** 欄は学術的な転写表記（IJMES方式）を推奨しますが、一般的なローマ字表記でも構いません
- 同じ地名・人物が重複して登録されないよう、追加前に一度検索して確認してください

追加後は、アプリ左側の「📋 ID Master 状態」エクスパンダー内にある「**🔄 再読み込み**」ボタンを押すと、最新のIDリストが反映されます。

</details>

---

## 翻訳について

解析後、画面左側の下部に「**🇯🇵 日本語訳**」と「**🇺🇸 English**」タブが表示されます。AIによる学術的な翻訳ですが、必ず原文と照らし合わせて確認してください。

---

## よくある問題

<details>
<summary>▶ 解析ボタンを押しても何も起きない</summary>

<br>

テキスト欄が空になっていないか確認してください。また、インターネット接続が切れている場合も解析できません。

</details>

<details>
<summary>▶ AIの抽出結果が明らかに間違っている</summary>

<br>

右側の各欄を直接編集して修正してください。AIはあくまで補助ツールです。

</details>

<details>
<summary>▶ スプレッドシートへの保存でエラーが出る</summary>

<br>

@source（12digitsID）欄が空の場合は保存できません。入力してから再度お試しください。それでもエラーが出る場合は担当者にご連絡ください。

</details>

<details>
<summary>▶ ページを閉じたらデータが消えた</summary>

<br>

このツールはブラウザを閉じるとデータがリセットされます。必ずXMLをコピーするか、スプレッドシートに保存してから作業を終了してください。

</details>

---

## 作業の基本的な注意事項

- 一度に入力するのは**人物一人分**のテキストにしてください
- AIの解析結果は必ず**目で確認**してください
- 作業が終わったら必ず**XMLのコピー**または**スプレッドシートへの保存**を行ってください
- 判断に迷う場合は **Editors' Notes** に記録を残しておくと、後で見直しやすくなります
