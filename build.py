# -*- coding: utf-8 -*-
import os,json,html
OUT=os.path.dirname(os.path.abspath(__file__))
# 캐시 버스팅 — 파일 '내용'으로 만든 짧은 지문을 ?v= 로 붙임. 같은 파일명으로 이미지·CSS를 바꿔도
# 브라우저가 예전 캐시를 보여주지 않음. (예전엔 수정 시각을 썼는데, 서버(Vercel)에서 빌드하면 매번 시각이 바뀌어
# 캐시가 매번 깨지므로 내용 기준으로 바꿈 — 맥에서 빌드하든 서버에서 빌드하든 결과가 같음)
import hashlib
_ver_cache={}
def file_ver(full):
    if not os.path.exists(full): return "0"
    if full not in _ver_cache:
        h=hashlib.md5()
        with open(full,"rb") as f:
            for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
        _ver_cache[full]=h.hexdigest()[:10]
    return _ver_cache[full]
CSS_VER=file_ver(os.path.join(OUT,"style.css"))
FAVICON_VER=file_ver(os.path.join(OUT,"favicon.svg"))
def av(path):
    return f"assets/{path}?v={file_ver(os.path.join(OUT,'assets',path))}"

# 폴더에서 prefix+번호(ph01, ph02 …) 파일을 연속으로 자동 수집 (jpg/png/mp4)
def autoseq(prefix):
    base=os.path.join(OUT,"assets")
    out=[];n=1
    while any(os.path.exists(os.path.join(base,f"{prefix}{n:02d}.{e}")) for e in ("jpg","png","mp4")):
        out.append(f"{prefix}{n:02d}");n+=1
    return out

# 01 상세페이지 — 보존용 그대로 (태블릿+폰 목업 쇼케이스 + 보존용 설명글)
detail_imgs=["ds01"]  # 맨 위 태블릿·폰 목업만 유지 (ds02~05 4열 통이미지는 아래 미리보기 목록으로 교체됨)
# 상세페이지 미리보기 목록 — assets/detail/details.json 순서대로 표시.
# pages가 비어 있으면(상세페이지 원본 없음) 미리보기만 보이고 클릭해도 반응 없음 → 목록 뒤쪽에 둘 것.
details=json.load(open(os.path.join(OUT,"assets","detail","details.json"),encoding="utf-8"))
# ── 사이트 내용 데이터 ─────────────────────────────────────────────
# 작업 목록·문구는 data/site.json에 있음(관리자 화면이 이 파일을 고침). 여기서는 읽어서 쓰기만 함.
SITE=json.load(open(os.path.join(OUT,"data","site.json"),encoding="utf-8"))
DETAIL_INITIAL=SITE["settings"]["detail_initial"]  # 처음에 보일 상세페이지 미리보기 개수(나머지는 「더보기」)
PHOTO_INITIAL=SITE["settings"]["photo_initial"]    # 사진 촬영 섹션 처음에 보일 개수
detail_desc=SITE["detail_desc"]
# 숨긴 항목(관리자 화면 '숨기기')은 사이트에 안 나옴 — 데이터는 그대로 남아 언제든 다시 보이게 할 수 있음
# 목록 항목: {"hidden": true} / 이미지 이름 목록(패키지·편집·사진): site.json의 hidden_images에 이름이 있으면 숨김
HIDDEN_IMAGES=set(SITE.get("hidden_images") or [])
def vis(xs): return [x for x in xs if not (isinstance(x,dict) and x.get("hidden")) and not (isinstance(x,str) and x in HIDDEN_IMAGES)]
details=[d for d in vis(details) if os.path.exists(os.path.join(OUT,"assets",d["preview"]))]  # 미리보기 이미지가 아직 없으면(올리는 중) 건너뜀
package=vis(SITE["package"])      # 패키지 코너 순서(3D 목업 영상 pk01-1 등은 숨김 — 파일만 남아 있음)
editorial=vis(SITE["editorial"])
photo=vis(SITE["photo"])          # 사진 촬영 순서(ph01~)
products=vis(SITE["products"])    # 기획·출시 제품
project=SITE["project"]      # 셀프 디자인 프로젝트
career=[(c["period"],c["company"],c["role"],c["desc"]) for c in vis(SITE["career"])]
ai_works=[dict(w,concepts=vis(w.get("concepts") or [])) for w in vis(SITE["ai_works"])]    # AI 활용 작업물(영상 + 콘셉트 이미지)
interview=[(x["q"],x["a"]) for x in vis(SITE["interview"])]  # 인터뷰 Q&A(질문이 null이면 마무리 인사)

def masonry(ids):
    return '<div class="masonry">'+''.join(f'<div class="ph" data-full="assets/{i}.jpg"><img src="assets/{i}.jpg" loading="lazy" alt=""></div>' for i in ids)+'</div>'

# 「더보기」 버튼 — 목록이 limit개보다 많을 때만 출력
def more_btn(total,limit):
    if total<=limit: return ''
    return f'<div class="morewrap"><button type="button" class="morebtn" data-more="{total-limit}">더보기 <span>+{total-limit}</span></button></div>'

# 동일 사이즈 썸네일 그리드(흰 배경 · 클릭 시 크게 보기 유지)
# 그리드에는 가벼운 -thumb 이미지(있을 때만), 크게 보기에는 원본 이미지. limit개 뒤는 「더보기」로 펼침
def tiles(ids,limit=None):
    def src(i):
        return av(f"{i}-thumb.jpg") if os.path.exists(os.path.join(OUT,"assets",f"{i}-thumb.jpg")) else f"assets/{i}.jpg"
    cells=''.join(f'<div class="tile{" more" if limit and n>=limit else ""}" data-full="assets/{i}.jpg"><img src="{src(i)}" loading="lazy" alt=""></div>' for n,i in enumerate(ids))
    return f'<div class="moregroup" data-limit="{limit or 0}"><div class="tiles">{cells}</div>{more_btn(len(ids),limit) if limit else ""}</div>'

# 실제 출시 제품 카드 — 사진(클릭 시 크게 보기)+제품명+역할 배지(1개)+성과 배지+컨셉 한 줄+실제 판매 페이지 링크(보조용, 새 탭)
# 전 제품 기획·촬영·상세페이지까지 의뢰인이 직접 담당해서, 역할 배지는 공통으로 고정.
# 배지 3개로 나눴더니 너저분해 보인다는 피드백으로 "기획·촬영·상세페이지" 하나로 합침.
# achieve(성과)는 제품마다 있을 수도 없을 수도 있어서(예: 04번은 없음) None이면 배지를 아예 안 넣는다.
# url도 없을 수 있음(판매 종료된 제품 — 예: 도깨비 소원카드) → 그럴 땐 링크 줄 자체를 아예 안 넣는다.
PROD_ROLES="기획·촬영·상세페이지"
def product_card(p):
    roles_html=f'<span class="contrib">{PROD_ROLES}</span>'
    achieve_html=f'<span class="achieve">{p["achieve"]}</span>' if p.get("achieve") else ''
    link_html=(f'<a class="prodlink" href="{p["url"]}" target="_blank" rel="noopener">실제 제품 보러가기 ↗</a>'
               if p.get("url") else '')
    return f'''<div class="prodcard reveal">
<div class="prodimg" data-full="assets/{p["img"]}.jpg"><img src="assets/{p["img"]}.jpg" loading="lazy" alt="{p["title"]}"></div>
<div class="prodbd"><h5>{p["title"]}</h5><div class="prodbadges">{roles_html}{achieve_html}</div><p>{p["concept"]}</p>{link_html}</div>
</div>'''
products_html=''.join(product_card(p) for p in products)

# AI 활용 작업물 카드 — 왼쪽은 대표 미디어(영상 또는 대표 이미지) 한 타일, 오른쪽엔 컨셉·작업방식·키워드.
# 대표 미디어 옆에 AI 생성 콘셉트 이미지가 더 있으면(영상·이미지 작업 모두 공통) 같은 방식의 썸네일 그리드로 노출됨.
def kw_html(keywords):
    return '<div class="aikw">'+''.join(f'<span>{k}</span>' for k in keywords)+'</div>'
