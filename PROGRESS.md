# 진행 상황 (이어서 작업용) — 최종 업데이트 2026-11-26 밤

> 의뢰인이 **"이어서 작업하자"**라고만 하면, 이 파일만 읽고 아래 **0절 → 3절 순서**로 바로 이어갈 것. 처음부터 다시 검토하지 말 것.
> 사이트: https://kimgeunha.vercel.app (GitHub kgh915/portfolio, main 푸시 → Vercel 자동 배포). 세부 배경은 `PROJECT_CONTEXT.md` 7절.

## 0. 이어서 시작할 때 맨 먼저 할 일 (순서대로)
1. `cd /Users/kgh/실습/portfolio_v2 && git switch admin-mode && git pull --ff-only origin admin-mode`
   - **의뢰인이 관리자 화면에서 저장하면 GitHub admin-mode 브랜치에 커밋이 생김** → 반드시 먼저 pull.
2. 의뢰인이 세션 사이에 관리자 화면으로 바꾼 내용 확인:
   `git log --oneline 694b51d..HEAD` (694b51d = 2026-11-26 마지막 세션 끝 기준)
   → "관리자 화면에서 내용 수정: …" 커밋이 있으면 `git diff 694b51d HEAD -- data/ assets/detail/details.json`로 무엇이 바뀌었는지 쉬운 말로 요약해 보여주고, **유지할지 되돌릴지 물어볼 것**
   (의뢰인이 순서 변경·삭제를 시험해 보기로 함. 시험용 변경이 실제 사이트에 합쳐지지 않게 확인 필요)
3. 의뢰인에게 "어디까지 끝났고 이번에 무엇을 할지" 한두 줄로 알린 뒤 3-5 시작.

## 1. 현재 상태
- **실제 사이트(main)**: 2026-11-26 밤 배포본(상세페이지 설명박스·패키지 설명박스·섹션 정리). 관리자 모드는 아직 **실제 사이트에 없음**.
- **관리자 모드 작업 공간**: 브랜치 `admin-mode` (시작 전 백업 태그 `backup-before-admin-mode-2026-11-26`)
  - 확인용 고정 주소(브랜치 주소, Vercel 로그인 필요): https://portfolio-git-admin-mode-kgh915.vercel.app/admin/
  - Vercel 비밀값 설정 완료(Production·Preview): `ADMIN_PASSWORD`(의뢰인이 정함), `GITHUB_TOKEN`(fine-grained, kgh915/portfolio만, Contents RW, 만료 없음)
- 요청서(전체 계획): https://claude.ai/artifact/BeASGj8VNebxUAvFPxwZuE

## 2. 관리자 모드 — 완료한 것
| 단계 | 내용 |
|---|---|
| 1 현황 파악 | `docs/admin/1단계_현황파악.md`, `docs/admin/1단계_글자목록.md`(글자 약 237개) |
| 3-1 | 작업 목록·제품·프로젝트·경력·AI작업물·인터뷰·패키지 설명 → `data/site.json` (build.py는 읽기만). 캐시 버스팅 = 파일 내용 해시, sips 대신 PNG 헤더로 투명 판정 |
| 3-2 | 히어로·프로필·섹션 소개/배지/안내·About·푸터·연락처 → `site.json`의 `texts` |
| 3-3 | `vercel.json`: 빌드 `python3 build.py --dist`, 공개 폴더 `dist`(index·style·favicon·assets·admin만 → 내부 문서 비공개) |
| 3-4 | 관리자 화면 `admin/`(index.html·admin.js·admin.css, 한글 메뉴 12개: 기본정보·섹션소개·인터뷰·제품·프로젝트·AI·상세페이지·패키지·편집·사진·경력·About) + API `api/`(login·content·save). 글자 수정·▲▼ 순서·삭제·인터뷰/경력/기여도 추가·컬러 선택·저장. 저장 = 두 데이터 파일 한 커밋으로 GitHub(배포된 브랜치)에 → Vercel 자동 재빌드. **의뢰인이 미리보기에서 로그인·저장 성공 확인** |

