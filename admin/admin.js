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
  let S = null, D = null, SHA = null, ORIGINAL = "", ASSETS = [], DETAIL_DIRS = [], TAB = "basic";
  const UPLOADS = new Map(), REMOVES = new Set(), PREVIEW = {}, OPEN = new WeakSet(); let BUSY = 0;

  // ── 이미지 경로 찾기(확장자 없는 이름 → 실제 파일) ─────────────
  function img(name) {
    if (!name) return "";
    if (PREVIEW[name]) return PREVIEW[name];
    if (/\.(jpe?g|png|webp|gif|svg)$/i.test(name)) return "../assets/" + name;
    for (const ext of ["-thumb.jpg", ".webp", ".jpg", ".png"]) if (ASSETS.includes(name + ext)) return "../assets/" + name + ext;
    return "";
  }

  // ── 변경 감지 ──────────────────────────────────────
  const snapshot = () => JSON.stringify([S, D]);
  const isDirty = () => !!S && (snapshot() !== ORIGINAL || UPLOADS.size > 0 || REMOVES.size > 0);
  function changed() {
    const dirty = isDirty();
    $("#saveBtn").disabled = !dirty || BUSY > 0;
    const st = $("#status"); st.textContent = dirty ? "저장하지 않은 변경이 있어요" : ""; st.classList.toggle("warn", dirty);
  }
  addEventListener("beforeunload", e => { if (isDirty() || BUSY) { e.preventDefault(); e.returnValue = ""; } });
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
      h("button", { class: "mini del", title: "완전히 삭제", onclick: () => { if (confirm("이 항목을 완전히 삭제할까요?\n잠시 안 보이게만 하려면 '숨기기'를 쓰세요. (저장 전까지는 되돌릴 수 있어요)")) { if (typeof arr[i] === "string" && S.hidden_images) setHidden(arr, i, false); arr.splice(i, 1); changed(); rerender(); } } }, "삭제"),
    ];
  }
  // ── 끌어서 옮기기 ───────────────────────────────────
  // el: 옮길 줄(카드/칩), handle: 잡는 곳. 같은 목록 안에서만 옮겨짐.
  let DRAG = null;
  function moveItem(arr, from, to, rerender) {
    if (from === to || to < 0 || to >= arr.length) return;
    const [x] = arr.splice(from, 1); arr.splice(to, 0, x); changed(); rerender();
  }
  function clearMarks() { document.querySelectorAll(".drop-before,.drop-after").forEach(x => x.classList.remove("drop-before", "drop-after")); }
  function dragSort(el, arr, i, rerender, handle, horizontal) {
    handle.addEventListener("mousedown", () => { el.draggable = true; });
    handle.addEventListener("mouseup", () => { el.draggable = false; });
    el.addEventListener("dragstart", e => {
      if (!el.draggable) return;
      e.stopPropagation(); DRAG = { arr, i };
      e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(i + 1));
      requestAnimationFrame(() => el.classList.add("dragging"));
    });
    el.addEventListener("dragend", () => { el.draggable = false; el.classList.remove("dragging"); clearMarks(); DRAG = null; });
    const after = e => { const r = el.getBoundingClientRect(); return horizontal ? e.clientX > r.left + r.width / 2 : e.clientY > r.top + r.height / 2; };
    el.addEventListener("dragover", e => {
      if (!DRAG || DRAG.arr !== arr) return;
      e.preventDefault(); e.stopPropagation(); e.dataTransfer.dropEffect = "move";
      const a = after(e); clearMarks(); if (DRAG.i !== i) el.classList.add(a ? "drop-after" : "drop-before");
    });
    el.addEventListener("drop", e => {
      if (!DRAG || DRAG.arr !== arr) return;
      e.preventDefault(); e.stopPropagation();
      const from = DRAG.i; let to = i + (after(e) ? 1 : 0); if (from < to) to--;
      clearMarks(); DRAG = null; moveItem(arr, from, to, rerender);
    });
  }
  // 끄는 중 화면 위/아래 끝에 가면 자동으로 스크롤
  addEventListener("dragover", e => {
    if (!DRAG) return;
    const edge = 80, y = e.clientY;
    if (y < edge) scrollBy(0, -Math.ceil((edge - y) / 3)); else if (y > innerHeight - edge) scrollBy(0, Math.ceil((y - innerHeight + edge) / 3));
  });
  // 번호 배지를 누르면 원하는 번호로 바로 이동
  function numBadge(arr, i, rerender, cls = "num") {
    return h("button", { class: cls + " jump", type: "button", title: "눌러서 원하는 번호로 옮기기", onclick: () => {
      const v = prompt(`몇 번째로 옮길까요? (1 ~ ${arr.length})`, String(i + 1));
      if (v === null) return; const n = parseInt(v, 10);
      if (!(n >= 1 && n <= arr.length)) { alert(`1부터 ${arr.length} 사이 숫자를 넣어 주세요.`); return; }
      moveItem(arr, i, n - 1, rerender);
    } }, i + 1);
  }
  const grip = () => h("span", { class: "grip", title: "잡고 끌어서 옮기기" }, "⠿");

  // ── 숨기기 ─────────────────────────────────────────
  // 목록 항목은 hidden:true, 이미지 이름(문자열)은 S.hidden_images에 이름을 넣어 숨김. 데이터는 지우지 않음.
  const isHidden = x => typeof x === "string" ? (S.hidden_images || []).includes(x) : !!(x && x.hidden);
  function setHidden(arr, i, on) {
    const x = arr[i];
    if (typeof x === "string") {
      const l = S.hidden_images || (S.hidden_images = []);
      const k = l.indexOf(x); if (on && k < 0) l.push(x); if (!on && k >= 0) l.splice(k, 1);
      if (!l.length) delete S.hidden_images;
    } else if (on) x.hidden = true; else delete x.hidden;
  }
  function hideBtn(arr, i, rerender) {
    const on = isHidden(arr[i]);
    return h("button", { class: "mini hide" + (on ? " on" : ""), type: "button", title: on ? "다시 사이트에 보이게 하기" : "사이트에서만 안 보이게 하기(자료는 남아 있음)",
      onclick: () => { setHidden(arr, i, !on); changed(); rerender(); } }, on ? "보이기" : "숨기기");
  }

  // ── 이미지 올리기 ───────────────────────────────────
  // 고른 이미지를 브라우저에서 사이트에 필요한 크기(보이는 크기의 약 2배)로 줄여 1장씩 올림.
  // 올린 이미지는 '저장'을 눌러야 글자 수정과 함께 사이트에 반영됨.
  function pickFiles(multiple) {
    return new Promise(res => {
      const inp = h("input", { type: "file", accept: "image/jpeg,image/png,image/webp,video/*", multiple: multiple || undefined });
      inp.addEventListener("change", () => res([...inp.files])); inp.click();
    });
  }
  function videoGuide(f) {
    const mb = f.size / 1048576;
    alert((mb > 30 ? `이 영상은 ${mb.toFixed(0)}MB라서 사이트가 느려질 수 있어요. HandBrake(무료 프로그램)로 'Fast 1080p30' 설정으로 줄이면 보통 10~20MB가 돼요.\n\n` : "") +
      "영상은 용량이 커서 관리자 화면에서 바로 올릴 수 없어요.\n\n올리는 방법:\n1. github.com/kgh915/portfolio 접속 → assets 폴더\n2. Add file → Upload files → 영상 끌어다 놓기\n3. 파일 이름을 이미지와 맞추기(예: pk08-1.mp4)\n4. Commit changes\n\n어려우면 Claude에게 영상 파일을 알려 주세요.");
  }
  function loadImage(f) {
    return new Promise((res, rej) => { const u = URL.createObjectURL(f), im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error(f.name + " 파일을 열 수 없어요.")); im.src = u; });
  }
  function hasAlpha(im, f) {
    if (f.type === "image/jpeg") return false;
    const c = document.createElement("canvas"); c.width = 96; c.height = Math.max(1, Math.round(96 * im.naturalHeight / im.naturalWidth));
    const x = c.getContext("2d"); x.drawImage(im, 0, 0, c.width, c.height);
    const d = x.getImageData(0, 0, c.width, c.height).data; for (let i = 3; i < d.length; i += 4) if (d[i] < 250) return true; return false;
  }
  // 줄이기: maxLong(긴 변) 또는 maxW(가로) 기준. sy·sh로 세로 일부분만 잘라 그릴 수 있음(상세페이지 자르기용)
  function shrink(im, o = {}) {
    const W = im.naturalWidth, H = im.naturalHeight;
    let k = 1;
    if (o.maxLong) k = Math.min(1, o.maxLong / Math.max(W, H));
    if (o.maxW) k = Math.min(1, o.maxW / W);
    if (o.minShort) k = Math.min(1, Math.max(o.minShort / Math.min(W, H), 0), o.capLong ? o.capLong / Math.max(W, H) : 1);
    const sy = o.sy || 0, sh = o.sh || H;
    const c = document.createElement("canvas"); c.width = Math.round(W * k); c.height = Math.round(sh * k);
    const x = c.getContext("2d");
    if (!o.png) { x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height); }
    x.imageSmoothingQuality = "high"; x.drawImage(im, 0, sy, W, sh, 0, 0, c.width, c.height);
    return new Promise(res => c.toBlob(b => res({ blob: b, w: c.width, h: c.height }), o.png ? "image/png" : "image/jpeg", 0.86));
  }
  const b64 = blob => new Promise(res => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1]); r.readAsDataURL(blob); });
  async function put(rel, out) {  // rel: assets/ 아래 경로
    let { blob } = out;
    if (blob.size > 3.3 * 1048576) throw new Error("줄인 뒤에도 이미지가 너무 커요. 조금 작은 이미지로 다시 골라 주세요.");
    const r = await api("upload", { method: "POST", body: JSON.stringify({ path: "assets/" + rel, data: await b64(blob) }) });
    UPLOADS.set("assets/" + rel, r.sha); REMOVES.delete("assets/" + rel);
    PREVIEW[rel] = URL.createObjectURL(blob);
    return out;
  }
  // 같은 이름의 다른 형식 파일(예: 예전 .webp)이 남아 있으면 사이트가 옛 이미지를 쓰므로 저장할 때 함께 지움
  function dropOld(base, keep) {
    for (const ext of [".png", ".webp", ".jpg", "-thumb.jpg"]) {
      const f = base + ext; if (!keep.includes(f) && (ASSETS.includes(f) || UPLOADS.has("assets/" + f))) { REMOVES.add("assets/" + f); UPLOADS.delete("assets/" + f); }
    }
  }
  // 다음 번호 이름(ph50, pk08 …) — 이미 있는 파일·목록·방금 올린 것과 겹치지 않게
  function nextName(prefix, extra = []) {
    let max = 0; const re = new RegExp("^" + prefix + "(\\d+)");
    for (const n of [...ASSETS, ...extra, ...Object.keys(PREVIEW), ...[...UPLOADS.keys()].map(p => p.replace(/^assets\//, ""))]) { const m = re.exec(n); if (m) max = Math.max(max, +m[1]); }
    return prefix + String(max + 1).padStart(2, "0");
  }
  // 진행 표시 + 실패 알림을 감싸는 공용 함수
  async function work(label, fn) {
    BUSY++; changed(); const st = $("#status"); st.textContent = label + "…"; st.classList.remove("warn");
    try { await fn(m => { st.textContent = label + " " + m; }); toast("이미지를 올렸어요. '저장'을 눌러야 사이트에 반영돼요.", 5000); return true; }
    catch (e) { alert(e.message); return false; }
    finally { BUSY--; changed(); }
  }
  // 종류별 이미지 만들기 — 파일 이름(확장자 없는 base)으로 저장
  const IMG = {
    // 사진 촬영: 큰 이미지 jpg(긴 변 2200) + 목록용 작은 이미지
    async photo(f, base) { const im = await loadImage(f); dropOld(base, [base + ".jpg", base + "-thumb.jpg"]);
      await put(base + ".jpg", await shrink(im, { maxLong: 2200 })); const t = await put(base + "-thumb.jpg", await shrink(im, { minShort: 400, capLong: 900 })); PREVIEW[base] = PREVIEW[base + "-thumb.jpg"]; return t; },
    // 패키지·편집: 투명 배경(누끼) PNG는 PNG로(긴 변 1600), 그 외는 jpg(긴 변 2200)
    async viewer(f, base) { const im = await loadImage(f); const png = hasAlpha(im, f); const name = base + (png ? ".png" : ".jpg"); dropOld(base, [name]);
      await put(name, await shrink(im, png ? { maxLong: 1600, png: true } : { maxLong: 2200 })); PREVIEW[base] = PREVIEW[name]; },
    // 기획·출시 제품: jpg(긴 변 1000, 기존과 같은 크기)
    async product(f, base) { const im = await loadImage(f); dropOld(base, [base + ".jpg"]); await put(base + ".jpg", await shrink(im, { maxLong: 1000 })); PREVIEW[base] = PREVIEW[base + ".jpg"]; },
    // AI 콘셉트 이미지: 큰 이미지(긴 변 1600) + 작은 이미지(긴 변 700)
    async ai(f, base) { const im = await loadImage(f); await put(base + ".jpg", await shrink(im, { maxLong: 1600 })); await put(base + "-thumb.jpg", await shrink(im, { maxLong: 700 })); },
  };
  // 상세페이지: 미리보기(가로 500) / 상세 이미지(가로 최대 860, 세로 4000px씩 잘라 01.jpg, 02.jpg …)
  async function detailPreview(x, f) { const im = await loadImage(f); const p = `detail/${x.id}/preview.jpg`; await put(p, await shrink(im, { maxW: 500 })); x.preview = p; }
  // 상세 이미지 첫 장의 맨 윗부분을 목록 칸 비율(307:787)로 잘라 미리보기로 만듦(가로 500)
  async function autoPreview(x, im) {
    const W = im.naturalWidth, sh = Math.min(im.naturalHeight, Math.round(W * 787 / 307));
    const p = `detail/${x.id}/preview.jpg`; await put(p, await shrink(im, { maxW: 500, sy: 0, sh })); x.preview = p;
  }
  async function detailPages(x, files, step, makePreview) {
    files = [...files].sort((a, b) => a.name.localeCompare(b.name, "ko", { numeric: true }));
    const old = (x.pages || []).map(p => "assets/" + p.src), pages = []; let n = 0;
    for (const [fi, f] of files.entries()) {
      const im = await loadImage(f); const W = im.naturalWidth, H = im.naturalHeight, k = Math.min(1, 860 / W), seg = Math.round(4000 / k);
      if (fi === 0 && makePreview) { step("(미리보기 만드는 중)"); await autoPreview(x, im); }
      for (let y = 0; y < H; y += seg) {
        n++; step(`(${fi + 1}/${files.length}번째 파일, ${n}조각)`);
        const src = `detail/${x.id}/${String(n).padStart(2, "0")}.jpg`; const out = await put(src, await shrink(im, { maxW: 860, sy: y, sh: Math.min(seg, H - y) }));
        pages.push({ src, w: out.w, h: out.h });
      }
    }
    for (const p of old) if (!pages.some(q => "assets/" + q.src === p)) { REMOVES.add(p); UPLOADS.delete(p); }
    x.pages = pages;
  }
  function filesOnly(fs) { const v = fs.find(f => f.type.startsWith("video/")); if (v) { videoGuide(v); return fs.filter(f => !f.type.startsWith("video/")); } return fs; }
  const upBtn = (label, onclick) => h("button", { class: "mini up", type: "button", onclick }, label);

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
        const g = grip(), row = h("div", { class: "str" }, g, inp, ...moveBtns(arr, i, render));
        dragSort(row, arr, i, render, g); list.append(row);
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
        const hid = o.hide !== false && isHidden(item);
        const card = h("div", { class: "item" + (OPEN.has(item) ? "" : " closed") + (hid ? " is-hidden" : "") });
        const t = o.thumb ? o.thumb(item) : "";
        const g = o.fixed ? null : grip();
        const head = h("div", { class: "item-head" }, g,
          o.fixed ? h("span", { class: "num" }, i + 1) : numBadge(arr, i, render), t ? h("img", { class: "thumb", src: t, alt: "", loading: "lazy", draggable: "false" }) : null,
          h("span", { class: "ttl" }, hid ? h("span", { class: "hidtag" }, "숨김") : null, o.title(item, i) || "(제목 없음)"),
          h("button", { class: "mini", onclick: () => { card.classList.toggle("closed"); card.classList.contains("closed") ? OPEN.delete(item) : OPEN.add(item); } }, "열기/닫기"),
          o.hide === false ? null : hideBtn(arr, i, render),
          ...(o.fixed ? [] : moveBtns(arr, i, render)));
        o.render(item, body, i);
        card.append(head, body); wrap.append(card);
        if (g) dragSort(card, arr, i, render, g);
      });
      if (o.add) wrap.append(h("button", { class: "mini add", onclick: () => { const it = o.add(); arr.push(it); OPEN.add(it); changed(); render(); } }, o.addLabel || "+ 항목 추가"));
    };
    wrap.rerender = render;
    render();
    return o.fixed || o.hide === false ? wrap : h("div", {}, h("div", { class: "note movehelp" }, "순서 바꾸기: 왼쪽 ⠿를 잡고 끌어서 옮기거나, 번호를 눌러 원하는 번호를 적으면 바로 옮겨져요. '숨기기'는 사이트에서만 안 보이게 하고 자료는 남겨 둬요(다시 '보이기' 가능). '삭제'는 완전히 필요 없을 때만 쓰세요."), wrap);
  }
  // 이미지 순서(썸네일 칩) — 파일 이름 목록의 순서 변경·빼기
  // kind: 이미지 올리기 종류(photo·viewer·ai). o.prefix: 새 이름 앞글자, o.onAdd: 추가 후 할 일
  function chips(label, arr, note, o = {}) {
    const box = h("div", { class: "field" }, h("label", {}, label), note ? h("div", { class: "note" }, note) : null,
      o.kind ? h("div", { class: "note" }, "이미지는 고르면 사이트에 맞는 크기로 자동으로 줄여서 올려요. 올린 뒤 '저장'을 눌러야 사이트에 반영돼요.") : null,
      h("div", { class: "note" }, "순서 바꾸기: 이미지를 잡고 끌어서 옮기거나, 번호를 눌러 원하는 번호를 적으면 돼요. '숨기기'는 사이트에서만 안 보이게 하고, '삭제'는 완전히 필요 없을 때만 쓰세요."));
    const list = h("div", { class: "chips" }); box.append(list);
    const render = () => {
      list.innerHTML = "";
      arr.forEach((name, i) => {
        const pic = h("img", { src: img(typeof name === "string" ? name : name.thumb), alt: "", loading: "lazy", draggable: "false", title: "잡고 끌어서 옮기기" });
        const chip = h("div", { class: "chip" + (isHidden(name) ? " is-hidden" : "") }, pic, isHidden(name) ? h("span", { class: "hidtag" }, "숨김") : null,
          h("span", { class: "id" }, numBadge(arr, i, render, "cnum"), " ", (typeof name === "string" ? name : name.full)),
          h("div", { class: "btns" }, ...moveBtns(arr, i, render)), hideBtn(arr, i, render),
          o.kind ? upBtn("이미지 교체", async () => {
            const [f] = filesOnly(await pickFiles(false)); if (!f) return;
            const ok = await work("이미지 올리는 중", async () => {
              if (o.kind === "ai") await IMG.ai(f, name.full.replace(/\.jpg$/, "")); else await IMG[o.kind](f, name);
            });
            if (ok) render();
          }) : null);
        dragSort(chip, arr, i, render, pic, true); list.append(chip);
      });
      if (o.kind) list.append(h("div", { class: "chip addchip" }, upBtn("+ 이미지 추가", async () => {
        const fs = filesOnly(await pickFiles(true)); if (!fs.length) return;
        const added = [];
        await work("이미지 올리는 중", async step => {
          for (const [k, f] of fs.entries()) {
            step(`(${k + 1}/${fs.length})`);
            if (o.kind === "ai") {
              const base = nextName(o.prefix() + "-", arr.map(c => c.full)); await IMG.ai(f, base);
              const it = { thumb: base + "-thumb.jpg", full: base + ".jpg" }; arr.push(it); added.push(it);
            } else { const base = nextName(o.prefix, arr); await IMG[o.kind](f, base); arr.push(base); added.push(base); }
          }
        });
        if (added.length) { changed(); o.onAdd ? o.onAdd(added) : render(); }
      })));
    };
    render(); return box;
  }
  // 이미지 한 장 칸(미리보기 + 교체 버튼)
  function imgRow(label, src, doUpload, after, note, btnLabel) {
    const pic = h("img", { class: "rowimg", src: src() || "", alt: "" });
    return h("div", { class: "field" }, h("label", {}, label), note ? h("div", { class: "note" }, note) : null,
      h("div", { class: "imgrow" }, pic, upBtn(btnLabel || (src() ? "이미지 교체" : "이미지 올리기"), async () => {
        const [f] = filesOnly(await pickFiles(false)); if (!f) return;
        if (await work("이미지 올리는 중", () => doUpload(f))) { pic.src = src(); changed(); after && after(); }
      })));
  }
  function nextDetailId() {
    let max = 0; for (const n of [...D.map(d => d.id), ...DETAIL_DIRS, ...Object.keys(PREVIEW)]) { const m = /^(?:detail\/)?dp(\d+)/.exec(n); if (m) max = Math.max(max, +m[1]); }
    return "dp" + String(max + 1).padStart(2, "0");
  }
  // 저장 전 확인: 이미지가 없는 새 항목
  function missingImages() {
    const miss = [];
    for (const d of D) if (!d.preview) miss.push("상세페이지 '" + d.title + "' 이미지(상세 이미지를 올리면 미리보기도 자동으로 생겨요)");
    for (const p of S.products) if (!img(p.img)) miss.push("제품 '" + p.title + "' 이미지");
    return miss;
  }
  // ── 사용법(5단계 사용 설명서) ─────────────────────────
  // 내용은 글자만 있는 고정 안내문. 바꿀 때는 아래 MANUAL 배열만 고치면 됨.
  const MANUAL = [
    ["처음 시작", `
      <p><b>관리자 주소</b>: 사이트 주소 뒤에 <code>/admin/</code>을 붙이면 돼요. (실제 사이트에 합친 뒤: <code>kimgeunha.vercel.app/admin/</code>)</p>
      <p>크롬·사파리·엣지 등 <b>어떤 브라우저든</b>, 휴대폰에서도 열려요. GitHub이나 Vercel에 로그인할 필요 없이 <b>관리자 비밀번호</b>만 있으면 돼요.</p>
      <p>한 번 로그인하면 <b>12시간</b> 동안 유지돼요. 다른 사람 컴퓨터에서 썼다면 오른쪽 위 <b>로그아웃</b>을 눌러 주세요.</p>`],
    ["기본 사용 순서", `
      <ol><li>왼쪽 메뉴에서 고칠 곳을 고르기</li><li>글자를 고치거나 이미지를 올리기 — 고친 칸은 <span class="mk">노란색</span>으로 표시돼요</li>
      <li>오른쪽 위 <b>저장</b> 누르기</li><li><b>약 1분 뒤</b> 사이트에 반영 — <b>사이트 보기 ↗</b>로 확인(안 바뀌었으면 새로고침)</li></ol>
      <p>저장하지 않고 창을 닫으려고 하면 경고가 떠요. 저장 전이라면 <b>새로고침</b>으로 고친 내용을 모두 취소할 수 있어요.</p>
      <p>여러 메뉴를 고친 뒤 한 번에 저장해도 돼요.</p>`],
    ["글자 고치기", `
      <p>칸에 바로 입력하면 돼요. 소개 글 같은 긴 칸에서는 이렇게 쓸 수 있어요.</p>
      <ul><li>굵게: <code>&lt;b&gt;굵게 할 글자&lt;/b&gt;</code></li><li>줄바꿈: 줄을 바꿀 곳에 <code>&lt;br&gt;</code></li></ul>
      <p>섹션 제목·소개·배지는 <b>섹션 제목·소개</b> 메뉴, 이름·연락처·첫 화면 문구는 <b>기본 정보</b> 메뉴에 있어요.</p>`],
    ["순서 바꾸기", `
      <ul><li><b>끌어서 옮기기</b>: 왼쪽 <b>⠿</b>를 잡고 원하는 자리로 끌기 (이미지 목록은 이미지를 잡고 끌기). 민트색 선이 놓일 자리예요.</li>
      <li><b>번호로 옮기기</b>: 번호(1, 2, 3…)를 누르고 원하는 번호 입력 → 멀리 옮길 때 편해요. <b>휴대폰에서는 이 방법</b>을 쓰세요.</li>
      <li>▲▼ 버튼은 한 칸씩 옮겨요.</li></ul>`],
    ["숨기기와 삭제", `
      <ul><li><b>숨기기</b>: 사이트에서만 안 보이고 자료는 그대로 남아요. 회색 점선 + <span class="hid">숨김</span> 표시. 다시 <b>보이기</b>를 누르면 원래 자리에 나타나요.</li>
      <li><b>삭제</b>: 목록에서 완전히 빼요. <b>정말 필요 없을 때만</b> 쓰세요. 잘 모르겠으면 숨기기를 쓰세요.</li></ul>
      <p>둘 다 <b>저장</b>을 눌러야 사이트에 반영돼요.</p>`],
    ["이미지 올리기·교체", `
      <p>원본 이미지를 그대로 골라도 <b>사이트에 맞는 크기로 자동으로 줄여서</b> 올려요(화질은 그대로, 사이트도 느려지지 않아요).</p>
      <ul><li><b>사진 촬영·패키지·편집디자인</b>: <b>+ 이미지 추가</b>(여러 장 한 번에), 이미지마다 <b>이미지 교체</b>. 배경이 투명한(누끼) PNG는 투명 그대로 올라가요.</li>
      <li><b>기획·출시 제품</b>: 제품을 열고 <b>이미지 교체</b>, 새 제품은 <b>+ 제품 추가</b></li>
      <li><b>AI 활용 작업물</b>: 작업을 열고 콘셉트 이미지 추가·교체</li>
      <li><b>상세페이지</b>: 아래 '새 상세페이지 추가' 참고</li></ul>
      <p>올린 이미지도 <b>저장</b>을 눌러야 사이트에 반영돼요. 올리는 중에는 저장 버튼이 잠깐 꺼져요.</p>`],
    ["새 상세페이지 추가", `
      <ol><li><b>상세페이지</b> 메뉴 맨 아래 <b>+ 상세페이지 추가</b></li>
      <li><b>상세 이미지 올리기</b> → 상세페이지 원본 선택(여러 장이면 파일 이름 순서대로 이어져요). 가로 860px로 줄이고 세로 4000px씩 잘라서 올려요.</li>
      <li><b>미리보기는 자동</b>으로 상세 이미지 맨 윗부분으로 만들어져요. 다른 이미지를 쓰고 싶을 때만 <b>직접 올리기</b></li>
      <li>작업명·기여도·사용툴·컬러무드·기획 컨셉 입력</li>
      <li>새 항목은 맨 뒤에 생기니, 번호를 눌러 원하는 자리로 옮기고 <b>저장</b></li></ol>`],
    ["영상(mp4) 올리기", `
      <p>영상은 용량이 커서 관리자 화면에서 올릴 수 없어요. 30MB가 넘으면 먼저 <b>HandBrake</b>(무료 프로그램)로 'Fast 1080p30' 설정으로 줄이세요.</p>
      <ol><li>github.com/kgh915/portfolio 접속 → <b>assets</b> 폴더</li><li><b>Add file → Upload files</b> → 영상 끌어다 놓기</li>
      <li>이름은 이미지와 맞추기(예: 패키지 pk08의 영상이면 <code>pk08-1.mp4</code>)</li><li><b>Commit changes</b></li></ol>
      <p>어려우면 Claude에게 영상 파일을 알려 주세요.</p>`],
    ["통계 보기", `
      <ul><li><b>📊 통계</b> 메뉴: 방문 수, 연락처(이메일·전화) 클릭, 많이 본 작업 순위, 들어온 곳(사람인·잡코리아 등)</li>
      <li><b>내 방문 빼기</b>: 쓰는 브라우저마다(맥 크롬·사파리, 휴대폰 등) 통계 메뉴에서 <b>이 브라우저는 통계에서 제외하기</b>를 한 번 눌러 두세요.</li>
      <li><b>주간 메일</b>: 매주 월요일 오전 8~9시에 지난주 요약이 메일로 와요. 안 보이면 스팸함도 확인(보내는 사람 onboarding@resend.dev).</li></ul>`],
    ["문제가 생겼을 때", `
      <ul><li><b>저장 전</b>에 잘못 고쳤다 → 새로고침하면 처음 상태로 돌아가요.</li>
      <li><b>저장 후</b>에 되돌리고 싶다 → Claude에게 "어제 저장하기 전으로 되돌려줘"처럼 말하면 돼요. 저장할 때마다 기록이 남아서 언제든 되돌릴 수 있어요.</li>
      <li><b>"다른 곳에서 먼저 저장된 내용이 있어요"</b> → 다른 창(또는 휴대폰)에서 먼저 저장한 경우예요. 새로고침한 뒤 다시 고쳐 주세요.</li>
      <li><b>"저장하지 못했어요. GitHub 401…"</b> → GitHub 열쇠(토큰)가 만료된 거예요. 아래 '비밀번호·열쇠 바꾸기' 참고.</li>
      <li><b>"로그인이 필요해요"</b> → 12시간이 지나 로그아웃된 거예요. 다시 로그인하세요(고친 내용은 저장 전이면 사라져요).</li></ul>`],
    ["비밀번호·열쇠 바꾸기", `
      <p>Vercel → 프로젝트 <b>portfolio</b> → <b>Environment Variables</b>(주소: vercel.com/kgh915/portfolio/settings/environment-variables)</p>
      <ul><li><b>관리자 비밀번호</b>: <code>ADMIN_PASSWORD</code> → <b>Edit</b> → 새 비밀번호 → Save</li>
      <li><b>GitHub 열쇠</b>: github.com/settings/personal-access-tokens 에서 새로 만들고(kgh915/portfolio만, Contents 읽기·쓰기) <code>GITHUB_TOKEN</code> 값을 바꾸기</li></ul>
      <p>바꾼 뒤에는 Vercel <b>Deployments</b> 화면 맨 위 배포의 <b>⋯ → Redeploy</b>를 눌러야 적용돼요(또는 Claude에게 "다시 배포해줘").</p>`],
    ["용량과 무료 한도", `
      <ul><li><b>저장소 용량</b>: 화면 오른쪽 위에 표시돼요. GitHub 권장 1GB 이하, 800MB가 넘으면 주황색으로 바뀌어요. 지운 이미지도 기록으로 남아서 용량이 줄지는 않아요.</li>
      <li><b>무료 한도</b>(모두 넉넉해요): Vercel 무료 플랜 / Upstash 월 50만 회 / Resend 월 3,000통(주 1통 사용)</li></ul>`],
  ];
  function manualPanel() {
    const wrap = h("div", { class: "manual" }, h("p", { class: "help" }, "관리자 화면 쓰는 방법이에요. 궁금한 항목을 눌러 펼쳐 보세요."));
    MANUAL.forEach(([title, body], i) => {
      const d = h("details", { class: "group" }); if (i < 2) d.open = true;
      const sm = h("summary", {}, title); const bd = h("div", { class: "mbody" }); bd.innerHTML = body;
      d.append(sm, bd); wrap.append(d);
    });
    return wrap;
  }

  // ── 통계 ───────────────────────────────────────────
  function itemName(k) {
    if (k === "mail") return "✉️ 이메일 클릭"; if (k === "tel") return "📞 전화번호 클릭"; if (k === "more") return "더보기 버튼";
    if (k.startsWith("link-")) { const p = S.products.find(p => p.img === k.slice(5)); return "제품 판매 페이지 이동 · " + (p ? p.title : k.slice(5)); }
    const d = D.find(d => d.id === k); if (d) return "상세페이지 · " + d.title;
    const p = S.products.find(p => p.img === k); if (p) return "제품 · " + p.title;
    const base = k.split("-")[0];
    if (/^pk\d+/.test(k)) return "패키지 · " + (S.package_notes[base]?.title || k);
    if (/^ed\d+/.test(k)) return "편집디자인 · " + k;
    if (/^ph\d+/.test(k)) return "사진 · " + k;
    const w = S.ai_works.find(w => (w.still || "").startsWith(base + "-")); if (w) return "AI 작업물 · " + w.title;
    return k;
  }
  function itemThumb(k) {
    const d = D.find(d => d.id === k); if (d) return img(d.preview);
    if (k.startsWith("link-")) k = k.slice(5);
    return img(k) || img(k.split("-")[0]) || img(k.split("-")[0] + "-still.jpg");
  }
  function trackToggle() {
    const get = () => { try { return !!localStorage.getItem("no-track"); } catch { return false; } };
    const btn = h("button", { class: "ghost", type: "button" });
    const paint = () => { btn.textContent = get() ? "✅ 이 브라우저는 통계에서 제외 중 (누르면 다시 셈)" : "이 브라우저는 통계에서 제외하기"; };
    btn.addEventListener("click", () => { try { get() ? localStorage.removeItem("no-track") : localStorage.setItem("no-track", "1"); } catch {} paint(); });
    paint(); return btn;
  }
  function statsPanel() {
    const box = h("div", {}, h("p", { class: "help" }, "불러오는 중…"));
    const sum = (days, f) => days.reduce((a, d) => a + f(d), 0);
    const merge = (days, key) => { const o = {}; for (const d of days) for (const [k, n] of Object.entries(d[key])) o[k] = (o[k] || 0) + n; return o; };
    const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);
    const exclude = group("내 방문은 빼기", h("p", { class: "note" }, "직접 사이트를 볼 때 숫자가 늘지 않도록, 쓰시는 브라우저마다(맥 크롬·사파리, 휴대폰 등) 이 화면에서 한 번씩 눌러 주세요."), trackToggle());
    api("stats").then(r => {
      box.innerHTML = "";
      if (!r.ready) { box.append(group("아직 준비 중이에요", h("p", {}, "통계 저장소(Upstash)를 연결하면 여기에 방문 수와 많이 본 작업이 나와요.")), exclude); return; }
      let range = 7;
      const view = h("div");
      const draw = () => {
        const days = r.days.slice(-range), prev = r.days.slice(-range * 2, -range);
        const v = sum(days, d => d.v), pv = sum(prev, d => d.v), clicks = merge(days, "c"), refs = merge(days, "r");
        const contact = (clicks.mail || 0) + (clicks.tel || 0);
        const max = Math.max(1, ...days.map(d => d.v));
        const works = top(Object.fromEntries(Object.entries(clicks).filter(([k]) => !["mail", "tel", "more"].includes(k))), 15);
        view.innerHTML = "";
        view.append(
          h("div", { class: "kpis" },
            h("div", { class: "kpi" }, h("span", {}, "방문"), h("b", {}, v + "회"), prev.length === range && pv ? h("em", {}, (v >= pv ? "▲ " : "▼ ") + Math.abs(v - pv) + " (이전 " + pv + ")") : null),
            h("div", { class: "kpi" }, h("span", {}, "연락처 클릭"), h("b", {}, contact + "회"), h("em", {}, "이메일 " + (clicks.mail || 0) + " · 전화 " + (clicks.tel || 0))),
            h("div", { class: "kpi" }, h("span", {}, "작업 클릭"), h("b", {}, sum(works, x => x[1]) + "회"))),
          group("날짜별 방문", h("div", { class: "bars" }, ...days.map(d => h("div", { class: "bar", title: d.day + " · " + d.v + "회" },
            h("i", { style: `height:${Math.round(d.v / max * 100)}%` }), h("small", {}, range <= 14 ? d.day.slice(5).replace("-", "/") : ""))))),
          group("가장 많이 눌러 본 작업", works.length ? h("div", { class: "ranks" }, ...works.map(([k, n], i) => h("div", { class: "rank" },
            h("span", { class: "num" }, i + 1), itemThumb(k) ? h("img", { src: itemThumb(k), alt: "" }) : h("span", { class: "noimg" }), h("span", { class: "ttl" }, itemName(k)), h("b", {}, n + "회")))) : h("p", { class: "note" }, "아직 없어요.")),
          group("어디서 들어왔나요", Object.keys(refs).length ? h("div", { class: "ranks" }, ...top(refs, 10).map(([k, n]) => h("div", { class: "rank" }, h("span", { class: "ttl" }, k), h("b", {}, n + "회")))) :
            h("p", { class: "note" }, "아직 없어요. (주소를 직접 입력하거나 즐겨찾기로 들어온 방문은 표시되지 않아요.)")));
      };
      const tabs = h("div", { class: "ranges" }, ...[[7, "최근 7일"], [28, "최근 4주"], [56, "최근 8주"]].map(([n, t]) => h("button", { class: "mini" + (n === range ? " on" : ""), type: "button",
        onclick: e => { range = n; tabs.querySelectorAll("button").forEach(b => b.classList.remove("on")); e.target.classList.add("on"); draw(); } }, t)));
      const mailBtn = h("button", { class: "ghost", type: "button", onclick: async () => {
        if (!confirm("지난주 통계를 지금 메일로 보내 볼까요?")) return;
        try { await api("weekly"); toast("메일을 보냈어요. 메일함을 확인해 주세요.", 5000); } catch (e) { alert(e.message); }
      } }, "시험 메일 보내기");
      box.append(h("p", { class: "help" }, "방문은 같은 사람이 같은 창에서 여러 번 새로고침해도 1번으로 세요. 검색 로봇은 빼고 셉니다. 매주 월요일 아침 8시에 지난주 요약을 메일로 보내 드려요."),
        tabs, view, exclude, group("주간 메일", h("p", { class: "note" }, r.mail ? "메일 설정이 되어 있어요. 실제 사이트(합친 뒤)에서 매주 자동으로 보내요." : "메일 설정(Resend)이 아직 없어요."), r.mail ? mailBtn : null));
      draw();
    }).catch(e => { box.innerHTML = ""; box.append(h("p", { class: "help" }, e.message)); });
    return box;
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
          field("실제 제품 링크", x, "url", { type: "url", note: "비워 두면 링크가 표시되지 않아요." }), imgRow("제품 이미지", () => img(x.img), async f => IMG.product(f, x.img))),
        add: () => ({ img: nextName("prod", S.products.map(p => p.img)), title: "새 제품", achieve: "", concept: "", url: "" }), addLabel: "+ 제품 추가" }),
    ]],
    project: ["셀프 디자인 프로젝트", () => {
      const p = S.project;
      return [group("", field("제목", p, "title"), field("소개", p, "lead", { type: "textarea", rows: 5 }), field("역할 배지", p, "roles"),
        strList("사실 배지", p, "stats"), strList("진행 과정", p, "steps", { textarea: true }), strList("기존 문제", p, "problem", { textarea: true }), strList("개선 결과", p, "solution", { textarea: true }))];
    }],
    ai: ["AI 활용 작업물", () => [
      objList(S.ai_works, { title: x => x.title, thumb: x => img(x.still),
        render: (x, b) => b.append(field("제목", x, "title"), field("컨셉", x, "concept", { type: "textarea" }), field("작업 방식", x, "flow", { type: "textarea", rows: 2 }),
          strList("키워드", x, "keywords"), chips("콘셉트 이미지 순서", x.concepts || (x.concepts = []), "그리드(여러 컷을 이어붙인) 이미지는 맨 뒤에 두는 게 원칙이에요.",
            { kind: "ai", prefix: () => (x.still || x.img || "ai").replace(/-still.*|\..*$/, "") })) }),
    ]],
    detail: ["상세페이지", () => [
      group("목록 설정", field("처음 보일 미리보기 개수", S.settings, "detail_initial", { type: "number", min: 1, note: "화면 열 개수에 맞춰 마지막 줄이 꽉 차도록 자동으로 조금 늘어날 수 있어요." })),
      h("p", { class: "help" }, "상세페이지가 없는 작업(미리보기만 있는 것)은 목록 맨 뒤에 두세요."),
      objList(D, { title: x => x.title + (x.pages?.length ? "" : "  · 미리보기만"), thumb: x => img(x.preview),
        add: () => ({ id: nextDetailId(), title: "새 상세페이지", preview: "", pages: [], contrib: [{ role: "기획", pct: 100 }, { role: "디자인", pct: 100 }], tools: ["Adobe Photoshop"], colors: [], concept: "" }),
        addLabel: "+ 상세페이지 추가",
        render: (x, b) => {
          b.append(field("작업명", x, "title"));
          const reList = () => { const w = b.closest(".items"); w && w.rerender ? w.rerender() : renderPanel(); };
          b.append(h("div", { class: "field" }, h("label", {}, "상세 이미지 (" + (x.pages?.length ? x.pages.length + "조각" : "없음") + ")"),
            h("div", { class: "note" }, "상세페이지 전체 이미지를 골라 주세요(여러 장이면 파일 이름 순서대로 이어져요). 가로 860px로 줄이고 세로 4000px씩 잘라서 올려요. 다시 올리면 기존 상세 이미지를 모두 바꿔요."),
            h("div", {}, upBtn(x.pages?.length ? "상세 이미지 다시 올리기" : "상세 이미지 올리기", async () => {
              const fs = filesOnly(await pickFiles(true)); if (!fs.length) return;
              const mk = !x.preview || confirm("미리보기 이미지도 새 상세 이미지의 맨 윗부분으로 바꿀까요?\n\n확인: 자동으로 바꾸기 / 취소: 지금 미리보기 그대로 두기");
              if (await work("상세 이미지 올리는 중", step => detailPages(x, fs, step, mk))) { changed(); reList(); }
            }))));
          b.append(imgRow("미리보기 이미지", () => img(x.preview), async f => detailPreview(x, f), reList,
            "상세 이미지를 올리면 첫 장의 맨 윗부분으로 자동으로 만들어져요. 다른 이미지로 쓰고 싶을 때만 직접 올리세요(상세 이미지가 없는 '미리보기만' 작업도 여기서 올려요).", "직접 올리기"));
          if (!x.pages?.length) return;
          const cs = x.contrib || (x.contrib = []);
          b.append(h("div", { class: "field" }, h("label", {}, "기여도"), h("div", { class: "note" }, "100%인 역할은 사이트에서 '기획·디자인 100%'처럼 자동으로 합쳐져요. %가 아닌 경우(업체제공 등)는 % 칸을 비우고 표시 문구를 쓰세요."),
            objList(cs, { title: c => c.role + " " + (c.pct != null ? c.pct + "%" : "- " + (c.text || "")), add: () => ({ role: "", pct: 100 }), hide: false,
              render: (c, bb) => bb.append(field("역할", c, "role"), field("%", c, "pct", { type: "number", min: 0, max: 100 }), field("표시 문구(% 대신)", c, "text")) })));
          b.append(strList("사용툴", x, "tools"), colorList("컬러무드", x, "colors"), field("기획 컨셉", x, "concept", { type: "textarea", rows: 4, note: "PC에서 2~3줄이 적당해요." }));
        } }),
    ]],
    package: ["패키지", () => [
      chips("패키지 순서", S.package, "", { kind: "viewer", prefix: "pk", onAdd: added => {
        for (const id of added) S.package_notes[id] ||= { title: "새 패키지", shot: false, colors: [], concept: "" };
        changed(); renderPanel(); toast("아래에 새 패키지 설명 칸이 생겼어요. 작업명·컨셉을 적어 주세요.", 5000);
      } }),
      h("p", { class: "help" }, "패키지 영상(mp4)은 용량이 커서 이 화면에서 올릴 수 없어요. 영상을 고르면 올리는 방법을 알려 드려요."),
      strList("공통 사용툴", S, "package_tools"),
      ...S.package.filter(id => S.package_notes[id]).map(id => {
        const n = S.package_notes[id];
        return group(n.title + " 설명", field("작업명", n, "title"), checkbox("제품촬영도 직접 함(기여도·DSLR 카메라 표시)", n, "shot"), colorList("컬러무드", n, "colors"),
          field("기획 컨셉", n, "concept", { type: "textarea", rows: 4 }));
      }),
    ]],
    editorial: ["편집디자인", () => [chips("편집디자인 순서", S.editorial, "", { kind: "viewer", prefix: "ed" })]],
    photo: ["사진 촬영", () => [
      group("목록 설정", field("처음 보일 사진 개수", S.settings, "photo_initial", { type: "number", min: 1 })),
      chips("사진 순서", S.photo, "", { kind: "photo", prefix: "ph" }),
    ]],
    career: ["경력", () => [
      objList(S.career, { title: x => x.period.replace(/<br>/g, " / ") + "  " + x.company.replace(/<[^>]+>/g, ""), add: () => ({ period: "", company: "", role: "", desc: "" }),
        render: (x, b) => b.append(field("기간", x, "period", { note: "두 기간은 <br> 로 줄바꿈" }), field("회사", x, "company", { note: "작은 메모는 <span class='conote'>메모</span>" }),
          field("직무·직급", x, "role"), field("주요 업무", x, "desc", { type: "textarea", rows: 2 })) }),
    ]],
    stats: ["📊 통계", () => [statsPanel()]],
    manual: ["📖 사용법", () => [manualPanel()]],
    about: ["About·푸터", () => [
      group("About", field("큰 제목", T().about, "lead"), strList("문단", T().about, "paragraphs", { textarea: true, note: HTML_NOTE })),
      group("푸터", field("큰 문구", T().footer, "big", { type: "textarea", rows: 2, note: "줄바꿈은 <br>" }), field("직함", T().footer, "role"), field("저작권 문구", T().footer, "copy")),
    ]],
  };

  function renderTabs() {
    const nav = $("#tabs"); nav.innerHTML = "";
    const keys = Object.keys(TABS).filter(k => k !== "stats" && k !== "manual").concat(["stats", "manual"]);  // 통계·사용법은 맨 아래
    for (const k of keys) { const [name] = TABS[k];
      if (k === "stats") nav.append(h("hr", { class: "tabsep" }));
      nav.append(h("button", { class: k === TAB ? "on" : "", onclick: () => { TAB = k; renderTabs(); renderPanel(); scrollTo(0, 0); } }, name)); }
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
  // 저장소 용량 — GitHub 권장 1GB 이하. 800MB 넘으면 주황색 경고
  function showRepo(mb) {
    const el = $("#repo"); if (mb == null) return;
    el.hidden = false; el.textContent = "저장소 " + (mb >= 1000 ? (mb / 1024).toFixed(2) + "GB" : mb + "MB") + " / 1GB";
    el.title = "GitHub 저장소 용량(권장 1GB 이하). 이미지를 올릴수록 늘어나요. 지운 이미지도 기록으로 남아서 용량은 줄지 않아요.";
    el.classList.toggle("warn", mb > 800);
  }
  async function load() {
    const [c, m] = await Promise.all([api("content"), fetch("manifest.json").then(r => r.ok ? r.json() : { assets: [] }).catch(() => ({ assets: [] }))]);
    S = c.site; D = c.details; SHA = c.sha; ASSETS = m.assets || []; DETAIL_DIRS = m.detail_dirs || []; ORIGINAL = snapshot();
    showRepo(c.repoMB);
    $("#branch").textContent = c.sha === "local" ? "내 컴퓨터 시험" : c.branch === "main" ? "실제 사이트" : "작업 공간: " + c.branch;
    $("#login").hidden = true; $("#app").hidden = false; renderTabs(); renderPanel(); changed();
  }
  $("#saveBtn").addEventListener("click", async () => {
    if (BUSY) return;
    const miss = missingImages();
    if (miss.length) { alert("이미지가 아직 없는 항목이 있어요. 이미지를 올리거나 항목을 삭제한 뒤 저장해 주세요.\n\n- " + miss.join("\n- ")); return; }
    const btn = $("#saveBtn"); btn.disabled = true; $("#status").textContent = "저장 중…";
    try {
      const uploads = [...UPLOADS].map(([path, sha]) => ({ path, sha })), removes = [...REMOVES];
      const r = await api("save", { method: "POST", body: JSON.stringify({ site: S, details: D, sha: SHA, summary: TABS[TAB][0] + (uploads.length ? ` (이미지 ${uploads.length}개)` : ""), uploads, removes }) });
      for (const u of uploads) { const n = u.path.replace(/^assets\//, ""); if (!n.includes("/") && !ASSETS.includes(n)) ASSETS.push(n); }
      for (const p of removes) { const n = p.replace(/^assets\//, ""); ASSETS = ASSETS.filter(a => a !== n); }
      UPLOADS.clear(); REMOVES.clear(); showRepo(r.repoMB);
      SHA = r.sha; ORIGINAL = snapshot(); changed();
      toast("저장했어요! 약 1분 뒤 사이트에 반영돼요.", 6000);
    } catch (e) { $("#status").textContent = e.message; $("#status").classList.add("warn"); btn.disabled = false; if (e.status === 401) location.reload(); }
  });
  $("#logoutBtn").addEventListener("click", async () => {
    if (isDirty() && !confirm("저장하지 않은 변경이 있어요. 그래도 로그아웃할까요?")) return;
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
