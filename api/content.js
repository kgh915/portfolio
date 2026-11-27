// 관리자 화면이 고칠 데이터 읽기 — data/site.json, assets/detail/details.json (+ 저장 충돌 방지용 기준 버전)
const L = require("./_lib");
module.exports = async (req, res) => {
  if (!L.requireAuth(req, res)) return;
  try {
    const sha = L.LOCAL ? "local" : await L.headSha();
    const [site, details, repoMB] = await Promise.all([L.readFile("data/site.json", sha), L.readFile("assets/detail/details.json", sha), L.repoSizeMB()]);
    L.send(res, 200, { sha, branch: L.BRANCH, site: JSON.parse(site), details: JSON.parse(details), repoMB });
  } catch (e) { L.send(res, 500, { error: "데이터를 불러오지 못했어요. " + e.message }); }
};
