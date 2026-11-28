"""独立校閲（Project doc「ニスバID付け違いPR_校閲結果_20261128.md」）の要裁定を当てる（Waka 裁定 2026-11-28）。
usage: python3 fix2_20261128.py REPO

1. D00448：corpus の「البسطيني」は入力誤りで、刊本（第1巻198頁）は「البطيني」。
   父 D00236・祖父 D06535 も「ويعرف بالبطيني」。corpus とレコード（persName full・nisbah・
   relation の desc 2か所・note source）を「البطيني」に直し、ref を TMP-N-01280 に戻す。
   ops_20261128.tsv の D00448 の行（01280 → 03097）はこれで取り消し。
   TMP-N-03097（البسطيني）は誤入力から生まれた番号なので retired。
   persons_registry.tsv の D00448 の名前も直す。
2. TMP-N-05531（المحمد ابادي）の note に一族の ID を書き添える。
"""
import sys, glob
REPO = sys.argv[1]
OLD, NEW = 'البسطيني', 'البطيني'
def sub(path, old, new, n):
    t = open(path, encoding='utf-8').read()
    assert t.count(old) == n, (path, old, t.count(old))
    open(path, 'w', encoding='utf-8').write(t.replace(old, new))
# corpus
sub(f'{REPO}/0__DawForAIND_renumbered_B54_split20260905.txt',
    '###$AIND-D00448 | 315227112412$# $ أحمد بن إبراهيم بن محمد بن إبراهيم ' + OLD,
    '###$AIND-D00448 | 315227112412$# $ أحمد بن إبراهيم بن محمد بن إبراهيم ' + NEW, 1)
# record
fp, = glob.glob(f'{REPO}/Individuals/*/AIND-D00448_*.xml')
t = open(fp, encoding='utf-8').read()
rs_old = ('<note xml:lang="ja">ニスバ ID の付け違いの修正（Waka 裁定 2026-11-28）。nisbah「البسطيني」の ref を '
          '#TMP-N-01280 から #TMP-N-03097 に直した（別の語の ID だったため）。</note>')
rs_new = ('<note xml:lang="ja">ニスバ ID の付け違いの修正（Waka 裁定 2026-11-28）。見出しの「البسطيني」は corpus の入力誤りで、'
          '刊本（第1巻198頁）は「البطيني」（父 D00236・祖父 D06535 も「ويعرف بالبطيني」）。persName full・nisbah・'
          'relation の desc 2か所・note source を「البطيني」に直した。nisbah の ref は #TMP-N-01280 のまま。</note>')
assert t.count(rs_old) == 1
t = t.replace(rs_old, '@@RS@@')
assert t.count(OLD) == 5, t.count(OLD)
t = t.replace(OLD, NEW)
a = '<persName type="nisbah" xml:lang="ar" ref="#TMP-N-03097">' + NEW + '</persName>'
assert t.count(a) == 1
t = t.replace(a, a.replace('03097', '01280')).replace('@@RS@@', rs_new)
open(fp, 'w', encoding='utf-8').write(t)
# persons registry
sub(f'{REPO}/authority/persons_registry.tsv',
    'AIND-D00448\tactive\t\tأحمد بن إبراهيم بن محمد بن إبراهيم ' + OLD,
    'AIND-D00448\tactive\t\tأحمد بن إبراهيم بن محمد بن إبراهيم ' + NEW, 1)
# entities registry
REG = f'{REPO}/authority/entities_registry.tsv'
L = open(REG, encoding='utf-8').read().split('\n'); hdr = L[0].split('\t'); n = 0
for i, l in enumerate(L):
    c = l.split('\t')
    if c[0] == 'TMP-N-03097':
        assert c[hdr.index('status')] == 'active' and c[hdr.index('note')] == ''
        c[hdr.index('status')] = 'retired'
        c[hdr.index('note')] = ('【2026-11-28】corpus の入力誤り「البسطيني」（D00448。刊本は「البطيني」）から一括登録された番号。'
                                'D00448 は TMP-N-01280（البطيني）を参照する（Waka 裁定）。以後使用しない')
        L[i] = '\t'.join(c); n += 1
    elif c[0] == 'TMP-N-05531':
        c[hdr.index('note')] += (' 【2026-11-28】刊本（第3巻 807番）も「المحمد ابادى」。一族は الأحمدابادي'
                                 '（TMP-N-02516。兄弟 D03173・子 D06215）')
        L[i] = '\t'.join(c); n += 1
assert n == 2
open(REG, 'w', encoding='utf-8').write('\n'.join(L))
print('ok')
