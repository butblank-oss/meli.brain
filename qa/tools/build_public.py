#!/usr/bin/env python3
"""QA 공개 보기 페이지 생성 — qa/index.html

작성용 claude.ai 보드(https://claude.ai/artifact/Y8DdDe5WdCxZ6CWPFee3tf)의 데이터를
읽기 전용 정적 페이지로 바꿔 GitHub Pages(…/meli.brain/qa/)에 올린다.

사용:
  python3 qa/tools/build_public.py <data_dir> <caps_dir>
    data_dir  ArtifactData list ... out_dir 로 받은 폴더 (tc/ · bugs/ · dec/ 아래 <doc_id>.json)
    caps_dir  Artifact read path=<asset id> 로 받은 캡처 파일 폴더 (파일명이 asset id로 시작)

결과: qa/index.html · qa/caps/<asset id>.<ext> · qa/tools/last_sync.json
변경이 없으면 파일을 다시 쓰지 않고 'NO_CHANGE'를 출력한다.
"""
import sys, json, html, shutil, hashlib, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
QA = ROOT / "qa"
STATIC = json.loads((QA / "tools" / "static.json").read_text(encoding="utf-8"))
BOARD = "https://claude.ai/artifact/Y8DdDe5WdCxZ6CWPFee3tf"
E = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def load_docs(d, col):
    out = {}
    p = pathlib.Path(d) / col
    if not p.exists():
        return out
    for f in sorted(p.glob("*.json")):
        j = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(j, dict) and "data" in j and isinstance(j["data"], dict):
            out[j.get("id", f.stem)] = j["data"]
        else:
            out[f.stem] = j
    return out


