# AINet-DB-Sakhawi
TEI-based Digital Prosopography for al-Sakhawi's al-Daw' al-Lami' (AINet-DB Project)

Arab-Islam Network DB Project (AINet-DB)
『輝く光』DB構築プロジェクト
本リポジトリは、15世紀の歴史家アル＝サハウィーによる人名録『輝く光（al-Daw' al-Lami'）』を構造化し、TEI形式のXMLおよびRDFとして蓄積・公開するための研究基盤です。

📌 プロジェクトの目的
構造化: 13,000人を超える人物情報をTEI（Text Encoding Initiative）に基づきタグ付け。

相互接続: 外部データベース（Wikidata, Ghent Mamluk Prosopography, PUA等）とID連携し、マムルーク朝期の知識グラフを構築。

AI活用: 高品質な教師データを作成し、機械学習による歴史テキストの自動構造化を推進。

📂 データ構造とディレクトリ構成
/data : TEI XMLファイル群（PID_XXXXX.xml 形式）

/schema : 本プロジェクト独自のTEIガイドライン（ODD/RNGファイル）

/scripts : RDF変換用およびバリデーション用のPythonスクリプト

/docs : タグ付けマニュアル、作業者向けのプロンプトエンジニアリング指針

🛠 ワークフロー
Extraction: 生成AIによる初期タグ付け。

Review: テキスト班による歴史学的校閲とdesc（根拠記述）の付与。

Commit: GitHub Desktopを用いたバージョン管理。

Integration: 500〜1,000件単位での機械学習フィードバックとルール更新。
