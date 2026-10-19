const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/df2482fe-47ce-4a4d-a5da-9d73e7847689_033db084-fa47-432a-8021-959d88fb4231/pptx/scripts/apply_theme.js");

// Palette and type follow the project site (wkmisr.github.io/arab-islamic-networks): night / lapis / gold on white
const THEME = {
  name: "LP12 Poster",
  headFontFace: "Cambria",
  bodyFontFace: "Arial",
  colors: {
    dk1: "000000", lt1: "FFFFFF", dk2: "0D2050", lt2: "F5F6F9",
    accent1: "1C3F8F", accent2: "D8AD52", accent3: "0D2050", accent4: "16306A",
    accent5: "8A5F0D", accent6: "D3D8E3", hlink: "1C3F8F", folHlink: "0D2050",
  },
};
const INK = "0D2050", LAPIS = "1C3F8F", NIGHT2 = "16306A", GOLDLT = "D8AD52", GOLD = "8A5F0D",
  TINT = "F5F6F9", LINE = "D3D8E3", BLACK = "000000", WHITE = "FFFFFF", BLUE = "1C3F8F", GREEN = "00FF00";

const pres = new pptxgen();
pres.defineLayout({ name: "A0P", width: 33.11, height: 46.81 });
pres.layout = "A0P";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Linked Pasts 12 poster";
pres.author = "Wakako Kumakura";

const W = 33.11, M = 1.2, CW = W - 2 * M;
const H1 = 46, BODY = 28;
const s = pres.addSlide();
s.background = { color: WHITE };

let n = 0;
function T(text, o) {
  s.addText(text, Object.assign({ isTextBox: true, fontFace: "Arial", color: BLACK, margin: 0, valign: "top", objectName: "t" + (n++) }, o));
}
function box(x, y, w, h, o) {
  s.addShape(pres.shapes.RECTANGLE, Object.assign({ x, y, w, h, fill: { color: TINT }, line: { color: LINE, width: 1 }, objectName: "box" + (n++) }, o || {}));
}
function header(num, label, x, y, w) {
  s.addShape(pres.shapes.OVAL, { x, y: y + 0.02, w: 0.95, h: 0.95, fill: { color: INK }, line: { color: INK }, objectName: "num" + num });
  T(String(num), { x, y: y + 0.02, w: 0.95, h: 0.95, fontSize: 34, bold: true, color: GOLDLT, align: "center", valign: "middle" });
  T(label, { x: x + 1.25, y, w: w - 1.25, h: 1.0, fontSize: H1, bold: true, fontFace: "Cambria", color: INK, valign: "middle" });
}
function code(txt, x, y, w, h, fs) {
  box(x, y, w, h);
  T(txt, { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: h - 0.3, fontFace: "Courier New", fontSize: fs || 18, lineSpacingMultiple: 1.08 });
}
const g = (t, o) => ({ text: t, options: Object.assign({ highlight: GREEN }, o || {}) }); // unverified → green marker
const r = (t, o) => ({ text: t, options: o || {} });

// ================= title =================
const TW = CW - 5.4;
T("Comparative Studies on Arab-Islamic Social Networks Based on Integrated Biographical Databases", { x: M, y: 0.6, w: TW, h: 0.6, fontSize: 28, bold: true, color: GOLD });
T("Encoding Arabic Biographical Dictionaries at Scale with AI and Humans in the Loop", {
  x: M, y: 1.1, w: TW, h: 2.55, fontSize: 66, fontFace: "Cambria", color: INK, valign: "middle", lineSpacingMultiple: 1.1,
});
T([r("The Evolution of a TEI-XML Pipeline for al-Sakhāwī's "), r("al-Ḍawʾ al-Lāmiʿ", { italic: true }), r(" — and its Conversion to Linked Data")], {
  x: M, y: 3.8, w: TW, h: 0.8, fontSize: 36, fontFace: "Cambria", color: BLACK, valign: "middle",
});
T("Wakako Kumakura  |  Faculty of Economics, Keio University  |  kuma@keio.jp", { x: M, y: 4.75, w: TW, h: 0.55, fontSize: 28, color: BLACK, valign: "middle" });
(function () { // network motif after the site's favicon
  const ox = W - M - 4.2, oy = 0.55, k = 4.2 / 64;
  const P = { c: [32, 31], a: [15, 18], b: [49, 16], d: [20, 49], e: [47, 45] };
  [["c", "a"], ["c", "b"], ["c", "d"], ["c", "e"], ["a", "d"], ["b", "e"]].forEach(([u, v], i) => {
    const [x1, y1] = P[u], [x2, y2] = P[v];
    s.addShape(pres.shapes.LINE, { x: ox + Math.min(x1, x2) * k, y: oy + Math.min(y1, y2) * k, w: Math.abs(x2 - x1) * k, h: Math.abs(y2 - y1) * k,
      flipV: (x2 - x1) * (y2 - y1) < 0, line: { color: GOLDLT, width: 6 }, objectName: "tie" + i });
  });
  Object.entries(P).forEach(([key, [x, y]], i) => {
    const rr = (key === "c" ? 6.5 : 4.2) * k;
    s.addShape(pres.shapes.OVAL, { x: ox + x * k - rr, y: oy + y * k - rr, w: 2 * rr, h: 2 * rr, fill: { color: key === "c" ? INK : LAPIS }, line: { color: WHITE, width: 2 }, objectName: "node" + i });
  });
})();
s.addShape(pres.shapes.LINE, { x: M, y: 5.55, w: CW, h: 0, line: { color: LINE, width: 2 }, objectName: "titlerule" });


