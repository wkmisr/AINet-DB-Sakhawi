"""Follow-up (Waka 2026-11-22): D00638 death place = Mecca; age-derived birth ranges with «بضع» recomputed with بضع = 1-9."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import set_date, path, Log, finish
from apply import add_note
LOG = Log()
f = path('D00638'); s = open(f, encoding='utf-8').read()
s = s.replace('<placeName xml:lang="ar" ref="#TMP-L-00010">الحمة</placeName>', '<placeName xml:lang="ar" ref="gn:104515">مكة</placeName>', 1)
s = s.replace('<placeName xml:lang="ar-Latn" ref="#TMP-L-00010">al-Ḥimma</placeName>', '<placeName xml:lang="ar-Latn" ref="gn:104515">Makka</placeName>', 1)
assert 'TMP-L-00010' not in re.sub(r'<note[^>]*>.*?</note>', '', s, flags=re.S)
s = add_note(s, s.index('<death'), 'Death place: «الشهير بالحمة . مات بها» — الحمة is his shuhrah; «بها» is read as Mecca (al-Makkī). Previously the reused TMP-L-00010 (إب) with the text «الحمة». (Waka ruling 2026-11-22)', lang='en')
LOG.add(f, 'Death place: reused TMP-L-00010 «الحمة» → gn:104515 Mecca («مات بها» refers to Mecca; الحمة is the shuhrah). Waka ruling 2026-11-22.')
open(f, 'w', encoding='utf-8').write(s)
for d, death, lo_age, hi_age in [('D03137', 846, 41, 49), ('D05964', 893, 31, 39), ('D06095', 859, 41, 49), ('D07057', 810, 61, 69)]:
    f = path(d); s = open(f, encoding='utf-8').read()
    m = re.search(r'<birth\b[^>]*>', s); old = m.group(0)
    o = re.search(r'notBefore-custom="0*(\d+)".*?notAfter-custom="0*(\d+)"', old)
    new = set_date(old, lo=death - hi_age, hi=death - lo_age)
    s = s[:m.start()] + new + s[m.end():]
    s = add_note(s, m.start(), 'Birth range recomputed with بضع = 1–9 (Waka ruling 2026-11-22): died %d aged %d–%d → born %d–%d (previously %s–%s).' % (death, lo_age, hi_age, death - hi_age, death - lo_age, o.group(1), o.group(2)), lang='en')
    LOG.add(f, 'Age-derived birth range recomputed with بضع = 1–9: %d–%d (was %s–%s).' % (death - hi_age, death - lo_age, o.group(1), o.group(2)))
    open(f, 'w', encoding='utf-8').write(s)
finish(LOG, 'Correction (follow-up to the 2026-11-22 rulings)', lang='en')
print(len(LOG.d))
