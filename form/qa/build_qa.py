# -*- coding: utf-8 -*-
"""TC 원본(_tc_data.py) → CSV + HTML 생성. 수정은 _tc_data.py 에서만."""
import csv, html, pathlib, collections, re
exec(open("_tc_data.py", encoding="utf-8").read())

HDR = ["TC ID","그룹","우선순위","화면","전제조건","절차","기대결과","근거 코드",
       "현장 위험","결과","실패 시 증상","담당","비고"]

# ─────────── CSV (구글시트·엑셀 import용) ───────────
with open("TC_신청폼.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(HDR)
    for t in TC: w.writerow(list(t)+["","","",""])
print("CSV", len(TC), "행")

# ─────────── HTML (현장 체크리스트) ───────────
G=collections.OrderedDict()
for t in TC: G.setdefault(t[1],[]).append(t)
PC={"P0":"p0","P1":"p1","P2":"p2"}

def esc(x):
    """반드시 escape 먼저. TC 본문에 <script> 같은 문자열이 들어있다 (E-05)."""
    x = html.escape(x)
    x = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", x)        # **굵게**
    x = re.sub(r"`([^`]+)`", r"<code>\1</code>", x)       # `코드`
    return x
rows=[]
for g,items in G.items():
    n0=sum(1 for i in items if i[2]=="P0")
    rows.append(f'<h2 id="g{len(rows)}">{html.escape(g)} <em>{len(items)}건 · P0 {n0}건</em></h2>')
    rows.append('<div class="tcs">')
    for t in items:
        tid,grp,pri,scr,pre,act,exp,ref,risk = t
        rows.append(f'''<div class="tc" data-p="{pri}">
<label class="hd"><input type="checkbox" class="ck"><span class="id">{html.escape(tid)}</span>
<span class="pri {PC[pri]}">{pri}</span><span class="scr">{html.escape(scr)}</span>
<span class="ref">{html.escape(ref)}</span></label>
<div class="bd">
<div class="kv"><b>전제</b><span>{esc(pre)}</span></div>
<div class="kv"><b>절차</b><span>{esc(act)}</span></div>
<div class="kv ok"><b>기대</b><span>{esc(exp)}</span></div>
{f'<div class="kv rk"><b>위험</b><span>{esc(risk)}</span></div>' if risk else ''}
<div class="res"><button type="button" class="b pass">통과</button><button type="button" class="b fail">실패</button><button type="button" class="b na">해당없음</button><input class="memo" placeholder="실패하면 무엇이 어떻게 됐는지 적어주세요"></div>
</div></div>''')
    rows.append('</div>')
BODY="\n".join(rows)
TOC="".join(f'<a href="#g{i}">{html.escape(g)} <b>{len(v)}</b></a>' for i,(g,v) in enumerate(G.items()))

pathlib.Path("TC_신청폼.html").write_text(f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>신청폼 QA 테스트 케이스 — {len(TC)}건</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">\n<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#1F3C5D;--ink:#1A1F26;--ink2:#59636D;--ink3:#8B95A1;--line:#E4E1DA;--bg:#F4F3F0;--wt:#fff;
--ok:#17624A;--ok-bg:#EAF3EF;--no:#9E241D;--no-bg:#FBEFED;--wa:#8A5412;--wa-bg:#FAF2E3}}
body{{font-family:'Pretendard Variable',Pretendard,-apple-system,system-ui,sans-serif;color:var(--ink);
background:var(--bg);line-height:1.7;-webkit-font-smoothing:antialiased}}
body,button,input{{word-break:keep-all;overflow-wrap:break-word}}
header{{background:linear-gradient(140deg,#1F3C5D,#132840);color:#fff;padding:40px 20px 34px;position:sticky;top:0;z-index:20}}
header .in{{max-width:920px;margin:0 auto}}
header h1{{font-size:26px;font-weight:800;letter-spacing:-.04em}}
header p{{font-size:14.5px;color:rgba(255,255,255,.85);margin-top:8px;line-height:1.65}}
.bar{{max-width:920px;margin:14px auto 0;display:flex;gap:7px;flex-wrap:wrap;align-items:center}}
.bar button{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#fff;
border-radius:8px;padding:8px 12px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit}}
.bar button.on{{background:#fff;color:var(--navy)}}
.bar .stat{{margin-left:auto;font-size:13px;font-weight:700;color:rgba(255,255,255,.9)}}
nav{{max-width:920px;margin:0 auto;padding:16px 20px 0;display:flex;gap:7px;flex-wrap:wrap}}
nav a{{background:var(--wt);border:1px solid var(--line);border-radius:999px;padding:7px 13px;
font-size:13px;font-weight:700;text-decoration:none;color:var(--ink)}}
nav a b{{color:var(--navy)}}
main{{max-width:920px;margin:0 auto;padding:20px 20px 90px}}
h2{{font-size:17px;font-weight:800;letter-spacing:-.03em;margin:28px 0 12px;display:flex;gap:9px;align-items:baseline}}
h2 em{{font-style:normal;font-size:12.5px;font-weight:600;color:var(--ink3)}}
.tc{{background:var(--wt);border:1px solid var(--line);border-radius:12px;margin-bottom:8px;overflow:hidden}}
.tc.done{{opacity:.5}}
.hd{{display:flex;align-items:center;gap:9px;padding:12px 14px;cursor:pointer;flex-wrap:wrap}}
.ck{{width:19px;height:19px;flex-shrink:0;accent-color:#17624A}}
.id{{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;font-weight:800;color:var(--navy);
background:#E8EEF4;border-radius:5px;padding:2px 7px}}
.pri{{font-size:11px;font-weight:800;border-radius:5px;padding:2px 7px}}
.pri.p0{{color:var(--no);background:var(--no-bg)}}.pri.p1{{color:var(--wa);background:var(--wa-bg)}}
.pri.p2{{color:var(--ink2);background:#EFEDE7}}
.scr{{font-size:13px;font-weight:700;color:var(--ink2)}}
.ref{{margin-left:auto;font-size:11.5px;color:var(--ink3);font-family:ui-monospace,Menlo,monospace}}
.bd{{padding:0 14px 14px;border-top:1px solid #F0EEE9}}
.kv{{display:flex;gap:10px;font-size:14px;line-height:1.65;margin-top:9px}}
.kv b{{flex-shrink:0;width:38px;font-size:12px;font-weight:800;color:var(--ink3);padding-top:2px}}
.kv.ok span{{color:var(--ok);font-weight:600}}
.kv.rk span{{color:var(--no)}}
.res{{display:flex;gap:6px;margin-top:12px;flex-wrap:wrap}}
.b{{border:1.5px solid var(--line);background:#fff;border-radius:8px;padding:7px 13px;font-size:13px;
font-weight:700;cursor:pointer;font-family:inherit;min-height:38px}}
.b.pass.on{{background:var(--ok);border-color:var(--ok);color:#fff}}
.b.fail.on{{background:var(--no);border-color:var(--no);color:#fff}}
.b.na.on{{background:#8B95A1;border-color:#8B95A1;color:#fff}}
.memo{{flex:1;min-width:180px;border:1.5px solid var(--line);border-radius:8px;padding:7px 11px;
font-size:13.5px;font-family:inherit}}
.note{{background:var(--wa-bg);border:1px solid #E6D3AE;border-left:4px solid #A9701A;border-radius:12px;
padding:15px 17px;font-size:14px;line-height:1.75;color:#6A4A11;margin-bottom:22px}}
.note b{{color:#4A340B}}
@media print{{header,nav,.bar,.res{{display:none}} .tc{{break-inside:avoid;border:1px solid #999}} body{{background:#fff}}}}
</style></head><body>
<header><div class="in">
<h1>신청폼 QA 테스트 케이스</h1>
<p>개발본 <code>dev-meli-web /invitations/namdong3/form</code> 기준 · {len(TC)}건 (P0 {sum(1 for t in TC if t[2]=="P0")} · P1 {sum(1 for t in TC if t[2]=="P1")} · P2 {sum(1 for t in TC if t[2]=="P2")})</p>
<div class="bar">
<button type="button" data-f="all" class="on">전체</button>
<button type="button" data-f="P0">P0만</button>
<button type="button" data-f="P1">P1까지</button>
<button type="button" data-f="todo">안 한 것만</button>
<button type="button" data-f="fail">실패만</button>
<span class="stat" id="stat"></span>
</div></div></header>
<nav>{TOC}</nav>
<main>
<div class="note">
<b>P0는 하나라도 실패하면 현장 투입을 미뤄야 합니다.</b>
P0 = 안 되면 접수 자체가 불가하거나 개인정보·명단 사고로 이어지는 것, P1 = 반드시 확인, P2 = 가능하면.<br>
기록은 이 브라우저에만 남습니다. 여러 명이 나눠 돌리면 <b>CSV를 구글시트로 올려서</b> 쓰세요.
실패한 건은 <b>무엇이 어떻게 됐는지</b>를 적어야 개발자가 재현할 수 있습니다.
</div>
{BODY}
</main>
<script>
const K='qa-tc-v1';
let S={{}}; try{{S=JSON.parse(localStorage.getItem(K)||'{{}}')}}catch(e){{}}
const save=()=>{{try{{localStorage.setItem(K,JSON.stringify(S))}}catch(e){{}}}};
document.querySelectorAll('.tc').forEach(tc=>{{
  const id=tc.querySelector('.id').textContent, st=S[id]||{{}};
  const ck=tc.querySelector('.ck'), memo=tc.querySelector('.memo');
  if(st.r){{tc.querySelector('.b.'+st.r)?.classList.add('on'); ck.checked=true; tc.classList.add('done');}}
  if(st.m) memo.value=st.m;
  tc.querySelectorAll('.b').forEach(b=>b.onclick=()=>{{
    const r=[...b.classList].find(c=>['pass','fail','na'].includes(c));
    tc.querySelectorAll('.b').forEach(x=>x.classList.remove('on'));
    if(st.r===r){{delete st.r; ck.checked=false; tc.classList.remove('done');}}
    else{{b.classList.add('on'); st.r=r; ck.checked=true; tc.classList.add('done');}}
    S[id]=st; save(); stat();
  }});
  memo.oninput=()=>{{st.m=memo.value; S[id]=st; save();}};
  ck.onchange=()=>{{tc.classList.toggle('done',ck.checked); if(!ck.checked){{delete st.r; tc.querySelectorAll('.b').forEach(x=>x.classList.remove('on'));}} S[id]=st; save(); stat();}};
}});
function stat(){{
  const all=[...document.querySelectorAll('.tc')];
  const p0=all.filter(t=>t.dataset.p==='P0');
  const d=all.filter(t=>S[t.querySelector('.id').textContent]?.r).length;
  const f=all.filter(t=>S[t.querySelector('.id').textContent]?.r==='fail').length;
  const p0f=p0.filter(t=>S[t.querySelector('.id').textContent]?.r==='fail').length;
  document.getElementById('stat').textContent=`진행 ${{d}}/${{all.length}} · 실패 ${{f}}` + (p0f?`  ⚠ P0 실패 ${{p0f}}`:'');
}}
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('.bar button').forEach(x=>x.classList.remove('on')); b.classList.add('on');
  const f=b.dataset.f;
  document.querySelectorAll('.tc').forEach(tc=>{{
    const r=S[tc.querySelector('.id').textContent]?.r, p=tc.dataset.p;
    let show=true;
    if(f==='P0') show = p==='P0';
    else if(f==='P1') show = p!=='P2';
    else if(f==='todo') show = !r;
    else if(f==='fail') show = r==='fail';
    tc.style.display=show?'':'none';
  }});
  document.querySelectorAll('h2,.tcs').forEach(h=>{{}});
}});
stat();
</script></body></html>''', encoding="utf-8")
print("HTML 생성")