function lead(text, y0, h, fs) {
  T(text, { x: M, y: y0, w: CW, h, fontSize: fs || 22, lineSpacingMultiple: 1.18, valign: "top" });
}

// ================= 1. goal and source =================
let y = 5.8;
header(1, "目標と史料：人名録から、中世アラビア語圏の社会的ネットワークを復元する", M, y, CW);
lead([r("中世アラビア語圏については、人物誌（MPP・PUA）、写本目録（Fihrist）、本文コーパス（OpenITI）などのデジタル資源が個別に整備されてきた。しかし共通の典拠 ID で結ばれていないため、資源をまたぐ分析はいまも手作業に頼っている。OpenITI によって大量の本文が機械可読になったいま、人物と場所を Linked Data で結べば、テキストと人のネットワークを横断する分析が大きく開ける。", {})], y + 1.0, 0.85, 18);
y += 0.9;
box(M, y + 1.1, CW, 2.05, { fill: { color: TINT }, line: { color: GOLDLT, width: 3 } });
T([r("プロジェクトの目標　", { bold: true, color: GOLD }),
   r("アラビア語の人名録を構造化した統合人物誌データベースを作り、著名人だけでなく無名の人々を含む中世アラビア語圏の社会的ネットワークが、何を資源に、いかに築かれ維持されたかを明らかにする。", { bold: true, color: INK, breakLine: true }),
   r("マムルーク朝（1250–1517）治世下のエジプトで書かれた15世紀の人名録『al-Ḍawʾ al-Lāmiʿ』と14世紀の人名録『al-Durar al-Kāmina』を TEI-XML で符号化し、既存の人物誌資源と結ぶ。", { fontSize: 22, color: BLACK })],
  { x: M + 0.35, y: y + 1.18, w: CW - 0.7, h: 1.9, fontSize: 27, lineSpacingMultiple: 1.15, paraSpaceAfter: 4, valign: "middle" });
lead([r("人名録の一項目には、一人の人物の名前・生没・師弟・移動・著作・伝達が凝縮されている（左）。その人々の足跡は、アンダルスからインドにまで及ぶ（右）。", { bold: true, color: BLUE })],
  y + 3.3, 0.5, 21);
const exW = 19.6, ex0 = y + 3.95;
T([r("一項目の例：数学者アル＝カラサーウィー（一般にはカラサーディーの名で知られる。約490語の項目からの抜粋）", { bold: true, color: INK })],
  { x: M, y: ex0, w: exW, h: 0.45, fontSize: 20 });
const CAT = [
  ["名前・出自", LAPIS, "علي بن محمد بن محمد بن علي أبو الحسن القرشي الأندلسي البسطي … المالكي ويعرف بالقلصاوي", "名・系譜・ニスバ・法学派・通称"],
  ["生年・生地", NIGHT2, "ولد قبل سنة خمس عشرة وثمانمائة في مدينة بسطة", "815年以前、バスタ（現バサ）に生まれる"],
  ["師と学問", LAPIS, "ثم إلى تلمسان سنة أربعين … فلازم الشيخ أحمد بن زاغو … ومحمد بن مرزوق", "840年トレムセンでイブン・ザーグーらに師事"],
  ["著作", GOLD, "وصنف في ذلك في تلمسان كتاب التبصرة في الغبار", "トレムセンで算術書を著す"],
  ["移動・巡礼", NIGHT2, "ثم رحل من تونس سنة خمسين فدخل القاهرة وفي التي بعدها حج", "850年チュニスからカイロへ、翌年巡礼"],
  ["伝達", GOLD, "قاله البقاعي وقال إنه أجاز له في سنة اثنتين وخمسين رواية جميع مصنفاته", "852年、ビカーイーに全著作の伝承を許可"],
  ["聴講", LAPIS, "وهو ممن سمع على شيخنا مع أبي عبد الله الراعي في سنة اثنتين وخمسين", "852年、著者の師イブン・ハジャルに聴講"],
];
const rowH1 = 0.64;
CAT.forEach(([cat, col, ar, ja], i) => {
  const yy = ex0 + 0.5 + i * rowH1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: yy + 0.06, w: 2.3, h: rowH1 - 0.12, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: "cat" + i });
  T(cat, { x: M, y: yy + 0.06, w: 2.3, h: rowH1 - 0.12, fontSize: 17, bold: true, color: WHITE, align: "center", valign: "middle" });
  T(ar, { x: M + 2.45, y: yy, w: 9.6, h: rowH1, fontSize: 17, align: "right", valign: "middle", rtlMode: true, lang: "ar-SA" });
  T(ja, { x: M + 12.25, y: yy, w: exW - 12.25, h: rowH1, fontSize: 17, valign: "middle" });
});
// map on the right
const mx = M + exW + 0.5, mw = CW - exW - 0.5, mh = mw * 2200 / 4250;
box(mx, ex0, mw, mh, { fill: { color: WHITE } });
s.addImage({ path: "map.png", x: mx + 0.04, y: ex0 + 0.04, w: mw - 0.08, h: mh - 0.08, objectName: "map" });
T("符号化済み項目に現れ、位置を特定できる69地点（言及3,280回、円は言及数、位置は都市単位の概略）。破線はアル＝カラサーウィーの移動（§3）。",
  { x: mx, y: ex0 + mh + 0.05, w: mw, h: 0.75, fontSize: 15, lineSpacingMultiple: 1.05 });