def ai_card(w):
    if w["kind"]=="video":
        media=(f'<div class="aimedia" data-kind="video" data-src="{av(w["src"])}" data-poster="{av(w["still"])}">'
               f'<img src="{av(w["still"])}" loading="lazy" alt="{w["title"]} 광고 영상"><span class="aitag">광고 영상</span><span class="playbadge">▶</span></div>')
    else:
        media=(f'<div class="aimedia" data-kind="image" data-src="{av(w["img"])}">'
               f'<img src="{av(w["img"])}" loading="lazy" alt="{w["title"]}"></div>')
    # 콘셉트 이미지는 여러 장이 나올 수 있어 목록으로 관리 — 옆으로 나란히 나열, 새 이미지가 추가되면 여기에 더 붙으면 됨
    # 이미지가 적을 때(1~2장)는 좌측 대표 미디어 높이에 맞춰 큼직한 정사각형으로, 많아지면(3장+) 작은 타일로 자동 전환
    concepts=w.get("concepts") or []
    if concepts:
        tiles=''.join(
            f'<div class="aimedia sub" data-kind="image" data-src="{av(c["full"])}">'
            f'<img src="{av(c["thumb"])}" loading="lazy" alt="{w["title"]} AI 생성 콘셉트 이미지"></div>'
            for c in concepts)
        concepts_cls="aiconcepts featured" if len(concepts)<=2 else "aiconcepts many"
        sub=f'<div class="{concepts_cls}">{tiles}</div>'
    else:
        sub=""
    return f'''<div class="airow reveal">{media}
<div class="aibd"><h3>{w["title"]}</h3>
<p class="lead-p">{w["concept"]}</p>
<div class="aiflow"><b>작업 방식</b>{w["flow"]}</div>
{kw_html(w["keywords"])}{sub}</div></div>'''
ai_html=''.join(ai_card(w) for w in ai_works)

# 인터뷰 채팅형 Q&A — 실제 채팅창처럼 새 질문·답변이 아래에 쌓이고, 박스가 자동으로 아래로 스크롤되면서
# 이전 대화는 위쪽으로 사라짐. 가만히 두면 자동 재생, 클릭하면 타이핑이 그 자리에서 멈추고 스크롤로 이미
# 타이핑된 내용을 자유롭게 볼 수 있음 — 다시 클릭하거나, 마우스가 영역을 벗어나거나, 5초간 마우스를 움직이지
# 않고 그대로 두면 멈췄던 지점부터 이어서 타이핑됨
chat_qa_json=html.escape(json.dumps(interview,ensure_ascii=False),quote=True)

# 상세페이지 — 목업 쇼케이스(세로 나열)
# 맨 위 목업(ds01): 태블릿 화면 → 휴대폰 화면 순서로 번갈아 공기청정기 상세페이지(dp10)가 천천히 자동 스크롤됨(무한 반복).
# 화면 위치는 ds01.jpg(2176x1040) 기준 실측값(%) — 목업 이미지를 바꾸면 MOCK_TABLET/MOCK_PHONE_SCREEN/MOCK_PHONE도 다시 재야 함.
# 휴대폰은 태블릿 위에 겹쳐 있으므로, 같은 목업 이미지를 휴대폰 모양으로만 잘라(MOCK_PHONE) 태블릿 화면 위에 한 번 더 얹음.
MOCK_W,MOCK_H=2176,1040
MOCK_TABLET=dict(x=675,y=106,w=626,h=827,radius="6px")
MOCK_PHONE_SCREEN=dict(x=1196,y=436,w=261,h=540,radius="8.4% / 4.1%")
MOCK_PHONE="inset(40.8% 32.4% 4.1% 54.1% round 2.1% / 4.4%)"
MOCK_DETAIL="dp10"
def mock_screen(cls,r,pages):
    return (f'<div class="mockscreen {cls}" style="left:{r["x"]/MOCK_W*100:.3f}%;top:{r["y"]/MOCK_H*100:.3f}%;'
            f'width:{r["w"]/MOCK_W*100:.3f}%;height:{r["h"]/MOCK_H*100:.3f}%;border-radius:{r["radius"]}">'
            f'<div class="mockscroll">{pages}</div></div>')
def mock_html():
    d=next(x for x in details if x["id"]==MOCK_DETAIL)
    pages=''.join(f'<img src="{av(p["src"])}" width="{p["w"]}" height="{p["h"]}" alt="" loading="lazy">' for p in d["pages"])
    return (f'<figure class="dshot"><div class="mockwrap">'
            f'<img src="{av("ds01.jpg")}" loading="lazy" alt="상세페이지 디자인 목업">'
            f'{mock_screen("tablet",MOCK_TABLET,pages)}'
            f'<img class="mockphone" src="{av("ds01.jpg")}" alt="" aria-hidden="true" style="clip-path:{MOCK_PHONE}">'
            f'{mock_screen("phone",MOCK_PHONE_SCREEN,pages)}'
            f'</div></figure>')
detail_html=mock_html()+''.join(f'<figure class="dshot"><img src="assets/{i}.jpg" loading="lazy" alt="상세페이지 디자인 목업"></figure>' for i in detail_imgs if i!="ds01")

# 상세페이지 미리보기 카드 — 클릭하면 상세페이지 전체가 팝업으로 열림(세로 스크롤).
# 상세페이지가 여러 장이면(분할 파일) 순서대로 틈 없이 이어 붙여 보여줌. 데이터는 data-pages(JSON)에 담음.
def dp_card(n,d):
    more=" more" if n>=DETAIL_INITIAL else ""
    img=f'<img src="{av(d["preview"])}" loading="lazy" alt="{html.escape(d["title"])} 상세페이지 미리보기">'
    if not d["pages"]:
        return f'<div class="dpcard nodetail{more}" data-k="{d["id"]}">{img}</div>'
    pages=html.escape(json.dumps([[av(p["src"]),p["w"],p["h"]] for p in d["pages"]]),quote=True)
    # 팝업 상단 메모(기여한 부분·기획 컨셉) — 둘 다 없으면 메모 영역 자체를 보이지 않음
    # 기여도: 100%인 역할은 한 배지로 합침(예: 기획/디자인 100%), 그 외(%가 다르거나 '업체제공' 등)는 각각 표시
    note=""
    contrib=d.get("contrib") or []
    full=[c["role"] for c in contrib if c.get("pct")==100]
    badges=([{"t":"·".join(full)+" 100%"}] if full else [])
    for c in contrib:
        if c.get("pct")==100: continue
        if c.get("pct") is not None: badges.append({"t":f'{c["role"]} {c["pct"]}%'})
        else: badges.append({"t":f'{c["role"]}-{c.get("text","")}',"ext":1})
    if badges or d.get("tools") or d.get("colors") or d.get("concept"):
        note=' data-note="'+html.escape(json.dumps({"contrib":badges,"tools":d.get("tools") or [],"colors":d.get("colors") or [],"concept":d.get("concept") or ""},ensure_ascii=False),quote=True)+'"'
    return (f'<button type="button" class="dpcard{more}" data-k="{d["id"]}" data-pages="{pages}" data-title="{html.escape(d["title"])}"{note}>'
            f'{img}<span class="dpview">상세보기</span></button>')
dp_html=(f'<div class="moregroup" data-limit="{DETAIL_INITIAL}"><div class="dpgrid">{"".join(dp_card(n,d) for n,d in enumerate(details))}</div>'
         f'{more_btn(len(details),DETAIL_INITIAL)}</div>')

# 큰 이미지 + 하단 썸네일 뷰어(클릭 시 큰 이미지 교체) — 패키지·편집 공용
# .png가 있으면 우선 사용. 단, 실제로 투명 영역이 있는 누끼 PNG만 대리석 배경 위에 그림자로 표시.
# 배경이 채워진 PNG(투명 없음)는 jpg처럼 원본 배경 그대로 표시.
def _has_alpha(path):
    # PNG 헤더만 읽어 투명(알파) 채널 여부 판단 — 맥 전용 sips 대신 어디서나 동작하도록
    try:
        with open(path,"rb") as f: data=f.read()
        if data[:8]!=b"\x89PNG\r\n\x1a\n": return False
        color_type=data[25]
        return color_type in (4,6) or b"tRNS" in data[:data.find(b"IDAT")]
    except Exception:
        return False

