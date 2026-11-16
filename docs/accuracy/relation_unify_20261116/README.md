# relation の向きと subtype の統一（2026-11-16、Waka 依頼）

## 背景
LLM 抽出の評価（gemma-4-12b-it ep4）で、正解データの師弟の向きが逆になっている例が見つかった。
原因は XML の符号化が2通りに読める書き方を含んでいたこと。

- 師弟（旧規則15）: active=師・passive=学生で、subtype は teacher でも student でもよい
  → subtype の語が向きを表さない（student・active=本項主 は「本項主が相手の学生」と読めてしまう）
- 親族・社会関係: active=相手・passive=本項主、subtype=相手の役割

## 統一規則（CHUNK_BRIEF 規則15 を改訂）
subtype は常に「active が passive の何にあたるか」。

- 師弟は常に `subtype="teacher"`・active=師・passive=学生（`student` は使わない）
- 親族・社会関係は active=相手・passive=本項主。本項主が相手の何かと書かれていても相手を active にし、逆関係の subtype で立てる（逆関係の語が統制語彙にない killer 等のみ本項主 active 可）
- active・passive は省かない（不明は `#NEEDID`）

これで、変換・表示のコードは「本項主が passive なら subtype＝相手の役割、active なら逆関係」の1規則で読める。

## 変更（Individuals 324 ファイル）

| 内容 | 件数 | 処置 |
|---|---|---|
| `student`・active=本項主 | 330 | subtype を teacher に（向きは不変） |
| `student`・passive=本項主（**向きの誤り**） | 14 | 本文照合のうえ本項主=師に是正（active/passive 入替え＋teacher）。すべて枝番項（D08902b・D08910a・D08929a・D09231a/b・D09851a・D10060b/c・D10176b・D10498a） |
| active の欠けた relation | 40 | `active="#NEEDID"` を補う（枝番項のみ） |
| 親族・社会で本項主 active・符号化が逆（「والد X」を son・active=本項主 等） | 32 | active/passive 入替え（うち対称関係 17） |
| 親族・社会で本項主 active・符号化は正しい（本項主が相手の father/uncle/patron 等） | 22 | active=相手 にし逆関係の subtype に |
| 「يعرف بصهر ابن الجندي」（D01435、son-in-law） | 1 | 規則52 により relative |
| killer（D04345） | 1 | 逆関係の語がないので維持 |

各ファイルに respStmt（`claude-opus-5-5-relation-unify`、2026-11-16）を追記。明細は `teacher_student_changes.tsv`・`kin_social_changes.tsv`、適用スクリプトは `unify.py`・`kin_fix.py`。

## コード
- `app.py`: 弟子を `subtype="teacher" active=本項主` で出力（従来は student）。
- `docs/browser/build.py`: 表示用の役割を「本項主が active なら逆関係」で求める（XML の値は `xml_subtype` に保持）。`app_template.html` に逆関係のラベルを追加。

## 統制外 subtype 7件の処理（Waka 裁定 2026-11-16、`vocab_fix.py`）

| 項 | 旧 | 処置 |
|---|---|---|
| D02046 | master（active=本項主） | 規則51 により patron（active=主人 #AIND-D02178） |
| D02512 | correspondent（active=本項主） | app の社会関係語彙にある対称の関係なので、active=相手 に入替えのみ |
| D01824 | praise | 人的関係ではないので relation を除去。既存の cultural event に persName（#TMP-P-000666）を付与（先例 D05997） |
| D02012・D02015 | see_also（対） | 編者の参照指示なので relation を除去し、`note type="cross-reference"`（@target）に |
| D02463×2・D06317 | educator_of | **社会関係の統制語彙に `educator` を新設**（active=養育者）。学問の伝授ではないので teacher にしない。逆の語は置かず、本項主 active を認める例外（killer と同じ） |

app.py の社会関係の選択肢に educator を追加。ブラウザは本項主が active の educator を「被養育者（ward）」として表示。

## 残る要確認
- D05634: listRelation の外に自己参照の possible_identity（active=passive=本項主）

## 独立校閲（claude-fable-5-2、2026-11-16）と反映（`review_fix.py`）
- 結論: データ変更（逆転是正14・親族社会56・統制外7・#NEEDID 40）は原文照合で誤りなし。relabel 330 件は全件照合し、意味が保たれていないのは D02097 の1件（main の時点で既に逆）。
- 反映: D02097 を是正（「ممن يتردد له الصلاح الطرابلسي ليقرئه」＝الصلاح が師）。relation 内の旧注記（「方向: 親がactive」「subtype=student の慣行」「educator_of」）と新しい向きの矛盾を、18 項の relation に改訂の注記を追記して明示。D02015 の移行で落ちた「Replaces contaminated TMP-P-000066.」を復元。
- コード: `derive_father_from_nasab` を name_only のみから作るよう変更（系譜のある full_name はラカブ等が混じるので使わない。単名の項のみ「والد＋呼称」）。بن の直後が أخت／أم／بنت／عم／خال 等なら作らない。番号の除去をフォールバックにも適用。自動生成の父は「ID再チェック」の照合対象から外す。弟子の n を師の後ろに続けて振る。family に姻戚（son-in-law・father-in-law・brother-in-law・relative）を追加。ブラウザの逆関係表を補充。
- プロンプト: educator の例を「لالاه X」に、predecessor の例を「رغب له X عن [職]」に訂正。姻戚の対応（زوج ابنته→son-in-law、صهر（向き不定）→relative 等、規則52）。
- D05634 は kin_social_changes.tsv で swap と記録されているが、active=passive=本項主のため実際は無変更（要確認として残す）。
- D03010 は respStmt が2つ（師弟の表記統一と親族の向きの統一、別々の変更の記録）。
