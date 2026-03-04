# Arab-Islam Network DB Project (AINet-DB)

本リポジトリは、アル＝サハウィーの『輝く光（al-Daw' al-Lami'）』を構造化し、マムルーク朝期の知識グラフを構築するためのプロジェクトです。

## 📌 プロジェクトの概要
* **対象**: 9世紀ヒジュラ暦の人物録（約13,000名）
* **手法**: 生成AI（Claude/Gemini）による抽出 ＋ 専門家による校閲
* **目標**: TEI形式による構造化および外部DB（Wikidata等）との連携

## 🛠 技術仕様（TEI Header 定義）
> [!NOTE]
> 以下のコードは、本プロジェクトで採用しているデータのメタデータ定義です。

<details>
<summary>▶ クリックして XML スキーマの詳細を表示</summary>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="[http://www.tei-c.org/ns/1.0](http://www.tei-c.org/ns/1.0)">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Arab-Islam Network DB Project (AINet-DB): al-Daw' al-Lami' Digital Edition</title>
        <author>AINet-DB Project Team</author>
      </titleStmt>
      <encodingDesc>
        <projectDesc>
          <p>このプロジェクトは、アル＝サハウィーの『輝く光』を構造化し、マムルーク朝期の人物知識グラフを構築することを目的とする。</p>
        </projectDesc>
      </editorialDecl>
    </encodingDesc>
  </teiHeader>
</TEI>
