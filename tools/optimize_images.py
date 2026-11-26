# 사이트에서 크게 보이는 이미지 용량 줄이기 — 화면에 보이는 최대 크기의 2배(레티나) 해상도는 유지.
# 원본은 assets/_orig_big/<날짜>/ 에 보관(깃에는 올라가지 않음). PNG는 원본을 남기고 같은 이름의 .webp를 만들어 사이트에서 사용.
import os, sys
from PIL import Image, ImageOps
A=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","assets")
MAX=2200  # 보기창 가로 최대 약 1090px·크게보기 880px의 2배 이상
def kb(p): return os.path.getsize(p)//1024
def jpg(name,q=85,maxside=MAX,keep_size=False):
    p=os.path.join(A,name); before=kb(p)
    im=ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    if not keep_size: im.thumbnail((maxside,maxside),Image.LANCZOS)
    im.save(p,quality=q,optimize=True,progressive=True)
    print(f"{name}: {before}KB -> {kb(p)}KB {im.size}")
def webp(name,maxside=MAX):
    p=os.path.join(A,name); before=kb(p)
    im=Image.open(p); im=im.convert("RGBA") if (im.mode in("RGBA","LA","P")) else im.convert("RGB")
    im.thumbnail((maxside,maxside),Image.LANCZOS)
    out=os.path.splitext(p)[0]+".webp"; im.save(out,"WEBP",quality=92,method=6)
    print(f"{name}: {before}KB -> {os.path.basename(out)} {kb(out)}KB {im.size}")
def thumb(name,side=500):
    p=os.path.join(A,name); im=ImageOps.exif_transpose(Image.open(p)).convert("RGB"); im.thumbnail((side,side),Image.LANCZOS)
    out=os.path.join(A,os.path.splitext(name)[0]+"-thumb.jpg"); im.save(out,quality=82,optimize=True,progressive=True)
    print(f"{os.path.basename(out)}: {kb(out)}KB")
if __name__=="__main__":
    for f in ["ed08.jpg","ed07.jpg","ph01.jpg"]: jpg(f)
    jpg("ds01.jpg",q=84,keep_size=True)      # 목업: 크기 유지(자동 스크롤 화면 위치가 이 크기 기준)
    jpg("marble.jpg",q=80)
    for f in ["pk01.png","pk02.png","pk03.png","pk04.png","pk05.png","ed01.png","ed02.png","ed03.png","ed04.png","ed05.png","ed06.png"]: webp(f)
    for i in range(1,7): thumb(f"ph{i:02d}.jpg")