def asset(im):
    png=os.path.join(OUT,"assets",f"{im}.png")
    if os.path.exists(png):
        # 같은 이름의 .webp가 있으면(tools/optimize_images.py로 만든 가벼운 버전) 그걸 사용. 누끼 여부는 원본 PNG로 판단.
        webp=os.path.join(OUT,"assets",f"{im}.webp")
        src=av(f"{im}.webp") if os.path.exists(webp) else f"assets/{im}.png"
        return (src, _has_alpha(png))
    return (f"assets/{im}.jpg", False)

# 항목별 미디어 판별: .mp4가 있으면 동영상(음소거·자동반복), 없으면 이미지(asset 규칙)
def media(im):
    base=os.path.join(OUT,"assets")
    if os.path.exists(os.path.join(base,f"{im}.mp4")):
        # 포스터: 자기 이름 이미지 우선, 없으면 base 제품 이미지(pk02-1 → pk02)
        poster=""
        for cand in (im, im.split("-")[0]):
            for ext in ("webp","png","jpg"):  # 가벼운 .webp가 있으면 우선
                if os.path.exists(os.path.join(base,f"{cand}.{ext}")):
                    poster=av(f"{cand}.{ext}");break
            if poster:break
        return {"kind":"video","src":f"assets/{im}.mp4","poster":poster,"cut":False}
    src,cut=asset(im)
    return {"kind":"image","src":src,"poster":"","cut":cut}

# 패키지 코너 설명 — 큰 이미지 바로 아래에 표시, 작은 이미지를 누르면 해당 제품 설명으로 바뀜.
# 키는 제품 기본 이름(pk01-1 영상은 pk01 설명을 함께 씀). shot=True면 제품촬영 100% + DSLR 카메라 추가.
PACKAGE_NOTES=SITE["package_notes"]  # 제품별 설명(제목·shot·colors·concept) — data/site.json
PACKAGE_TOOLS=SITE["package_tools"]
def pkg_note_html(key,n,active):
    roles="기획·디자인"+("·제품촬영" if n["shot"] else "")+" 100%"  # 상세페이지와 같은 '역할 → %' 순서
    tools=PACKAGE_TOOLS+(["DSLR 카메라"] if n["shot"] else [])
    tools_html=''.join(f'<span>{html.escape(t)}</span>' for t in tools)
    sw=''.join(f'<span class="dpsw" style="background:{c}" title="{c}"></span>' for c in n["colors"][:3])
    return (f'<div class="vnote" data-for="{key}"{"" if active else " hidden"}><h3>{html.escape(n["title"])}</h3>'
            f'<div class="dprow"><div class="dplabel">기여도</div><div class="dproles"><span>{roles}</span></div></div>'
            f'<div class="dprow"><div class="dplabel">사용툴</div><div class="dproles dptools">{tools_html}</div></div>'
            f'<div class="dprow"><div class="dplabel">컬러무드</div><div class="dpcolors">{sw}</div></div>'
            f'<div class="dplabel">기획 컨셉</div><p>{html.escape(n["concept"])}</p></div>')

def viewer(ids):
    items=[media(im) for im in ids]
    def thumb(i,it):
        active=" active" if i==0 else ""
        if it["kind"]=="video":
            return (f'<button class="vt vid{active}" data-kind="video" data-src="{it["src"]}" data-poster="{it["poster"]}" data-cut="0">'
                    f'<img src="{it["poster"]}" loading="lazy" alt=""><span class="playbadge">▶</span></button>')
        cutc=" cut" if it["cut"] else ""
        return (f'<button class="vt{cutc}{active}" data-kind="image" data-src="{it["src"]}" data-cut="{1 if it["cut"] else 0}">'
                f'<img src="{it["src"]}" loading="lazy" alt=""></button>')
    thumbs=''.join(thumb(i,it) for i,it in enumerate(items))
    # 제품 설명(패키지 코너만 해당) — 썸네일마다 어떤 설명을 보여줄지 data-note로 연결
    keys=[im.split("-")[0] for im in ids]
    notes_html=''.join(pkg_note_html(k,PACKAGE_NOTES[k],k==keys[0]) for k in dict.fromkeys(keys) if k in PACKAGE_NOTES)
    if notes_html:
        tl=[thumb(i,it) for i,it in enumerate(items)]
        thumbs=''.join(t.replace('<button ',f'<button data-note="{keys[i]}" ',1) if keys[i] in PACKAGE_NOTES else t for i,t in enumerate(tl))
    f=items[0]
    if f["kind"]=="video":
        cls=" video";data_cut="0"
        big=f'<img class="vm-img" alt="" hidden><video class="vm-vid" src="{f["src"]}" poster="{f["poster"]}" muted loop playsinline autoplay></video>'
    else:
        cls=" cut" if f["cut"] else "";data_cut="1" if f["cut"] else "0"
        big=f'<img class="vm-img" src="{f["src"]}" alt=""><video class="vm-vid" muted loop playsinline hidden></video>'
    return f'''<div class="viewer reveal">
    <div class="vmain{cls}" data-full="{f["src"]}" data-cut="{data_cut}" data-kind="{f["kind"]}" data-poster="{f["poster"]}">{big}<span class="vcap">AI를 이용하여 제작된 3D 목업 영상입니다</span></div>
    {notes_html}<div class="vthumbs">{thumbs}</div>
  </div>'''

# 자사몰 고도화 — 아래 요약(지표 카드 · 기존/개선 비교)
pj=project
# 우측 텍스트(bd)가 좌측 이미지보다 짧아서 그 아래에 "한눈에 보는 핵심"이 별도 섹션으로 다시 나오면
# 여백만 있다가 또 내용이 이어지는 것처럼 보인다는 피드백 → 핵심 요약(스탯 카드·비교박스)을 아예
# bd 안으로 옮겨서, 이미지 오른쪽 공간 하나에만 전체 내용이 들어가도록 통합함. 겹치던 points 목록은 삭제.
badges_html=''.join(f'<span class="contrib">{s}</span>' for s in [pj['roles'],*pj['stats']])
steps_html=''.join(f'<li>{x}</li>' for x in pj['steps'])
prob_html=''.join(f'<li>{x}</li>' for x in pj['problem'])
sol_html=''.join(f'<li>{x}</li>' for x in pj['solution'])
proj_html=f'''<div class="case reveal">
  <div class="magrow"><div class="im" data-full="assets/{pj['img']}.jpg"><img src="assets/{pj['img']}.jpg" loading="lazy" alt="{pj['title']}"></div>
  <div class="bd"><h3>{pj['title']}</h3><p class="lead-p">{pj['lead']}</p>
    <ul class="steps">{steps_html}</ul>
    <div class="projfacts">{badges_html}</div>
    <div class="compare">
      <div class="cbox before"><span class="clab">기존 방식</span><ul>{prob_html}</ul></div>
      <div class="cbox after"><span class="clab">시스템 도입 후</span><ul>{sol_html}</ul></div>
    </div>
  </div></div>
</div>'''
cv_html=''.join(f'''<div class="row"><div class="yr">{y}</div><div><div class="co">{c}</div><div class="ro">{r}</div><div class="du">{d}</div></div></div>''' for (y,c,r,d) in career[::-1])

ICON_CHAT='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>'
ICON_HEART='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 1 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
ICON_UP='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'

