#!/usr/bin/env python3
"""Two works were cited by the Wikidata item of one printed edition; point them at the item of the work.
Also write verdicts for the flagged rows of the review queue. WK 裁定 2026-11-28.

  apply.py apply
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'authority'))
import build_authority as B

DATE = '2026-11-28'
MOVE = {'wd:Q120635850': 'wd:Q6058980',    # مقدمة ابن الصلاح: Dār al-Fikr 1986 edition -> the work
        'wd:Q115616574': 'wd:Q12236919'}   # لامية الأفعال: an edition in a series -> the work
TAG = re.compile(r'<(\w+)\b[^<>]*>')
ATTR = re.compile(r'\b(ref|active|passive)="([^"]*)"')
VERDICTS = [  # uri, verdict, seen_label, note
    ('wd:Q6058980', 'OK', 'مقدمة ابن الصلاح (Introduction to the Science of Hadith)', '著作の項目。WK が指定、Wikidata で確認（كتاب من تأليف ابن الصلاح）'),
    ('wd:Q120635850', '付替', 'مقدمة ابن الصلاح (دار الفكر، 1986م)', '刊本（版）の項目。著作は wd:Q6058980'),
    ('wd:Q12236919', 'OK', 'لامية الأفعال', '著作の項目。WK が指定、Wikidata で確認（منظومة في التصريف لابن مالك。英語ラベルなし）'),
    ('wd:Q115616574', '付替', 'لامية الأفعال (متون طالب العلم - المتون الإضافية؛ 10)', '叢書の一冊としての版の項目。著作は wd:Q12236919'),
    ('wd:Q5612976', 'OK', 'مجذوب', 'Wikidata の種別は「イスラームの用語」。職・称号の位置で使ってよい'),
    ('wd:Q25633535', '付替', '(Q12241661 のリダイレクト)', '→ wd:Q12241661（المدرسة الكاملية）。レコード・典拠表は 2026-11-06 に付替え済み'),
    ('wd:Q1248893', '毒', 'Rhipsalis paradoxa subsp. septentrionalis', '拒否リスト。جامع الترمذي の誤番号。正は wd:Q2998769。使用 0'),
    ('wd:Q470381', '毒', 'Heliangelus amethysticollis', '拒否リスト。المؤيد شيخ の誤番号。正は AIND-D03345。使用 0'),
    ('wd:Q310636', '毒', 'Aichryson', '拒否リスト。قايتباي の治世表現に流用された番号。使用 0'),
    ('wd:Q593290', '毒', '(Wikidata に存在しない)', '拒否リスト。سنن أبي داود の誤番号。正は wd:Q947278。使用 0'),
    ('wd:Q420040', '毒', '(Wikidata に存在しない)', '拒否リスト。قايتباي の誤番号。正は AIND-D06305。使用 0'),
    ('wd:Q259', '毒', '(Wikidata に存在しない)', '拒否リスト。アゼルバイジャンの誤番号。正は wd:Q12836408。使用 0'),
    ('wd:Q561280', '毒', 'César-François Cassini de Thury', '拒否リスト。قايتباي の誤番号。正は AIND-D06305。使用 0'),
    ('wd:Q900871', '毒', 'Ai Ōkawa', '拒否リスト。الموطأ の誤番号。正は wd:Q1050556。使用 0'),
    ('wd:Q311637', '毒', 'Louis Philippe II, Duke of Orléans', 'ابن تيمية に付いていた誤番号。正は wd:Q491558（Waka 照合 2026-09-24）。使用 0'),
    ('wd:Q802521', '毒', '(railway line in Sudan)', '拒否リスト（B18 破棄）。使用 0'),
    ('wd:Q6835017', '毒', '(ラベルなし)', '拒否リスト。حاجب の照合不可の番号。使用 0'),
]

def main():
    rows, n = [], 0
    for d, _, fs in sorted(os.walk(os.path.join(ROOT, 'Individuals'))):
        for f in sorted(fs):
            if not f.endswith('.xml'): continue
            p = os.path.join(d, f); t = open(p, encoding='utf-8', newline='').read()
            own = re.search(r'<person\b[^>]*xml:id="([^"]+)"', t)[1]; done = []
            def tag(m):
                def attr(a):
                    vals = a[2].split(); new = [MOVE.get(v, v) for v in vals]
                    for v, x in zip(vals, new):
                        if v != x: rows.append(dict(record=own, element=m[1], attribute=a[1], old=v, new=x)); done.append((v, x))
                    return f'{a[1]}="{" ".join(new)}"'
                return ATTR.sub(attr, m[0])
            new = TAG.sub(tag, t)
            if done:
                what = '、'.join(f'{v} → {x}' for v, x in sorted(set(done)))
                note = (f'著作の番号の付け替え（WK 裁定 {DATE}）。刊本（版）の Wikidata 項目を指していた参照を、著作の項目に付け替えた（{len(done)}か所：{what}）。')
                stmt = (f'    <respStmt><resp xml:lang="ja">修正</resp><note xml:lang="ja">{note}</note>'
                        f'<persName>claude-fable-5-2-workids-20261128</persName><date when="{DATE}"/></respStmt>\n')
                i = new.rindex('</person>'); open(p, 'w', encoding='utf-8', newline='').write(new[:i] + stmt + new[i:]); n += 1
    open(os.path.join(HERE, 'changes.tsv'), 'w', encoding='utf-8', newline='').write(B.dump(rows, ['record', 'element', 'attribute', 'old', 'new']))
    ent = B.read_tsv(B.ENT); E = {r['id']: r for r in ent}
    def hist(r, s): r['history'] = (r['history'] + ' | ' if r['history'] else '') + f'{DATE} WK 裁定（著作の番号）: ' + s
    for old, new in MOVE.items():
        r = E[old]; r['status'] = 'merged'; r['target'] = new
        hist(r, f'Wikidata の項目は刊本（版）で著作ではない。著作の項目 {new} に統合。番号は使わない')
    w = E['wd:Q6058980']
    w['variants'] = ' | '.join(x for x in [w['variants'], 'علوم الحديث لابن صلاح', 'مقدمة ابن صلاح', 'مقدمة ابن الصلاح'] if x)
    hist(w, 'wd:Q120635850（刊本の項目）を統合。異表記を引き継いだ')
    assert 'wd:Q12236919' not in E
    o = E['wd:Q115616574']
    newrow = dict(o, id='wd:Q12236919', status='active', target='', note='ابن مالك の صرف の韻文。Wikidata に英語ラベルなし（ar: لامية الأفعال）', history='')
    hist(newrow, 'wd:Q115616574（版の項目。Waka 照合 2026-09-24、B88 D07516）に代えて著作の項目を登録')
    ent.insert(ent.index(o) + 1, newrow)
    open(B.ENT, 'w', encoding='utf-8', newline='').write(B.dump(ent, B.ENT_COLS))
    vp = os.path.join(ROOT, 'docs', 'authority', 'verified.tsv'); v = open(vp, encoding='utf-8', newline='').read()
    have = {l.split('\t')[0] for l in v.split('\n')}
    add = [x for x in VERDICTS if x[0] not in have]
    v = v.rstrip('\n') + '\n' + ''.join(f'{u}\t{vd}\t{lab}\tWK\t{DATE}\t{note}\n' for u, vd, lab, note in add)
    open(vp, 'w', encoding='utf-8', newline='').write(v)
    print('re-pointed', len(rows), 'records', n, 'verdicts added', len(add))

if __name__ == '__main__':
    if sys.argv[1:] != ['apply']: sys.exit(__doc__)
    main()
