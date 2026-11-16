"""記録単位の付け替え案（流用・統合・汎用化）を作る"""
import glob, re, json, csv, os, collections
W = '/home/claude/work/'; ROOT = '/home/claude/ainet-db-sakhawi/'
acts = {o['id']: o for o in json.load(open(W + 'office_actions.json'))}
O = lambda n: 'TMP-O-%05d' % n
NEW = {'NEW-1': ('تاجر المماليك', '行政・財務'), 'NEW-2': ('خليفة (شيخ الطريقة)', '宗教・学術職'),
       'NEW-3': ('الإعلام بالموتى | الدوران للإعلام بالموتى', '職業・生業'), 'NEW-4': ('شيخ المقادسة', '統治者・首長'),
       'NEW-5': ('رأس المعاملين (حمل اللحم للمماليك)', '職業・生業'), 'NEW-6': ('نظر الأوصياء', '司法')}
# 流用の付け替え（aind, 旧ID, ラベル先頭） → (新ID or 'DELETE', 根拠, 要判断)
C = {
 ('D00200', 14): (O(171), 'مقرئ في الجوق＝قارئ الجوق', ''),
 ('D00225', 14): ('NEW-1', 'تاجر المماليك は宮廷の職（マムルーク購入係）', ''),
 ('D00227', 14): ('DELETE', 'صاحب المدرسة＝学院の創建者で職ではない（施設との関係は note か affiliation）', '★'),
 ('D00241', 14): (O(101), 'أمرة عشرة', ''), ('D00413', 14): (O(101), 'أحد العشرات', ''),
 ('D02010', 14): (O(101), 'إمرة عشرة', ''), ('D02088', 14): (O(101), 'أمير (عشرة)', ''), ('D02092', 14): (O(101), 'أمير عشرة', ''),
 ('D00400', 14): (O(163), 'صاحب سيواس＝統治者', ''),
 ('D00406', 14): ('NEW-2', 'خليفة الشيخ علي كهنفوشي＝スーフィーのハリーファ', '★'),
 ('D00463', 17): (O(311), 'قطان', ''), ('D00464', 17): (O(353), 'أحد الخدام في ضريح الليث → خادم＋施設', ''),
 ('D00485', 17): ('DELETE', '原文は「اشتغل عند الكافياجي」（学んだ）で職の記述なし', ''),
 ('D00486', 17): ('wd:Q7492880', 'مشيخة الزمامية → مشيخة＋施設', ''),
 ('D00705', 17): ('DELETE', '「كتب في الاستدعاآت」＝イジャーザ請求書に署名（学術活動で職ではない）', '★'),
 ('D00708', 17): (O(205), 'حائك', ''),
 ('D00717', 17): ('DELETE', 'المدير は見出しの通称。職は「الدوران للأعلام بالموتى」（別 state）', ''),
 ('D00719', 17): (O(108), 'أحد الأطباء', ''), ('D00725', 17): (O(163), 'صاحب جازان', ''),
 ('D00730', 17): (O(88), 'انتهت إليه رياسة هذا الشأن（رياسة الإقراء）', ''),
 ('D00717', 18): ('NEW-3', '「تكسب … بالدوران للأعلام بالموتى」（死亡の触れ回り）', ''),
 ('D00700', 76): (O(265), 'شيخ زاوية → 汎用 شيخ زاوية＋施設', ''),
 ('D00774', 31): (O(390), '「باشر في ديوان السلطان」→ مباشر＋施設', ''),
 ('D00529', 77): ('NEW-4', 'شيخ المقادسة（エルサレム出身者集団の長）', '★'),
 ('D00565', 77): (O(15), 'أحد خواص الظاهر＝خاصكي', ''), ('D00886', 77): (O(219), 'شيخ الإقراء', ''),
 ('D00927', 77): (O(106), 'شيخ الفراشين والمداحين', ''),
 ('D01098', 77): ('NEW-5', 'رأس المعاملين الذين يحملون اللحم للمماليك', '★'),
 ('D01250', 77): (O(163), 'صاحب كجرات', ''), ('D01604', 77): ('NEW-6', 'ولي نظر الأوصياء', ''),
 ('D01670', 77): (O(146), 'رياسة قراء الجوق', ''), ('D01692', 77): (O(373), 'قاضي الجماعة', ''),
 ('D01998', 77): (O(244), 'نائب كاتب السر', ''),
 ('D01106', 2): (O(171), 'أحد قراء الجوق', ''),
 ('D01512', 2): ('DELETE', '「وخلف والده بسعيد السعداء」は父の職を継いだという記述で職名なし（note に移す）', '★'),
 ('D01732', 2): (O(353), '「خدمة السيد قاضي الحنابلة」→ خادم（patron relation の追加は別途）', '★'),
 ('D02072', 2): (O(69), 'ولاه أبوه أذربيجان → والي＋地名', ''),
}
out = []; used = set()
for f in sorted(glob.glob(ROOT + 'Individuals/*/AIND-D*.xml')):
    me = re.search(r'AIND-(D\w+?)_', f).group(1); t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'<state\b([^>]*)>(.*?)</state>', t, re.S):
        r = re.search(r'ref="#?([^"]+)"', m.group(1))
        if not r: continue
        ref = r.group(1); ref = ('TMP-O-' + ref.split('TMP-O-')[1]) if 'TMP-O-' in ref else ref
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', m.group(2)) or [''])[0]
        has_q = bool(re.search(r'<(placeName|orgName)\b', m.group(2)))
        n = int(ref[-5:]) if ref.startswith('TMP-O-') else None
        row = None
        if (me, n) in C and (me, n) not in used:
            new, why, flag = C[(me, n)]; used.add((me, n))
            row = ('流用', new, why, flag)
        elif ref == O(53) and 'قلعة' in lab:
            row = ('汎用化', O(338), 'نائب القلعة は制度上の職名（00338 に集約）', '')
        elif ref in acts and acts[ref]['action'] == 'merge':
            row = ('統合', acts[ref]['target'], f'{acts[ref]["arabic"]} は {acts[ref]["target"]} と同じ職', '')
        elif ref in acts and acts[ref]['action'] == 'collapse':
            tgt = acts[ref]['target']
            row = ('汎用化', tgt, f'「{acts[ref]["arabic"]}」→ 汎用職＋場所・施設', '' if has_q else '要: 場所・施設を補う')
        if row:
            kind, new, why, flag = row
            out.append(dict(aind='AIND-' + me, label=lab, old=ref, new=new, kind=kind, reason=why,
                            has_place_or_org='yes' if has_q else 'no', flag=flag))
missing = set(C) - used
print('changes', len(out), collections.Counter(o['kind'] for o in out), 'unused contamination keys', missing)
print('need qualifier', sum(1 for o in out if o['flag'].startswith('要')))
json.dump(out, open(W + 'office_records.json', 'w'), ensure_ascii=False)
json.dump(NEW, open(W + 'office_new.json', 'w'), ensure_ascii=False)
