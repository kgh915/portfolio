import os, unicodedata
from PIL import Image, ImageOps
SRC=os.path.expanduser("~/Desktop/근하_포폴/자료/촬영이미지_썸네일")
A="/Users/kgh/실습/portfolio_v2/assets/"
fs=sorted((f for f in os.listdir(SRC) if f.lower().endswith((".jpg",".jpeg",".png"))),key=lambda s:unicodedata.normalize("NFC",s))
n=7
for f in fs:
    assert not os.path.exists(A+f"ph{n:02d}.jpg")
    im=ImageOps.exif_transpose(Image.open(os.path.join(SRC,f))).convert("RGB")
    full=im.copy(); full.thumbnail((1500,1500),Image.LANCZOS); full.save(A+f"ph{n:02d}.jpg",quality=85,optimize=True,progressive=True)
    th=im.copy(); th.thumbnail((500,500),Image.LANCZOS); th.save(A+f"ph{n:02d}-thumb.jpg",quality=82,optimize=True,progressive=True)
    print(f"ph{n:02d}",unicodedata.normalize("NFC",f)); n+=1
