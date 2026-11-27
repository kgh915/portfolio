// 관리자 화면 '통계' 메뉴용 — 최근 N일(기본 56일) 숫자. 로그인 필요.
const L = require("./_lib");
module.exports = async (req, res) => {
  if (!L.requireAuth(req, res)) return;
  if (!L.kvReady()) return L.send(res, 200, { ready: false });
  try {
    const n = Math.min(400, Math.max(7, parseInt(new URL(req.url, "http://x").searchParams.get("days") || "56", 10)));
    L.send(res, 200, { ready: true, days: await L.readDays(n), mail: !!(process.env.RESEND_API_KEY && process.env.STATS_EMAIL) });
  } catch (e) { L.send(res, 500, { error: "통계를 불러오지 못했어요. " + e.message }); }
};
