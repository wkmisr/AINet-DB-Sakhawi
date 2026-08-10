#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""precheck_aind_v11.py — 旧版生成XMLバッチの機械検疫(校閲前プリチェック)

v10→v11 (2026-08-09, B31成果反映):
  - WD_GN_DENYLIST 追加: Q310636(=Aichryson。ベンケイソウ科の植物属! B31 D02236でالأشرف قايتباي治世表現relationに
    流用→relation自体削除。人物参照はD-3形式=#AIND-D06305+corresp)
  - ★WD_REDIRECT 追加: Q553204(شاه رخ)→「#AIND-D03298+corresp=\"wd:Q553204\"」形式(B31 D02125で本伝D03298を確認・適用。
    D-3裁定と同型。Q553204はWD_ALLOWLIST=corresp用に残置)
  - TMP_WATCHLIST 追加: TMP-O-00108(登録=طبيب。B31で كبير أغوات السلطان/أمير سلاح/ولي عهد の3実体に流用=
    正規登録番号の複数実体流用)・TMP-O-00096(登録=نائب الحكم。B20 خادم・B31 باش مكة流用)・
    TMP-O-00107(登録=رأس نوبة。B31でالحاجب الصغير流用)・TMP-N-05471(幻番号。B31でبرسباي(主君名)とالطويل(shuhrah)の2件に流用)
  - TMP-P-000638注記にB31流用3件(الزرندي D05499/محمد بن شاه رخ D07471/بقر D02205)を追記