// corpus figures
const fy = ex0 + 0.5 + 7 * rowH1 + 0.2, fw = (exW - 0.6) / 4;
[["ca. 14,000 人", "立項人物（全12巻）"],
 ["1〜9,634 語", "項目の長さ。最短は名のみ、最長は著者自身の項"],
 ["中央値 46 語", "37% が30語以内。現在はこの短い項目から処理"],
 ["約132万語", "コーパス全体（アラビア文字の語）"]].forEach(([v, l], i) => {
  const bx = M + i * (fw + 0.2), by0 = fy;
  box(bx, by0, fw, 1.25);
  T(v, { x: bx + 0.18, y: by0 + 0.04, w: fw - 0.36, h: 0.5, fontSize: 24, bold: true, color: INK });
  T(l, { x: bx + 0.18, y: by0 + 0.55, w: fw - 0.36, h: 0.66, fontSize: 14, lineSpacingMultiple: 1.05 });
});

// ================= 2. pipeline =================
y = Math.max(fy + 1.3, ex0 + mh + 0.75) + 0.1;
header(2, "人間とAIの協働パイプライン", M, y, CW);
lead([r("下書きと点検を役割の異なる商用LLMに分担させ、最終判断は研究者が下す。運用を重ねながら、単一モデルによる校閲（v1）から、別モデルによる独立検証の追加（v2）、5並行の校閲と集約（v3）へと段階的に発展させてきた。", { breakLine: true }), r("金＝人間、青＝商用LLM（初版は Gemini 2.5 → 3.5 Flash、校閲以降は Claude）。箱の中の件数は直近500項目（16,089語）の記録から集計した参考値で、精度測定のために設計したデータではない。", { fontSize: 17 })],
  y + 1.1, 0.95, 21);
const steps = [
  ["原文", "OpenITI の刊本テキストを研究チームが校閲し、項目ごとに切り分ける", "src"],
  ["初版生成", "Gemini が項目を読み、名前・日付・場所・人間関係を TEI-XML の下書きにする", "ai"],
  ["機械前処理", "プログラムが、既知の誤った ID や形式の誤りを自動で拾い出す", "tool"],
  ["校閲", "Claude が5つに分けて並行に作業し、原文と典拠表に照らして下書きを直す（100項目あたり約400〜500か所）", "ai"],
  ["独立検証", "校閲に関わらなかった別の Claude が、直した結果を原文と突き合わせ、残った誤りを探す（100項目あたり38〜79件）", "ai"],
  ["集約", "検証の指摘を反映し、人の判断が要る点を一覧にする", "ai"],
  ["裁定", "研究者が判断の要る点を決め、Wikidata・GeoNames の ID を自分の目で確かめる", "human"],
];
const bw = 3.72, gap = 0.36, by = y + 2.15, bh = 2.42;
steps.forEach((st, i) => {
  const bx = M + (CW - (steps.length * bw + (steps.length - 1) * gap)) / 2 + i * (bw + gap);
  const fill = st[2] === "human" ? GOLDLT : st[2] === "ai" ? LAPIS : st[2] === "tool" ? NIGHT2 : TINT;
  const fc = (st[2] === "src" || st[2] === "human") ? INK : WHITE;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: by, w: bw, h: bh, rectRadius: 0.2, fill: { color: fill }, line: { color: st[2] === "src" ? LINE : fill, width: 1 }, objectName: "step" + i });
  T(`${i + 1}. ${st[0]}`, { x: bx + 0.15, y: by + 0.1, w: bw - 0.3, h: 0.6, fontSize: 25, bold: true, color: fc, align: "center" });
  T(st[1], { x: bx + 0.2, y: by + 0.72, w: bw - 0.4, h: bh - 0.8, fontSize: 17, color: fc, lineSpacingMultiple: 1.12 });
  if (i < steps.length - 1) s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: bx + bw + 0.05, y: by + bh / 2 - 0.25, w: 0.26, h: 0.5, fill: { color: INK }, line: { color: INK }, objectName: "arr" + i });
});
// LLM ID problem (why step 7 is manual)
// identification: what AI makes possible
const idy = by + bh + 0.2, idh = 2.2;
box(M, idy, CW, idh, { fill: { color: TINT }, line: { color: LAPIS, width: 2 } });
T([r("AI が可能にしたこと：コーパス全体にわたる人物の同定。", { bold: true, color: LAPIS }),
   r("項目の中の人物は通称やニスバだけで呼ばれ、その人自身の項目が約1万4千項目のどこにあるかは分からない。AI が全コーパスを照合して候補を示し、研究者が確定する。人手だけでは到底できない規模である。", { color: INK })],
  { x: M + 0.3, y: idy + 0.08, w: CW - 0.6, h: 0.95, fontSize: 19, lineSpacingMultiple: 1.12 });