# 상세페이지 팝업 + 더보기/접기 스크립트 (f-string 밖에 두어 중괄호 이스케이프 불필요)
DP_JS=r'''
// 목업 자동 스크롤 — 태블릿 → 휴대폰 순서로 번갈아 재생(무한 반복). 약 45px/초로 천천히.
// 한 화면의 순서: 첫 화면에서 잠깐 멈춤 → 끝까지 스크롤 → 잠깐 멈춤 → 흰색으로 서서히 사라짐 → 첫 화면이 서서히 나타나 멈춤.
// 그동안 다른 화면은 첫 화면에서 멈춰 있음. 화면 크기가 바뀌면 거리·시간을 다시 계산.
(function(){
  const wrap=document.querySelector('.mockwrap');if(!wrap)return;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const screens=['tablet','phone'].map(c=>wrap.querySelector('.mockscreen.'+c)).filter(Boolean);
  const SPEED=45,HOLD=1500,FADE=2500,WHITE=400;
  let anims=[],visible=false;
  function setup(){
    const segs=screens.map(scr=>{const inner=scr.querySelector('.mockscroll');
      const dist=inner.offsetHeight-scr.clientHeight;
      return {inner,dist,len:dist>0?HOLD+dist/SPEED*1000+HOLD+FADE+WHITE+FADE:0};});
    if(segs.some(g=>g.len<=0))return;
    anims.forEach(a=>a.cancel());
    const total=segs.reduce((t,g)=>t+g.len,0);let start=0;
    anims=segs.map(g=>{
      const o=t=>(start+t)/total, top='translateY(0)', bot=`translateY(${-g.dist}px)`;
      let t=0;const k=[{offset:0,transform:top,opacity:1}];
      if(start>0)k.push({offset:o(0),transform:top,opacity:1});
      t+=HOLD;k.push({offset:o(t),transform:top,opacity:1});
      t+=g.dist/SPEED*1000;k.push({offset:o(t),transform:bot,opacity:1});
      t+=HOLD;k.push({offset:o(t),transform:bot,opacity:1});
      t+=FADE;k.push({offset:o(t),transform:bot,opacity:0});
      k.push({offset:o(t)+0.0001,transform:top,opacity:0});
      t+=WHITE;k.push({offset:o(t),transform:top,opacity:0});
      t+=FADE;k.push({offset:Math.min(1,o(t)),transform:top,opacity:1});
      if(o(t)<1)k.push({offset:1,transform:top,opacity:1});
      start+=g.len;
      return g.inner.animate(k,{duration:total,iterations:Infinity});
    });
    if(!visible)anims.forEach(a=>a.pause());
  }
  let timer;new ResizeObserver(()=>{clearTimeout(timer);timer=setTimeout(setup,150);}).observe(wrap);
  // 목업이 화면에 보일 때만 움직이고, 화면 밖으로 나가면 그 자리에서 멈춤(배터리·처리 부담 줄이기)
  new IntersectionObserver(es=>es.forEach(e=>{visible=e.isIntersecting;anims.forEach(a=>visible?a.play():a.pause());})).observe(wrap);
})();
// 더보기 / 접기 — .moregroup 안의 .more 항목을 한꺼번에 펼치고 접음
// 처음 보일 개수(data-limit)는 화면 폭에 따른 열 개수에 맞춰 마지막 줄이 꽉 차도록 올림(예: 20개·3열 → 21개)
document.querySelectorAll('.moregroup').forEach(g=>{
  const b=g.querySelector('.morebtn'),grid=g.firstElementChild,base=+g.dataset.limit||0;if(!b||!base)return;
  const items=[...grid.children];
  const label=()=>{b.innerHTML=g.classList.contains('open')?'접기':'더보기 <span>+'+b.dataset.more+'</span>';};
  function fit(){
    const cols=getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length||1;
    const limit=Math.ceil(base/cols)*cols;
    items.forEach((el,i)=>el.classList.toggle('more',i>=limit));
    const rest=items.length-limit;b.dataset.more=rest;b.parentElement.hidden=rest<=0;label();
  }
  fit();let t;new ResizeObserver(()=>{clearTimeout(t);t=setTimeout(fit,100);}).observe(grid);
  b.addEventListener('click',()=>{
    const open=g.classList.toggle('open');label();
    if(!open)b.scrollIntoView({block:'center'});
  });
});
// 상세페이지 팝업 — 전체 화면, 팝업 안에서 위아래 스크롤. X 버튼·바깥 클릭·ESC로 닫힘
// ‹ › 버튼(또는 ←/→ 키)으로 상세페이지가 있는 다음·이전 작업으로 바로 이동. 어떤 경우든 항상 맨 위부터 보여줌
(function(){
  const pop=document.getElementById('dpop'),body=pop.querySelector('.dpop-body'),note=pop.querySelector('.dpop-note'),wrap=pop.querySelector('.dpop-wrap'),scroller=pop.querySelector('.dpop-scroll');
  const cards=[...document.querySelectorAll('.dpcard[data-pages]')];let cur=0;
  function show(i){
    cur=(i+cards.length)%cards.length;const card=cards[cur];
    const pages=JSON.parse(card.dataset.pages);
    body.innerHTML=pages.map((p,i)=>'<img src="'+p[0]+'" width="'+p[1]+'" height="'+p[2]+'" alt="" '+(i?'loading="lazy"':'')+'>').join('');
    body.setAttribute('aria-label',card.dataset.title+' 상세페이지');
    // 상단 메모 — 작업명 · 기여한 부분(배지) · 기획 컨셉 (상세 이미지 위, 별도 박스)
    note.innerHTML='';note.hidden=!card.dataset.note;
    if(card.dataset.note){
      const n=JSON.parse(card.dataset.note),box=note;
      const h=document.createElement('h3');h.textContent=card.dataset.title;box.appendChild(h);
      function row(label,items,cls){const w=document.createElement('div');w.className='dprow';
        const l=document.createElement('div');l.className='dplabel';l.textContent=label;w.appendChild(l);
        const r=document.createElement('div');r.className='dproles '+cls;
        items.forEach(it=>{const s=document.createElement('span');s.textContent=it.t;if(it.ext)s.className='ext';r.appendChild(s);});
        w.appendChild(r);box.appendChild(w);}
      if(n.contrib.length)row('기여도',n.contrib,'');
      if(n.tools.length)row('사용툴',n.tools.map(t=>({t})),'dptools');
      // 컬러무드 — 디자인의 주컬러(동그라미, 최대 3개)
      if(n.colors&&n.colors.length){const w=document.createElement('div');w.className='dprow';
        const l=document.createElement('div');l.className='dplabel';l.textContent='컬러무드';w.appendChild(l);
        const r=document.createElement('div');r.className='dpcolors';
        n.colors.slice(0,3).forEach(c=>{const sw=document.createElement('span');sw.className='dpsw';sw.style.background=c;sw.title=c;r.appendChild(sw);});
        w.appendChild(r);box.appendChild(w);}
      if(n.concept){const l=document.createElement('div');l.className='dplabel';l.textContent='기획 컨셉';box.appendChild(l);
        const p=document.createElement('p');p.textContent=n.concept;box.appendChild(p);}
    }
    scroller.scrollTop=0;
    // 다음·이전 상세페이지 첫 장을 미리 받아 두기(지금 보는 첫 장이 다 뜬 뒤) → 다음 버튼을 누르면 바로 보임
    const first=body.querySelector('img'),pre=()=>[cur+1,cur-1].forEach(j=>{const c=cards[(j+cards.length)%cards.length];try{const p=JSON.parse(c.dataset.pages);p.slice(0,2).forEach(x=>{new Image().src=x[0];});}catch(e){}});
    if(first&&!first.complete)first.addEventListener('load',pre,{once:true});else pre();
  }
  function open(i){pop.classList.add('on');document.body.style.overflow='hidden';show(i);scroller.scrollTop=0;}
  function close(){pop.classList.remove('on');document.body.style.overflow='';body.innerHTML='';}
  cards.forEach((c,i)=>c.addEventListener('click',()=>open(i)));
  pop.querySelector('.dpop-x').addEventListener('click',close);
  pop.querySelector('.dpop-nav.prev').addEventListener('click',()=>show(cur-1));
  pop.querySelector('.dpop-nav.next').addEventListener('click',()=>show(cur+1));
  scroller.addEventListener('click',e=>{if(!body.contains(e.target)&&!note.contains(e.target))close();});
  addEventListener('keydown',e=>{if(!pop.classList.contains('on'))return;
    if(e.key==='Escape')close();else if(e.key==='ArrowLeft')show(cur-1);else if(e.key==='ArrowRight')show(cur+1);});
})();
'''

