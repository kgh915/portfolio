// 매주 월요일 아침 8시(한국) 지난주(월~일) 통계 요약 메일 — Vercel 크론이 부름(vercel.json).
// 관리자 화면 '시험 메일 보내기'로도 부를 수 있음(로그인 필요).
// 필요한 비밀값(Vercel): RESEND_API_KEY(메일 보내기 열쇠), STATS_EMAIL(받을 주소 = Resend 가입 주소), CRON_SECRET(크론 확인용 아무 글자)
const L = require("./_lib");
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
function namer(site, details) {
  const dp = Object.fromEntries(details.map(d => [d.id, d.title]));
  const prod = Object.fromEntries(site.products.map(p => [p.img, p.title]));
  const ai = Object.fromEntries(site.ai_works.map(w => [(w.still || "").replace(/-still.*$/, ""), w.title]));
  return k => {
    if (k === "mail") return "✉️ 이메일 클릭"; if (k === "tel") return "📞 전화번호 클릭"; if (k === "more") return "더보기 버튼";
    if (k.startsWith("link-")) return "제품 판매 페이지 이동: " + (prod[k.slice(5)] || k.slice(5));
    if (dp[k]) return "상세페이지 · " + dp[k];
    if (prod[k]) return "제품 · " + prod[k];
    const base = k.split("-")[0];
    if (/^pk\d+/.test(k)) return "패키지 · " + (site.package_notes[base]?.title || k);
    if (/^ed\d+/.test(k)) return "편집디자인 · " + k;
    if (/^ph\d+/.test(k)) return "사진 · " + k;
    if (ai[base]) return "AI 작업물 · " + ai[base];
    return k;
  };
}
const sum = (days, f) => days.reduce((a, d) => a + f(d), 0);
function merge(days, key) { const o = {}; for (const d of days) for (const [k, n] of Object.entries(d[key])) o[k] = (o[k] || 0) + n; return o; }
const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);

module.exports = async (req, res) => {
  const cronOk = process.env.CRON_SECRET && req.headers.authorization === "Bearer " + process.env.CRON_SECRET;
  if (!cronOk && !L.isAuthed(req)) return L.send(res, 401, { error: "권한이 없어요." });
  if (!L.kvReady()) return L.send(res, 400, { error: "통계 저장소가 아직 연결되지 않았어요." });
  if (!process.env.RESEND_API_KEY || !process.env.STATS_EMAIL) return L.send(res, 400, { error: "메일 설정(RESEND_API_KEY, STATS_EMAIL)이 아직 없어요." });
  try {
    const yesterday = Date.now() - 86400e3;
    const all = await L.readDays(14, yesterday), prev = all.slice(0, 7), week = all.slice(7);
    const ref = L.LOCAL ? "local" : L.BRANCH;
    const [site, details] = (await Promise.all([L.readFile("data/site.json", ref), L.readFile("assets/detail/details.json", ref)])).map(JSON.parse);
    const name = namer(site, details);
    const v = sum(week, d => d.v), pv = sum(prev, d => d.v), clicks = merge(week, "c"), refs = merge(week, "r");
    const diff = v - pv, diffTxt = pv ? (diff >= 0 ? `▲ ${diff}` : `▼ ${-diff}`) + " (지지난주 " + pv + ")" : "";
    const contact = (clicks.mail || 0) + (clicks.tel || 0);
    const row = (a, b) => `<tr><td style="padding:6px 10px;border-bottom:1px solid #eee">${esc(a)}</td><td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right;font-weight:700">${b}</td></tr>`;
    const table = (title, rows) => `<h3 style="margin:22px 0 6px;font-size:15px;color:#159489">${title}</h3><table style="border-collapse:collapse;width:100%;font-size:14px">${rows || row("아직 없어요", "")}</table>`;
    const daily = week.map(d => row(d.day.slice(5).replace("-", "/") + " (" + "일월화수목금토"[new Date(d.day + "T00:00:00Z").getUTCDay()] + ")", d.v)).join("");
    const html = `<div style="font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;max-width:560px;color:#17302E">
<h2 style="font-size:19px;margin:0 0 4px">포트폴리오 주간 통계</h2><p style="color:#4F635F;margin:0 0 16px">${week[0].day} ~ ${week[6].day}</p>
<div style="background:#E7F6F4;border-radius:12px;padding:16px 18px"><div style="font-size:13px;color:#4F635F">방문</div><div style="font-size:28px;font-weight:800">${v}회 <span style="font-size:14px;font-weight:600;color:#4F635F">${diffTxt}</span></div>
<div style="font-size:13px;color:#4F635F;margin-top:6px">연락처(이메일·전화) 클릭 ${contact}회</div></div>
${table("가장 많이 눌러 본 작업", top(Object.fromEntries(Object.entries(clicks).filter(([k]) => !["mail", "tel", "more"].includes(k))), 10).map(([k, n]) => row(name(k), n)).join(""))}
${table("어디서 들어왔나요", top(refs, 8).map(([k, n]) => row(k, n)).join(""))}
${table("요일별 방문", daily)}
<p style="color:#8a9a97;font-size:12px;margin-top:20px">관리자 화면 '통계' 메뉴에서 더 자세히 볼 수 있어요. 직접 접속한 기록은 '이 브라우저는 통계에서 제외'를 켠 브라우저에서는 세지 않아요.</p></div>`;
    const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: "Bearer " + process.env.RESEND_API_KEY, "Content-Type": "application/json" },
      body: JSON.stringify({ from: "포트폴리오 통계 <onboarding@resend.dev>", to: [process.env.STATS_EMAIL], subject: `[포트폴리오] 지난주 방문 ${v}회 · 연락처 클릭 ${contact}회`, html }) });
    if (!r.ok) throw new Error("메일 " + r.status + " " + (await r.text()).slice(0, 150));
    L.send(res, 200, { ok: true });
  } catch (e) { L.send(res, 500, { error: "메일을 보내지 못했어요. " + e.message }); }
};
