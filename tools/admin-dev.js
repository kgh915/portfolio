// 관리자 화면을 내 컴퓨터에서 시험하는 서버 (실제 GitHub 대신 이 폴더의 파일에 바로 저장하고 build.py 실행)
// 사용: node tools/admin-dev.js  →  http://localhost:8130/admin/   (로컬 전용 비밀번호: 환경변수 ADMIN_PASSWORD, 기본 local-test)
process.env.ADMIN_LOCAL = "1";
process.env.ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "local-test";
const http = require("http"), fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml", ".mp4": "video/mp4" };
http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x"); let p = decodeURIComponent(url.pathname);
  if (p.startsWith("/api/")) {
    const name = p.slice(5).replace(/[^a-z]/g, "");
    try { delete require.cache[require.resolve(path.join(ROOT, "api", name))]; return await require(path.join(ROOT, "api", name))(req, res); }
    catch (e) { res.statusCode = 500; return res.end(String(e)); }
  }
  if (p.endsWith("/")) p += "index.html";
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.statusCode = 404; return res.end("not found"); }
  res.setHeader("Content-Type", TYPES[path.extname(f).toLowerCase()] || "application/octet-stream");
  fs.createReadStream(f).pipe(res);
}).listen(8130, () => console.log("admin dev: http://localhost:8130/admin/"));
