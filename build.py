# -*- coding: utf-8 -*-
import os
OUT=os.path.dirname(os.path.abspath(__file__))

# 폴더에서 prefix+번호(ph01, ph02 …) 파일을 연속으로 자동 수집 (jpg/png/mp4)
def autoseq(prefix):
    base=os.path.join(OUT,"assets")
    out=[];n=1
    while any(os.path.exists(os.path.join(base,f"{prefix}{n:02d}.{e}")) for e in ("jpg","png","mp4")):
        out.append(f"{prefix}{n:02d}");n+=1
    return out

# 01 상세페이지 — 보존용 그대로 (태블릿+폰 목업 쇼케이스 + 보존용 설명글)
detail_imgs=["ds01","ds02","ds03","ds04","ds05"]
detail_desc="PC와 모바일 어디서나 가독성과 설득력을 잃지 않는 상세페이지입니다. 제품의 핵심 가치를 한눈에 전달하고, 감각적이고 트렌디한 비주얼로 구매 전환까지 이끄는 것을 목표로 작업했습니다. 공기청정기·건강기능·뷰티·생활용품 등 다양한 카테고리의 상세페이지를 기획부터 디자인, 제품 촬영까지 직접 진행했습니다."

package=["pk01","pk01-1","pk02","pk02-1","pk04","pk04-1","pk05","pk05-1","pk03"]
editorial=["ed01","ed02","ed03","ed04","ed05","ed06","ed07","ed08"]
photo=autoseq("ph")  # assets 폴더의 ph01,ph02… 를 자동 인식 (파일만 넣으면 추가됨)

# 05 상품기획 = 신제품 + 이벤트 (구조화된 잡지형: 핵심 포인트 + 성과 지표)
planning=[
 dict(img="pj01",
   title="신제품 기획 — 새해선물 ‘도깨비 소원카드’",
   lead="드라마 ‘도깨비’에서 착안한 새해 선물입니다. 전통 도깨비 문양과 부적 스타일의 소망 문구를 결합해, 가볍고 유쾌하게 주고받는 이벤트성 선물로 기획했습니다.",
   role="기획 · 디자인 · 촬영 · 일정관리", contrib="기여도 100%",
   points=[
     "앞면은 전통 도깨비 문양, 뒷면은 ‘가족건강·로또일등·시험합격’ 소망 문구를 부적 스타일로 디자인",
     "주고받고 싶게 만드는 이벤트성 컨셉으로 자발적 공유·재구매 유도",
     "아이디어 발굴부터 디자인·촬영·일정 관리까지 전 과정 단독으로 진행",
   ],
   results=[("조기 마감","예상 판매량을 초과하는 주문"),("재문의 지속","판매 종료 후에도 추가 주문 문의")]),
 dict(img="pj03",
   title="이벤트 상품 기획 — 악성 재고를 효자 상품으로",
   lead="폐기 직전의 악성 재고였던 크리스탈·유리 제품을, 캘리그라피 문구와 포인트 이미지를 더한 감성 기성품 라인으로 재기획했습니다.",
   role="기획 · 디자인", contrib="기여도 100%",
   points=[
     "1:1 맞춤 제작 방식에서 기성품 라인으로 전환해 대량 생산 체계를 확보",
     "이벤트·기념품 시장을 겨냥해 상품 포지셔닝과 컨셉을 재정의",
   ],
   results=[("작업시간 70%↓","기존 1:1 제작 대비"),("매출 200%↑","이전 3년 평균 판매량 대비")]),
]

