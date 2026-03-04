---
# Arab-Islam Network DB Project (AINet-DB)
---

### プロジェクト概要（TEI Header）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="[http://www.tei-c.org/ns/1.0](http://www.tei-c.org/ns/1.0)">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Arab-Islam Network DB Project (AINet-DB): al-Daw' al-Lami' Digital Edition</title>
        <author>AINet-DB Project Team</author>
        <respStmt>
          <resp>Principal Investigator</resp>
          <name xml:id="PI_ID">Your Name</name>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>Arab-Islam Network DB Project (AINet-DB)</publisher>
        <availability status="restricted">
          <p>Available for research and academic purposes. Distributed under Creative Commons Attribution 4.0 International (CC BY 4.0).</p>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <bibl xml:id="Sakhawi_Source">
          <author>al-Sakhawi</author>
          <title>al-Daw' al-Lami' li-ahl al-qarn al-tasi'</title>
          <note>Biographical dictionary of the 9th century Hijri.</note>
        </bibl>
      </sourceDesc>
    </fileDesc>
    <encodingDesc>
      <projectDesc>
        <p>このプロジェクトは、アル＝サハウィーの『輝く光』を構造化し、マムルーク朝期の人物知識グラフを構築することを目的とする。</p>
        <p>13,000人のエントリーに対し、AIを用いた半自動アノテーションと、専門家による厳密な校閲（Human-in-the-loop）を組み合わせて実施する。</p>
      </projectDesc>
      <editorialDecl>
        <interpretation>
          <p>人名、地名、親族・師弟関係、および歴史学的な評価を抽出。評価には &lt;desc&gt; タグを用いて原文の根拠を付与する。</p>
        </interpretation>
        <segmentation>
          <p>各人物には独自の内部ID（PID_XXXXX）を付与し、外部データベース（Wikidata, Ghent, PUA等）とのマッピングを行う。</p>
        </segmentation>
      </editorialDecl>
    </encodingDesc>
  </teiHeader>
</TEI>
