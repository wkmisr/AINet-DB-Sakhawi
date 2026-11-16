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

## 対象外（要判断として残す）
- 統制外 subtype で本項主 active のもの: praise（D01824）・see_also（D02012）・master（D02046）・educator_of（D02463×2・D06317）・correspondent（D02512）
- D05634: listRelation の外に自己参照の possible_identity（active=passive=本項主）
