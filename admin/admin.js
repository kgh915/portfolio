// 포트폴리오 관리자 화면
// 데이터 두 개(data/site.json, assets/detail/details.json)를 불러와 고치고, '저장'을 누르면 /api/save로 GitHub에 저장.
// 저장되면 Vercel이 사이트를 다시 만들어 약 1분 뒤 실제 사이트에 반영됨.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") el.className = v; else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (v !== undefined && v !== null && v !== false) el.setAttribute(k, v === true ? "" : v);
    }
    for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) el.append(k.nodeType ? k : String(k));
    return el;
  };
  let S = null, D = null, SHA = null, ORIGINAL = "", ASSETS = [], TAB = "basic";

  // ── 이미지 경로 찾기(확장자 없는 이름 → 실제 파일) ─────────────
  function img(name) {
    if (!name) return "";
    if (/\.(jpe?g|png|webp|gif|svg)$/i.test(name)) return "../assets/" + name;
    for (const ext of ["-thumb.jpg", ".webp", ".jpg", ".png"]) if (ASSETS.includes(name + ext)) return "../assets/" + name + ext;
    return "";
  }

  // ── 변경 감지 ──────────────────────────────────────
  const snapshot = () => JSON.stringify([S, D]);
  function changed() {
    const dirty = snapshot() !== ORIGINAL;
    $("#saveBtn").disabled = !dirty;
    const st = $("#status"); st.textContent = dirty ? "저장하지 않은 변경이 있어요" : ""; st.classList.toggle("warn", dirty);
  }
  addEventListener("beforeunload", e => { if (S && snapshot() !== ORIGINAL) { e.preventDefault(); e.returnValue = ""; } });
  function toast(msg, ms = 4000) { const t = h("div", { class: "toast" }, msg); document.body.append(t); setTimeout(() => t.remove(), ms); }

  // ── 입력 칸 만들기 ───────────────────────────────────
  // 한 줄/여러 줄/숫자/주소 입력 — obj[key]를 직접 고침
  function field(label, obj, key, o = {}) {
    const type = o.type || "text";
    const val = obj[key] ?? "";
    const input = type === "textarea" ? h("textarea", { rows: o.rows || 3 }) : h("input", { type, min: o.min, max: o.max });
    input.value = val;
    input.addEventListener("input", () => {
      obj[key] = type === "number" ? (input.value === "" ? null : Number(input.value)) : input.value;
      wrap.classList.add("changed"); changed();
    });
    const wrap = h("div", { class: "field" }, h("label", {}, label), input, o.note ? h("div", { class: "note" }, o.note) : null);
    return wrap;
  }
  function checkbox(label, obj, key) {
    const c = h("input", { type: "checkbox" }); c.checked = !!obj[key];
    c.addEventListener("change", () => { obj[key] = c.checked; changed(); });
    return h("div", { class: "field" }, h("label", {}, h("span", {}, label, " "), c));
  }
  // 위·아래·삭제 버튼 공용
  function moveBtns(arr, i, rerender) {
    return [
      h("button", { class: "mini", title: "위로", onclick: () => { if (i > 0) { [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]]; changed(); rerender(); } } }, "▲"),
      h("button", { class: "mini", title: "아래로", onclick: () => { if (i < arr.length - 1) { [arr[i + 1], arr[i]] = [arr[i], arr[i + 1]]; changed(); rerender(); } } }, "▼"),
      h("button", { class: "mini del", title: "삭제", onclick: () => { if (confirm("이 항목을 목록에서 뺄까요? (저장 전까지는 되돌릴 수 있어요)")) { arr.splice(i, 1); changed(); rerender(); } } }, "삭제"),
    ];
  }
  // 문자열 목록(배지·툴·문단 등)
  function strList(label, obj, key, o = {}) {
    const box = h("div", { class: "field" }, h("label", {}, label));
    const list = h("div", { class: "strs" }); box.append(list);
    if (o.note) box.append(h("div", { class: "note" }, o.note));
    const render = () => {
      list.innerHTML = ""; const arr = obj[key] || (obj[key] = []);
      arr.forEach((v, i) => {
        const inp = o.textarea ? h("textarea", { rows: 3 }) : h("input", { type: "text" }); inp.value = v;
        inp.addEventListener("input", () => { arr[i] = inp.value; changed(); });
        list.append(h("div", { class: "str" }, inp, ...moveBtns(arr, i, render)));
      });
      list.append(h("button", { class: "mini add", onclick: () => { arr.push(""); changed(); render(); } }, "+ 추가"));
    };
    render(); return box;
  }
  // 컬러무드(동그라미 2~3개)
  function colorList(label, obj, key) {
    const box = h("div", { class: "field" }, h("label", {}, label), h("div", { class: "note" }, "많이 쓴 색 1~2개 + 포인트 색 1개 (최대 3개)"));
    const list = h("div", { class: "strs" }); box.append(list);
    const render = () => {
      list.innerHTML = ""; const arr = obj[key] || (obj[key] = []);
      arr.forEach((v, i) => {
        const pick = h("input", { type: "color" }); pick.value = /^#[0-9a-f]{6}$/i.test(v) ? v : "#ffffff";
        const txt = h("input", { type: "text", style: "max-width:110px" }); txt.value = v;
        pick.addEventListener("input", () => { arr[i] = pick.value.toUpperCase(); txt.value = arr[i]; changed(); });
        txt.addEventListener("input", () => { arr[i] = txt.value.trim(); if (/^#[0-9a-f]{6}$/i.test(arr[i])) pick.value = arr[i]; changed(); });
        list.append(h("div", { class: "str color" }, pick, txt, ...moveBtns(arr, i, render)));
      });
      if (arr.length < 3) list.append(h("button", { class: "mini add", onclick: () => { arr.push("#FFFFFF"); changed(); render(); } }, "+ 색 추가"));
    };
    render(); return box;
  }
  // 객체 목록(제품·경력·상세페이지 등) — 접었다 펼치기, 순서 변경, 삭제, 추가
  function objList(arr, o) {
    const wrap = h("div", { class: "items" });
    const render = () => {
      wrap.innerHTML = "";
      arr.forEach((item, i) => {
        const body = h("div", { class: "item-body" });
        const card = h("div", { class: "item closed" });
        const t = o.thumb ? o.thumb(item) : "";
        const head = h("div", { class: "item-head" },
          h("span", { class: "num" }, i + 1), t ? h("img", { class: "thumb", src: t, alt: "", loading: "lazy" }) : null,
          h("span", { class: "ttl" }, o.title(item, i) || "(제목 없음)"),
          h("button", { class: "mini", onclick: () => card.classList.toggle("closed") }, "열기/닫기"),
          ...(o.fixed ? [] : moveBtns(arr, i, render)));
        o.render(item, body, i);
        card.append(head, body); wrap.append(card);
      });
      if (o.add) wrap.append(h("button", { class: "mini add", onclick: () => { arr.push(o.add()); changed(); render(); wrap.lastElementChild.previousElementSibling?.classList.remove("closed"); } }, "+ 항목 추가"));
    };
    render(); return wrap;
  }
  // 이미지 순서(썸네일 칩) — 파일 이름 목록의 순서 변경·빼기
  function chips(label, arr, note) {
    const box = h("div", { class: "field" }, h("label", {}, label), note ? h("div", { class: "note" }, note) : null);
    const list = h("div", { class: "chips" }); box.append(list);
    const render = () => {
      list.innerHTML = "";
      arr.forEach((name, i) => list.append(h("div", { class: "chip" },
        h("img", { src: img(typeof name === "string" ? name : name.thumb), alt: "", loading: "lazy" }),
        h("span", { class: "id" }, (i + 1) + ". " + (typeof name === "string" ? name : name.full)),
        h("div", { class: "btns" }, ...moveBtns(arr, i, render)))));
    };
    render(); return box;
  }
  const group = (title, ...kids) => h("div", { class: "group" }, title ? h("h3", {}, title) : null, ...kids);
  const HTML_NOTE = "굵게 하려면 <b>글자</b>, 줄바꿈은 <br> 을 쓰면 돼요.";

  // ── 메뉴(탭)별 화면 ──────────────────────────────────
  const T = () => S.texts, SEC = () => S.texts.sections;
  const TABS = {
    basic: ["기본 정보", () => [
      group("연락처 (프로필·푸터에 함께 쓰여요)", field("이름", T().contact, "name"), field("영문 이름(상단 메뉴)", T().contact, "name_en"),
        field("전화번호", T().contact, "phone"), field("이메일", T().contact, "email")),
      group("첫 화면(히어로)", field("작은 제목", T().hero, "eyebrow"), field("큰 제목 1줄", T().hero, "title1"), field("큰 제목 2줄(민트색)", T().hero, "title2"),
        field("소개 문장", T().hero, "sub"), strList("아래 작은 글(점으로 구분)", T().hero, "meta")),
      group("프로필 카드", field("카드 제목", T().profile, "title"), field("학력", T().profile, "education"), field("자격증", T().profile, "certificates"),
        strList("Tools 배지", T().profile, "tools")),
      group("검색·공유용 정보", field("브라우저 탭 제목", T().meta, "title"), field("검색 설명", T().meta, "description", { type: "textarea", rows: 2 })),
    ]],
    sections: ["섹션 제목·소개", () => [
      ...[["interview", "인터뷰"], ["products", "기획·출시 제품"], ["project", "셀프 디자인 프로젝트"], ["ai", "AI 활용 작업물"], ["detail", "상세페이지"],
        ["package", "패키지"], ["editorial", "편집디자인"], ["photo", "사진 촬영"], ["career", "경력"]].map(([k, name]) => {
        const s = SEC()[k]; const kids = [field("영문 작은 제목", s, "en"), field("섹션 제목", s, "title")];
        if (k === "detail") kids.push(field("소개 글", S, "detail_desc", { type: "textarea", note: HTML_NOTE }));
        else if ("desc" in s) kids.push(field("소개 글", s, "desc", { type: "textarea", note: HTML_NOTE }));
        if ("tools" in s) kids.push(strList("사용 툴 배지", s, "tools"));
        if ("badges" in s) kids.push(strList("배지", s, "badges"));
        if ("hint" in s) kids.push(field("안내 문구", s, "hint"));
        return group(name, ...kids);
      }),
    ]],
    interview: ["인터뷰", () => [
      h("p", { class: "help" }, "질문을 비워 두면 마지막 인사말로 보여요."),
      objList(S.interview, { title: (x, i) => x.q || "(마무리 인사)", add: () => ({ q: "", a: "" }),
        render: (x, b) => b.append(field("질문", x, "q"), field("답변", x, "a", { type: "textarea", rows: 5 })) }),
    ]],
    products: ["기획·출시 제품", () => [
      objList(S.products, { title: x => x.title, thumb: x => img(x.img),
        render: (x, b) => b.append(field("제품명", x, "title"), field("성과 배지", x, "achieve"), field("한 줄 소개", x, "concept", { type: "textarea", rows: 2 }),
          field("실제 제품 링크", x, "url", { type: "url", note: "비워 두면 링크가 표시되지 않아요." }), field("이미지 파일 이름", x, "img", { note: "이미지 교체는 다음 단계에서 버튼으로 할 수 있게 돼요." })) }),
    ]],
    project: ["셀프 디자인 프로젝트", () => {
      const p = S.project;
      return [group("", field("제목", p, "title"), field("소개", p, "lead", { type: "textarea", rows: 5 }), field("역할 배지", p, "roles"),
        strList("사실 배지", p, "stats"), strList("진행 과정", p, "steps", { textarea: true }), strList("기존 문제", p, "problem", { textarea: true }), strList("개선 결과", p, "solution", { textarea: true }))];
    }],
    ai: ["AI 활용 작업물", () => [
      objList(S.ai_works, { title: x => x.title, thumb: x => img(x.still),
        render: (x, b) => b.append(field("제목", x, "title"), field("컨셉", x, "concept", { type: "textarea" }), field("작업 방식", x, "flow", { type: "textarea", rows: 2 }),
          strList("키워드", x, "keywords"), chips("콘셉트 이미지 순서", x.concepts, "그리드(여러 컷을 이어붙인) 이미지는 맨 뒤에 두는 게 원칙이에요.")) }),
    ]],
    detail: ["상세페이지", () => [
      group("목록 설정", field("처음 보일 미리보기 개수", S.settings, "detail_initial", { type: "number", min: 1, note: "화면 열 개수에 맞춰 마지막 줄이 꽉 차도록 자동으로 조금 늘어날 수 있어요." })),
      h("p", { class: "help" }, "상세페이지가 없는 작업(미리보기만 있는 것)은 목록 맨 뒤에 두세요."),
      objList(D, { title: x => x.title + (x.pages?.length ? "" : "  · 미리보기만"), thumb: x => img(x.preview),
        render: (x, b) => {
          b.append(field("작업명", x, "title"));
          if (!x.pages?.length) return;
          const cs = x.contrib || (x.contrib = []);
          b.append(h("div", { class: "field" }, h("label", {}, "기여도"), h("div", { class: "note" }, "100%인 역할은 사이트에서 '기획·디자인 100%'처럼 자동으로 합쳐져요. %가 아닌 경우(업체제공 등)는 % 칸을 비우고 표시 문구를 쓰세요."),
            objList(cs, { title: c => c.role + " " + (c.pct != null ? c.pct + "%" : "- " + (c.text || "")), add: () => ({ role: "", pct: 100 }),
              render: (c, bb) => bb.append(field("역할", c, "role"), field("%", c, "pct", { type: "number", min: 0, max: 100 }), field("표시 문구(% 대신)", c, "text")) })));
          b.append(strList("사용툴", x, "tools"), colorList("컬러무드", x, "colors"), field("기획 컨셉", x, "concept", { type: "textarea", rows: 4, note: "PC에서 2~3줄이 적당해요." }));
        } }),
    ]],
    package: ["패키지", () => [
      chips("패키지 순서", S.package),
      strList("공통 사용툴", S, "package_tools"),
      ...S.package.filter(id => S.package_notes[id]).map(id => {
        const n = S.package_notes[id];
        return group(n.title + " 설명", field("작업명", n, "title"), checkbox("제품촬영도 직접 함(기여도·DSLR 카메라 표시)", n, "shot"), colorList("컬러무드", n, "colors"),
          field("기획 컨셉", n, "concept", { type: "textarea", rows: 4 }));
      }),
    ]],
    editorial: ["편집디자인", () => [chips("편집디자인 순서", S.editorial)]],
    photo: ["사진 촬영", () => [
      group("목록 설정", field("처음 보일 사진 개수", S.settings, "photo_initial", { type: "number", min: 1 })),
      chips("사진 순서", S.photo),
    ]],
    career: ["경력", () => [
      objList(S.career, { title: x => x.period.replace(/<br>/g, " / ") + "  " + x.company.replace(/<[^>]+>/g, ""), add: () => ({ period: "", company: "", role: "", desc: "" }),
        render: (x, b) => b.append(field("기간", x, "period", { note: "두 기간은 <br> 로 줄바꿈" }), field("회사", x, "company", { note: "작은 메모는 <span class='conote'>메모</span>" }),
          field("직무·직급", x, "role"), field("주요 업무", x, "desc", { type: "textarea", rows: 2 })) }),
    ]],
    about: ["About·푸터", () => [
      group("About", field("큰 제목", T().about, "lead"), strList("문단", T().about, "paragraphs", { textarea: true, note: HTML_NOTE })),
      group("푸터", field("큰 문구", T().footer, "big", { type: "textarea", rows: 2, note: "줄바꿈은 <br>" }), field("직함", T().footer, "role"), field("저작권 문구", T().footer, "copy")),
    ]],
  };

  function renderTabs() {
    const nav = $("#tabs"); nav.innerHTML = "";
    for (const [k, [name]] of Object.entries(TABS))
      nav.append(h("button", { class: k === TAB ? "on" : "", onclick: () => { TAB = k; renderTabs(); renderPanel(); scrollTo(0, 0); } }, name));
  }
  function renderPanel() {
    const [name, fn] = TABS[TAB]; const p = $("#panel"); p.innerHTML = "";
    p.append(h("h2", {}, name), ...fn());
  }

  // ── 서버와 주고받기 ─────────────────────────────────
  async function api(path, opts = {}) {
    const r = await fetch("/api/" + path, { credentials: "same-origin", headers: { "Content-Type": "application/json" }, ...opts });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error(j.error || "요청 실패 (" + r.status + ")"); e.status = r.status; throw e; }
    return j;
  }
  async function load() {
    const [c, m] = await Promise.all([api("content"), fetch("manifest.json").then(r => r.ok ? r.json() : { assets: [] }).catch(() => ({ assets: [] }))]);
    S = c.site; D = c.details; SHA = c.sha; ASSETS = m.assets || []; ORIGINAL = snapshot();
    $("#branch").textContent = c.sha === "local" ? "내 컴퓨터 시험" : c.branch === "main" ? "실제 사이트" : "작업 공간: " + c.branch;
    $("#login").hidden = true; $("#app").hidden = false; renderTabs(); renderPanel(); changed();
  }
  $("#saveBtn").addEventListener("click", async () => {
    const btn = $("#saveBtn"); btn.disabled = true; $("#status").textContent = "저장 중…";
    try {
      const r = await api("save", { method: "POST", body: JSON.stringify({ site: S, details: D, sha: SHA, summary: TABS[TAB][0] }) });
      SHA = r.sha; ORIGINAL = snapshot(); changed();
      toast("저장했어요! 약 1분 뒤 사이트에 반영돼요.", 6000);
    } catch (e) { $("#status").textContent = e.message; $("#status").classList.add("warn"); btn.disabled = false; if (e.status === 401) location.reload(); }
  });
  $("#logoutBtn").addEventListener("click", async () => {
    if (snapshot() !== ORIGINAL && !confirm("저장하지 않은 변경이 있어요. 그래도 로그아웃할까요?")) return;
    await api("login", { method: "DELETE" }).catch(() => {}); ORIGINAL = snapshot(); location.reload();
  });
  $("#loginForm").addEventListener("submit", async e => {
    e.preventDefault(); $("#loginMsg").textContent = "확인 중…";
    try { await api("login", { method: "POST", body: JSON.stringify({ password: $("#pw").value }) }); $("#pw").value = ""; $("#loginMsg").textContent = ""; await load(); }
    catch (err) { $("#loginMsg").textContent = err.message; }
  });
  // 처음 열 때: 이미 로그인돼 있으면 바로 편집 화면
  api("login").then(r => r.authed ? load() : ($("#login").hidden = false)).catch(() => ($("#login").hidden = false));
})();