# 06 자사몰 고도화 — 플래그십(05와 동일 폼: 텍스트 + 아래 요약)
project=dict(img="pj02",
   title="설치 없는 ‘셀프 디자인 편집 시스템’ 구축",
   lead="고객이 별도 설치 없이 웹에서 직접 텍스트·로고·이미지를 편집하고 즉시 제작까지 진행하는 셀프 편집 시스템을 도입·총괄한 자사몰 고도화 프로젝트입니다. 외주 개발사 선정 및 미팅 진행부터 사내 프로젝트 팀과의 협업·일정 관리, 도입 후 운영까지 — 프로젝트 전 과정을 총괄 PM으로 직접 이끌었습니다.",
   role="총괄 PM · 기획", contrib="기여도 100% · 총괄 PM",
   points=[
     "현황 분석·기획 — 기존 리드타임(주문→요청→시안→피드백→수정)을 진단하고 셀프 편집 시스템의 요건을 정의",
     "외주 개발사 선정·계약 — 업체 비교·선정과 미팅·계약 조건 협의를 직접 진행",
     "구축·협업 — 사내 프로젝트 팀(3인)과 개발사 사이 커뮤니케이션 허브로 기능·일정을 조율",
     "도입·운영 — 시스템 적용 후 운영을 안정화하고 매출 기여까지 확인",
   ],
   stats=[
     ("프로젝트 기간","2025.03 – 2025.09","예상 일정보다 4개월 단축 완료"),
     ("역할","프로젝트 총괄","외주업체 및 사내 프로젝트 팀(3인) 핸들링"),
     ("성과","매출 30%+ 기여","시스템 도입 후 추가 매출"),
   ],
   problem=["주문 → 고객 요청 → 시안 제작 → 메일 피드백 → 수정의 반복","긴 리드타임으로 응대 부담과 제작 지연 발생"],
   solution=["주문 → 고객 셀프 디자인 → 제작 → 출고로 단순화","설치 없이 웹에서 직접 편집해 즉시 제작로 연결","작업 속도 향상으로 제작·응대 효율 개선","고객·직원 만족도 동반 상승"])

career=[("2002.02–2005.05","광선기공사","디자인 · 사원","홈페이지 제작·관리, 제품 촬영, 카탈로그 디자인"),
 ("2005.07–2010.09","프린센스 스튜디오","촬영·편집 · 실장","제품·웨딩·프로필 촬영, 리터칭 및 편집"),
 ("2012.02–2015.12","(주)가주 / 쿨맥스","웹·편집 · 대리","카드뉴스·홍보물 디자인, 제품 촬영, 블로그 관리"),
 ("2016.02–2019.04","(주)청송기획","디자인 및 마케팅 총괄 · 실장","신제품 기획·개발, 마케팅 총괄 전략, 고객 관리"),
 ("2020.05–2021.04","이원의료기","웹·편집 · 과장","상세페이지 리뉴얼, 패키지·카탈로그, 이벤트 상품 기획"),
 ("2022.09–2026.04","(주)주렁주렁 <span class='conote'>(주)청송기획 자매회사</span>","기획·디자인 총괄 · 과장","UI/UX 리뉴얼, 신규 상품 개발, VIP 관리, 자사몰 고도화 총괄")]

minimap=[("01","상세페이지 디자인","s01"),
 ("02","패키지 디자인","s02"),
 ("03","편집디자인","s03"),
 ("04","사진 촬영","s04"),
 ("05","상품기획","s05"),
 ("06","자사몰 고도화 프로젝트","s06")]

def masonry(ids):
    return '<div class="masonry">'+''.join(f'<div class="ph" data-full="assets/{i}.jpg"><img src="assets/{i}.jpg" loading="lazy" alt=""></div>' for i in ids)+'</div>'

# 동일 사이즈 썸네일 그리드(흰 배경 · 클릭 시 크게 보기 유지)
def tiles(ids):
    return '<div class="tiles">'+''.join(f'<div class="tile" data-full="assets/{i}.jpg"><img src="assets/{i}.jpg" loading="lazy" alt=""></div>' for i in ids)+'</div>'

mm_html=''.join(f'''<a class="mm" href="#{a}"><span class="n">{n}</span><span class="t">{t}</span><span class="ar">→</span></a>''' for (n,t,a) in minimap)

# 상세페이지 — 목업 쇼케이스(세로 나열)
detail_html=''.join(f'<figure class="dshot"><img src="assets/{i}.jpg" loading="lazy" alt="상세페이지 디자인 목업"></figure>' for i in detail_imgs)

