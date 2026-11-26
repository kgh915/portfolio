// 관리자 로그인 — 비밀번호가 맞으면 12시간짜리 로그인 쿠키 발급
const L = require("./_lib");
module.exports = async (req, res) => {
  if (req.method === "DELETE") { L.setSession(res, "", 0); return L.send(res, 200, { ok: true }); }   // 로그아웃
  if (req.method === "GET") return L.send(res, 200, { authed: L.isAuthed(req), branch: L.BRANCH });
  if (req.method !== "POST") return L.send(res, 405, { error: "허용되지 않은 요청" });
  if (!process.env.ADMIN_PASSWORD) return L.send(res, 500, { error: "관리자 비밀번호가 아직 설정되지 않았어요(Vercel 환경변수 ADMIN_PASSWORD)." });
  const body = await L.readBody(req);
  await new Promise(r => setTimeout(r, 600)); // 비밀번호 무작위 대입을 느리게
  if (!L.passwordOk(body.password)) return L.send(res, 401, { error: "비밀번호가 맞지 않아요." });
  L.setSession(res, L.makeSession(), L.SESSION_HOURS * 3600);
  L.send(res, 200, { ok: true });
};