v9→v10 (2026-07-31, B30成果反映):
  - WD_GN_DENYLIST 追加: Q1988240(B30 D02344でجقمق المحمدي流用。正=#AIND-D02426=زوجの後夫はスルターンでなくجقمق المحمدي)・
    Q282928(B30 D02359でالمظفر أحمد治世表現に流用。治世relation自体を削除。人物本伝=#AIND-D00775)
  - GN_ALLOWLIST 追加: 304922(ملطية=Malatya。B30でWebSearch照合)
  - GN_PAIR_DENY 追加: (البحيره, 361300)・(البحيره, 359146)=B30で新変種2件(→TMP-L-00162)・
    (الماعوصه, 146313)=B30 D02367で照合不可(→TMP-L-00165)
  - TMP_WATCHLIST 追加: TMP-P-000347(زينب ابنة الكمال。B30 D02344で別のزينب=D13141に流用)・
    TMP-L-00151(مصلى المومني。B30でملطية・البحيرةの2実体に流用)・TMP-L-00154(وادي أبي عروة。B30でمصلى باب النصر流用)・
    TMP-O-00099(أمير الراكز。B22/B30でأمير عشرة=O-00101に流用)


v8→v9 (2026-07-31, B29成果+同日Waka裁定2件反映):
  - 毒wd 4件追加: Q4120025(=jet airliner。B29 D02383でالظاهر جقمق流用→正=#AIND-D02423)、
    Q1341072(=Hermann Sander。B29 D02396でجقمق流用→正=#AIND-D02423)、
    Q12190807(=Al-Farabi関連記事。B29 D02402でالأدب المفرد流用→正=wd:Q12201305)、
    Q199464(B29 D02387のdesc文中に混入=属性外だが再発監視用)
  - ★WD_REDIRECT に Q647942・Q286532・Q561219 追加(Waka裁定 2026-07-31): الظاهر جقمق=
    「#AIND-D02423+corresp=\"wd:Q647942\"」、الأشرف إينال=「#AIND-D02110+corresp=\"wd:Q286532\"」、
    جهانشاه=「#AIND-D02400+corresp=\"wd:Q561219\"」形式を正とする(قايتباي のD-3裁定と同型。B29適用済)
  - WD_ALLOWLIST 追加(B29でWebSearch実item照合済): Q647942(جقمق。corresp用)・Q553204(شاه رخ)・
    Q206231(قلعة حلب=Citadel of Aleppo)・Q12201305(الأدب المفرد)
  - GN_ALLOWLIST 追加: 361546(العريش=Arīsh)
  - GN_PAIR_DENY 追加: (العريش, 361139)・(البحيره, 358941)=いずれもB29で照合不可。
    ★البحيرة はWaka裁定(2026-07-31)により TMP-L-00162 で参照(歴史的管区に現代行政区item gn:361370 を充てない)
  - watchlist追加: TMP-P-000638(登録=ابن مكتوم الرحبي。B29でتغري برمش التركماني=D02279に流用)、
    TMP-P-000502(登録=إينال الأمير。B29でالأشرف إينال治世表現に流用=治世はrelation化しない)、
    TMP-I-00069(B17発行の未登録繰越。B29でقلعة حلب/別マドラサの2実体に流用)
  - TMP-P-000663/000664/000665 の注記にB29流用を追記

v7→v8 (2026-07-31, B28成果+B27繰越候補。D-3裁定反映):
  - Q282218(=ABC motorcycles) を WD_GN_DENYLIST に追加(B28 D02425でالمؤيد شيخ流用→正=#AIND-D03345)
  - Q412004(="D7") を WD_GN_DENYLIST に追加(B28 D02430でقايتباي流用→正=#AIND-D06305+corresp)
  - ★WD_REDIRECT 新設(D-3裁定 2026-07-31): wd:Q557847(قايتباي)の属性ref使用を検出し
    「#AIND-D06305+corresp=\"wd:Q557847\"」形式への修正を[要修正(D-3)]として報告(毒ではない)
  - watchlist追加: TMP-P-000665/000666(B20/B28発行帯。B28でブルキーニー兄弟に流用)、
    TMP-P-000663/000664 の注記更新(B28でも流用継続)、
    TMP-P-000530/000204(B27で別人流用=v8候補繰越)、TMP-N-01988(قطلي=名の一部のニスバ化元)
  - TMP-L-00153(الدشت)の別文脈流用注意を watchlist に追加(v8候補繰越)
  - GN_PAIR_DENY に (سمنود, 360980) を追加(B28 D02416で照合不可gn→正=gn:349715)


v6→v7 (2026-07-30, B26成果。全裁定済み):
  - ★Q368154 を WD_ALLOWLIST から削除し WD_GN_DENYLIST へ(実item=Sigismund Báthory。ID-Master「الأزهر」行自体が誤item
    =B25のالمنهاج=Q6806081と同型のマスタ発毒。正=wd:Q312342 Al-Azhar Mosque。マスタ清掃依頼済=要判断B26 §A-2)
  - Q28974579 を WD_GN_DENYLIST に追加(照合不可。B26 D02485でالناصر فرج流用→正=#AIND-D06160/wd:Q698037)
  - WD_ALLOWLIST に Q312342(جامع الأزهر)・Q56284343(تربة الظاهر برقوق=خانقاه فرج بن برقوق)・
    Q30685598(أحمد بن عجلان)・Q39048909(علي بن عجلان) 追加(B26でWebSearch照合済)
  - watchlist追加: TMP-P-000200/000202(登録=أحمد/علي بن「حسن بن」عجلان。B26で一世代上のابنا عجلانに流用=「一世代違い流用」型)
  - ロジック変更なし

v5→v6 (2026-07-30, B25成果):
  - Q2726390(=String Quartet No. 3) を WD_GN_DENYLIST に追加(B25 D02525でالسيرة لابن إسحاقに流用→wd:Q112671686へ)
  - GN_PAIR_DENY に ("حصن كيفا", "295470") 追加(照合不可→wd:Q756957 Hasankeyfへ)
  - WD_ALLOWLIST に Q112671686(السيرة لابن إسحاق)・Q756957(حصن كيفا) 追加(B25でWebSearch照合済)
  - watchlist追加: TMP-P-000663/000664(B19発行の関係専用person=B25で計10人に流用)、TMP-P-000655(別人流用歴B25)、
    TMP-P-000416(Note空欄・B25で別人疑い=要名寄せ)、TMP-N-00413(幻番号。النجار は TMP-N-05486)
  - ロジック変更なし

v4→v5 (2026-07-26, B24成果):
  - Q420040 を WD_GN_DENYLIST に追加(B24 D01877でقايتبايに流用・WebSearch照合不可→wd:Q557847へ)
  - ロジック変更なし(watchlist追加事由なし)

v3→v4 (2026-07-25, B22成果):
  - watchlist追加: TMP-P-000490/000634/000635/000636(関係専用person・B22で全て別人流用)、
    TMP-O-00098/00099/00100(役職の別item流用)、TMP-T-00035(幻番号)
  - Q3306083(الأشرفية قايتباイのマドラサ)を person文脈のみdeny に追加(B22でقايتباي人物に流用→wd:Q557847へ)

v2→v3 (2026-07-25, B21成果):
  - TMP-P-000618 を watchlist 追加(別人流用常習)
  - Q23975569 を全面denyから「person文脈のみdeny」へ変更(機関文脈は正当・マスタ行251と一致)
  - TMP番号の書式チェック追加(桁欠け TMP-N-0317 型を検出)
  - 連番訳混入チェックを訳頭のみ→訳文全体走査へ拡張(D01823 en「died in 799 AH」型を捕捉)

AINet-DB Researcher Pro v20.11 の検疫ロジックを、生成済み TEI-XML に後掛けする。
旧バージョン(〜v20.10)で生成されたバッチ(B20〜B33等)の校閲着手時に実行し、
「校閲者が解決すべき箇所」の一覧を機械的に洗い出す。

使い方:
    python3 precheck_aind.py --xml-dir <XMLフォルダ> --idmaster <ID-Master TSV> \
        [--corpus <0__DawForAIND_*.txt>] [--out report.md]

チェック内容(v20.11 app.py と同一基準):
  1. 既知汚染/要注意 TMP 番号(watchlist: 066/087/127/632/633/004/258/513 等)
  2. ID-Master 未登録 TMP(幻番号)
  3. ID-Master 登録名と XML 内の名前テキストの不一致(別人/別item流用)
  4. カテゴリ不一致(person 欄にニスバID等・要素種別と TMP 種別の齟齬)
  5. 確定毒 wd:Q(Chemical Brothers 等15件) + 未照合 wd/gn の洗い出し
  6. 汎称語(جماعة/آخرين等)の person 化
  7. 立項連番アーティファクト(没年=連番・訳頭混入) ※--corpus 指定時
"""
import argparse
import csv
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

# ================= v20.11 と同期する定数(変更時は app.py と両方更新) =================

# D-3裁定(2026-07-31): AIND本伝が同定済みの人物は ref=AIND+corresp=wd 形式を正とする。
# wd直指しは毒ではないが要修正として報告する。
WD_REDIRECT = {
    "Q557847": "#AIND-D06305 + corresp=\"wd:Q557847\" (al-Ashraf Qāytbāy。D-3裁定)",
    "Q647942": "#AIND-D02423 + corresp=\"wd:Q647942\" (al-Ẓāhir Jaqmaq。2026-07-31裁定)",
    "Q286532": "#AIND-D02110 + corresp=\"wd:Q286532\" (al-Ashraf Īnāl。2026-07-31裁定=B29 §D-8)",
    "Q561219": "#AIND-D02400 + corresp=\"wd:Q561219\" (Jahān Shāh b. Qarā Yūsuf。2026-07-31裁定=B29 §D-9)",
    "Q553204": "#AIND-D03298 + corresp=\"wd:Q553204\" (Shāh Rukh b. Tīmūr。B31適用=本伝D03298あり)",
}

WD_GN_DENYLIST = {
    "Q208507": "The Chemical Brothers(音楽)",
    "Q193272": "ECOWAS(国際機関)",
    "Q1248893": "サボテン亜種",
    "Q593290": "照合不可",
    "Q1140365": "映画イカレスラー",
    "Q940817": "1988五輪トーゴ選手団",
    "Q900871": "大川藍(タレント)",
    "Q561280": "Cassini(18C仏天文学者)",
    "Q259": "Azerbaijan非該当",
    "Q285077": "Serri(伊)",
    "Q470381": "Heliangelus(ハチドリ)",
    "Q287515": "Neumühle(独)",
    "Q802521": "B18破棄",
    "Q6835017": "ḥājib照合不可",
    "Q285640": "2-pyrrolidone(化学物質)。B20でبرسباي流用",
    "Q420040": "照合不可。B24でقايتباي流用",
    "Q2726390": "String Quartet No. 3(弦楽四重奏曲)。B25でالسيرة لابن إسحاق流用",
    "Q368154": "Sigismund Báthory(16Cトランシルヴァニア公)。★マスタ「الأزهر」行の誤item(B26 D02491で検出。マスタ清掃依頼済)",
    "Q28974579": "照合不可。B26 D02485でالناصر فرج流用",
    "Q282218": "ABC motorcycles(オートバイ)。B28 D02425でالمؤيد شيخ流用",
    "Q412004": "\"D7\"。B28 D02430でقايتباي流用",
    "Q4120025": "jet airliner(ジェット旅客機)。B29 D02383でالظاهر جقمق流用",
    "Q1341072": "Hermann Sander(墺写真家)。B29 D02396でجقمق流用",
    "Q12190807": "Al-Farabi関連記事。B29 D02402でالأدب المفرد流用",
    "Q199464": "照合不可。B29 D02387のdesc文中に混入",
    "Q1988240": "実item未照合。B30 D02344でجقمق(未亡人の後夫=جقمق المحمدي)に流用",
    "Q282928": "実item未照合。B30 D02359でالمظفر أحمد治世表現に流用(治世はrelation化しない)",
    "Q310636": "Aichryson(ベンケイソウ科植物属)。B31 D02236でقايتباي治世表現に流用(治世はrelation化しない。人物参照はD-3形式)",
}
WD_PERSON_ONLY_DENY = {
    "Q23975569": "Madrasa of al-Ashraf Barsbay(機関item)。person文脈への流用のみ毒(B18)。orgName/affiliation文脈は正当(マスタ行251)",
    "Q3306083": "المدرسة الأشرفية قايتباي(機関item)。person文脈への流用のみ毒(B22 D02340)。orgName/affiliation文脈は正当(マスタ登録あり)",
}
WD_GN_SUGGESTIONS = {
    "Q208507": "wd:Q1023470 (Ṣaḥīḥ al-Bukhārī)",
    "Q193272": "wd:Q886659 (Ṣaḥīḥ Muslim)",
    "Q1248893": "wd:Q2998769 (Jāmiʿ al-Tirmidhī)",
    "Q593290": "wd:Q947278 (Sunan Abī Dāwūd)",
    "Q1140365": "wd:Q2175237 (Sunan al-Nasāʾī)",
    "Q940817": "wd:Q1187931 (Sunan Ibn Mājah)",
    "Q900871": "wd:Q1050556 (al-Muwaṭṭaʾ)",
    "Q561280": "wd:Q557847 (Qāytbāy)",
    "Q259": "wd:Q12836408 (Azerbaijan region)",
    "Q285077": "#AIND-D02178 (al-Ẓāhir Barqūq)",
    "Q470381": "#AIND-D03345 (al-Muʾayyad Shaykh)",
    "Q287515": "#AIND-D02423 (al-Ẓāhir Jaqmaq)",
    "Q285640": "wd:Q557812 (al-Ashraf Barsbāy)",
    "Q23975569": "wd:Q557812 (al-Ashraf Barsbāy)※人物を指す場合",
    "Q420040": "wd:Q557847 (al-Ashraf Qāytbāy)",
    "Q3306083": "wd:Q557847 (Qāytbāy)※人物を指す場合",
    "Q2726390": "wd:Q112671686 (al-Sīra al-Nabawiyya li-Ibn Isḥāq)",
    "Q368154": "wd:Q312342 (Al-Azhar Mosque)",
    "Q282218": "#AIND-D03345 (al-Muʾayyad Shaykh)",
    "Q412004": "#AIND-D06305 + corresp=\"wd:Q557847\" (al-Ashraf Qāytbāy)",
    "Q28974579": "#AIND-D06160 (al-Nāṣir Faraj) / wd:Q698037",
    "Q4120025": "#AIND-D02423 (al-Ẓāhir Jaqmaq)",
    "Q1341072": "#AIND-D02423 (al-Ẓāhir Jaqmaq)",
    "Q12190807": "wd:Q12201305 (al-Adab al-Mufrad)",
    "Q1988240": "#AIND-D02426 (Jaqmaq al-Muḥammadī)",
    "Q282928": "#AIND-D00775 (al-Muẓaffar Aḥmad b. Shaykh)※relation自体の要否を先に確認",
}
WD_ALLOWLIST = {
    "Q4120128", "Q471116", "Q1023470", "Q886659", "Q2998769", "Q947278",
    "Q2175237", "Q1187931", "Q1050556", "Q12217063",
    "Q557847", "Q248996", "Q698037", "Q730299",
    "Q293604", "Q4664581", "Q4725309", "Q257745", "Q6798541", "Q12198099",
    "Q486080", "Q428858", "Q8462", "Q12836408",
    "Q82245", "Q160851", "Q191314", "Q48221",
    "Q217029", "Q484181", "Q12227702", "Q1817983", "Q1866303",
    "Q557812", "Q559146",
    "Q112671686", "Q756957",
    "Q312342", "Q56284343", "Q30685598", "Q39048909",
    "Q647942", "Q553204", "Q206231", "Q12201305",
    "Q286532", "Q561219",
}
GN_ALLOWLIST = {"360630", "109223", "104515", "170063", "170654", "358048",
                "266826", "2464915",
                "2472706", "692713", "2464470", "293100",
                "361546", "304922"}
GN_PAIR_DENY = [("سواكن", "105299"), ("سوسه", "2464917"), ("قرم", "692131"), ("حصن كيفا", "295470"),
    ("سمنود", "360980"),   # B28 D02416: 照合不可gn。正=gn:349715(Samannūd, Gharbia)
    ("العريش", "361139"),  # B29 D02383: 照合不可gn。正=gn:361546(Arīsh)
    ("البحيره", "358941"),  # B29 D02392: 照合不可gn。正=#TMP-L-00162(Waka裁定=TMP-L化。gn:361370は参考のみ)
    ("البحيره", "361370"),  # 同上: 現Beheira県item。歴史的管区への直接参照は不採用(2026-07-31裁定)
    ("البحيره", "361300"),  # B30 D02346: 新変種。→#TMP-L-00162
    ("البحيره", "359146"),  # B30 D02362: 新変種。→#TMP-L-00162
    ("الماعوصه", "146313"), # B30 D02367: 照合不可。→#TMP-L-00165
]

# 既知汚染/要注意 TMP(handover v13.0 §確定リスト由来)
TMP_WATCHLIST = {
    "TMP-O-00108": "登録=طبيب。B31で3実体(كبير أغوات السلطان→O-00126/أمير سلاح→O-00127/ولي عهد→O-00130)に流用",
    "TMP-O-00096": "登録=نائب الحكم。B20でخادم・B31でباش مكة(→O-00132)に流用",
    "TMP-O-00107": "登録=رأس نوبة(汎用canonical)。B31でالحاجب الصغير(→O-00133)に流用",
    "TMP-N-05471": "幻番号(未登録)。B31でبرسباي(主君名=削除)とالطويل(→shuhrah)の2件に流用",
    "TMP-P-000066": "汚染常習(実体=ابن الكويك D08850)。B18で3人・B19で4人に流用",
    "TMP-P-000087": "汚染常習(実体=ابن فهد D09211)",
    "TMP-P-000127": "汚染常習(実体=ابن فهد D09211)",
    "TMP-P-000166": "汚染番号(handover継承)",
    "TMP-P-000591": "汚染番号(handover継承)",
    "TMP-P-000618": "別人流用常習(登録実体=أبو بكر الديوان・D01737の父)。B21で父捏造(D01819)・مساعد بن حامد流用(D01826)",
    "TMP-P-000632": "汚染常習(実体=إسحاق D02006兄弟)。B25でもالسيد أبو القاسم(=AIND-D11070)に流用",
    "TMP-P-000663": "登録=أبو بكر(ティムールの息子・関係専用/B19発行)。B25×7・B26×3・B27×4・B28×2・B29×2(→D03090/P-000524)で別人流用(常習)",
    "TMP-P-000664": "登録=عمر(ティムールの息子・関係専用/B19発行)。B25×3・B28・B29×2(→D08044/P-000680)で別人流用",
    "TMP-P-000665": "登録=محمد خان(B20発行)。B28でD07184・B29×2(→D02423/P-000681)に流用",
    "TMP-P-000638": "登録=ابن مكتوم الرحبي。B29 D02386でتغري برمش التركماني(=D02279)に流用",
    "TMP-P-000502": "登録=إينال الأمير(父・関係専用)。B29 D02398でالأشرف إينال治世表現に流用(治世はrelation化しない)",
    "TMP-I-00069": "B17発行の未登録繰越(実体=B17機関)。B29でقلعة حلب(→wd:Q206231)と別マドラサ(→TMP-I-00078)、B30でجامع ابن ميالة・خان السليماني(いずれもaffiliation自体が誤構造=削除)に流用",
    "TMP-P-000347": "登録=زينب ابنة الكمال。B30 D02344で別のزينب(ابنة الأمين الاقصرائي=AIND-D13141)に流用",
    "TMP-L-00151": "登録=مصلى المومني。B30でملطية(→gn:304922)・البحيرة(→TMP-L-00162)の2実体に流用",
    "TMP-L-00154": "登録=وادي أبي عروة。B30 D02345でمصلى باب النصر(→TMP-L-00163)に流用",
    "TMP-O-00099": "登録=أمير الراكز。B22・B30でأمير عشرة(→TMP-O-00101)に流用",
    "TMP-P-000666": "登録=فتح الدين المحرقي。B28でالشهاب أحمد البلقيني(=D00589)に流用",
    "TMP-P-000530": "登録=علي(関係専用・独立立項なし)。B27で別人流用",
    "TMP-P-000204": "登録=حسن(D0106の息子・関係専用)。B27で別人流用",
    "TMP-N-01988": "登録=قطلي。名の一部(شرا قطلي等)のニスバ化元(B27)=nisbah切り出しの妥当性を必ず原文確認",
    "TMP-L-00153": "登録=الدشت|الدست(キプチャク草原)。B27で別文脈(別のدشت)への流用例=文脈確認必須",
    "TMP-P-000655": "登録=إبراهيم بن محمد بن عمر…。B25でالشهاب الأذرعي(=AIND-D00665)に流用",
    "TMP-P-000416": "登録=الجمال محمد(Note空欄)。B25でD02528息子(=AIND-D07337)に流用・名寄せ要確認",
    "TMP-P-000200": "登録=أحمد بن حسن بن عجلان(D02560の兄弟)。B26で一世代上のأحمد بن عجلان(=wd:Q30685598)に流用",
    "TMP-P-000202": "登録=علي بن حسن بن عجلان(同上)。B26で一世代上のعلي بن عجلان(=wd:Q39048909)に流用",
    "TMP-N-00413": "幻番号(未登録)。النجار には TMP-N-05486(B25発行)",
    "TMP-P-000633": "汚染流用歴(実体=يوسف العجمي)",
    "TMP-P-000004": "جماعة(汎称)。個人relationに使用不可",
    "TMP-P-000065": "العامة(汎称的擬似person)。運用方針要確認",
    "TMP-P-000258": "登録=عبد الله بن جماعة。ابن اللبودي(=D12697)への流用歴",
    "TMP-P-000513": "登録=تاج الدين ابن الجيعان。誤brother流用歴(B19)",
    "TMP-P-000550": "登録=علي(共同朗誦者HOLD)。一人称عليَّ誤読の流用先になりがち",
    "TMP-O-00038": "幻番号(未登録)。عشرات には TMP-O-00101",
    "TMP-O-00092": "رأس نوبة كبير(筆頭職)。汎用رأس نوبة は TMP-O-00107",
    "TMP-O-00096": "نائب الحكم。خادم への流用歴",
    "TMP-I-00066": "ダマスクスのマドラサ。مسجد نبوي/مصلى への流用歴",
    "TMP-I-00058": "الشرابشية。تربة الماس(=TMP-I-00070)への流用歴",
    "TMP-N-05395": "اردباي(≠أردباسي=TMP-N-03501)",
    "TMP-N-02166": "الانباسي(≠المومني)",
    "TMP-N-04779": "الاقتمري。اليشبكي(=TMP-N-00479)との桁転倒流用歴",
    "TMP-L-00014": "未登録幻(破棄済)。وادي الآبار には TMP-L-00155(B22発行)",
    "TMP-P-000490": "登録=عبد الله(al-Zuhrīの祖父)。名のみ父への流用歴(B22 D02337=関係ごと削除)",
    "TMP-P-000634": "登録=العز السنباطي。ابن قديد(=AIND-D05925)への流用歴(B22)",
    "TMP-P-000635": "登録=أم أحمد النحريري(女性)。ملا شيخ(=TMP-P-000670)への流用歴(B22)",
    "TMP-P-000636": "登録=مصطفى بن بقطمر الحنفي。خضر بن شماف(=AIND-D02845)への流用歴(B22)",
    "TMP-O-00098": "登録=جابي。B22でأمير عشرة(→O-00101)/المؤدب(→O-00111)に2件流用",
    "TMP-O-00099": "登録=أمير الراكز。汎用رأس نوبة(=O-00107)への流用歴(B22)",
    "TMP-O-00100": "登録=رأس نوبة الجمدارية。رأس نوبة ثاني(=O-00110)への流用歴(B22)",
    "TMP-T-00035": "幻番号(未登録)。صحيح البخاري には wd:Q1023470",
}

# 要素コンテキスト → 期待される参照種別
#   P=TMP-P/AIND/wd(person), N=TMP-N, O=TMP-O/wd, L=TMP-L/gn/wd,
#   I=TMP-I/wd, T=TMP-T/wd, S=TMP-S/wd
EXPECTED = {
    "relation.active": "P", "relation.passive": "P",
    "persName.ref": None,  # 文脈依存(nisbah→N / Pattern A persName→P)
    "state.ref": "O",
    "affiliation.ref": "I",  # madhhab は wd で例外処理
    "placeName.ref": "L",
    "bibl.ref": "T",
    "desc.ref": "S",
}
PREFIX_OK = {
    "P": ("TMP-P-", "AIND-", "#AIND-", "#TMP-P-", "wd:"),
    "N": ("TMP-N-", "#TMP-N-"),
    "O": ("TMP-O-", "#TMP-O-", "wd:"),
    "L": ("TMP-L-", "#TMP-L-", "gn:", "wd:"),
    "I": ("TMP-I-", "#TMP-I-", "wd:", "gn:"),
    "T": ("TMP-T-", "#TMP-T-", "wd:"),
    "S": ("TMP-S-", "#TMP-S-", "wd:"),
}

_GENERIC_RE = re.compile(
    r"^(?:جماعه(?: من .{0,60})?|(?:و)?غيره(?:م|ما|ن)?|(?:و)?اخر(?:ون|ين)"
    r"|غير واحد(?:ه)?|جمع(?: من .{0,60})?|خلق(?: كثير)?|الناس|العامه)$"
)

_AR_TR = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
                        "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})
_AR_DIA = re.compile(r"[ً-ٰٟ]")


def norm_ar(s):
    if not s:
        return ""
    s = str(s).strip().translate(_AR_TR)
    s = _AR_DIA.sub("", s)
    return re.sub(r"\s+", " ", s)


def load_idmaster(path):
    """TSV → {id: {"alts": [正規化名...], "raw_ar": 原文, "category": str}}"""
    idmap = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 5:
                continue
            cat = (row[1] or "").strip()
            ar = (row[2] or "").strip()
            idv = (row[4] or "").strip()
            if not idv:
                continue
            alts = [norm_ar(a) for a in ar.split("|")]
            alts = [a for a in alts if a]
            if idv not in idmap:
                idmap[idv] = {"alts": alts, "raw_ar": ar, "category": cat}
    return idmap


def strip_ref(v):
    v = (v or "").strip()
    return v[1:] if v.startswith("#") else v


def classify(v):
    """参照値の種別: TMP / AIND / WD / GN / OTHER"""
    if v.startswith("TMP-"):
        return "TMP"
    if v.startswith("AIND-"):
        return "AIND"
    m = re.match(r"^(?:wd:)?(Q\d+)$", v)
    if m:
        return "WD"
    m = re.match(r"^(?:gn:)?(\d+)$", v)
    if m:
        return "GN"
    return "OTHER"


def nearest_name(elem, attr_holder):
    """参照の近傍にあるアラビア語名テキストを拾う(照合用・ベストエフォート)"""
    # 自要素のテキスト(persName/placeName/bibl/orgName/label)
    tag = attr_holder.tag
    if tag in ("persName", "placeName", "bibl", "orgName"):
        return (attr_holder.text or "").strip()
    if tag == "state":
        for lab in attr_holder.findall("label"):
            if lab.get("{http://www.w3.org/XML/1998/namespace}lang") == "ar":
                return (lab.text or "").strip()
    if tag == "relation":
        for desc in attr_holder.findall("desc"):
            if desc.get("type") is None:
                return (desc.text or "").strip()
    if tag == "affiliation":
        for org in attr_holder.findall("orgName"):
            if org.get("{http://www.w3.org/XML/1998/namespace}lang") == "ar":
                return (org.text or "").strip()
    return ""


def expected_kind(holder, attr, parent_map):
    tag = holder.tag
    if tag == "relation" and attr in ("active", "passive"):
        return "P"
    if tag == "persName" and attr == "ref":
        if holder.get("type") == "nisbah":
            return "N"
        parent = parent_map.get(holder)
        if parent is not None and parent.tag == "event":
            return "P"  # Pattern A の言及者
        return "P"
    if tag == "state":
        return "O"
    if tag == "placeName":
        return "L"
    if tag == "bibl":
        return "T"
    if tag == "affiliation":
        return "I"
    if tag == "desc":
        return "S"
    return None


def check_file(path, idmap, corpus_index):
    findings = []
    text = open(path, encoding="utf-8").read()
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return [("PARSE", f"XML 解析失敗: {e}", "")]

    parent_map = {c: p for p in root.iter() for c in p}
    aind_id = root.get("{http://www.w3.org/XML/1998/namespace}id", "")

    for holder in root.iter():
        for attr in ("active", "passive", "ref", "target", "corresp"):
            raw = holder.get(attr)
            if not raw:
                continue
            v = strip_ref(raw)
            kind = classify(v)
            exp = expected_kind(holder, attr, parent_map)
            name = nearest_name(holder, holder)
            loc = f"{holder.tag}/@{attr}"

            if kind == "TMP":
                # (0) 書式チェック(桁欠け TMP-N-0317 型)
                if not re.match(r"^TMP-(?:P-\d{6}|[ONILTS]-\d{5})$", v):
                    findings.append(("TMP書式不正",
                                     f"{loc} = {raw} — 正書式は TMP-P-xxxxxx(6桁)/その他 xxxxx(5桁)", v))
                # (1) watchlist
                if v in TMP_WATCHLIST:
                    findings.append(("汚染注意", f"{loc} = {raw} — {TMP_WATCHLIST[v]}"
                                     + (f"(名前: {name})" if name else ""), v))
                # (2) 未登録(幻)
                if v not in idmap and not re.match(r"^TMP-[A-Z]-0+$", v):
                    findings.append(("幻番号", f"{loc} = {raw} — ID-Master 未登録"
                                     + (f"(名前: {name})" if name else ""), v))
                # (3) 名前不一致
                elif v in idmap and name:
                    alts = idmap[v]["alts"]
                    if alts and norm_ar(name) not in alts:
                        findings.append(("名前不一致",
                                         f"{loc} = {raw}(登録: {idmap[v]['raw_ar']}) ≠ 記載名「{name}」", v))
                # (4) カテゴリ
                if exp and not v.startswith(tuple(p for p in PREFIX_OK[exp] if p.startswith("TMP"))) \
                        and v.startswith("TMP-"):
                    findings.append(("カテゴリ不一致",
                                     f"{loc} = {raw} — この位置の期待種別は {exp}", v))
            elif kind == "WD":
                q = re.match(r"^(?:wd:)?(Q\d+)$", v).group(1)
                if q in WD_PERSON_ONLY_DENY:
                    if exp == "P":
                        sug = WD_GN_SUGGESTIONS.get(q, "")
                        findings.append(("毒wd", f"{loc} = {raw} — {WD_PERSON_ONLY_DENY[q]}"
                                         + (f" → 候補: {sug}" if sug else ""), q))
                elif q in WD_GN_DENYLIST:
                    sug = WD_GN_SUGGESTIONS.get(q, "")
                    findings.append(("毒wd", f"{loc} = {raw} — {WD_GN_DENYLIST[q]}"
                                     + (f" → 候補: {sug}" if sug else ""), q))
                elif q in WD_REDIRECT and attr != "corresp":
                    # corresp="wd:..." は裁定形式そのもの=正。ref/active/passive等の直指しのみ要修正
                    findings.append(("要修正(D-3)", f"{loc} = {raw} — → {WD_REDIRECT[q]}", q))
                elif q in idmap and name:
                    alts = idmap[q]["alts"]
                    if alts and norm_ar(name) not in alts:
                        findings.append(("名前不一致",
                                         f"{loc} = {raw}(登録: {idmap[q]['raw_ar']}) ≠ 記載名「{name}」", q))
                elif q not in WD_ALLOWLIST and q not in idmap:
                    findings.append(("要照合wd", f"{loc} = {raw}"
                                     + (f"(名前: {name})" if name else "")
                                     + " — WebSearch で実item名を照合", q))
            elif kind == "GN":
                g = re.match(r"^(?:gn:)?(\d+)$", v).group(1)
                hit_pair = False
                for word, bad in GN_PAIR_DENY:
                    if g == bad and word in norm_ar(name):
                        findings.append(("毒gn", f"{loc} = {raw} — 既知誤指し(名前: {name})", g))
                        hit_pair = True
                if not hit_pair and g not in GN_ALLOWLIST and g not in idmap:
                    findings.append(("要照合gn", f"{loc} = {raw}"
                                     + (f"(名前: {name})" if name else "")
                                     + " — 実地名を照合", g))

        # (6) 汎称語 person 化(relation の desc 名)
        if holder.tag == "relation":
            for desc in holder.findall("desc"):
                if desc.get("type") is None:
                    nm = norm_ar(desc.text or "")
                    protected = (" بن " in f" {nm} ") or nm.startswith(("ابن ", "بن "))
                    if nm and not protected and _GENERIC_RE.match(nm):
                        findings.append(("汎称person化",
                                         f"relation desc =「{desc.text.strip()}」— 関係ごと削除を検討", nm))

    # (7) 立項連番アーティファクト
    if corpus_index and aind_id in corpus_index:
        serial = corpus_index[aind_id]
        if serial:
            for death in root.findall("death"):
                y = (death.get("when-custom") or "").split("-")[0].lstrip("0")
                if y and y == serial.lstrip("0"):
                    findings.append(("連番=没年",
                                     f"death when-custom={death.get('when-custom')} が立項連番 {serial} と一致 — 原文に年の記載があるか要確認", serial))
            for birth in root.findall("birth"):
                y = (birth.get("when-custom") or "").split("-")[0].lstrip("0")
                if y and y == serial.lstrip("0"):
                    findings.append(("連番=生年",
                                     f"birth when-custom={birth.get('when-custom')} が立項連番 {serial} と一致", serial))
            for note in root.findall("note"):
                if note.get("type") == "translation":
                    t = (note.text or "").strip()
                    lang = note.get("{http://www.w3.org/XML/1998/namespace}lang", "")
                    if re.match(r"^0*" + re.escape(serial) + r"(?![0-9])", t):
                        findings.append(("連番訳混入",
                                         f"translation({lang}) が「{t[:18]}…」で開始 — 立項連番 {serial} の混入疑い", serial))
                    else:
                        m2 = re.search(r"(?<![0-9])" + re.escape(serial) + r"(?![0-9])", t)
                        if m2:
                            s2 = max(0, m2.start() - 10)
                            findings.append(("連番訳混入疑い",
                                             f"translation({lang}) 中に立項連番 {serial} が出現(「…{t[s2:m2.end() + 10]}…」)— 生没年扱いされていないか原文と要突合", serial))

    return findings


def build_corpus_index(corpus_path):
    """corpus から {AIND-Dxxxxx: 立項連番 or ""} を構築"""
    idx = {}
    pat = re.compile(r"###\$(AIND-D\d+)\s*\|\s*\d+\$#\s*\${1,3}\s+(?:(\d{1,4})(?=\s))?")
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            m = pat.search(line)
            if m:
                idx[m.group(1)] = m.group(2) or ""
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml-dir", required=True)
    ap.add_argument("--idmaster", required=True)
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    idmap = load_idmaster(args.idmaster)
    corpus_index = build_corpus_index(args.corpus) if args.corpus else {}

    files = sorted(glob.glob(os.path.join(args.xml_dir, "*.xml")))
    lines = [f"# プリチェック検疫レポート", "",
             f"- 対象: {args.xml_dir}({len(files)}ファイル) / ID-Master: {os.path.basename(args.idmaster)}",
             f"- 判定基準: v20.11.1同等+v9拡張(v3〜v8+毒wd Q4120025/Q1341072/Q12190807/Q199464・WD_REDIRECT Q647942(جقمق裁定)・watchlist P638/P502/I-00069・gn 361139/358941/361370ペア)", ""]
    total = 0
    counts = {}
    for fp in files:
        findings = check_file(fp, idmap, corpus_index)
        if not findings:
            continue
        lines.append(f"## {os.path.basename(fp)}")
        for tag, msg, _key in findings:
            lines.append(f"- **[{tag}]** {msg}")
            counts[tag] = counts.get(tag, 0) + 1
            total += 1
        lines.append("")
    summary = " / ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    lines.insert(4, f"- 検出合計: **{total} 件**({summary})")
    report = "\n".join(lines)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(report)
        print(f"written: {args.out}({total} findings)")
    else:
        print(report)


if __name__ == "__main__":
    main()
