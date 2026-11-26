// 관리자 화면에서 고친 내용 저장 — 두 데이터 파일을 한 번의 커밋으로 GitHub에 저장 → Vercel이 자동으로 사이트를 다시 만듦
const L = require("./_lib");
module.exports = async (req, res) => {
  if (!L.requireAuth(req, res)) return;
  if (req.method !== "POST") return L.send(res, 405, { error: "허용되지 않은 요청" });
  try {
    const b = await L.readBody(req);
    if (!b.site || !b.details || !b.site.texts || !Array.isArray(b.details)) return L.send(res, 400, { error: "저장할 내용이 올바르지 않아요." });
    const files = [
      { path: "data/site.json", content: JSON.stringify(b.site, null, 1) + "\n" },
      { path: "assets/detail/details.json", content: JSON.stringify(b.details, null, 1) + "\n" },
    ];
    const msg = "관리자 화면에서 내용 수정" + (b.summary ? ": " + String(b.summary).slice(0, 80) : "");
    const sha = await L.commitFiles(files, msg, b.sha);
    L.send(res, 200, { ok: true, sha });
  } catch (e) { L.send(res, e.conflict ? 409 : 500, { error: e.conflict ? e.message : "저장하지 못했어요. " + e.message }); }
};