# 큰 이미지 + 하단 썸네일 뷰어(클릭 시 큰 이미지 교체) — 패키지·편집 공용
# .png가 있으면 우선 사용. 단, 실제로 투명 영역이 있는 누끼 PNG만 대리석 배경 위에 그림자로 표시.
# 배경이 채워진 PNG(투명 없음)는 jpg처럼 원본 배경 그대로 표시.
import subprocess
def _has_alpha(path):
    try:
        return "hasAlpha: yes" in subprocess.check_output(["sips","-g","hasAlpha",path],text=True)
    except Exception:
        return False

def asset(im):
    png=os.path.join(OUT,"assets",f"{im}.png")
    if os.path.exists(png):
        return (f"assets/{im}.png", _has_alpha(png))
    return (f"assets/{im}.jpg", False)

# 항목별 미디어 판별: .mp4가 있으면 동영상(음소거·자동반복), 없으면 이미지(asset 규칙)
def media(im):
    base=os.path.join(OUT,"assets")
    if os.path.exists(os.path.join(base,f"{im}.mp4")):
        # 포스터: 자기 이름 이미지 우선, 없으면 base 제품 이미지(pk02-1 → pk02)
        poster=""
        for cand in (im, im.split("-")[0]):
            for ext in ("png","jpg"):
                if os.path.exists(os.path.join(base,f"{cand}.{ext}")):
                    poster=f"assets/{cand}.{ext}";break
            if poster:break
        return {"kind":"video","src":f"assets/{im}.mp4","poster":poster,"cut":False}
    src,cut=asset(im)
    return {"kind":"image","src":src,"poster":"","cut":cut}

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
    f=items[0]
    if f["kind"]=="video":
        cls=" video";data_cut="0"
        big=f'<img class="vm-img" alt="" hidden><video class="vm-vid" src="{f["src"]}" poster="{f["poster"]}" muted loop playsinline autoplay></video>'
    else:
        cls=" cut" if f["cut"] else "";data_cut="1" if f["cut"] else "0"
        big=f'<img class="vm-img" src="{f["src"]}" alt=""><video class="vm-vid" muted loop playsinline hidden></video>'
    return f'''<div class="viewer reveal">
    <div class="vmain{cls}" data-full="{f["src"]}" data-cut="{data_cut}" data-kind="{f["kind"]}" data-poster="{f["poster"]}">{big}<span class="vcap">AI를 이용하여 제작된 3D 목업 영상입니다</span></div>
    <div class="vthumbs">{thumbs}</div>
  </div>'''

# 상품기획 잡지형(이미지 좌측 · 구조화 설명 우측)
def points_ul(points):
    return '<ul class="points">'+''.join(f'<li>{p}</li>' for p in points)+'</ul>'
def res_bar(results):
    return '<div class="resbar">'+''.join(f'<div class="res"><div class="v">{v}</div><div class="k">{k}</div></div>' for (v,k) in results)+'</div>'
def plan_row(p):
    return f'''<div class="magrow reveal"><div class="im" data-full="assets/{p['img']}.jpg"><img src="assets/{p['img']}.jpg" loading="lazy" alt="{p['title']}"></div>
<div class="bd"><h3>{p['title']}</h3><p class="lead-p">{p['lead']}</p>{points_ul(p['points'])}<div class="rolebar"><span class="role">{p['role']}</span><span class="contrib">{p['contrib']}</span></div>{res_bar(p['results'])}</div></div>'''
plan_html=''.join(plan_row(p) for p in planning)

# 자사몰 고도화 — 05와 동일 폼(텍스트) + 아래 요약(지표 카드 · 기존/개선 비교)
pj=project
stat_html=''.join(f'<div class="statcard"><div class="cap">{c}</div><div class="big">{v}</div><div class="lab">{s}</div></div>' for (c,v,s) in pj['stats'])
prob_html=''.join(f'<li>{x}</li>' for x in pj['problem'])
sol_html=''.join(f'<li>{x}</li>' for x in pj['solution'])
proj_html=f'''<div class="case reveal">
  <div class="magrow"><div class="im" data-full="assets/{pj['img']}.jpg"><img src="assets/{pj['img']}.jpg" loading="lazy" alt="{pj['title']}"></div>
  <div class="bd"><h3>{pj['title']}</h3><p class="lead-p">{pj['lead']}</p>{points_ul(pj['points'])}<div class="rolebar"><span class="role">{pj['role']}</span><span class="contrib">{pj['contrib']}</span></div></div></div>
  <div class="case-sum">
    <div class="sum-title">한눈에 보는 핵심</div>
    <div class="stats3">{stat_html}</div>
    <div class="compare">
      <div class="cbox before"><span class="clab">기존 방식</span><ul>{prob_html}</ul></div>
      <div class="cbox after"><span class="clab">시스템 도입 후</span><ul>{sol_html}</ul></div>
    </div>
  </div>
</div>'''
cv_html=''.join(f'''<div class="row"><div class="yr">{y}</div><div><div class="co">{c}</div><div class="ro">{r}</div><div class="du">{d}</div></div></div>''' for (y,c,r,d) in career[::-1])

