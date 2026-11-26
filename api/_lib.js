// 관리자 API 공용 기능 — 로그인 확인, GitHub에 파일 저장/읽기
// 비밀값은 Vercel 환경변수에만 둠: ADMIN_PASSWORD(관리자 비밀번호), GITHUB_TOKEN(저장소 쓰기 권한 토큰)
// 저장 대상 저장소·브랜치는 Vercel이 자동으로 넣어주는 값(VERCEL_GIT_*)을 사용 → 미리보기 배포는 그 브랜치에, 실제 사이트는 main에 저장
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const LOCAL = process.env.ADMIN_LOCAL === "1"; // 내 컴퓨터 테스트용(파일에 바로 저장)
const ROOT = path.join(__dirname, "..");
const OWNER = process.env.VERCEL_GIT_REPO_OWNER || process.env.GITHUB_OWNER || "kgh915";
const REPO = process.env.VERCEL_GIT_REPO_SLUG || process.env.GITHUB_REPO || "portfolio";
const BRANCH = process.env.GITHUB_BRANCH || process.env.VERCEL_GIT_COMMIT_REF || "main";
const SESSION_HOURS = 12;

function secret() {
  const p = process.env.ADMIN_PASSWORD || "";
  const t = process.env.GITHUB_TOKEN || "";
  return crypto.createHash("sha256").update("portfolio-admin|" + p + "|" + t).digest();
}
function sign(v) { return crypto.createHmac("sha256", secret()).update(v).digest("hex"); }
function makeSession() {
  const exp = String(Date.now() + SESSION_HOURS * 3600e3);
  return exp + "." + sign(exp);
}
function readCookie(req, name) {
  const m = (req.headers.cookie || "").split(/;\s*/).find(c => c.startsWith(name + "="));
  return m ? decodeURIComponent(m.slice(name.length + 1)) : "";
}
function isAuthed(req) {
  const v = readCookie(req, "adm"); const [exp, sig] = v.split(".");
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  const good = sign(exp);
  return sig.length === good.length && crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(good));
}
function setSession(res, value, maxAge) {
  const secure = LOCAL ? "" : "; Secure";
  res.setHeader("Set-Cookie", `adm=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${secure}`);
}
function passwordOk(input) {
  const want = process.env.ADMIN_PASSWORD || "";
  if (!want) return false;
  const a = crypto.createHash("sha256").update(String(input || "")).digest();
  const b = crypto.createHash("sha256").update(want).digest();
  return crypto.timingSafeEqual(a, b);
}
function send(res, code, obj) {
  res.statusCode = code; res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store"); res.end(JSON.stringify(obj));
}
function requireAuth(req, res) {
  if (isAuthed(req)) return true;
  send(res, 401, { error: "로그인이 필요해요." }); return false;
}

// ── GitHub ─────────────────────────────────────────
async function gh(pathname, opts = {}) {
  const r = await fetch("https://api.github.com/repos/" + OWNER + "/" + REPO + pathname, {
    ...opts,
    headers: { Authorization: "Bearer " + process.env.GITHUB_TOKEN, Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "portfolio-admin", ...(opts.headers || {}) },
  });
  if (!r.ok) { const t = await r.text(); throw new Error("GitHub " + r.status + ": " + t.slice(0, 200)); }
  if (opts.raw) return r.text();  // 파일 내용 그대로(글자)로 받기
  return r.headers.get("content-type")?.includes("json") ? r.json() : r.text();
}
async function headSha() { return (await gh("/git/ref/heads/" + encodeURIComponent(BRANCH))).object.sha; }
async function readFile(p, ref) {
  if (LOCAL) return fs.readFileSync(path.join(ROOT, p), "utf8");
  return gh("/contents/" + p + "?ref=" + ref, { raw: true, headers: { Accept: "application/vnd.github.raw+json" } });
}
// files: [{path, content (utf8 text) | base64}] 를 한 번의 커밋으로 저장
async function commitFiles(files, message, expectSha) {
  if (LOCAL) {
    for (const f of files) {
      const full = path.join(ROOT, f.path); fs.mkdirSync(path.dirname(full), { recursive: true });
      fs.writeFileSync(full, f.base64 ? Buffer.from(f.base64, "base64") : f.content);
    }
    require("child_process").execSync("python3 build.py", { cwd: ROOT });
    return "local";
  }
  const head = await headSha();
  if (expectSha && head !== expectSha) {
    const e = new Error("다른 곳에서 먼저 저장된 내용이 있어요. 새로고침한 뒤 다시 수정해 주세요."); e.conflict = true; throw e;
  }
  const baseTree = (await gh("/git/commits/" + head)).tree.sha;
  const tree = [];
  for (const f of files) {
    const blob = await gh("/git/blobs", { method: "POST", body: JSON.stringify(
      f.base64 ? { content: f.base64, encoding: "base64" } : { content: f.content, encoding: "utf-8" }) });
    tree.push({ path: f.path, mode: "100644", type: "blob", sha: blob.sha });
  }
  const t = await gh("/git/trees", { method: "POST", body: JSON.stringify({ base_tree: baseTree, tree }) });
  const c = await gh("/git/commits", { method: "POST", body: JSON.stringify({ message, tree: t.sha, parents: [head] }) });
  await gh("/git/refs/heads/" + encodeURIComponent(BRANCH), { method: "PATCH", body: JSON.stringify({ sha: c.sha }) });
  return c.sha;
}
async function readBody(req) {
  if (req.body !== undefined) return typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body;
  const chunks = []; for await (const c of req) chunks.push(c);
  return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
}
module.exports = { LOCAL, BRANCH, OWNER, REPO, isAuthed, makeSession, setSession, passwordOk, send, requireAuth,
  headSha, readFile, commitFiles, readBody, SESSION_HOURS };