# ── 페이지 고정 문구(제목·소개·프로필·About·푸터) — data/site.json의 texts ─────────
# 방문·클릭 세기(4단계 통계) — 화면이 다 뜬 뒤 작은 신호만 보냄(navigator.sendBeacon, 쿠키·개인정보 없음).
# 관리자 화면에서 '이 브라우저는 통계에서 제외'를 켜면(localStorage no-track) 세지 않음. 같은 탭에서 새로고침해도 방문은 1번만.
TRACK_JS=("(function(){try{if(localStorage.getItem('no-track'))return;}catch(e){}"
 "var send=function(o){try{navigator.sendBeacon('/api/track',JSON.stringify(o));}catch(e){}};"
 "addEventListener('load',function(){setTimeout(function(){try{if(sessionStorage.getItem('vt'))return;sessionStorage.setItem('vt','1');}catch(e){}"
 "var r='';try{var u=new URL(document.referrer);if(u.host!==location.host)r=u.hostname;}catch(e){}send({t:'v',r:r});},1500);});"
 "var key=function(el){if(el.dataset.k)return el.dataset.k;var s=el.dataset.full||el.dataset.src||'';var m=s.match(/assets\\/([a-z]+\\d+(?:-[a-z0-9]+)?)/i);return m?m[1].replace(/-(thumb|still)$/,''):'';};"
 "document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('a,.dpcard,.vt,.vmain,.tile,.prodimg,.aimedia,.morebtn');if(!t)return;var k='';"
 "if(t.tagName==='A'){var h=t.getAttribute('href')||'';if(h.indexOf('mailto:')===0)k='mail';else if(h.indexOf('tel:')===0)k='tel';"
 "else if(t.classList.contains('prodlink')){var c=t.closest('.prodcard');var im=c&&c.querySelector('.prodimg');k=im?'link-'+key(im):'';}}"
 "else if(t.classList.contains('morebtn'))k='more';else k=key(t);if(k)send({t:'c',k:k.slice(0,40)});},true);})();")

T=SITE["texts"]; C=T["contact"]; S=T["sections"]
def esc(x): return html.escape(x,quote=False)
def spans(items): return ''.join(f'<span>{esc(x)}</span>' for x in items)
def contribs(items): return ''.join(f'<span class="contrib">{esc(x)}</span>' for x in items)
def hint(sec): return f'<span class="vhint">{esc(sec["hint"])}</span>' if sec.get("hint") else ''
TEL=C["phone"].replace("-","")
tel_link=f'<a href="tel:{TEL}">{esc(C["phone"])}</a>'
mail_link=f'<a href="mailto:{C["email"]}">{esc(C["email"])}</a>'
career_badges='\n'.join(f'      <span>{esc(x)}</span>' for x in S["career"]["badges"])
about_html='\n'.join(f'    <p>{p}</p>' for p in T["about"]["paragraphs"])  # About 문단은 <br>·<b> 허용