const tw4 = (CW - 0.6 - 0.6) / 4;
[["5,493 件", "符号化済み 3,195 項目の中の人物参照（師・親族・言及など）"],
 ["2,805 件（51%）", "コーパス内の別の項目に同定（1,411人）"],
 ["約 3,200 項目", "参照先までの距離の中央値。77% は1,000項目以上離れた項目"],
 ["1,315 件", "本人の項目がない人物に仮 ID を発行（1,025人）。ほかに Wikidata 1,053件、保留 317件"]].forEach(([v, l], i) => {
  const bx = M + 0.3 + i * (tw4 + 0.2), yy = idy + 1.05;
  box(bx, yy, tw4, 1.1, { fill: { color: WHITE } });
  T(v, { x: bx + 0.2, y: yy + 0.02, w: tw4 - 0.4, h: 0.5, fontSize: 24, bold: true, color: INK });
  T(l, { x: bx + 0.2, y: yy + 0.5, w: tw4 - 0.4, h: 0.58, fontSize: 14, lineSpacingMultiple: 1.05 });
});
// accuracy (brief)
const py = idy + idh + 0.15, ph = 1.85;
box(M, py, CW, ph, { fill: { color: WHITE }, line: { color: GOLD, width: 2 } });
T([r("精度の目安（直近の200項目＝6,440語、コーパスの約0.5%。主張 4,394件を数え上げ）：", { bold: true, color: INK }),
   r("初版の誤り 932件（主張の約21%）を校閲で修正し、独立検証がさらに 89件（約2%）を検出して修正した。重大な誤りは、記録方式をそろえた最初の100項目（3,071語）の17件から、最新の100項目（3,465語）の1件へ減った。ただし対象は短い項目が中心（中央値26語、最長123語）で、長い項目での検証はこれから。", { breakLine: true }),
   r("残る課題：商用LLMは Wikidata・GeoNames の ID をうまく拾えない。", { bold: true, color: GOLD }),
   r("立項があるのに無関係の ID を付ける（ハナフィー派 → Lomske、スルターン・ジャクマク → ジェット旅客機など）。拒否リスト 31件、直近500項目（16,089語）で誤った ID 76件を修正。だから最終確認は研究者が行う。", { breakLine: true }),
   r("→ ID は LLM に生成させず検索で与える：手元の Wikidata・GeoNames 索引で候補を絞り、LLM には選択だけをさせる。ローカルLLMでも回せる構成で、照合の手作業を減らせる見込み（今後検証）。", { bold: true, color: BLUE })],
  { x: M + 0.3, y: py + 0.08, w: CW - 0.6, h: ph - 0.16, fontSize: 17, lineSpacingMultiple: 1.1, paraSpaceAfter: 3, valign: "middle" });

// ================= 3. linked data =================
y = py + ph + 0.25;
header(3, "Linked Data：一書の人物誌を、地域・時代、そしてモノへ", M, y, CW);
lead([r("符号化した全 3,195 項目を RDF に変換した。独自の URI を核に外部の典拠・目録・人物誌と結ぶと、一書の中では見えない地域・時代・モノへのつながりが現れる。", {})],
  y + 1.05, 0.5, 20);
const dy = y + 1.65, dh = 4.6;
box(M, dy, CW, dh, { fill: { color: WHITE } });
const hubW = 9.6, hubH = 2.2, hubX = W / 2 - hubW / 2, hubY = dy + 0.5;
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: hubX, y: hubY, w: hubW, h: hubH, rectRadius: 0.25, fill: { color: INK }, line: { color: INK }, objectName: "hub" });
T([r("本プロジェクトの URI", { bold: true, fontSize: 27, breakLine: true }),
   r("『al-Ḍawʾ al-Lāmiʿ』 3,195 項目 → 227,547 トリプル", { fontSize: 19, breakLine: true }),
   r("CIDOC-CRM（生没・出来事・場所）＋ 関係語彙 ＋ PROV-O（人間とAIの作業来歴）", { fontSize: 18 })],
  { x: hubX + 0.3, y: hubY + 0.12, w: hubW - 0.6, h: hubH - 0.24, color: WHITE, align: "center", valign: "middle", lineSpacingMultiple: 1.1 });
const satW = 7.6, sh = 1.2;
const LX = M + 0.3, RX = W - M - 0.3 - satW;
const sats = [
  { x: LX, y: dy + 0.2, hy: -0.7, title: "Wikidata", body: [r("人物・学派・機関 89 ID")], solid: true, link: "owl:sameAs ／ 参照" },
  { x: LX, y: dy + 1.7, hy: 0, title: "GeoNames", body: [r("地名 51 ID")], solid: true, link: "crm:P7_took_place_at" },
  { x: LX, y: dy + 3.2, hy: 0.7, title: "Fihrist（英・愛のイスラーム写本目録）", body: [r("著者典拠 10,078件（VIAF に基づく ID）")], solid: false, link: "VIAF 経由（予定）", lab: "L" },
  { x: RX, y: dy + 0.3, hy: -0.6, h: 1.75, title: "Mamluk Prosopography Project（MPP）", body: [r("ゲント大学、マムルーク朝の人物誌（"), g("2009–2021"), r("）。他史料に基づき、『ダウ』にない情報を含む")], solid: false, link: "owl:sameAs（予定）" },
  { x: RX, y: dy + 2.55, hy: 0.6, h: 1.75, title: "Prosopografía de los Ulemas de al-Andalus（PUA）", body: [r("スペイン高等科学研究院、アンダルスのウラマー人物誌（12,813人、没年 91–921/709–1515年）。『ダウ』とほとんど重ならない地域")], solid: false, link: "owl:sameAs（試行）", lab: "R" },
];
sats.forEach((st, k) => {
  const hh = st.h || sh, col = st.solid ? LAPIS : GOLD;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: st.x, y: st.y, w: satW, h: hh, rectRadius: 0.16, fill: { color: st.solid ? TINT : WHITE },
    line: { color: col, width: 3, dashType: st.solid ? "solid" : "dash" }, objectName: "sat" + k });
  T(st.title, { x: st.x + 0.22, y: st.y + 0.04, w: satW - 0.44, h: 0.48, fontSize: st.title.length > 40 ? 17 : (st.title.length > 14 ? 19 : 24), bold: true, color: col, valign: "middle" });
  T(st.body, { x: st.x + 0.22, y: st.y + 0.54, w: satW - 0.44, h: hh - 0.58, fontSize: 17, lineSpacingMultiple: 1.05 });
  const left = st.x < hubX;
  const x1 = left ? st.x + satW : st.x, y1 = st.y + hh / 2;
  const x2 = left ? hubX : hubX + hubW, y2 = hubY + hubH / 2 + st.hy;
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.max(Math.abs(y2 - y1), 0.001),
    flipV: (x2 - x1) * (y2 - y1) < 0, line: { color: col, width: 4, dashType: st.solid ? "solid" : "dash" }, objectName: "edge" + k });
  const above = st.hy <= 0 && !st.below;
  if (st.lab) { T(st.link, { x: st.lab === "L" ? x1 - 0.1 : x1 - 2.35, y: y1 + 0.12, w: st.lab === "L" ? 2.8 : 2.3, h: 0.4, fontSize: 14, bold: true, color: col, align: st.lab === "L" ? "left" : "right" }); return; }
  T(st.link, { x: Math.min(x1, x2) - 0.3, y: above ? Math.min(y1, y2) - 0.44 : Math.max(y1, y2) + 0.03, w: Math.abs(x2 - x1) + 0.6, h: 0.4, fontSize: 15, bold: true, color: col, align: "center" });
});
T([r("実装済み", { bold: true, color: LAPIS }), r("（実線）　"), r("予定・試行", { bold: true, color: GOLD }), r("（破線）")],
  { x: W / 2 - 3, y: dy + 0.05, w: 6, h: 0.42, fontSize: 15, align: "center", valign: "middle" });