def main(data_dir, caps_dir):
    TC = load_docs(data_dir, "tc")
    BUGS = load_docs(data_dir, "bugs")
    DEC = load_docs(data_dir, "dec")
    caps_src = {}
    if caps_dir and pathlib.Path(caps_dir).exists():
        for f in pathlib.Path(caps_dir).rglob("*"):
            if f.is_file():
                caps_src[f.name.split(".")[0]] = f
    used = set()

    def cap(aid):
        f = caps_src.get(aid)
        if not f:
            ex = list((QA / "caps").glob(aid + ".*"))
            return ("caps/" + ex[0].name) if ex else ""
        name = aid + (f.suffix or ".jpg")
        used.add((f, name))
        return "caps/" + name

    S = STATIC
    def acc_label(k):
        a = next((x for x in S["acc"] if x["k"] == k), None)
        return f'{a["k"]} {a["name"]} · {a["tier"]}' if a else str(k)
    fig = S["fig_of"]
    tcs = S["tc"]
    # 판정은 계정별 문서 tc/<TC>@<계정>. 예전 문서 tc/<TC> 는 acct 로 계정을 읽고, 없으면 '미지정'
    SL = {a["k"]: f"a{i+1}" for i, a in enumerate(S["acc"])}
    SYM = {v: k for k, v in SL.items()}
    def acc_name(sl):
        a = next((x for x in S["acc"] if SL[x["k"]] == sl), None)
        return f'{a["k"]} {a["name"]} · {a["tier"]}' if a else ("계정 무관" if sl == "a0" else "계정 미지정 (예전 기록)")
    RUNS = {}
    for did, v in sorted(TC.items(), key=lambda x: "@" in x[0]):
        if "@" in did:
            tid, sl = did.split("@", 1); RUNS.setdefault(tid, {})[sl] = v
        else:
            RUNS.setdefault(did, {}).setdefault(SL.get(v.get("acct"), "ax"), v)
    accs_of = lambda t: [SL[k] for k in SL if k in t["acc"]] or ["a0"]
    done = lambda x: bool(x and (x.get("a") or x.get("i")))
    fail_accs = lambda tid: [sl for sl, x in RUNS.get(tid, {}).items() if "실패" in (x.get("a"), x.get("i"))]
    def tc_res(t, k="a"):
        R = RUNS.get(t["id"], {}); v = [x.get(k) for x in R.values() if x.get(k)]
        if "실패" in v: return "실패"
        if "보류" in v: return "보류"
        if all(R.get(sl, {}).get(k) for sl in accs_of(t)): return "해당없음" if all(x == "해당없음" for x in v) else "통과"
        return "진행 중" if v else "미실행"
    by = lambda p: [t for t in tcs if t["pr"] == p]
    cnt = lambda a, v: sum(1 for t in a if tc_res(t) == v)
    p1 = by("P1"); f1 = cnt(p1, "실패"); done1 = sum(1 for t in p1 if tc_res(t) not in ("미실행", "진행 중"))
    verdict = f"배포 불가 — P1 실패 {f1}건" if f1 else (f"판단 보류 — P1 미완료 {len(p1)-done1}건" if done1 < len(p1) else "배포 가능 — P1 전부 통과")
    autos = sorted([(k, v) for k, v in BUGS.items() if v.get("auto")], key=lambda x: x[0])

    def cmp_block(fk, shots, sel=None):
        fimg = f'<img src="fig/fig_{E(fk)}.png" alt="피그마 목업" data-zoom loading="lazy">' if fk else '<div class="none">피그마 목업 없음</div>'
        caps = [cap(a) for a in shots]; caps = [c for c in caps if c]
        main = caps[-1] if caps else ""
        aimg = f'<img src="{E(main)}" alt="앱 캡처" data-zoom loading="lazy">' if main else '<div class="none">아직 올린 앱 캡처가 없습니다</div>'
        thumbs = "".join(f'<img src="{E(c)}" alt="앱 캡처 {i+1}" data-zoom loading="lazy">' for i, c in enumerate(caps)) if len(caps) > 1 else ""
        return (f'<div class="cmpbox"><div class="col"><div class="cap"><span class="tag">피그마 목업</span></div><div class="frame">{fimg}</div></div>'
                f'<div class="col"><div class="cap"><span class="tag app">앱 캡처</span>{f" {len(caps)}장" if len(caps)>1 else ""}</div><div class="frame">{aimg}</div></div></div>'
                + (f'<div class="ups">{thumbs}</div>' if thumbs else ""))

    def res_pill(v):
        cls = {"통과": "pass", "실패": "fail", "보류": "hold", "해당없음": "na"}.get(v, "")
        return f'<span class="rp {cls}">{E(v or "미실행")}</span>'

    # TC
    tc_html = []
    for t in tcs:
        R = RUNS.get(t["id"], {})
        keys = list(dict.fromkeys(accs_of(t) + list(R)))
        bl = ([b["id"] for b in S["bugs"] if t["id"] in str(b["tc"]).split(" · ")] if fail_accs(t["id"]) else []) + [k for k, v in autos if v.get("tc") == t["id"]]
        bugs = " ".join(f'<a class="pill bug" href="#bug-{E(b)}">{E(b)}</a>' for b in bl)
        shots = [a for sl in keys for a in R.get(sl, {}).get("shots", [])]
        def row(sl):
            x = R.get(sl, {}); dash = '<span class="note">—</span>'
            ty = " ".join('<span class="rp fail">' + E(y) + '</span>' for y in x.get("types", [])) or dash
            return f'<tr><td>{E(acc_name(sl))}</td><td>{res_pill(x.get("a"))}</td><td>{res_pill(x.get("i"))}</td><td>{ty}</td><td>{E(x.get("memo")) or dash}</td><td class="note">{E(x.get("date", ""))}</td></tr>'
        rows = "".join(row(sl) for sl in keys)
        tc_html.append(f'''<div class="card" id="tc-{E(t["id"])}" data-pr="{E(t["pr"])}" data-stage="{E(t["stage"])}" data-res="{E(tc_res(t))}">
<div class="hd"><span class="id">{E(t["id"])}</span><span class="pill {E(t["pr"])}">{E(t["pr"])}</span><span class="pill">{E(t["stage"])}</span><span class="pill">{E(t["scr"])}</span><span class="pill">대상 {E(" ".join(SYM.get(x, "무관") for x in accs_of(t)))}</span><span class="pill">{E(t["env"])}</span>{bugs}</div>
<dl>{f'<dt>사전 조건</dt><dd>{E(t["pre"])}</dd>' if t["pre"] and t["pre"] != "—" else ""}<dt>절차</dt><dd>{E(t["step"])}</dd><dt>기대 결과</dt><dd><b>{E(t["exp"])}</b></dd><dt>근거</dt><dd class="note">{E(t["ref"])}</dd>
</dl>
{cmp_block(fig.get(t["id"]), shots)}
<div class="judge"><div class="jt">계정별 판정 · 종합 {res_pill(tc_res(t))}</div><div class="tablewrap"><table class="runs"><tr><th>계정</th><th>Android</th><th>iOS</th><th>오류 유형</th><th>다른 점</th><th>날짜</th></tr>{rows}</table></div></div></div>''')

    # 결함
    def bug_card(bid, base, auto):
        s = BUGS.get(bid, {})
        if auto:
            t = next((x for x in tcs if x["id"] == s.get("tc")), {})
            title, pr, sev = s.get("title", ""), s.get("pr", ""), s.get("sev", "")
            scr, path, exp, act, ref, tcid = t.get("scr", ""), ((t.get("pre") + " → ") if t.get("pre") and t.get("pre") != "—" else "") + t.get("step", ""), t.get("exp", ""), s.get("act", ""), t.get("ref", ""), s.get("tc", "")
            fa = fail_accs(tcid); shots = [a for sl in fa for a in RUNS.get(tcid, {}).get(sl, {}).get("shots", [])]; fk = fig.get(tcid)
        else:
            title, pr, sev, scr, path, exp, act, ref, tcid = base["title"], base["pr"], base["sev"], base["scr"], base["path"], base["exp"], base["act"], base["ref"], base["tc"]
            shots = s.get("shots", []); fk = fig.get(bid)
        status = s.get("status") or (base or {}).get("status", "")
        memo = s.get("memo", "")
        return f'''<div class="card{' new' if auto else ''}" id="bug-{E(bid)}"><div class="hd"><span class="id">{E(bid)}</span><span class="pill {E(pr)}">{E(pr)}</span><span class="pill">{E(sev)}</span><span class="pill st">{E(status)}</span><b>{E(title)}</b></div>
<dl><dt>화면</dt><dd>{E(scr)}</dd><dt>재현 경로</dt><dd>{E(path)}</dd><dt>기대</dt><dd>{E(exp)}</dd><dt>실제</dt><dd><b>{E(act)}</b></dd><dt>근거</dt><dd class="note">{E(ref)}</dd><dt>관련 TC</dt><dd>{E(tcid)}</dd>{f'<dt>실패한 계정</dt><dd>{E(" · ".join(acc_name(x) for x in fail_accs(tcid)))}</dd>' if auto and fail_accs(tcid) else ''}{f'<dt>메모</dt><dd>{E(memo)}</dd>' if memo else ''}</dl>
{cmp_block(fk, shots)}</div>'''
    bug_html = ("".join(bug_card(k, None, True) for k, _ in autos) and f'<h3>새로 생긴 결함 ({len(autos)})</h3>' + "".join(bug_card(k, None, True) for k, _ in autos)) + f'<h3>기획이 웹 샘플로 찾은 결함 ({len(S["bugs"])})</h3>' + "".join(bug_card(b["id"], b, False) for b in S["bugs"])

    fig_html = "".join(f'<div class="card"><div class="hd"><span class="id">{E(f["id"])}</span><b>{E(f["scr"])}</b><span class="pill">노드 {E(f["node"])}</span></div><dl><dt>목업</dt><dd>{E(f["mock"])}</dd><dt>디스크립션</dt><dd>{E(f["desc"])}</dd><dt>처리</dt><dd><b>{E(f["res"])}</b></dd></dl></div>' for f in S["fig"])
    dec_html = "".join(f'<div class="card"><div class="hd"><span class="id">{E(d["id"])}</span><b>{E(d["title"])}</b><span class="pill P1">기한 {E(d["due"])}</span></div><dl><dt>지금 상태</dt><dd>{E(d["now"])}</dd><dt>선택지</dt><dd>{E(d["opts"])}</dd><dt>결정</dt><dd><b>{E(DEC.get(d["id"], {}).get("memo") or "미정")}</b></dd><dt>근거</dt><dd class="note">{E(d["ref"])}</dd></dl></div>' for d in S["dec"])
    data_html = '<div class="tablewrap"><table><tr><th>#</th><th>요청 (개발)</th><th>왜</th><th>관련 TC</th></tr>' + "".join(f'<tr><td>{d["n"]}</td><td>{E(d["req"])}</td><td>{E(d["why"])}</td><td>{E(d["tc"])}</td></tr>' for d in S["data"]) + "</table></div>"
    CMP = [("01","SC-RP-01 표지"),("02","SC-RP-02"),("03","SC-RP-03"),("04","SC-RP-04"),("04B","SC-RP-04B"),("05","SC-RP-05"),("06","SC-RP-06"),("07A","SC-RP-07 A"),("07B","SC-RP-07 B"),("07C","SC-RP-07 C"),("07h","07-h 시트"),("07l","07-l"),("08","SC-RP-08"),("sys05","SYS-05")]
    shot_html = '<p class="note">기획이 10/12에 개발 서버 웹 샘플을 열어 찍은 비교입니다. 왼쪽 빨간 테두리 = 개발 dev · 오른쪽 초록 테두리 = 피그마 목업.</p><div class="cmpgrid">' + "".join(f'<figure><img src="shots/cmp_{k}.png" alt="{c} 비교" data-zoom loading="lazy"><figcaption>{c}</figcaption></figure>' for k, c in CMP) + "</div>"
    def prog(sl):
        tot = [t for t in tcs if sl in accs_of(t)]; d = [t["id"] + ("(실패)" if sl in fail_accs(t["id"]) else "") for t in tcs if done(RUNS.get(t["id"], {}).get(sl))]
        return f'{sum(1 for t in tot if done(RUNS.get(t["id"], {}).get(sl)))} / {len(tot)} 완료' + (" · " + ", ".join(d) if d else "")
    acc_html = f'<p class="note">{E(S.get("acc_note",""))}</p><div class="tablewrap"><table><tr><th></th><th>번호</th><th>이름</th><th>등급</th><th>주로 볼 것</th><th>진행 · 한 TC</th></tr>' + "".join(f'<tr><td>{a["k"]}</td><td>{E(a["tel"])}</td><td>{E(a["name"])}</td><td>{E(a["tier"])}</td><td>{E(a["see"])}</td><td>{E(prog(SL[a["k"]]))}</td></tr>' for a in S["acc"]) + "</table></div>" + '<h3>앱 설치 — [QA]맬리브레인 (안드로이드 · Firebase App Distribution)</h3><ol>' + "".join(f"<li>{E(x)}</li>" for x in S.get("install", [])) + "</ol>"
    stages = list(dict.fromkeys(t["stage"] for t in tcs))
    stats = "".join(f'<div class="stat"><span>{p} · {next(x["name"] for x in S["pri"] if x["p"]==p)}</span><b>{cnt(by(p),"통과")} / {len(by(p))}</b><span>실패 {cnt(by(p),"실패")} · 보류 {cnt(by(p),"보류")}</span></div>' for p in ("P1","P2","P3"))
    stats += f'<div class="stat"><span>결함</span><b>{len(S["bugs"])+len(autos)}</b><span>새로 생긴 결함 {len(autos)}</span></div>'

    body = f'''<div class="wrap">
<h1>3기 종료 리포트 QA</h1>
<p class="sub">dev 10/7 빌드 · 기준은 피그마 목업 + 디스크립션 (페이지 1028:3313) · <b>읽기 전용 공개본</b> · 마지막 동기화 <b>__SYNCED__</b></p>
<div class="banner">결과 입력 · 캡처 업로드는 내부 작성 보드에서 합니다. 이 페이지는 그 내용을 매시간(또는 [공개본에 반영]을 누를 때) 옮겨 온 사본입니다.</div>
<div class="top">{stats}<div class="stat verdict" style="color:{'var(--fail)' if f1 else 'var(--ink)'}">{verdict} <span class="note">(Android · 대상 계정 전부 기준)</span></div></div>
<div class="tabs" role="tablist">{"".join(f'<button class="tab" role="tab" data-k="{k}" aria-selected="{str(i==0).lower()}">{n}</button>' for i,(k,n) in enumerate([("tc",f"TC ({len(tcs)})"),("bug",f"결함 ({len(S['bugs'])+len(autos)})"),("fig",f"피그마 정리 ({len(S['fig'])})"),("dec",f"결정 필요 ({len(S['dec'])})"),("data","데이터 요청"),("shot","개발 웹 샘플 비교"),("guide","계정 · 설치")]))}</div>
<section id="v-tc"><div class="bar"><select id="fp" aria-label="우선순위"><option value="">우선순위 전체</option><option>P1</option><option>P2</option><option>P3</option></select><select id="fs" aria-label="여정"><option value="">여정 전체</option>{"".join(f"<option>{E(s)}</option>" for s in stages)}</select><select id="fr" aria-label="결과"><option value="">결과 전체</option>{"".join(f"<option>{v}</option>" for v in ["미실행","진행 중","통과","실패","보류","해당없음"])}</select><span class="note" id="cnt"></span></div>{"".join(tc_html)}</section>
<section id="v-bug" hidden>{bug_html}</section><section id="v-fig" hidden><p class="note">피그마 안에서 목업과 디스크립션이 서로 달랐던 곳 · 목업 우선으로 정리(10/12).</p>{fig_html}</section>
<section id="v-dec" hidden>{dec_html}</section><section id="v-data" hidden>{data_html}</section><section id="v-shot" hidden>{shot_html}</section>
<section id="v-guide" hidden><h3>테스트 계정 (번호는 가림)</h3>{acc_html}<h3>우선순위</h3><div class="tablewrap"><table>{"".join(f'<tr><td><b>{p["p"]}</b></td><td>{p["name"]}</td><td>{E(p["desc"])}</td></tr>' for p in S["pri"])}</table></div>
<p class="note">문서 목록 <a href="../docs.html">docs.html</a> · 프로토타입 <a href="../index.html">index.html</a></p></section>
</div><div class="zoom" id="zoom" hidden></div>'''

    page = PAGE.replace("__BODY__", body)
    digest = hashlib.sha256((page + "".join(sorted(n for _, n in used))).encode()).hexdigest()
    last = QA / "tools" / "last_sync.json"
    prev = json.loads(last.read_text()) if last.exists() else {}
    if prev.get("digest") == digest and (QA / "index.html").exists():
        print("NO_CHANGE"); return
    for f, name in used:
        dst = QA / "caps" / name
        if not dst.exists():
            shutil.copyfile(f, dst)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    (QA / "index.html").write_text(page.replace("__SYNCED__", now), encoding="utf-8")
    last.write_text(json.dumps({"digest": digest, "synced": now, "tc": len(TC), "bugs": len(BUGS), "caps": len(used)}, ensure_ascii=False, indent=1))
    print("UPDATED", now, "tc", len(TC), "bugs", len(BUGS), "caps", len(used))