html=f'''<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(T["meta"]["title"])}</title>
<meta name="description" content="{html.escape(T["meta"]["description"])}">
<link rel="icon" type="image/svg+xml" href="favicon.svg?v={FAVICON_VER}">
<link rel="stylesheet" href="style.css?v={CSS_VER}">
</head><body>

<nav class="nav" id="nav">
  <a href="#top" class="brand"><span class="ko">{esc(C["name"])}</span><span class="en">{esc(C["name_en"])}</span></a>
  <div class="nav-links"><a href="#s01">Work</a><a href="#about">About</a><a href="#contact">Contact</a></div>
</nav>

<header class="hero" id="top"><div class="wrap">
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="eyebrow reveal">{esc(T["hero"]["eyebrow"])}</div>
      <h1 class="reveal">{esc(T["hero"]["title1"])}<br><span class="mark">{esc(T["hero"]["title2"])}</span></h1>
      <p class="hero-sub reveal">{esc(T["hero"]["sub"])}</p>
      <div class="hero-meta reveal">{'<span class="dot"></span>'.join(f'<span>{esc(x)}</span>' for x in T["hero"]["meta"])}</div>
    </div>
    <div class="profile reveal">
      <h3>{esc(T["profile"]["title"])}</h3>
      <div class="kv"><span class="k">이름</span><span class="v">{esc(C["name"])}</span></div>
      <div class="kv"><span class="k">연락처</span><span class="v">{tel_link}</span></div>
      <div class="kv"><span class="k">이메일</span><span class="v">{mail_link}</span></div>
      <div class="kv"><span class="k">학력</span><span class="v">{esc(T["profile"]["education"])}</span></div>
      <div class="kv"><span class="k">자격증</span><span class="v">{esc(T["profile"]["certificates"])}</span></div>
      <div class="kv"><span class="k">Tools</span><span class="v"><div class="tags">{spans(T["profile"]["tools"])}</div></span></div>
    </div>
  </div>
</div></header>

<div class="wrap"><div class="hr"></div></div>

<section class="sec tight" id="interview"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["interview"]["en"])}</div><h2>{esc(S["interview"]["title"])}</h2><p>{S["interview"]["desc"]}</p></div>
  <div class="chatbox reveal" id="chatbox" data-qa='{chat_qa_json}'>
    <div class="chatview" id="chatview"></div>
  </div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec tight" id="products"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["products"]["en"])}</div><h2>{esc(S["products"]["title"])}</h2><p>{S["products"]["desc"]}</p></div>
  <div class="prodgrid">{products_html}</div>
</div></section>

<section class="sec" id="s06" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["project"]["en"])}</div><h2>{esc(S["project"]["title"])}</h2></div>
  {proj_html}
</div></section>

<section class="sec tight" id="ai"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["ai"]["en"])}</div><h2>{esc(S["ai"]["title"])}</h2>
    <div class="aitools">{spans(S["ai"]["tools"])}</div>
    <p>{S["ai"]["desc"]}{hint(S["ai"])}</p>
  </div>
  <div class="airows">{ai_html}</div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec" id="s01"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["detail"]["en"])}</div><h2>{esc(S["detail"]["title"])}</h2><p>{detail_desc}</p></div>
  <div class="dshots reveal">{detail_html}</div>
  <div class="reveal">{dp_html}</div>
</div></section>

<section class="sec" id="s02" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["package"]["en"])}</div><h2>{esc(S["package"]["title"])}</h2><p>{S["package"]["desc"]}</p>{contribs(S["package"]["badges"])}{hint(S["package"])}</div>
  {viewer(package)}
</div></section>

<section class="sec" id="s03"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["editorial"]["en"])}</div><h2>{esc(S["editorial"]["title"])}</h2><p>{S["editorial"]["desc"]}</p>{contribs(S["editorial"]["badges"])}{hint(S["editorial"])}</div>
  {viewer(editorial)}
</div></section>

<section class="sec" id="s04" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["photo"]["en"])}</div><h2>{esc(S["photo"]["title"])}</h2><p>{S["photo"]["desc"]}</p>{contribs(S["photo"]["badges"])}{hint(S["photo"])}</div>
  <div class="reveal">{tiles(photo,PHOTO_INITIAL)}</div>
</div></section>

<section class="sec tight" id="career"><div class="wrap">
  <div class="sec-head reveal"><div class="en">{esc(S["career"]["en"])}</div><h2>{esc(S["career"]["title"])}</h2>
    <div class="cvmeta reveal">
{career_badges}
    </div>
  </div>
  <div class="cv reveal">{cv_html}</div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec about" id="about"><div class="wrap">
  <div class="about-head reveal">
    <div class="lead"><span class="hl">{esc(T["about"]["lead"])}</span></div>
  </div>
  <div class="story-one reveal">
{about_html}
  </div>
</div></section>

<footer class="foot" id="contact"><div class="wrap">
  <div class="big">{T["footer"]["big"]}</div>
  <div class="info">{esc(T["footer"]["role"])} {esc(C["name"])}<br>{tel_link}<br>{mail_link}</div>
</div><div class="wrap"><div class="copy">{esc(T["footer"]["copy"])}</div></div></footer>

<div class="lb" id="lb"><div class="x">×</div><div class="navbtn prev" id="lbPrev">‹</div><div class="navbtn next" id="lbNext">›</div><img src="" alt=""><video class="lb-vid" playsinline controls hidden></video><div class="lbplay" id="lbPlay" hidden>▶</div><span class="lbcap"></span></div>
<div class="dpop" id="dpop" role="dialog" aria-modal="true"><button type="button" class="dpop-x" aria-label="닫기">×</button><button type="button" class="dpop-nav prev" aria-label="이전 상세페이지">‹</button><button type="button" class="dpop-nav next" aria-label="다음 상세페이지">›</button><div class="dpop-scroll"><div class="dpop-wrap"><div class="dpop-note" hidden></div><div class="dpop-body"></div></div></div></div>

<script>
const nav=document.getElementById('nav');
addEventListener('scroll',()=>nav.classList.toggle('scrolled',scrollY>40));
// 글자를 실제로 추가하지 않고, 미리 전체 글자를 (안 보이게) 다 배치해두기만 한다(prepare).
// → 줄바꿈 위치가 처음부터 고정돼 있어서 타이핑 중간에 단어가 다음 줄로 튀는 현상이 없고,
//   Q·A 두 문단을 쌍으로 만들 때 "둘 다" 미리 배치해두면 나중에 A 타이핑이 시작되는 순간
//   레이아웃 높이가 갑자기 늘어나며 스크롤이 튀는 현상도 함께 방지된다.
function prepareType(el){{
  const text=el.dataset.text||'';
  el.innerHTML='';
  // 텍스트 속 줄바꿈(\\n)은 타이핑 애니메이션 없이 <br>로 즉시 배치(한 말풍선 안에서 문장을 줄만 나눠 보여줄 때 사용)
  const spans=[...text].map(ch=>{{
    if(ch==='\\n'){{el.appendChild(document.createElement('br'));return null;}}
    const s=document.createElement('span');s.className='ch';s.textContent=ch;el.appendChild(s);return s;
  }}).filter(Boolean);
  const cur=document.createElement('span');cur.className='cur';
  el.insertBefore(cur,spans[0]||null);
  let i=0,done=false,paused=false,timer=null,curSpeed=0,onDoneCb=null,onTickCb=null;
  function scheduleNext(delay){{timer=setTimeout(tick,delay);}}
  // setTimeout 체인 + 약간의 랜덤 편차를 줘서 기계적으로 균일하지 않고 사람이 타이핑하듯 자연스럽게
  function tick(){{
    if(spans[i])spans[i].classList.add('on');
    i++;el.insertBefore(cur,spans[i]||null);if(onTickCb)onTickCb();
    if(i>=spans.length){{finish();return;}}
    if(paused)return; // pause() 호출로 멈춘 상태면 다음 글자를 예약하지 않고 여기서 대기(위치 i는 유지)
    const jitter=curSpeed*0.35;
    scheduleNext(curSpeed+(Math.random()*jitter*2-jitter));
  }}
  // play(): 실제로 한 글자씩 보이게 전환을 시작한다(호출 전까지는 전부 투명 상태로 자리만 차지)
  function play(speed,onDone,onTick){{curSpeed=speed;onDoneCb=onDone;onTickCb=onTick;scheduleNext(speed);}}
  function finish(){{if(done)return;done=true;clearTimeout(timer);if(cur.parentNode)cur.remove();if(onDoneCb)onDoneCb();}}
  // pause(): 멈췄던 글자 위치(i)는 그대로 두고 다음 글자 타이머만 취소. resume(): 그 자리에서 이어서 진행.
  function pause(){{if(done||paused)return;paused=true;clearTimeout(timer);}}
  function resume(){{if(done||!paused)return;paused=false;scheduleNext(curSpeed);}}
  return {{play,pause,resume}};
}}
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{
  e.target.classList.add('in');io.unobserve(e.target);
}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

// 인터뷰: 고정 크기 박스 안에서 한 쌍씩 타이핑하며 계속 자동으로 다음 대화로 넘어감. 클릭하면 그 자리에서
// 타이핑이 멈추고(위치는 유지) 휠로 지나간 대화를 자유롭게 볼 수 있음 — 다시 클릭/마우스가 영역을 벗어남/
// 5초간 마우스 정지 중 하나라도 일어나면 멈췄던 자리에서 이어서 타이핑 재생.
const chatbox=document.getElementById('chatbox');
if(chatbox){{
  const pairs=JSON.parse(chatbox.dataset.qa);
  const view=document.getElementById('chatview');
  let idx=-1,timer=null,started=false,browsing=false;
  // 일시정지 상태 관리 — sched()는 setTimeout의 대체제로, 일시정지 중이면 예약된 함수를 큐에만 담아뒀다가
  // resumeTyping()에서 이어서 실행한다(다음 대화/다음 말풍선으로 넘어가는 대기시간도 함께 멈추기 위함).
  let paused=false,activeTyper=null,activeEl=null,queuedFn=null,pendingFn=null,idleT=null;
  function sched(fn,delay){{
    clearTimeout(timer);
    pendingFn=fn; // 지금 예약해두는 함수를 기억해뒀다가, 일시정지가 그 대기시간 중에 걸리면 잃어버리지 않게 함
    if(paused){{queuedFn=fn;pendingFn=null;return;}}
    timer=setTimeout(()=>{{pendingFn=null;fn();}},delay);
  }}
  function resetIdle(){{clearTimeout(idleT);idleT=setTimeout(resumeTyping,5000);}}
  function pauseTyping(){{
    if(paused)return;
    paused=true;browsing=true;
    clearTimeout(timer);
    // 대화/말풍선 전환 사이의 "쉬는 시간" 도중에 멈춘 경우, 그때 예약돼 있던 다음 진행을 잃어버리지 않도록
    // queuedFn으로 옮겨서 재개 시 이어서 실행되게 한다(안 그러면 타이핑 도중이 아닌 순간에 멈췄을 때 영원히 멈춰버림).
    if(pendingFn){{queuedFn=pendingFn;pendingFn=null;}}
    if(activeTyper)activeTyper.pause();
    resetIdle();
  }}
  function resumeTyping(){{
    if(!paused)return;
    paused=false;browsing=false;clearTimeout(idleT);
    if(activeTyper){{activeTyper.resume();if(activeEl)followCursor(activeEl);}}
    if(queuedFn){{const f=queuedFn;queuedFn=null;timer=setTimeout(f,150);}}
  }}
  // 새 대화가 시작될 땐 항상 바닥으로 스크롤. 타이핑 중엔(한 글자씩) 이미 바닥 근처에 있을 때만 계속 따라가고,
  // 사용자가 위로 스크롤해서 읽고 있으면 그 위치를 건드리지 않음(타이핑 자체는 배경에서 계속 진행)
  // 대화 로그가 길어질수록 한 번에 스크롤해야 할 거리가 커지는데, 'smooth'로 멀리 스크롤을 시키면
  // 애니메이션이 끝까지 진행되지 못하고 중간에 멈춰버려(특히 답변이 긴 마지막 문항에서) 답변이
  // 화면 밖에 가려진 채로 타이핑되는 버그가 있었음 → 즉시 이동으로 바꿔 항상 확실하게 바닥까지 붙게 한다
  // ★ 스크롤은 "내용의 맨 아래"가 아니라 "지금 타이핑 중인 커서"를 따라간다.
  //   글자는 줄바꿈이 튀지 않도록 안 보이는 상태로 미리 다 배치해두는데, 그 상태에서 맨 아래로 스크롤하면
  //   아직 아무것도 안 찍힌 빈 공간이 화면을 가득 채우고(질문이 위로 밀려 안 보이고) 답변도 화면 밖에서
  //   타이핑되다 중간부터 갑자기 나타나는 문제가 있었음 → 커서가 항상 화면 안에 있도록 최소한만 스크롤.
  const PAD=44; // 위·아래 페이드 영역에 글자가 가리지 않도록 확보하는 여백
  function followCursor(el){{
    if(browsing)return;
    const cur=el&&el.querySelector('.cur');
    if(!cur)return;
    const cr=cur.getBoundingClientRect(),vr=view.getBoundingClientRect();
    const below=cr.bottom-(vr.bottom-PAD);
    if(below>0){{view.scrollTop+=below;return;}}
    const above=(vr.top+PAD)-cr.top;
    if(above>0)view.scrollTop-=above;
  }}
  function appendPair(i){{
    const [q,a]=pairs[i];
    const pair=document.createElement('div');
    pair.className='chatpair';
    // q 또는 a가 없으면(null) 그쪽 말풍선은 아예 만들지 않고 반대쪽만 혼자 나온다(첫 자기소개용)
    const turns=[];
    if(q){{const qP=document.createElement('p');qP.className='type';qP.dataset.text=q;
      const qB=document.createElement('div');qB.className='bubble q';qB.appendChild(qP);
      pair.appendChild(qB);turns.push({{p:qP,speed:100,b:qB}});}}
    if(a){{const aP=document.createElement('p');aP.className='type';aP.dataset.text=a;
      const aB=document.createElement('div');aB.className='bubble a';aB.appendChild(aP);
      pair.appendChild(aB);turns.push({{p:aP,speed:100,b:aB}});}}
    // 자기 차례가 되기 전까지는 말풍선 배경 자체를 숨겨둔다(레이아웃 공간은 이미 확보돼 있지만, 빈 말풍선이 미리 보이지 않도록)
    turns.slice(1).forEach(t=>t.b.classList.add('pending'));
    view.appendChild(pair);
    // 이 쌍에 포함된 말풍선들의 전체 레이아웃을 지금 미리 다 잡아둔다(투명 상태) — 나중 차례가 와도 높이가 갑자기 안 늘어남
    turns.forEach(t=>t.t=prepareType(t.p));
    // turns를 순서대로 하나씩 타이핑(마우스와 무관하게 항상 같은 속도) — 마지막 것까지 끝나면 다음 쌍으로
    function playTurn(k){{
      const t=turns[k];
      activeTyper=t.t;activeEl=t.p; // 일시정지 시 이 타이핑을 멈추고, 재개 시 이 위치로 스크롤을 되돌리기 위해 기억해둠
      t.b.classList.remove('pending');
      followCursor(t.p); // 새 말풍선이 시작될 때 그 첫 줄이 보이도록 필요한 만큼만 스크롤
      t.t.play(t.speed,()=>{{
        followCursor(t.p);
        // 다음 말풍선으로 넘어가기 전 쉬는 동안 미리 위치를 잡아둬서, 타이핑 시작과 스크롤이 겹치지 않게 한다
        if(k+1<turns.length){{followCursor(turns[k+1].p);sched(()=>playTurn(k+1),350);}}
        // 마지막 마무리 인사까지 끝나면 3초 쉬었다가 처음 인사부터 다시 재생
        else{{sched(next,i===pairs.length-1?3000:500);}}
      }},()=>followCursor(t.p));
    }}
    playTurn(0);
  }}
  function next(){{
    // 마지막 대화(마무리 인사)까지 다 본 뒤 처음으로 돌아가는 경우에만: 3초 대기(playTurn 쪽에서 이미 처리)
    // 후 전체 내용을 서서히 페이드아웃(0.6초) → 완전히 사라진 채로 4초 더 대기 → 비우고 첫 인사부터 다시 시작.
    // 그 외(평소 다음 대화로 넘어갈 때)엔 페이드 없이 바로 이어짐.
    const wrapping=idx===pairs.length-1;
    idx=(idx+1)%pairs.length;
    clearTimeout(timer);
    if(wrapping){{
      view.classList.add('fadeout');
      setTimeout(()=>{{
        view.innerHTML='';
        view.scrollTop=0;
        view.classList.remove('fadeout');
        appendPair(idx);
      }},600+4000);
    }}else{{
      appendPair(idx);
    }}
  }}
  // 클릭하면 타이핑을 그 자리에서 멈추고(browsing=true라 자동 스크롤도 함께 멈춤) 휠로 자유롭게 훑어볼 수 있게 함.
  // 다시 클릭하거나, 마우스가 인터뷰 영역을 벗어나거나, 5초간 마우스를 움직이지 않으면(정지 상태) 자동으로 재개.
  view.addEventListener('click',()=>{{paused?resumeTyping():pauseTyping();}});
  view.addEventListener('mouseleave',()=>{{if(paused)resumeTyping();}});
  view.addEventListener('mousemove',()=>{{if(paused)resetIdle();}});
  // 휠로 위로 스크롤해도(클릭하지 않은 상태여도) 지나간 대화를 읽는 중으로 보고 자동 따라가기만 멈춘다.
  // 다시 지금 타이핑 중인 위치까지 내려오면 자동 따라가기가 스스로 복구된다(일시정지 중이 아닐 때만).
  view.addEventListener('wheel',e=>{{if(e.deltaY<0)browsing=true;}},{{passive:true}});
  view.addEventListener('scroll',()=>{{
    if(!browsing||paused)return;
    const cur=view.querySelector('.cur');
    if(!cur)return;
    const cr=cur.getBoundingClientRect(),vr=view.getBoundingClientRect();
    if(cr.top>=vr.top&&cr.bottom<=vr.bottom)browsing=false;
  }},{{passive:true}});
  new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting&&!started){{started=true;next();}}}}),{{threshold:.4}}).observe(chatbox);
}}
document.querySelectorAll('.viewer').forEach(v=>{{
  const main=v.querySelector('.vmain'),mimg=main.querySelector('.vm-img'),mvid=main.querySelector('.vm-vid');
  v.querySelectorAll('.vt').forEach(t=>t.addEventListener('click',()=>{{
    main.dataset.full=t.dataset.src;main.dataset.cut=t.dataset.cut;main.dataset.kind=t.dataset.kind;main.dataset.poster=t.dataset.poster||'';
    if(t.dataset.kind==='video'){{
      mvid.src=t.dataset.src;mvid.poster=t.dataset.poster||'';mvid.hidden=false;mvid.play().catch(()=>{{}});
      mimg.hidden=true;mimg.removeAttribute('src');main.classList.add('video');main.classList.remove('cut');
    }}else{{
      mvid.pause();mvid.hidden=true;mvid.removeAttribute('src');
      mimg.src=t.dataset.src;mimg.hidden=false;main.classList.remove('video');main.classList.toggle('cut',t.dataset.cut==='1');
    }}
    v.querySelectorAll('.vt').forEach(x=>x.classList.remove('active'));t.classList.add('active');
    if(t.dataset.note)v.querySelectorAll('.vnote').forEach(n=>n.hidden=n.dataset.for!==t.dataset.note);
  }}));
}});
const lb=document.getElementById('lb'),lbimg=lb.querySelector('img'),lbvid=lb.querySelector('.lb-vid'),lbcap=lb.querySelector('.lbcap'),lbPlay=document.getElementById('lbPlay');
let gallery=[],gi=0;
function show(i){{gi=(i+gallery.length)%gallery.length;const it=gallery[gi];lb.classList.toggle('vidcap',it.kind==='video');
  if(it.kind==='video'){{lbimg.hidden=true;lbimg.removeAttribute('src');lbvid.src=it.src;lbvid.poster=it.poster||'';
    lbvid.muted=it.muted!==false;lbvid.loop=it.loop!==false;lbvid.hidden=false;
    if(it.autoplay===false){{lbvid.pause();lbPlay.hidden=false;}}else{{lbvid.play().catch(()=>{{}});lbPlay.hidden=true;}}
    lbcap.textContent=it.cap||'AI를 이용하여 제작된 3D 목업 영상입니다';lb.classList.remove('cut');}}
  else{{lbvid.pause();lbvid.hidden=true;lbvid.removeAttribute('src');lbimg.src=it.src;lbimg.hidden=false;lb.classList.toggle('cut',!!it.cut);lbPlay.hidden=true;}}
  // 다음·이전 이미지를 미리 받아 두기(지금 이미지가 다 뜬 뒤) → 넘길 때 바로 보임
  if(gallery.length>1){{const pre=()=>[gi+1,gi-1].forEach(j=>{{const n=gallery[(j+gallery.length)%gallery.length];if(n&&n.kind!=='video')new Image().src=n.src;}});
    if(it.kind!=='video'&&!lbimg.complete)lbimg.addEventListener('load',pre,{{once:true}});else pre();}}}}
lbPlay.addEventListener('click',e=>{{e.stopPropagation();lbvid.play().catch(()=>{{}});lbPlay.hidden=true;}});
function openLb(list,idx){{gallery=list;lb.classList.toggle('nav',list.length>1);show(idx);lb.classList.add('on');document.body.style.overflow='hidden';}}
const handled=new Set();
// 패키지·편집 뷰어: 썸네일 전체를 갤러리로, 현재 활성 이미지에서 시작
document.querySelectorAll('.viewer').forEach(v=>{{
  const main=v.querySelector('.vmain');handled.add(main);
  const thumbs=[...v.querySelectorAll('.vt')];
  const list=thumbs.map(t=>({{src:t.dataset.src,cut:t.dataset.cut==='1',kind:t.dataset.kind,poster:t.dataset.poster||''}}));
  main.addEventListener('click',()=>{{const idx=Math.max(0,thumbs.findIndex(t=>t.classList.contains('active')));openLb(list,idx);}});
}});
// 상세페이지: _full 이미지들을 하나의 갤러리로
const dEls=[...document.querySelectorAll('.dshots [data-full]')];
const dList=dEls.map(el=>({{src:el.dataset.full,cut:el.dataset.cut==='1'}}));
dEls.forEach((el,i)=>{{handled.add(el);el.addEventListener('click',()=>openLb(dList,i));}});
// 사진 촬영: 타일 전체를 하나의 갤러리로
const pEls=[...document.querySelectorAll('.tiles [data-full]')];
const pList=pEls.map(el=>({{src:el.dataset.full,cut:el.dataset.cut==='1'}}));
pEls.forEach((el,i)=>{{handled.add(el);el.addEventListener('click',()=>openLb(pList,i));}});
// AI 활용 작업물: 대표 이미지를 클릭했을 때만 화면 가득 확대 (설명 텍스트는 클릭 대상 아님)
// 상품(행)의 영상+콘셉트 이미지를 하나의 갤러리로 묶어서, 영상 재생 후 좌우로 넘기면 그 상품의 콘셉트 이미지로 넘어가도록 함
// (다른 상품으로는 넘어가지 않음 — 갤러리가 상품 단위로 분리돼 있음)
document.querySelectorAll('.airow').forEach(row=>{{
  const els=[...row.querySelectorAll('.aimedia')];
  const list=els.map(el=>({{src:el.dataset.src,kind:el.dataset.kind,poster:el.dataset.poster||'',
    cap:el.dataset.kind==='video'?'AI로 기획부터 제작까지 진행한 브랜드 영상입니다':'',
    muted:false,loop:false,autoplay:el.dataset.kind==='video'?false:undefined}}));
  els.forEach((el,i)=>el.addEventListener('click',()=>openLb(list,i)));
}});
// 콘셉트 이미지가 3장+ 그리드일 때, 스크롤이나 잘림 없이 "영상 커버 하단 끝을 넘지 않는 선"에서
// 타일이 최대한 커지도록 열 개수·타일 크기를 계산해서 배치함(좌우 여백은 생겨도 무방, 세로만 제한).
// 그리드 위에 제목·리드문·작업방식·배지가 먼저 오는 만큼, "영상 하단 좌표 − 그리드 시작 좌표"로
// 실제 남은 세로 공간을 구하고, 그 안에 n장이 다 들어가는 열 개수 중 타일이 가장 커지는 조합을 선택.
// 데스크톱 2단 레이아웃에서만 적용하고, 모바일 1단 스택에서는 기본 3열 그리드로 되돌림.
(function(){{
  const rows=[...document.querySelectorAll('.airow')].map(row=>({{row,cover:row.querySelector('.aimedia'),grid:row.querySelector('.aiconcepts.many')}})).filter(x=>x.cover&&x.grid);
  if(!rows.length)return;
  const GAP=10;
  function bestLayout(n,w,h){{
    let best=null;
    for(let c=1;c<=n;c++){{
      const r=Math.ceil(n/c);
      const tw=(w-(c-1)*GAP)/c;
      if(tw<=0)continue;
      const neededH=r*tw+(r-1)*GAP;
      if(neededH<=h+28&&(!best||tw>best.tw))best={{c,tw}};
    }}
    if(!best){{const tw=Math.max(20,h);best={{c:Math.max(1,Math.floor((w+GAP)/(tw+GAP))),tw}};}}
    return best;
  }}
  function sync(){{
    const twoCol=matchMedia('(min-width:901px)').matches;
    rows.forEach(({{cover,grid}})=>{{
      if(!twoCol){{grid.style.gridTemplateColumns='';return;}}
      if(cover.offsetHeight===0)return;
      const n=grid.children.length,w=grid.clientWidth;
      const h=cover.getBoundingClientRect().bottom-grid.getBoundingClientRect().top;
      if(w<=0||h<=0)return;
      const {{c,tw}}=bestLayout(n,w,h);
      grid.style.gridTemplateColumns=`repeat(${{c}}, ${{tw}}px)`;
    }});
  }}
  new ResizeObserver(sync).observe(document.body);
  rows.forEach(({{row,cover}})=>{{new ResizeObserver(sync).observe(cover);new ResizeObserver(sync).observe(row.querySelector('.aibd'));}});
  sync();
}})();
// 그 외 단일 이미지(상품기획 등)
document.querySelectorAll('[data-full]').forEach(el=>{{if(handled.has(el))return;el.addEventListener('click',()=>openLb([{{src:el.dataset.full,cut:el.dataset.cut==='1'}}],0));}});
function close(){{lb.classList.remove('on');document.body.style.overflow='';lbimg.src='';lbvid.pause();lbvid.removeAttribute('src');lbPlay.hidden=true;}}
lb.addEventListener('click',close);
document.getElementById('lbPrev').addEventListener('click',e=>{{e.stopPropagation();show(gi-1);}});
document.getElementById('lbNext').addEventListener('click',e=>{{e.stopPropagation();show(gi+1);}});
lbimg.addEventListener('click',e=>e.stopPropagation());
lbvid.addEventListener('click',e=>e.stopPropagation());
addEventListener('keydown',e=>{{if(!lb.classList.contains('on'))return;if(e.key==='Escape')close();else if(e.key==='ArrowLeft')show(gi-1);else if(e.key==='ArrowRight')show(gi+1);}});
{DP_JS}
</script>
<script>{TRACK_JS}</script>
</body></html>'''