(function () { // OpenITI below the hub
  const ow = hubW + 1.0, ox = W / 2 - ow / 2, oy = hubY + hubH + 0.45, oh = 1.45;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ox, y: oy, w: ow, h: oh, rectRadius: 0.16, fill: { color: TINT }, line: { color: LAPIS, width: 3 }, objectName: "satOITI" });
  T([r("OpenITI", { bold: true, fontSize: 22 }), r("　KITAB プロジェクトらが整備・公開する刊本中心のデジタル本文コーパス", { bold: true, fontSize: 15 })],
    { x: ox + 0.2, y: oy + 0.03, w: ow - 0.4, h: 0.45, color: LAPIS, valign: "middle" });
  T([r("2025.1.9 版：アラビア語 8,755点（著者 3,373人）、ペルシア語 351点（262人）、写本文書 433点。著者の比定：『ダウ』に立項 125人（800–930年没の 231人中）、符号化済み項目に人物・書物の著者として現れる 138人（うち前代 70人）、重複を除き計 198人。")],
    { x: ox + 0.2, y: oy + 0.48, w: ow - 0.4, h: oh - 0.52, fontSize: 15, lineSpacingMultiple: 1.05 });
  s.addShape(pres.shapes.LINE, { x: W / 2, y: hubY + hubH, w: 0, h: 0.45, line: { color: LAPIS, width: 4 }, objectName: "edgeOITI" });
  T([r("本文の出典（prov:wasDerivedFrom）", { color: LAPIS }), r("　著者 ID（予定）", { color: GOLD })],
    { x: W / 2 + 0.15, y: hubY + hubH + 0.02, w: 9, h: 0.42, fontSize: 14, bold: true, valign: "middle" });
})();

// --- 3b TEI | Turtle | SPARQL ---
const ry = dy + dh + 0.2, rh = 2.85;
const xW = 9.4, qW = 7.0, tW = CW - xW - qW - 0.8;
T("TEI-XML（抜粋）", { x: M, y: ry, w: xW, h: 0.4, fontSize: 19, bold: true, color: INK });
code(`<person xml:id="AIND-D04744">
 <affiliation type="madhhab" ref="wd:Q228986"/>
 <birth when-custom="0840" when="1436"
   cert="medium"/>
 <relation subtype="teacher" active="#AIND-D06936"
   passive="#AIND-D04744"><desc type="method"
   ref="#TMP-S-00003"/></relation>
 <event type="visit">
  <placeName ref="gn:360630"/></event>`, M, ry + 0.42, xW, rh - 0.42, 12);
const tx = M + xW + 0.4;
T("Turtle（同じ項目）", { x: tx, y: ry, w: tW, h: 0.4, fontSize: 19, bold: true, color: INK });
code(`aind:AIND-D04744 a crm:E21_Person ; aindv:madhhab wd:Q228986 ;
  crm:P98i_was_born aind:AIND-D04744-birth .
aind:AIND-D04744-birth a crm:E67_Birth ; aindv:certainty aindv:cert_medium ;
  crm:P4_has_time-span [ crm:P82_at_some_time_within "1436" ;
                         aindv:hijriDate "0840" ] .
aind:AIND-D06936 aindv:teacherOf aind:AIND-D04744 .      # shortcut
aind:AIND-D04744-rel-5 a aindv:Relationship ; aindv:relType aindv:teacher ;
  aindv:active aind:AIND-D06936 ; aindv:method aind:TMP-S-00003 .   # samāʿ
aind:AIND-D04744-ev-1 crm:P7_took_place_at <https://sws.geonames.org/360630/> .
rec:AIND-D04744 prov:qualifiedAttribution [ prov:agent agent:claude_b94_review ;
  prov:hadRole "校閲"@ja ; prov:atTime "2026-10-03"^^xsd:date ] .`, tx, ry + 0.42, tW, rh - 0.42, 12);
const qx = tx + tW + 0.4;
T("SPARQL（§4 の金色の点）", { x: qx, y: ry, w: qW, h: 0.4, fontSize: 19, bold: true, color: INK });
code(`SELECT ?student ?name WHERE {
  ?r aindv:relType aindv:teacher ;
     aindv:active  aind:AIND-D06936 ;
     aindv:passive ?student .
  ?student rdfs:label ?name . }
# al-Jamāl al-Kāzarūnī の弟子 → 9名、
# 全員マディーナの人。うち4名は
# ザランディー家、2名は兄弟`, qx, ry + 0.42, qW, rh - 0.42, 12);

