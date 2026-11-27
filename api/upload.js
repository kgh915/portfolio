// 관리자 화면 이미지 올리기 — 브라우저에서 이미 알맞은 크기로 줄인 이미지 1장을 받아 GitHub에 '파일 조각(blob)'으로만 올려 둠.
// 이 단계에서는 사이트가 바뀌지 않음. 관리자 화면에서 '저장'을 누를 때 글자 수정과 함께 한 번의 커밋으로 묶여 반영됨.
// (Vercel 함수 요청 한도 4.5MB → 한 번에 1장, 3.4MB 이하만)
const L = require("./_lib");
const MAX = 3.4 * 1024 * 1024;
module.exports = async (req, res) => {
  if (!L.requireAuth(req, res)) return;
  if (req.method !== "POST") return L.send(res, 405, { error: "허용되지 않은 요청" });
  try {
    const b = await L.readBody(req);
    if (!L.assetPathOk(b.path)) return L.send(res, 400, { error: "올릴 수 없는 파일 이름이에요." });
    const data = String(b.data || "");
    if (!/^[A-Za-z0-9+/=]+$/.test(data)) return L.send(res, 400, { error: "이미지 내용이 올바르지 않아요." });
    const buf = Buffer.from(data, "base64");
    if (!buf.length || buf.length > MAX) return L.send(res, 413, { error: "이미지가 너무 커요(3.4MB 이하)." });
    const isJpg = buf[0] === 0xff && buf[1] === 0xd8, isPng = buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
    if (!(b.path.endsWith(".png") ? isPng : isJpg)) return L.send(res, 400, { error: "이미지 형식이 파일 이름과 맞지 않아요." });
    const sha = await L.uploadBlob(b.path, data);
    L.send(res, 200, { ok: true, sha, path: b.path });
  } catch (e) { L.send(res, 500, { error: "이미지를 올리지 못했어요. " + e.message }); }
};
