# ★1〜★8 の TEI での書き方（案、2026-11-22）

いずれも TEI P5 の既存の属性・要素の範囲で書ける。新しい要素は作らない。

## 1. 出発地・到着地：placeName の @role
`placeName` は att.naming を持つので `@role` が使える（TEI P5）。値は `origin`・`destination`。

## 2. 出来事の関係者：event の中の persName（@role）
既存の書き方（event の中の persName、@ref）に `@role` を足す。値は `companion`（同行者）、`killer`（殺害者）、`co-victim`（同時に殺された人）、`appointer`（任じた人）など。

## 3. 繰り返し：note type="frequency"
TEI の event には頻度の属性がないので、本文の語をそのまま注記に置く。YAML へは `repeated: true` と `quote` に変換する。

## 4. 二択の場所：placeName role="alternative" ＋ cert="low"
「إما بالروم أو حلب」のように本文が二択で示す場所は、1件の event に placeName を並べ、どちらも `role="alternative"`・`cert="low"`。

## 例
★1 D00005
```xml
<event type="travel" n="1">
  <placeName ref="gn:281184" role="origin">بيت المقدس</placeName>
  <placeName ref="gn:104515" role="destination">مكة</placeName>
  <persName ref="#TMP-P-000005" role="companion">الزين عبد القادر النووي المقدسي</persName>
  <note type="frequency" xml:lang="ar">يكثر</note>
</event>
```
★8 D02136（行き先ごとの件数はそのまま）
```xml
<event type="travel" n="1">
  <placeName ref="gn:104515" role="destination">مكة</placeName>
  <note type="frequency" xml:lang="ar">يكثر السفر</note>
</event>
<event type="travel" n="2">
  <placeName ref="gn:361058" role="destination">الاسكندرية</placeName>
  <note type="frequency" xml:lang="ar">يكثر السفر</note>
</event>
```
★2 D01363
```xml
<event type="residence" n="1" when-custom="897">
  <placeName ref="TMP-L-00038" role="alternative" cert="low">الروم</placeName>
  <placeName ref="gn:170063" role="alternative" cert="low">حلب</placeName>
  <note xml:lang="ja">本文は「إما بالروم أو حلب」の二択（897年時点の居所）。</note>
</event>
```