- 로컬 시험: `node tools/admin-dev.js` → http://localhost:8130/admin/ (비번 `local-test`, launch.json `admin-dev`). 로컬 저장은 폴더 파일을 직접 바꾸므로 시험 후 `git checkout data/ assets/detail/details.json`
- 비밀값 안내 문서: `docs/admin/관리자_비밀값_설정방법.md`

## 3. 다음에 할 일 (순서대로)
1. **3-5 이미지 올리기·교체·작업 추가/삭제**
   - 브라우저에서 이미지를 고르면 canvas로 **보이는 크기의 2배**(긴 변 최대 2200px, 미리보기·썸네일은 별도 크기) JPEG/WebP로 줄여 업로드 → 새 API(예: `api/upload.js`)가 GitHub에 커밋 (Vercel 함수 요청 4.5MB 한도 → 줄인 뒤 1장씩 보내기)
   - 대상: 상세페이지(미리보기 + 상세 이미지 여러 장, 세로 4000px 단위로 잘라 `assets/detail/dpNN/`), 패키지·편집·사진·제품·AI 콘셉트 이미지 추가/교체
   - 영상: 30MB 넘으면 경고 + 줄이는 방법(HandBrake) 안내, 큰 파일은 GitHub 웹 업로드 방법 안내
   - 관리자 화면에 **저장소 용량 표시**, 저장 전 미리보기(가능하면)
2. **4단계 통계**: Vercel Web Analytics 켜기(무료 월 5만 건, 1개월 보관) + 관리자 화면에 "이 브라우저는 통계에서 제외" 버튼 + 자체 클릭 카운터(무료 저장소) + 매주 메일(Resend 무료, 본인 이메일 — **받을 주소 의뢰인에게 확인**). 속도 영향 검토 후 보고
3. **5단계 사용 설명서**: 로그인, 수정, 이미지, 되돌리기(태그·GitHub), 토큰/비밀번호 교체, 통계, 용량
4. **합치기**: 의뢰인 승인 후 admin-mode → main 병합, 배포 확인. 그 뒤 관리자 주소 = https://kimgeunha.vercel.app/admin/

## 4. 일하는 방식 (의뢰인 선호)
- 비개발자. 한국어, 쉬운 말. 폴더·파일은 **찾기 전에 먼저 물어보기**
- 문구는 초안을 보여주고 확정 후 반영(완성 문구를 주면 그대로). 레이아웃·스타일은 적용 후 미리보기로 보여주기
- 배포(main 반영)는 의뢰인이 "반영해"라고 할 때만. 배포 전 로딩 영향 검토 원함
- 비밀번호·토큰은 의뢰인이 직접 입력(Claude가 대신 입력하지 않음)
- 사용량: Pro 플랜. '무료로 초기화'(12/11 오전 7시 만료)는 주간 한도 임박 시 쓰라고 안내함

## 5. 지난 작업 기록(요약)
- 2026-11-26: 상세페이지 미리보기 51개+팝업 설명박스 49개(기여도: 업체제공 17개 표시순서 1,3,4,5,6,8,9,10,13,14,26,29,31,32,39,40,46 / 컬러무드 = 페이지에서 많이 쓴 색 1~2+포인트 1, 제품 색 아님 / 컨셉 PC 2~3줄·문체 경산대추 기준), 목업 태블릿↔휴대폰 자동 스크롤, 이미지 최적화 28→12MB(원본 `assets/_orig_big/2026-11-26/`), 패키지 7개+설명박스(영상 숨김), 섹션 소개·배지 정리 — 모두 main 배포 완료
- 아베나키 랜턴 'GIF영역'·다시,꽃 Before/After 빈 박스는 그대로 두기로 함