// --- 3c PUA: same person, two dictionaries ---
const cy = ry + rh + 0.2, ch = 2.15;
box(M, cy, CW, ch, { fill: { color: TINT }, line: { color: GOLD, width: 2 } });
T([r("地域をまたぐ：", { bold: true, color: GOLD }),
   r("同じ人物を、東の『ダウ』と西の PUA が別々の側から記録している。結ぶと、互いに欠けた部分が補われ、矛盾も見えてくる。", { bold: true, color: INK })],
  { x: M + 0.25, y: cy + 0.08, w: CW - 0.5, h: 0.5, fontSize: 20 });
const hw = (CW - 0.75 - 7.6) / 2;
[["『ダウ』：カイロから見た数学者アル＝カラサーウィー", [
    r("3つの項目に現れる（本伝、短い別項、転送見出し）。カイロでの教授、イブン・ハジャルへの聴講、ビカーイーへのイジャーザを記す。短い別項は没年を「85x年」とする（"), g("同一人物と判断"), r("）。")]],
 ["PUA：アンダルス・マグリブから見た同じ人物（6245番）", [
    r("バスタ出身、グラナダに居住、トレムセン・チュニスで修学、巡礼。典拠は『ナフフ・アッ＝ティーブ』など5点で、『ダウ』は使われていない。没年 891/1486。")]]].forEach(([t, body], i) => {
  const bx = M + 0.25 + i * (hw + 0.25);
  box(bx, cy + 0.62, hw, 1.43, { fill: { color: WHITE } });
  T(t, { x: bx + 0.2, y: cy + 0.66, w: hw - 0.4, h: 0.45, fontSize: 18, bold: true, color: i === 0 ? LAPIS : GOLD });
  T(body, { x: bx + 0.2, y: cy + 1.1, w: hw - 0.4, h: 1.05, fontSize: 17, lineSpacingMultiple: 1.12 });
});
T([r("→ 一人の生涯が東西の両端からそろい、『ダウ』内部の重複項目と没年の食い違いも浮かび上がる。852年に同席した聴講者アッ＝ラーイー（853年没）も PUA に立項されている。", { bold: true, color: BLUE })],
  { x: M + 0.25 + 2 * (hw + 0.25), y: cy + 0.6, w: 7.35, h: 1.6, fontSize: 16, lineSpacingMultiple: 1.15, valign: "middle" });

// --- 3d Fihrist: person -> work -> manuscript -> owner -> library ---
const fy2 = cy + ch + 0.2, fh = 2.45;
box(M, fy2, CW, fh, { fill: { color: TINT }, line: { color: GOLD, width: 2 } });
T([r("モノへ：", { bold: true, color: GOLD }),
   r("人物誌の人物は、著作を介して現存する写本につながり、写本は後世の人々の手を経て図書館に至る。Fihrist と結ぶと、この来歴が一続きのデータとしてたどれる。", { bold: true, color: INK })],
  { x: M + 0.25, y: fy2 + 0.08, w: CW - 0.5, h: 0.85, fontSize: 20, lineSpacingMultiple: 1.1 });
const chain = [
  ["人物", "サハーウィー", "1497没。『ダウ』の著者", LAPIS],
  ["著作", "al-Ḍawʾ al-Lāmiʿ", "15世紀の人名録", LAPIS],
  ["人物", "イブン・アッ＝シャンマーウ", "1529没。後代の学者", LAPIS],
  ["写本", "MS Marsh 645", "摘要『al-Qabas al-ḥāwī』の自筆本", GOLD],
  ["人物", "マーシュ大主教", "1713没。ダブリン、のちアーマー大主教", LAPIS],
  ["図書館", "ボドリアン図書館", "オックスフォード", GOLD],
];
const verbs = ["が著す", "を要約する", "が自筆で書く", "を所蔵する", "1714年に遺贈"];
const cbw = 3.65, cgap = (CW - 0.5 - 6 * cbw) / 5, cy0 = fy2 + 0.85, cbh = 1.45;
chain.forEach(([tag, main, sub, col], i) => {
  const bx = M + 0.25 + i * (cbw + cgap);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: cy0, w: cbw, h: cbh, rectRadius: 0.14, fill: { color: i === 5 ? GOLDLT : WHITE }, line: { color: col, width: col === GOLD ? 3 : 2 }, objectName: "ch" + i });
  T(tag, { x: bx + 0.15, y: cy0 + 0.06, w: cbw - 0.3, h: 0.36, fontSize: 15, bold: true, color: col });
  T(main, { x: bx + 0.15, y: cy0 + 0.42, w: cbw - 0.3, h: 0.62, fontSize: 18, bold: true, color: INK, italic: i === 1, lineSpacingMultiple: 1.0 });
  T(sub, { x: bx + 0.15, y: cy0 + 1.0, w: cbw - 0.3, h: 0.6, fontSize: 14, lineSpacingMultiple: 1.05 });
  if (i < 5) {
    const ax = bx + cbw;
    s.addShape(pres.shapes.LINE, { x: ax + 0.05, y: cy0 + cbh / 2, w: cgap - 0.1, h: 0, line: { color: GOLD, width: 3, endArrowType: "triangle" }, objectName: "cl" + i });
    T(verbs[i], { x: ax, y: cy0 + cbh / 2 - 0.62, w: cgap, h: 0.55, fontSize: 14, bold: true, color: GOLD, align: "center", valign: "bottom" });
  }
});