ICON_CHAT='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>'
ICON_HEART='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 1 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
ICON_UP='<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'

html=f'''<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>김근하 — 웹 디자이너 포트폴리오</title>
<meta name="description" content="웹 디자이너 김근하 포트폴리오 — 상세페이지·패키지·편집디자인·촬영·상품기획">
<link rel="stylesheet" href="style.css">
</head><body>

<nav class="nav" id="nav">
  <a href="#top" class="brand"><span class="ko">김근하</span><span class="en">KIM GEUNHA · WEB DESIGNER</span></a>
  <div class="nav-links"><a href="#work">Work</a><a href="#about">About</a><a href="#contact">Contact</a></div>
</nav>

<header class="hero" id="top"><div class="wrap">
  <div class="eyebrow reveal">Portfolio · 2026</div>
  <h1 class="reveal">긍정의 마인드,<br><span class="mark">무한한 가능성</span></h1>
  <p class="hero-sub reveal">보기만 좋은 디자인이 아닌, 마음을 움직이는 디자인을 고민합니다.</p>
  <div class="hero-meta reveal"><span>웹 디자이너 김근하</span><span class="dot"></span><span>기획 · 디자인 · 촬영</span><span class="dot"></span><span>상품기획 · 자사몰 운영</span></div>
</div></header>

<div class="wrap"><div class="hr"></div></div>

<section class="sec tight" id="intro"><div class="wrap">
  <div class="about-grid">
    <div class="intro reveal">
      <p>안녕하세요. 기획부터 디자인까지, 모든 과정을 책임지는 웹 디자이너 <b>김근하</b>입니다.</p>
      <p>컴퓨터디자인을 전공하고 스튜디오 촬영, 웹·편집 디자인, 상품 기획, 자사몰 운영까지 폭넓은 현장을 직접 거쳤습니다. 한 자리에 머물기보다 “안 될 게 뭐 있어?”라는 마음으로, 늘 새로운 영역에 호기심을 갖고 부딪혀 온 덕분입니다.</p>
      <p>그래서 저에게 좋은 디자인은 기술이 아니라 <b>호기심</b>에서 시작됩니다. ‘예쁘기만 한 디자인’을 넘어 그 이상을 고민하고, 빠르게 변하는 흐름에 발맞춰 요즘은 AI까지 익히며 디자인의 가능성을 넓혀가고 있습니다.</p>
    </div>
    <div class="profile reveal">
      <h3>Profile</h3>
      <div class="kv"><span class="k">이름</span><span class="v">김근하</span></div>
      <div class="kv"><span class="k">연락처</span><span class="v"><a href="tel:01023861832">010-2386-1832</a></span></div>
      <div class="kv"><span class="k">이메일</span><span class="v"><a href="mailto:goldps365@naver.com">goldps365@naver.com</a></span></div>
      <div class="kv"><span class="k">학력</span><span class="v">전북과학대학 컴퓨터디자인과 졸업</span></div>
      <div class="kv"><span class="k">자격증</span><span class="v">컴퓨터그래픽스 산업기사 · 컬러리스트 산업기사</span></div>
      <div class="kv"><span class="k">Tools</span><span class="v"><div class="tags"><span>Photoshop</span><span>Illustrator</span><span>Figma</span></div></span></div>
    </div>
  </div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec tight" id="career"><div class="wrap">
  <div class="sec-head reveal"><div class="en">Career</div><h2>경력</h2><p>가장 최근 경력부터 정리했습니다.</p></div>
  <div class="cv reveal">{cv_html}</div>
  <div class="cvmeta reveal">
    <span>전북과학대학 컴퓨터디자인과 졸업</span>
    <span>컴퓨터그래픽스 산업기사</span>
    <span>컬러리스트 산업기사</span>
    <span><b>Tools</b> · Photoshop · Illustrator · Figma</span>
  </div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec tight" id="work"><div class="wrap">
  <div class="sec-head reveal"><div class="en">Index</div><h2>작업 둘러보기</h2><p>보고 싶은 작업을 누르면 해당 영역으로 이동합니다.</p></div>
  <div class="minimap reveal">{mm_html}</div>
</div></section>

<div class="wrap"><div class="hr"></div></div>

<section class="sec" id="s01"><div class="wrap">
  <div class="sec-head reveal"><div class="en">01 — Product Detail</div><h2>상세페이지 디자인</h2><p>{detail_desc}</p><span class="contrib">기여도 100%</span></div>
  <div class="dshots reveal">{detail_html}</div>
</div></section>

<section class="sec" id="s02" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">02 — Package</div><h2>패키지 디자인</h2><p>브랜드의 특징을 효과적으로 전달하기 위해 패키지 디자인을 기획하고, <b>소비자의 시선을 끌 수 있는 컬러와 레이아웃</b>을 적용해 제품 정보를 직관적으로 전달하는 것을 목표로 제작하였습니다.<span class="vhint">작은 이미지를 클릭하시면 큰 이미지로 볼 수 있습니다</span></p><span class="contrib">기여도 100%</span></div>
  {viewer(package)}
</div></section>

<section class="sec" id="s03"><div class="wrap">
  <div class="sec-head reveal"><div class="en">03 — Editorial</div><h2>편집디자인</h2><p>잡지광고·포스터부터 브로셔·리플릿·메뉴판까지 — 제품과 브랜드 성격에 맞춘 <b>다양한 컨셉의 편집물</b>을 기획·디자인했습니다.<span class="vhint">작은 이미지를 클릭하시면 큰 이미지로 볼 수 있습니다</span></p><span class="contrib">기여도 100%</span></div>
  {viewer(editorial)}
</div></section>

<section class="sec" id="s04" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">04 — Photography</div><h2>사진 촬영</h2><p>DSLR을 이용한 제품·인물 직접 촬영. 조명과 연출을 설계해 디자인에 바로 쓰이는 결과물을 만듭니다.<span class="vhint">이미지를 누르면 크게 볼 수 있습니다</span></p><span class="contrib">기여도 100%</span></div>
  <div class="reveal">{tiles(photo)}</div>
</div></section>

<section class="sec" id="s05"><div class="wrap">
  <div class="sec-head reveal"><div class="en">05 — Planning</div><h2>상품기획</h2><p>신제품 기획부터 이벤트 상품까지</p></div>
  <div class="mag">{plan_html}</div>
</div></section>

<section class="sec" id="s06" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head reveal"><div class="en">06 — Flagship Project</div><h2>자사몰 고도화 프로젝트</h2></div>
  {proj_html}
</div></section>

<section class="sec about" id="about"><div class="wrap">
  <div class="about-head reveal">
    <div class="lead">저의 경험이 누군가의 어제가 아니라,<br><span class="hl">함께 만드는 내일이 되길 바랍니다.</span></div>
    <p class="about-intro">좋은 디자인은 기술이 아니라 ‘호기심’에서 나옵니다.</p>
  </div>
  <div class="story-one reveal">
    <p>저의 평소 모토는 <b>‘Why not?’</b>입니다. 안 된다고 포기하기 전에 “왜 안돼?”라는 마음으로, 많은 영역에 가능성과 호기심을 가지고 새로운 걸 배우는 데서 즐거움을 찾는 편입니다.</p>
    <p>그러다 보니 이전 회사에서도 한 가지 포지션에 머물지 않게 되었고, 총괄 역할까지 맡게 되었습니다. 이런 저를 보고 주변에서는 종종 “어떻게 이런 것까지 생각했냐”, “어떻게 이런 일까지 하게 됐냐”고 묻곤 했는데, 저의 생활신조가 기본적으로 바탕에 깔려 있기 때문이 아닐까 싶습니다.</p>
    <p>배움에는 끝이 없다고 하죠. 특히 시시각각 발전하는 요즘 같은 AI 시대에는 더 적극적인 자세가 필요하다고 생각합니다. 그래서 지금도 뒤처지지 않으려 AI를 익히고 있고, 이 사이트와 목업 영상도 AI를 활용해 만들어 보게 되었습니다. 아직은 물론 서툰 부분도 있지만, 활용법을 하나씩 알아갈수록 세상의 빠른 변화가 두려움보다는 기대와 설렘, 더 큰 호기심으로 다가옵니다.</p>
    <p>어떠신가요? 저와 함께하는 모습, 벌써 설레지 않으세요? 지금까지 쌓아온 저의 풍부한 경험이 과거에 머물기보다는, 함께 만드는 새로운 내일이 되기를 바랍니다.</p>
  </div>
</div></section>

<footer class="foot" id="contact"><div class="wrap">
  <div class="big">기획부터 디자인까지,<br>끝까지 책임지겠습니다.</div>
  <div class="info">웹 디자이너 김근하<br><a href="tel:01023861832">010-2386-1832</a><br><a href="mailto:goldps365@naver.com">goldps365@naver.com</a></div>
</div><div class="wrap"><div class="copy">© 2026 KIM GEUNHA — PORTFOLIO. ALL RIGHTS RESERVED.</div></div></footer>

<div class="lb" id="lb"><div class="x">×</div><div class="navbtn prev" id="lbPrev">‹</div><div class="navbtn next" id="lbNext">›</div><img src="" alt=""><video class="lb-vid" muted loop playsinline controls hidden></video><span class="lbcap">AI를 이용하여 제작된 3D 목업 영상입니다</span></div>

<script>
const nav=document.getElementById('nav');
addEventListener('scroll',()=>nav.classList.toggle('scrolled',scrollY>40));
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target)}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
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
  }}));
}});
const lb=document.getElementById('lb'),lbimg=lb.querySelector('img'),lbvid=lb.querySelector('.lb-vid');
let gallery=[],gi=0;
function show(i){{gi=(i+gallery.length)%gallery.length;const it=gallery[gi];lb.classList.toggle('vidcap',it.kind==='video');
  if(it.kind==='video'){{lbimg.hidden=true;lbimg.removeAttribute('src');lbvid.src=it.src;lbvid.poster=it.poster||'';lbvid.hidden=false;lbvid.play().catch(()=>{{}});lb.classList.remove('cut');}}
  else{{lbvid.pause();lbvid.hidden=true;lbvid.removeAttribute('src');lbimg.src=it.src;lbimg.hidden=false;lb.classList.toggle('cut',!!it.cut);}}}}
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
// 그 외 단일 이미지(상품기획 등)
document.querySelectorAll('[data-full]').forEach(el=>{{if(handled.has(el))return;el.addEventListener('click',()=>openLb([{{src:el.dataset.full,cut:el.dataset.cut==='1'}}],0));}});
function close(){{lb.classList.remove('on');document.body.style.overflow='';lbimg.src='';lbvid.pause();lbvid.removeAttribute('src');}}
lb.addEventListener('click',close);
document.getElementById('lbPrev').addEventListener('click',e=>{{e.stopPropagation();show(gi-1);}});
document.getElementById('lbNext').addEventListener('click',e=>{{e.stopPropagation();show(gi+1);}});
lbimg.addEventListener('click',e=>e.stopPropagation());
lbvid.addEventListener('click',e=>e.stopPropagation());
addEventListener('keydown',e=>{{if(!lb.classList.contains('on'))return;if(e.key==='Escape')close();else if(e.key==='ArrowLeft')show(gi-1);else if(e.key==='ArrowRight')show(gi+1);}});
</script>
</body></html>'''

with open(os.path.join(OUT,"index.html"),"w",encoding="utf-8") as f:
    f.write(html)
print("built single-page index.html")