PAGE = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>3기 리포트 QA</title>
<style>
:root{--bg:#F4F6F5;--card:#FFFFFF;--ink:#17201C;--ink2:#46524C;--ink3:#7D8A84;--line:#DDE3E0;--acc:#0E7A52;--accbg:#E3F1EA;--pass:#0E7A52;--passbg:#E3F4EC;--fail:#C2410C;--failbg:#FCEBE2;--hold:#8A6D00;--holdbg:#FFF3C9;--nabg:#ECEFEE}
@media (prefers-color-scheme:dark){:root{--bg:#101513;--card:#19201D;--ink:#E7EEEA;--ink2:#B3BFB9;--ink3:#7F8C86;--line:#2A332F;--acc:#3DD598;--accbg:#173528;--pass:#3DD598;--passbg:#173326;--fail:#FF8A5B;--failbg:#3A2117;--hold:#E8C547;--holdbg:#3A3315;--nabg:#242C29;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 -apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}
[hidden]{display:none!important}a{color:var(--acc)}
.wrap{max-width:1080px;margin:0 auto;padding-block:20px 80px;padding-inline:16px}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--ink2);margin:0 0 12px}h3{margin:18px 0 8px;font-size:16px}
.banner{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:10px 14px;margin-bottom:12px;font-size:13px;color:var(--ink2)}
.top{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:12px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;min-width:0}.stat b{font-size:22px;display:block;font-variant-numeric:tabular-nums}.stat span{color:var(--ink3);font-size:12px}
.verdict{grid-column:1/-1;font-weight:700;font-size:15px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 14px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5}
.tab{border:1px solid var(--line);background:var(--card);color:var(--ink2);border-radius:999px;padding:7px 14px;cursor:pointer;font:inherit;font-weight:700}.tab[aria-selected="true"]{background:var(--acc);color:var(--card);border-color:var(--acc)}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px}select{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin-bottom:10px;scroll-margin-top:60px}.card.new{border-color:var(--fail)}
.hd{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:6px}.id{font-weight:800}
.pill{font-size:12px;font-weight:700;border-radius:999px;padding:2px 9px;background:var(--nabg);color:var(--ink2);text-decoration:none}.pill.P1,.pill.bug{background:var(--failbg);color:var(--fail)}.pill.st{background:var(--accbg);color:var(--acc)}
dl{display:grid;grid-template-columns:72px minmax(0,1fr);gap:3px 10px;margin:6px 0}dt{color:var(--ink3);font-size:12px;padding-top:2px}dd{margin:0;min-width:0;overflow-wrap:anywhere}.note{color:var(--ink3);font-size:12px}
.rp{font-size:12px;font-weight:700;border-radius:6px;padding:1px 8px;background:var(--nabg);color:var(--ink2)}.rp.pass{background:var(--passbg);color:var(--pass)}.rp.fail{background:var(--failbg);color:var(--fail)}.rp.hold{background:var(--holdbg);color:var(--hold)}
.runs td,.runs th{font-size:13px;padding:5px 8px;vertical-align:top}.runs th{color:var(--ink3);font-weight:500;text-align:left}
.judge{margin-top:10px;border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--bg)}.jt{font-size:13px;font-weight:700;margin-bottom:4px}
.cmpbox{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;margin-top:10px}.col{min-width:0;display:flex;flex-direction:column;gap:6px}
.cap{font-size:12px;font-weight:700;color:var(--ink2)}.tag{font-size:11px;border-radius:999px;padding:1px 8px;background:var(--accbg);color:var(--acc)}.tag.app{background:var(--failbg);color:var(--fail)}
.frame{border:1px solid var(--line);border-radius:12px;background:var(--bg);height:460px;display:flex;align-items:center;justify-content:center;overflow:hidden}.frame img{max-width:100%;max-height:100%;object-fit:contain;cursor:zoom-in}.frame .none{color:var(--ink3);font-size:12px;text-align:center;padding:12px}
.ups{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}.ups img{width:72px;height:72px;object-fit:cover;border-radius:8px;border:1px solid var(--line);cursor:zoom-in}
@media(max-width:560px){.frame{height:320px}}
table{width:100%;border-collapse:collapse;background:var(--card)}th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{font-size:12px;color:var(--ink3);background:var(--bg)}.tablewrap{overflow-x:auto;border-radius:12px;border:1px solid var(--line)}
.cmpgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.cmpgrid figure{margin:0}.cmpgrid img{width:100%;border-radius:10px;border:1px solid var(--line);cursor:zoom-in}.cmpgrid figcaption{font-size:12px;color:var(--ink2)}
.zoom{position:fixed;inset:0;background:rgba(0,0,0,.78);display:flex;align-items:center;justify-content:center;z-index:20;padding:16px}.zoom img{max-width:100%;max-height:100%;border-radius:10px}
</style></head><body>
__BODY__
<script>
const q=s=>document.querySelector(s);
document.addEventListener('click',e=>{const z=e.target.closest('[data-zoom]');if(z){q('#zoom').innerHTML='<img src="'+z.src+'" alt="확대">';q('#zoom').hidden=false;return}
 if(e.target.closest('#zoom')){q('#zoom').hidden=true;return}
 const t=e.target.closest('.tab');if(t){document.querySelectorAll('.tab').forEach(x=>x.setAttribute('aria-selected',String(x===t)));document.querySelectorAll('section').forEach(s=>s.hidden=s.id!=='v-'+t.dataset.k)}
 const a=e.target.closest('a[href^="#bug-"]');if(a){e.preventDefault();q('.tab[data-k="bug"]').click();setTimeout(()=>q(a.getAttribute('href')).scrollIntoView(),50)}});
function filt(){const p=q('#fp').value,s=q('#fs').value,r=q('#fr').value;let n=0;document.querySelectorAll('#v-tc .card').forEach(c=>{const ok=(!p||c.dataset.pr===p)&&(!s||c.dataset.stage===s)&&(!r||c.dataset.res===r);c.hidden=!ok;if(ok)n++});q('#cnt').textContent=n+'건'}
['#fp','#fs','#fr'].forEach(s=>q(s).onchange=filt);filt();
</script></body></html>"""

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/nonexistent", sys.argv[2] if len(sys.argv) > 2 else None)
