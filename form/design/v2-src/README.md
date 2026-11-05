# 신청폼 v2 — 눌러보는 프로토타입 (소스)

`form/design/v2.html` 은 이 폴더를 빌드한 **단일 파일 결과물**입니다. 직접 고치지 마세요.

## 고치고 다시 뽑기

```
npm install
npm run build          # dist/index.html 이 나옵니다
cp dist/index.html ../v2.html
```

## 무엇으로 만들었나

- **stageshow 키트** — 폰 프레임(`Phone`), 열고 닫히는 안내(`Collapse`), 체크(`Check`), 조회 중 표시(`Spinner`)
- 손이 닿는 컨트롤(입력칸·버튼·동 고르기)은 **직접 만들었습니다.** 키트의 기본 버튼은
  데스크톱 앱 크기(24~32px)라 시니어 기준인 56~64px과 맞지 않습니다.
- 키트 자체는 빌드할 때만 쓰이고 결과물 안에 들어갑니다. `src/kit/` 은 커밋하지 않습니다.

## 시니어 기준

본문 17px · 입력 19px · 터치 62~64px · 체크 34px · `word-break: keep-all`
