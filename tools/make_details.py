# 상세페이지 원본 → 사이트용 이미지(분할·압축) + 미리보기 + details.json 생성
import os, re, json, sys, unicodedata
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

SRC = os.path.expanduser("~/Desktop/근하_포폴/자료/상세페이지")
OUT = "/Users/kgh/실습/portfolio_v2/assets/detail"
MAXW = 860          # 팝업 표시 폭
CHUNK = 4000        # 세로 분할 높이(모바일 디코딩 안정 + 순차 로딩)
PW, PH = 500, 1282  # 미리보기 (기존 4열 칸 비율 307:787, 표시폭 약 250px의 2배)
Q = 80

files = sorted((f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".jpeg", ".png"))), key=lambda s: unicodedata.normalize("NFC", s))
groups = {}
for f in files:
    stem = os.path.splitext(f)[0]
    m = re.match(r"^(.*?)[_-]?(\d{2})$", stem)
    key = m.group(1) if m else stem
    groups.setdefault(key, []).append(f)
# 번호 붙은 파일이 1개뿐이면 원래 이름을 그대로 키로
final = {}
for k, fs in groups.items():
    if len(fs) == 1:
        final[os.path.splitext(fs[0])[0]] = fs
    else:
        final[k] = sorted(fs)

os.makedirs(OUT, exist_ok=True)
items = []
for n, (key, fs) in enumerate(sorted(final.items(), key=lambda kv: unicodedata.normalize("NFC", kv[0])), 1):
    slug = f"dp{n:02d}"
    d = os.path.join(OUT, slug); os.makedirs(d, exist_ok=True)
    pages = []; idx = 0
    for f in fs:
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        if idx == 0 and f == fs[0]:
            # 미리보기: 첫 장 맨 위를 칸 비율로 잘라냄
            ch = round(im.width * PH / PW)
            pv = im.crop((0, 0, im.width, min(ch, im.height))).resize((PW, round(min(ch, im.height) * PW / im.width)), Image.LANCZOS)
            pv.save(os.path.join(d, "preview.jpg"), quality=82, optimize=True, progressive=True)
        for y in range(0, im.height, CHUNK):
            part = im.crop((0, y, im.width, min(y + CHUNK, im.height)))
            idx += 1
            name = f"{idx:02d}.jpg"
            part.save(os.path.join(d, name), quality=Q, optimize=True, progressive=True)
            pages.append({"src": f"detail/{slug}/{name}", "w": part.width, "h": part.height})
    title = unicodedata.normalize("NFC", key).replace("_", " ").replace("-", " ").strip()
    items.append({"id": slug, "title": title, "source": [unicodedata.normalize("NFC", x) for x in fs], "preview": f"detail/{slug}/preview.jpg", "pages": pages})
    print(slug, title, len(fs), "files ->", len(pages), "parts", file=sys.stderr)

json.dump(items, open(os.path.join(OUT, "details.json"), "w"), ensure_ascii=False, indent=1)
print(len(items), "items")