// ================= 4 | 5 bottom row =================
y = fy2 + fh + 0.25;
const colW = (CW - 0.6) / 2, c2x = M + colW + 0.6, yEnd = 45.2;
header(4, "いま見えている人のつながり", M, y, colW);
header(5, "今後の目標", c2x, y, colW);
const iy = y + 1.1;
const imH = yEnd - iy, imW = Math.min(colW * 0.6, imH * 3300 / 2220);
box(M, iy, imW, imH, { fill: { color: WHITE } });
s.addImage({ path: "network_s.png", x: M + 0.04, y: iy + (imH - (imW - 0.08) * 2220 / 3300) / 2, w: imW - 0.08, h: (imW - 0.08) * 2220 / 3300, objectName: "network" });
T([r("符号化済みの短い項目だけからでも、2,216人が一つにつながる（師弟 1,871・親族 1,844 の紐帯）。最大の結節点は著者自身、次いでイブン・ハジャル。", { breakLine: true }),
   r("金色の点（§3 の SPARQL）：アル＝カーザルーニーの弟子9名は全員マディーナの人で、うち4名がザランディー家。学者家系の中で聴講が受け継がれていた。", { bold: true, color: BLUE, breakLine: true }),
   r("━ ", { color: LAPIS, bold: true }), r("師弟　"), r("━ ", { color: "C8961E", bold: true }), r("親族　"), r("● ", { color: GOLDLT }), r("SPARQL の結果")],
  { x: M + imW + 0.3, y: iy, w: colW - imW - 0.3, h: imH, fontSize: 18, lineSpacingMultiple: 1.12, paraSpaceAfter: 6, valign: "middle" });
box(c2x, iy, colW, yEnd - iy, { fill: { color: TINT }, line: { color: LINE, width: 1 } });
T([r("データを広げる", { bold: true, color: INK, fontSize: 19, breakLine: true }),
   r("対象項目を30語から70語、130語へと段階的に長くし、『ダウ』全体を処理する。続いて『al-Durar al-Kāmina』を同じモデルで符号化する。", { breakLine: true }),
   r("外とつなぐ", { bold: true, color: INK, fontSize: 19, breakLine: true }),
   r("OpenITI・MPP・PUA・Fihrist との対応づけを進め、Wikidata とは識別子プロパティの申請と、複数の人名録に共通する人物の選択的な立項でつなぐ。写本上の聴講証明書（ACP など）とも結び、伝記の「聴いた」を聴講の現場で裏づける。", { breakLine: true }),
   r("パイプラインを改良する", { bold: true, color: INK, fontSize: 19, breakLine: true }),
   r("ID は LLM に生成させず検索で与える方式に切り替え、ローカルLLMでの運用とあわせて、照合の手作業とコストがどこまで減るかを検証する。", { breakLine: true }),
   r("→ 人物・地域・時代、そしてモノを越えるネットワークから、アラビア語文化圏の社会を描き直す。", { bold: true, color: BLUE })],
  { x: c2x + 0.3, y: iy + 0.1, w: colW - 0.6, h: yEnd - iy - 0.2, fontSize: 16, lineSpacingMultiple: 1.08, paraSpaceAfter: 2, valign: "middle" });

// ================= footer =================
y = 45.4;
s.addShape(pres.shapes.LINE, { x: M, y: y - 0.05, w: CW, h: 0, line: { color: LINE, width: 2 }, objectName: "footrule" });
T([r("URI の基底 https://wkmisr.github.io/arab-islamic-networks/ は暫定（符号化完了後に w3id.org の永続 URI へ移行予定）。", { breakLine: true }),
   r("謝辞：JSPS KAKENHI 26K00196。テキストの校閲は前科研から続く研究チームが行った。前身プロジェクトでの基礎作業に協力いただいた Maxim Romanov 氏に感謝する。")],
  { x: M, y: y + 0.08, w: CW - 2.2, h: 1.2, fontSize: 18, lineSpacingMultiple: 1.1, valign: "middle" });
s.addImage({ path: "qr_site.png", x: W - M - 1.3, y: y + 0.05, w: 1.3, h: 1.3, objectName: "qr" });

