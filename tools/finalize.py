import json, os, shutil
from PIL import Image
A="/Users/kgh/실습/portfolio_v2/assets/"
items={it["id"]:it for it in json.load(open(A+"detail/details.json"))}
# 기존 사이트 미리보기(ds02~05의 16칸) ↔ 새 상세페이지 대응
old=[("ds02_1","dp45"),("ds02_2","dp24"),("ds02_3","dp23"),("ds02_4","dp27"),
     ("ds03_1","dp44"),("ds03_2","dp11"),("ds03_3","dp48"),("ds03_4",None),
     ("ds04_1","dp10"),("ds04_2","dp03"),("ds04_3","dp25"),("ds04_4","dp06"),
     ("ds05_1",None),("ds05_2","dp12"),("ds05_3","dp30"),("ds05_4","dp20")]
nodetail_titles={"ds03_4":"세미 극세사 차렵이불","ds05_1":"승원 파라베스"}
drop={"dp41","dp49"}  # 캠핑-750 = 쓰리본 랜턴과 같은 제품, 휴대용산소-750 = 클린산소와 같은 제품
front=[];back=[];used=set()
for crop,dp in old:
    im=Image.open(f"oldpv/{crop}.png").convert("RGB")
    if dp:
        it=items[dp]; im.save(A+it["preview"],quality=90,optimize=True,progressive=True)
        it["preview_from"]="기존 사이트 "+crop; front.append(it); used.add(dp)
    else:
        nid="old-"+crop.replace("_","-"); os.makedirs(A+"detail/"+nid,exist_ok=True)
        im.save(A+f"detail/{nid}/preview.jpg",quality=90,optimize=True,progressive=True)
        back.append({"id":nid,"title":nodetail_titles[crop],"source":[],"preview":f"detail/{nid}/preview.jpg","preview_from":"기존 사이트 "+crop,"pages":[]})
middle=[it for k,it in items.items() if k not in used and k not in drop]
for k in drop: shutil.rmtree(A+"detail/"+k)
final=front+middle+back
json.dump(final,open(A+"detail/details.json","w"),ensure_ascii=False,indent=1)
print(len(front),len(middle),len(back),len(final))
