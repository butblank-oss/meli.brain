#!/usr/bin/env python3
"""form/ 안의 .md 를 깃허브 페이지에서 바로 볼 수 있는 .html 로 변환한다.

    python3 build_docs.py

- 결과는 같은 위치에 같은 이름의 .html 로 떨어진다 (README.md → README.html)
- 문서 사이의 .md 링크는 .html 로 바꿔 준다
- 수정은 항상 .md 에서 하고 이 스크립트를 다시 돌린다
"""
import re, pathlib, html as _html
import markdown

ROOT = pathlib.Path(__file__).parent
SKIP_DIRS = {"handoff"}

SHELL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title} — 맬리브레인 신청폼</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--ink:#1A1F26;--ink2:#4E5968;--ink3:#8B95A1;--line:#E4E1DA;--bg:#F4F3F0;--accent:#1F3C5D}}
body{{font-family:'Pretendard Variable',Pretendard,-apple-system,'Apple SD Gothic Neo',system-ui,sans-serif;
 color:var(--ink);background:var(--bg);line-height:1.8;font-size:16px}}
.top{{background:#fff;border-bottom:1px solid var(--line);padding:14px 20px;position:sticky;top:0;z-index:10;
 display:flex;align-items:center;gap:14px;flex-wrap:wrap}}
.top a{{color:var(--accent);text-decoration:none;font-weight:700;font-size:14px}}
.top a:hover{{text-decoration:underline}}
.top .sep{{color:#C8C3B8}}
.wrap{{max-width:860px;margin:0 auto;padding:40px 24px 120px}}
h1{{font-size:30px;font-weight:800;letter-spacing:-.04em;line-height:1.3;margin:0 0 20px}}
h2{{font-size:22px;font-weight:800;letter-spacing:-.035em;margin:44px 0 10px;padding-top:16px;border-top:2px solid var(--ink);line-height:1.4}}
h3{{font-size:18px;font-weight:800;letter-spacing:-.03em;margin:30px 0 8px}}
h4{{font-size:16px;font-weight:800;margin:22px 0 6px}}
p{{margin:10px 0;color:var(--ink2)}}
ul,ol{{margin:10px 0 10px 22px;color:var(--ink2)}}
li{{margin:6px 0}}
b,strong{{color:var(--ink);font-weight:700}}
code{{background:#EDEBE5;color:#1A3654;padding:2px 6px;border-radius:5px;font-size:13.5px;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:600}}
pre{{background:#1A1F26;color:#E6EAF0;padding:18px 20px;border-radius:12px;overflow-x:auto;margin:14px 0}}
pre code{{background:none;color:inherit;padding:0;font-size:13px;font-weight:400}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14.5px;background:#fff;display:block;overflow-x:auto}}
th,td{{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;line-height:1.65}}
th{{background:#EDEBE5;font-weight:700;color:var(--ink);white-space:nowrap}}
blockquote{{border-left:4px solid var(--accent);background:#ECF1F6;margin:16px 0;padding:14px 18px;border-radius:0 10px 10px 0}}
blockquote p{{margin:6px 0;color:#1A3654}}
a{{color:var(--accent)}}
hr{{border:0;border-top:1px solid var(--line);margin:34px 0}}
footer{{max-width:860px;margin:0 auto;padding:0 24px 80px;font-size:13px;color:var(--ink3)}}
@media(max-width:640px){{.wrap{{padding:24px 18px 80px}}h1{{font-size:24px}}h2{{font-size:19px}}}}
</style>
</head>
<body>
<nav class="top">
  <a href="{up}index.html">← 신청폼 목차</a><span class="sep">·</span>
  <a href="{up}design/index.html">프로토타입</a><span class="sep">·</span>
  <a href="{up}terms/README.html">약관</a>
</nav>
<div class="wrap">
{body}
</div>
<footer>맬리브레인 신청폼 개선 · 인천 남동구 보건소 치매예방교실 · 이 문서는 <code>{src}</code> 에서 생성됐습니다</footer>
</body>
</html>
"""

def convert(md_path: pathlib.Path):
    raw = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(raw, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    # 문서끼리의 .md 링크를 .html 로
    body = re.sub(r'(href="[^"]*?)\.md(["#])', r'\1.html\2', body)
    m = re.search(r"^#\s+(.+)$", raw, re.M)
    title = m.group(1).strip() if m else md_path.stem
    up = "../" * len(md_path.relative_to(ROOT).parts[:-1])
    out = md_path.with_suffix(".html")
    out.write_text(SHELL.format(title=_html.escape(title), body=body, up=up,
                                src=md_path.relative_to(ROOT)), encoding="utf-8")
    return out

def main():
    made = []
    for md in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_DIRS for part in md.relative_to(ROOT).parts):
            continue
        made.append(convert(md))
    for f in made:
        print("  ", f.relative_to(ROOT))
    print(f"{len(made)}개 변환 완료")

if __name__ == "__main__":
    main()
