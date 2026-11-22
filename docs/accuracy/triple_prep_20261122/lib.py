"""Helpers for the 2026-11-22 fixes: text-level edits that keep each file's formatting."""
import glob, re

def jd(y, m, d):
    return (11*y+3)//30 + 354*y + 30*m - (m-1)//2 + d + 1948440 - 385

def g(J):
    a = J + 32044; b = (4*a+3)//146097; c = a - 146097*b//4
    d = (4*c+3)//1461; e = c - 1461*d//4; m = (5*e+2)//153
    return (100*b + d - 4800 + m//10, m + 3 - 12*(m//10), e - (153*m+2)//5 + 1)

def ce(ah, end=False):
    """AH 'YYYY' / 'YYYY-MM' / 'YYYY-MM-DD' -> CE string at the same precision (start, or end if end=True)."""
    p = [int(x) for x in str(ah).split('-')]
    y = p[0]
    if len(p) == 1:
        J = jd(y + 1, 1, 1) - 1 if end else jd(y, 1, 1)
        return '%04d' % g(J)[0]
    if len(p) == 2:
        m = p[1]
        J = (jd(y + 1, 1, 1) - 1 if m == 12 else jd(y, m + 1, 1) - 1) if end else jd(y, m, 1)
        Y, M, _ = g(J); return '%04d-%02d' % (Y, M)
    Y, M, D = g(jd(*p)); return '%04d-%02d-%02d' % (Y, M, D)

def pad(ah):
    p = str(ah).split('-'); p[0] = '%04d' % int(p[0]); return '-'.join(p)

DATE_ATTRS = ('when', 'when-custom', 'notBefore', 'notAfter', 'notBefore-custom', 'notAfter-custom')

def set_date(tag, when=None, lo=None, hi=None, drop_cert=False):
    """Rewrite the date attributes of one start tag (string). AH values in, AH+CE attributes out."""
    for a in DATE_ATTRS:
        tag = re.sub(r'\s%s="[^"]*"' % re.escape(a), '', tag)
    if drop_cert:
        tag = re.sub(r'\scert="low"', '', tag)
    add = ''
    if when is not None:
        add = ' when-custom="%s" when="%s"' % (pad(when), ce(when))
    else:
        if lo is not None: add += ' notBefore-custom="%s"' % pad(lo)
        if hi is not None: add += ' notAfter-custom="%s"' % pad(hi)
        if lo is not None: add += ' notBefore="%s"' % ce(lo)
        if hi is not None: add += ' notAfter="%s"' % ce(hi, end=True)
    m = re.match(r'(<[\w:]+(?:\s+(?:type|subtype|n)="[^"]*")*)', tag)
    return tag[:m.end()] + add + tag[m.end():]

def path(d):
    f = glob.glob('Individuals/**/AIND-%s_*.xml' % d, recursive=True)
    assert len(f) == 1, (d, f); return f[0]

def note_before_close(s, start_idx, tagname, text):
    """Insert a ja note before the closing tag of the element whose start tag begins at start_idx."""
    end = s.index('</%s>' % tagname, start_idx)
    line_start = s.rfind('\n', 0, start_idx) + 1
    ind = s[line_start:start_idx]
    ind = ind if ind.strip() == '' else '    '
    ins = '    <note xml:lang="ja">%s</note>\n%s' % (text, ind)
    # put the note on its own line, indented one level deeper than the element
    pre = s[:end].rstrip(' ')
    if not pre.endswith('\n'): pre += '\n'
    return pre + ind + ins + '</%s>' % tagname + s[end + len('</%s>' % tagname):]

class Log:
    def __init__(self): self.d = {}
    def add(self, f, msg): self.d.setdefault(f, []).append(msg)

RS = '''    <respStmt>
        <resp xml:lang="ja">{resp}</resp>
        <persName>claude-opus-5-5-triples-20261122</persName>
        <date when="2026-11-22"/>
        <note xml:lang="ja">{note}</note>
    </respStmt>
'''

def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def finish(log, resp):
    for f, msgs in log.d.items():
        s = open(f, encoding='utf-8').read()
        i = s.rstrip().rfind('</person>')
        s = s[:i] + RS.format(resp=resp, note=esc(' '.join('(%d) %s' % (k + 1, m) for k, m in enumerate(msgs)))) + s[i:]
        open(f, 'w', encoding='utf-8').write(s)