s.addNotes([
  "【出典・根拠】",
  "§1：目標＝アブスト第1段落・サイトの記述。例＝corpus（0__DawForAIND_renumbered_B54_split20260905.txt）の AIND-D05552（約490語、未符号化）から抜粋。ca. 14,000＝プロジェクトサイトの表記。項目の長さ＝同 corpus の AIND 番号付き項目 13,968件（本伝 13,722・転送見出し 246）についてアラビア文字の語を数えた値（Claude 集計）：本伝の最短 1語（名のみの欠損項目、例 D11288）、最長 9,634語（D07578＝サハーウィー自身の項）、中央値 46、30語以内 5,019件（37%）、総計 1,326,798語。",
  "§2 同定：Individuals/*.xml の relation/@active と event 内 persName/@ref を集計（自項目は除く、Claude 集計）：5,493件＝AIND-D 2,805（異なり1,411）・TMP-P 1,315（異なり1,025）・wd 1,053（異なり31）・#NEEDID 317・その他3。距離＝参照元と参照先の AIND 番号の差（中央値3,208、≥1,000 が2,172/2,805）。コーパスの項目数＝AIND 番号付き13,968。\n§2 精度の対象範囲：1バッチ群＝100項目。B94–98＝D04738–D04953（3,071語）、B99–103（2,731語）、B104–108（3,847語）、B109–113＝D05956–D06102（2,975語）、B114–118＝D06103–D07130（3,465語）。直近200項目＝B109–118 計6,440語（中央値26、最短4、最長123）、500項目＝B94–118 計16,089語（中央値28）。語数は docs/_work/<batch>_incoming/corpus_<batch>.json の項目IDを corpus と照合しアラビア文字の語を数えた値（Claude 集計）。B94 以降は主張単位の記録方式が統一されているため起点とした。精度：model_accuracy_log.tsv の B109–113（主張 995＋1,087、FIXLOG 426、残存38）と B114–118（968＋1,344、FIXLOG 506、残存51）。21%＝932/4,394 は FIXLOG（初版修正）を最終データの主張数で割った概算。\n§2：Gemini 切替日＝app.py PREFERRED_MODELS の git 履歴。v1/v2/v3＝docs/精度検証/精度指標_定義書_20260926.md。件数＝model_accuracy_log.tsv の notes。重大（H）＝model_accuracy_findings.tsv で caught_stage=verify_* かつ severity=H（Claude 集計）。",
  "§3 モデル図：変換＝docs/lod_prototype/xml2ttl.py。Wikidata 89・GeoNames 51＝出力中の異なり数。Fihrist＝github.com/fihristorg/fihrist-mss authority（person 10,078件）。MPP 2009–2021＝timemachine.eu の IHODP 紹介（要確認・緑）。PUA 12,813人＝github.com/EIS1600/hdis-pua の data/PUA_processed/PUA_allDataTables_asList_UPDATED.rds の personaje 表。",
  "§1 冒頭・§3 OpenITI：数値は KITAB「OpenITI Release version 2025.1.9」（kitab-project.org、2026年2月12日公開）の表。アラビア語 13,320 テキスト／8,755 タイトル／3,373 著者、ペルシア語 354／351／262、写本文書（OpenITI-mss）433。Zenodo 記録の作成者は Nigst・Romanov・Savant・Seydi・Verkinderen（アガ・ハーン大学、ハンブルク大学）。著者の比定（Claude 集計、表＝docs/poster_LP12/data/OpenITI_matches_AIND.tsv）：(1)『ダウ』に立項＝同版メタデータの date 800–930 のアラビア語著者 231人を、corpus 13,968項目の見出し（nasab 3要素＋固有のニスバ）と没年記述で照合し目視確認。125人（うち名の一致は強いが没年が食い違う等の「probable」3人＝0837IbnNajiTannukhi・0871MuhammadCuqbani・0830IbnMuhammadBasiliTunisi）。本文の没年が OpenITI の年と一致 81、±2年 3、著者執筆時に存命（897年以降没）21、没年記述と照合できず名で同定 20。ほかに索引項目のみで本伝未確認 2（Fanārī、Khayḍarī）。(2) 符号化済み 3,195項目＝AIND-D・wd・TMP-P の人物参照と、bibl の書名（ID-Master Text 194件）の著者を照合。人物として 73人、書物の著者として 82人（確実）、重複を除き 138人（790年以前の著者 70人）。著者推定が確実でない書名 11件（著者 6人分）は数えていない。(1)(2) の重複を除き計 198人。例：0852IbnHajarCasqalani＝D01068、0902Sakhawi＝D07578、0256Bukhari＝『サヒーフ』（wd:Q1023470）。\n§3 PUA 対象年代：hdis-pua の personaje.muerte（ヒジュラ暦）／muerteec（西暦）で没年判明 6,983人の最小・最大＝91/709年〜921/1515年（98%は 180〜774/796〜1371年）（Claude 集計）。§3 PUA 事例：名の形＝『ダウ』D05552 は「ويعرف بالقلصاوي بفتح القاف وسكون اللام ثم مهملة」と綴りまで指定（D05513 の見出しは القلصادي、D05575 は القلصاوي）。PUA 6245 は القلصادي。『ダウ』側＝corpus の AIND-D05552（本伝）・D05513（القلصادي الأندلسي الحيسوب、没「بضع وخمسين」、ابن عزم）・D05575（転送見出し「هو البسطي」）。D05513 を同一人物とするのは Claude の判断（緑）。PUA 側＝personaje 6245（muerte 891, 15 ḏū al-ḥiğğa/12 de diciembre, 1486）、personaje_lugar（بسطة・غرناطة استوطن・المشرق・تلمسان・تونس طلب العلم・مكة 巡礼・بجاية）、personaje_fuente（Nafḥ al-ṭīb, Nayl al-ibtihāğ, Durrat al-ḥiğāl, al-Bustān ×2, al-Ḥulal al-sundusiyya）。アッ＝ラーイー＝PUA personaje 10467（d. 853）。",
  "§3 Fihrist：MS Marsh 645＝Ibn al-Shammāʿ, al-Qabas al-ḥāwī li-ghurar al-Ḍawʾ al-lāmiʿ, part 1 only [autograph]、provenance Marsh、acquisition「The Marsh bequest entered the Bodleian Library in 1714」（fihrist-mss collections/oxford university/MS_Marsh_645.xml）。サハーウィー＝Fihrist person_118408498（Claude 照合）。",
  "§2 ID の課題：拒否リスト 31件＝docs/precheck_aind_v12.py WD_GN_DENYLIST。Lomske＝ID-Master 注記（Q160851）。ジャクマク→Q4120025、インド洋→Q1283＝拒否リスト。76件＝findings の wd_ref/gn_ref かつ gemini_draft→claude_review。検索ベースの ID 付与とローカルLLM の効果は未検証の見込み。",
  "§1 地図：docs/poster_LP12/data/places.tsv（符号化済み項目の placeName、304種）のうち都市単位で位置を特定できる 69 地点。座標は Claude が都市単位で与えた概略値（al-Thurayya 等の自動照合は同名地名の誤りが多かったため不使用）→ 要確認。基図＝Natural Earth 50m。ルート＝D05552 本文と PUA personaje_lugar。",
  "§4 ネットワーク：docs/poster_LP12/data/edges.tsv（Claude 集計）、networkx spring layout。",
].join("\n"));

(async () => {
  await pres.writeFile({ fileName: "LP12_poster_A0_draft.pptx" });
  await applyTheme("LP12_poster_A0_draft.pptx", THEME);
  console.log("written");
})();