with open(os.path.join(OUT,"index.html"),"w",encoding="utf-8") as f:
    f.write(html)

# 관리자 화면용 이미지 목록(admin/manifest.json) — 관리자 화면이 미리보기 썸네일 경로를 찾을 때 사용(자동 생성, 깃 제외)
if os.path.isdir(os.path.join(OUT,"admin")):
    files=sorted(f for f in os.listdir(os.path.join(OUT,"assets")) if not f.startswith(".") and os.path.isfile(os.path.join(OUT,"assets",f)))
    with open(os.path.join(OUT,"admin","manifest.json"),"w",encoding="utf-8") as f:
        ddir=os.path.join(OUT,"assets","detail")
        dirs=sorted(x for x in os.listdir(ddir) if os.path.isdir(os.path.join(ddir,x))) if os.path.isdir(ddir) else []
        json.dump({"assets":files,"detail_dirs":dirs},f,ensure_ascii=False)
print("built single-page index.html")

# ── 배포용 폴더(dist) 만들기 ───────────────────────────────────────────
# Vercel은 `python3 build.py --dist`로 사이트를 만든 뒤 dist 폴더만 공개함(vercel.json).
# → 작업 기록(PROGRESS.md)·문서·도구·원본 데이터 같은 내부 파일은 방문자에게 공개되지 않음.
import sys, shutil
if "--dist" in sys.argv:
    D=os.path.join(OUT,"dist")
    shutil.rmtree(D,ignore_errors=True); os.makedirs(D)
    for f in ("index.html","style.css","favicon.svg"):
        shutil.copy2(os.path.join(OUT,f),D)
    shutil.copytree(os.path.join(OUT,"assets"),os.path.join(D,"assets"),
                    ignore=shutil.ignore_patterns("_orig_big",".DS_Store"))
    if os.path.isdir(os.path.join(OUT,"admin")):   # 관리자 화면(3-4에서 추가)
        shutil.copytree(os.path.join(OUT,"admin"),os.path.join(D,"admin"))
    print("dist ready:",D)
