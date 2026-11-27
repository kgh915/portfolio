// 방문·클릭 숫자 세기 — 사이트가 화면을 다 띄운 뒤 아주 작은 신호를 보냄(쿠키·IP 등 개인정보는 저장하지 않음)
// {t:"v", r:"들어온 사이트"} = 방문 1회 / {t:"c", k:"dp07"} = 그 작업 클릭 1회
const L = require("./_lib");
const BOT = /bot|crawl|spider|slurp|preview|headless|lighthouse|facebookexternalhit|kakaotalk-scrap|yeti|daum/i;
module.exports = async (req, res) => {
  res.statusCode = 204; res.setHeader("Cache-Control", "no-store");
  try {
    if (req.method !== "POST" || !L.kvReady() || BOT.test(req.headers["user-agent"] || "")) return res.end();
    let b = await L.readBody(req); if (typeof b === "string") b = JSON.parse(b);
    const key = "st:" + L.kstDay(), cmds = [];
    if (b.t === "v") {
      cmds.push(["HINCRBY", key, "v", 1]);
      const r = String(b.r || "").toLowerCase().replace(/^www\./, "");
      if (/^[a-z0-9.\-]{3,60}$/.test(r)) cmds.push(["HINCRBY", key, "r:" + r, 1]);
    } else if (b.t === "c" && /^[A-Za-z0-9_\-]{1,40}$/.test(String(b.k || ""))) {
      cmds.push(["HINCRBY", key, "c:" + b.k, 1]);
    }
    if (cmds.length) { cmds.push(["EXPIRE", key, 400 * 86400]); await L.kv(cmds); }
  } catch (e) { /* 통계 실패는 방문자에게 영향 없게 조용히 무시 */ }
  res.end();
};
