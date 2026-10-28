import json, sys
src, dst = sys.argv[1], sys.argv[2]
data = json.load(open(src, encoding="utf-8"))
import os
BASE = os.path.dirname(os.path.abspath(__file__))
_ao = json.load(open(BASE + "/data/asof.json", encoding="utf-8"))
_latest = max((c[0] for g in json.load(open(BASE + "/data/regional.json", encoding="utf-8")) for c in g.get("계약", [])), default="-")

import re, importlib.util
spec = importlib.util.spec_from_file_location("m", os.path.dirname(os.path.abspath(__file__)) + "/sgg_master.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
MASTER, OLD = m.SGG, m.OLD
for d in data:
    sd, sg = d["시도"], d["시군구"]
    sg = OLD.get(sd, {}).get(sg, sg)
    d["시군구"] = sg
    units = []
    if sd == "세종":
        units = ["세종시"]
    elif sg != "광역":
        for tok in re.split(r"[·/,]|\s+", sg):
            tok = tok.strip()
            if not tok: continue
            hit = [x for x in MASTER.get(sd, []) if x == tok or x.startswith(tok)]
            if hit: units.append(hit[0])
    if sd == "서울" and d["서비스"].startswith("브레인핏45"):
        units = list(MASTER["서울"])  # 서울시 전 시민 대상 앱(손목닥터9988 연동) -> 25개 구 전체
    d["units"] = sorted(set(units))
    d["counts"] = "교구" not in d["서비스"]
html = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="시니어 디지털 서비스가 시·도와 시·군·구별로 어디에 들어가 있는지 보는 전체 현황 지도">
<title>전체 현황 지도</title>
<link rel="stylesheet" href="ui.css?v=20261028d">
<style>
.stats{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-bottom:16px}
@media (max-width:1100px){.stats{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:600px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.stat{display:flex;flex-direction:column;align-items:flex-start;gap:4px;min-height:44px;background:var(--surface);border:0;border-radius:var(--r-lg);box-shadow:var(--shadow);padding:16px 20px;text-align:left;cursor:pointer;transition:box-shadow var(--dur-micro) var(--ease),transform var(--dur-micro) var(--ease)}
.stat:hover{box-shadow:var(--shadow-pop)}
.stat:active{transform:scale(0.98)}
.stat span{color:var(--ink-3);font-size:var(--fs-sm);font-weight:600;display:flex;align-items:center;gap:8px}
.stat span i{width:10px;height:10px;border-radius:3px;display:inline-block}
.stat b{font-size:var(--fs-num);font-weight:800;line-height:1.2;font-variant-numeric:tabular-nums;color:var(--ink)}
.stat small{font-size:var(--fs-cap);color:var(--ink-4)}
.stat[aria-pressed="true"]{background:var(--ink)}
.stat[aria-pressed="true"] span,.stat[aria-pressed="true"] small{color:var(--surface-3)}
.stat[aria-pressed="true"] b{color:var(--surface)}
.sorts{margin:0 0 8px}
.sorts button{text-align:center;font-size:var(--fs-sm);font-weight:600;min-height:36px}
.sdlist{display:flex;flex-direction:column}
.sdrow{display:grid;grid-template-columns:48px minmax(0,1fr) 72px 112px;gap:12px;align-items:center;width:100%;min-height:52px;border:0;border-top:1px solid var(--line);background:none;padding:8px;border-radius:var(--r-md);cursor:pointer;text-align:left;transition:background-color var(--dur-micro) var(--ease)}
.sdrow:first-child{border-top:0}
.sdrow:hover{background:var(--surface-2)}
.sdn{font-weight:700;color:var(--ink)}
.sdbar{height:8px;border-radius:4px;background:var(--surface-3);overflow:hidden}
.sdbar i{display:block;height:100%;background:var(--brand-2);border-radius:4px}
.sdv{font-size:var(--fs-sm);color:var(--ink-4);text-align:right;font-variant-numeric:tabular-nums}
.sdv b{color:var(--ink);font-size:var(--fs-body)}
.sde{font-size:var(--fs-sm);color:var(--ink-2);font-weight:600;text-align:right}
.sde small{display:block;font-weight:500;color:var(--ink-4);font-size:var(--fs-cap)}
.back{min-height:36px;border:0;background:var(--surface-3);color:var(--ink-2);border-radius:var(--r-pill);padding:4px 12px;font-size:var(--fs-sm);font-weight:600;cursor:pointer;margin-bottom:12px}
.back:hover{background:var(--line)}
.cov{background:var(--surface-2);border-radius:var(--r-md);padding:16px;margin-bottom:16px;display:grid;gap:16px}
.covh{font-size:var(--fs-sm);color:var(--ink-3);font-weight:600;margin-bottom:8px}
.covh b{color:var(--ink);font-size:var(--fs-body);margin-left:4px;font-variant-numeric:tabular-nums}
.covnote{margin:0;font-size:var(--fs-sm);color:var(--ink-4)}
.none{font-size:var(--fs-sm);color:var(--ink-4)}
.echips{display:flex;flex-wrap:wrap;gap:8px}
.echip{min-height:36px;font-size:var(--fs-sm);border:0;border-radius:var(--r-pill);padding:4px 12px;display:inline-flex;align-items:center;gap:8px}
.echip.yes{background:var(--surface);color:var(--ink);font-weight:600;box-shadow:var(--shadow);cursor:pointer;transition:background-color var(--dur-micro) var(--ease),color var(--dur-micro) var(--ease)}
.echip.yes:hover{background:var(--surface-3)}
.echip.yes .n{font-size:var(--fs-cap);font-weight:700;color:var(--ink-4);font-variant-numeric:tabular-nums}
.echip.yes[aria-pressed="true"]{background:var(--ink);color:var(--surface)}
.echip.yes[aria-pressed="true"] .n{color:var(--surface-3)}
.echip.no{background:transparent;color:var(--ink-3);box-shadow:inset 0 0 0 1px var(--line-2)}
.searchrow{display:flex;gap:8px;align-items:center;margin-bottom:8px}
.searchrow .search{margin:0;flex:1 1 auto;min-width:0}
.clr{min-height:44px;border:0;background:var(--surface-3);color:var(--ink-2);border-radius:var(--r-md);padding:8px 12px;font-size:var(--fs-sm);font-weight:600;cursor:pointer;white-space:nowrap}
.grid{display:grid;grid-template-columns:minmax(0,500px) minmax(0,1fr);gap:16px;align-items:start}
@media (max-width:860px){.grid{grid-template-columns:minmax(0,1fr)}}
.mapbox{background:var(--surface);border-radius:var(--r-lg);box-shadow:var(--shadow);padding:20px;position:sticky;top:72px}
@media (max-width:860px){.mapbox{position:static}}
.mhint{font-size:var(--fs-sm);color:var(--ink-4);margin:0 0 12px}
.mlegend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:var(--fs-cap);color:var(--ink-3);margin-top:12px}
.mlegend i{display:inline-block;width:12px;height:12px;border-radius:4px;margin-right:4px;vertical-align:-1px}
.panel{color:var(--ink);background:var(--surface);border-radius:var(--r-lg);box-shadow:var(--shadow);padding:24px}
.panel h2{font-size:var(--fs-xl);font-weight:800}
.panel .sub{color:var(--ink-3);font-size:var(--fs-sm);margin:4px 0 16px}
.search{width:100%;min-height:44px;padding:12px 16px;border:1px solid var(--line);border-radius:var(--r-md);background:var(--surface-2);color:var(--ink);margin-bottom:8px}
.search::placeholder{color:var(--ink-4)}
.sgg{border-top:1px solid var(--line);padding:16px 0}
.sgg h3{font-size:var(--fs-md);font-weight:700;margin:0 0 8px}
.svc{display:flex;gap:12px;align-items:flex-start;margin:12px 0;font-size:var(--fs-body);color:var(--ink)}
.svc .dot{flex:0 0 10px;height:10px;border-radius:3px;margin-top:8px}
.svc .meta{color:var(--ink-4);font-size:var(--fs-sm)}
.svc a{color:var(--brand-2)}
.svc.ours{background:var(--brand-soft);border-radius:var(--r-md);padding:12px 12px;margin-left:-12px;margin-right:-12px}
.tag{font-size:var(--fs-cap);background:var(--surface-2);border-radius:6px;padding:2px 8px;margin-left:8px;color:var(--ink-3);font-weight:600}
.ctr{margin-top:8px;font-size:var(--fs-sm)}
.ctr summary{cursor:pointer;color:var(--brand-2);font-weight:600}
.ctr ul{margin:8px 0 0;padding-left:16px}
.ctr li{margin:8px 0;color:var(--ink-2)}
.ctr .cd{color:var(--ink-4);font-variant-numeric:tabular-nums}
.ctr .ck{font-size:var(--fs-cap);background:var(--surface-2);border-radius:5px;padding:2px 8px;color:var(--ink-3)}
.ctr a.cn{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line-2);text-underline-offset:3px}
.ctr a.cn:hover{color:var(--brand-2);text-decoration-color:var(--brand-2)}
.ctr b{font-variant-numeric:tabular-nums}
</style></head><body>
<header class="topbar"><div class="topbar-in"><a class="wordmark" href="status.html">맬리브레인 <span>B2G</span></a><nav class="tabsnav" aria-label="지도 메뉴"><a href="status.html" aria-current="page">전체 현황</a><a href="vendors.html">경쟁 서비스</a><a href="sales.html" class="soon">영업 지도<small>준비 중</small></a></nav></div></header>
<main class="page">
<div class="pagehead"><h1>전체 현황 지도</h1><p>시니어 디지털 서비스가 지역별로 어디에 들어가 있는지 봅니다. 시·도를 고르면 시·군·구마다 무엇이 들어갔는지 나옵니다.</p><div class="asof"><span>데이터 기준 <b>__ASOF__</b></span><span>나라장터 최근 계약일 __LATEST__</span><a class="refresh" href="https://github.com/butblank-oss/meli.brain/actions/workflows/b2g-refresh.yml" target="_blank" rel="noopener" title="GitHub에서 Run workflow를 누르면 그 시점 기준으로 나라장터를 다시 불러와 3~5분 뒤 이 화면에 반영됩니다">최신 데이터 불러오기</a></div></div>
<div class="stats" id="stats"></div>

<div class="grid">
 <div class="mapbox"><p class="mhint">시·도를 누르면 확대되고 오른쪽에 상세가 나옵니다. 확대한 뒤 시·군·구를 누르면 그곳만 걸러집니다.</p><div id="map"></div><div class="mlegend" id="mlegend"></div></div>
 <div class="panel" id="panel"></div>
</div>
<ul class="foot">
<li><b>나라장터</b> 표시는 실제 계약이 있었던 것, <b>기사</b> 표시는 보도자료와 공식 페이지로 확인한 것입니다. 나라장터에는 돈을 주고 계약한 것만 잡혀서 시·도 자체 개발 앱, 무상 제공, 연구 협약은 빠질 수 있습니다.</li>
<li>계약명 키워드로 분류해 일부 오분류가 있을 수 있습니다. 교구·교재 구매는 빈 곳 계산에서 뺐습니다.</li>
<li>정부사업(AI·IoT 어르신건강관리, 모바일헬스케어) 기기 구매와 경로당 가전, 실종 예방 태그, 경품 같은 일반 물품은 뺐습니다.</li>
<li>서울 인지훈련은 브레인핏45(서울시 운영, 주식회사 기억산책 개발)가 45세 이상 전 시민 대상이라 25개 구 전체로 봤습니다.</li>
<li>인천은 2026.7 개편 기준(영종구, 제물포구, 검단구, 서해구), 대구는 군위군 포함 기준입니다. 경계: vuski/admdongkor 행정동 경계(2023.7)를 2026년 시·군·구로 합쳐 그렸습니다.</li>
</ul>
</main>
<script src="kmap.js?v=20261028d"></script>
<script>
const DATA = __DATA__;
const MASTER = __MASTER__;
const TYPES = [["인지훈련·치매예방","var(--c1)"],["걸음·건강관리","var(--c2)"],["AI돌봄·안부","var(--c3)"],["돌봄로봇","var(--c4)"],["스마트경로당","var(--c5)"]];
const COLOR = Object.fromEntries(TYPES);
const POS = {"인천":[0,0],"서울":[1,0],"강원":[2,0],"충남":[0,1],"경기":[1,1],"충북":[2,1],"경북":[3,1],"세종":[0,2],"대전":[1,2],"대구":[2,2],"울산":[3,2],"전북":[0,3],"경남":[2,3],"부산":[3,3],"광주":[0,4],"전남":[1,4],"제주":[0,5]};
let filter = "인지훈련·치매예방", sel = null, q = "", sortSd = "order";
const ORDER = ["서울","인천","경기","강원","충북","충남","세종","대전","전북","광주","전남","경북","대구","울산","경남","부산","제주"];
const TOTAL = ORDER.reduce((n,sd)=>n+MASTER[sd].length,0);
const rows = () => DATA.filter(d => filter==="전체" || d["유형"]===filter);
function covered(sido, f){ const s=new Set(); DATA.filter(d=>(f===undefined?(filter==="전체"||d["유형"]===filter):(f==="전체"||d["유형"]===f))&&d["시도"]===sido&&d.counts).forEach(d=>d.units.forEach(u=>s.add(u))); return s }
function hasWide(sido){ return rows().some(d=>d["시도"]===sido&&d.counts&&d["시군구"]==="광역") }
function natCount(f){ return ORDER.reduce((n,sd)=>n+covered(sd,f).size,0) }
function renderStats(){
  const opts=[...TYPES.map(([t,c])=>[t,t,c]),["전체","전체 서비스","var(--ink)"]];
  document.getElementById("stats").innerHTML = opts.map(([t,label,c])=>`<button class="stat" data-t="${t}" aria-pressed="${t===filter}"><span><i style="background:${c}"></i>${label}</span><b>${natCount(t)}곳</b><small>시·군·구 ${TOTAL}곳 중</small></button>`).join("");
  document.querySelectorAll(".stat").forEach(b=>b.onclick=()=>{filter=b.dataset.t;q="";render()});
}
function renderFilters(){ const f=document.getElementById("filters"); if(f) f.remove(); }
let KM=null;
function renderMap(){
  if(!window.__GEO){ return; }
  const opt={geo:window.__GEO, order:ORDER,
    sdTip:sd=>`<b>${esc(sd)}</b><br>${esc(filter)} 있음 ${covered(sd).size} / ${MASTER[sd].length}<br><span style="opacity:.75">눌러서 확대</span>`,
    fill:(sd,sgg)=>{const t=new Set(rows().filter(d=>d["시도"]===sd&&d.counts&&d.units.includes(sgg)).map(d=>d["유형"])).size;
      if(!t) return {fill:"var(--none)"};
      if(filter!=="전체") return {fill:COLOR[filter]};
      return {fill:t>=3?"var(--cov-3)":t===2?"var(--cov-2)":"var(--cov-1)"}},
    selected:()=>null,
    sdLabel:sd=>[sd,`${covered(sd).size}/${MASTER[sd].length}`],
    tip:(sd,sgg)=>{const n=rows().filter(d=>d["시도"]===sd&&d.counts&&d.units.includes(sgg)).map(d=>d["서비스"]);return `<b>${esc(sd)} ${esc(sgg)}</b><br>${n.length?n.slice(0,4).map(esc).join("<br>")+(n.length>4?`<br>외 ${n.length-4}개`:""):"확인된 서비스 없음"}`},
    onSido:sd=>{ sel=sd||null; q=""; renderPanel() },
    onSgg:(sd,sgg)=>{sel=sd;q=sgg;renderPanel();document.getElementById("panel").scrollIntoView({behavior:"smooth",block:"start"})}};
  document.getElementById("mlegend").innerHTML = filter==="전체"
    ? `<span><i style="background:var(--cov-1)"></i>유형 1개</span><span><i style="background:var(--cov-2)"></i>2개</span><span><i style="background:var(--cov-3)"></i>3개 이상</span><span><i style="background:var(--none)"></i>없음</span>`
    : `<span><i style="background:${COLOR[filter]}"></i>${esc(filter)} 있음</span><span><i style="background:var(--none)"></i>없음</span>`;
  if(!KM){ KM=KMap.create(document.getElementById("map"),opt) } else { KM.paint(); KM.relabel() }
}
function esc(s){return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function won(n){ if(!n) return "-"; if(n>=1e8) return (n/1e8).toFixed(n%1e8?1:0)+"억 원"; return Math.round(n/1e4).toLocaleString()+"만 원" }
function ctr(d){
  const c=d["계약"]; if(!c||!c.length) return "";
  const list=[...c].sort((a,b)=>b[0].localeCompare(a[0])).map(x=>`<li><span class="cd">${esc(x[0])}</span> <span class="ck">${esc(x[3])}·${esc(x[4]||"")}</span> ${x[5]?`<a class="cn" href="${esc(x[5])}" target="_blank" rel="noopener">${esc(x[1])}</a>`:esc(x[1])} <b>${won(x[2])}</b></li>`).join("");
  const tot=c.reduce((s,x)=>s+(x[2]||0),0);
  return `<details class="ctr" ${c.length<=2?"open":""}><summary>계약 ${c.length}건, 합계 ${won(tot)}</summary><ul>${list}</ul></details>`;
}
function goSido(sd){ sel=sd; q=""; KM&&KM.zoom(sd); renderPanel(); }
function renderNational(){
  let list=ORDER.map(sd=>{const c=covered(sd).size, n=MASTER[sd].length; return {sd,c,n,e:n-c,w:hasWide(sd)}});
  if(sortSd==="empty") list.sort((a,b)=>b.e-a.e||a.c-b.c);
  if(sortSd==="ratio") list.sort((a,b)=>b.c/b.n-a.c/a.n);
  const tot=list.reduce((x,r)=>x+r.c,0);
  const label=filter==="전체"?"전체 서비스":filter;
  document.getElementById("panel").innerHTML = `<h2>전국</h2><div class="sub">${esc(label)} 기준, 시·군·구 ${TOTAL}곳 중 <b>${tot}곳</b>에 들어가 있습니다.</div>
  <div class="sorts seg" role="group" aria-label="정렬">${[["order","지역순"],["empty","빈 곳 많은 순"],["ratio","들어간 비율 순"]].map(([k,l])=>`<button data-s="${k}" aria-pressed="${sortSd===k}">${l}</button>`).join("")}</div>
  <div class="sdlist">${list.map(r=>`<button class="sdrow" data-sd="${r.sd}"><span class="sdn">${r.sd}</span><span class="sdbar"><i style="width:${r.c/r.n*100}%"></i></span><span class="sdv"><b>${r.c}</b>/${r.n}곳</span><span class="sde">${r.e?`빈 곳 ${r.e}`:"빈 곳 없음"}${r.w?`<small>시·도 단위 있음</small>`:""}</span></button>`).join("")}</div>`;
  document.querySelectorAll(".sdrow").forEach(b=>b.onclick=()=>goSido(b.dataset.sd));
  document.querySelectorAll(".sorts [data-s]").forEach(b=>b.onclick=()=>{sortSd=b.dataset.s;renderNational()});
}
function renderPanel(){
  if(!sel){ renderNational(); return; }
  const rs = rows().filter(d=>d["시도"]===sel);
  const groups = {}; rs.forEach(d=>{(groups[d["시군구"]] ||= []).push(d)});
  let keys = Object.keys(groups).sort((a,b)=> (a==="광역"?-1:b==="광역"?1:a.localeCompare(b,"ko")));
  if(q) keys = keys.filter(k=>k.includes(q) || groups[k].some(d=>(d["서비스"]+d["업체"]).includes(q)));
  const body = keys.map(k=>{
    const items = groups[k].sort((a,b)=>TYPES.findIndex(t=>t[0]===a["유형"])-TYPES.findIndex(t=>t[0]===b["유형"]));
    return `<div class="sgg"><h3>${k==="광역"?sel+" 광역 단위":esc(k)}</h3>${items.map(d=>{
      const ours = /맬리/.test(d["서비스"]);
      const src = d["출처"]==="나라장터" ? `<span>나라장터</span><span>최근 ${esc(d["최근"])}</span>` : `<span>기사</span><span>${esc(d["최근"])}</span>`;
      const link = (d["링크"] && d["출처"]!=="나라장터") ? `<span><a href="${esc(d["링크"])}" target="_blank" rel="noopener">원문 보기</a></span>` : "";
      return `<div class="svc ${ours?'ours':''}"><span class="dot" style="background:${COLOR[d["유형"]]||'var(--ink-4)'}"></span><div><div>${esc(d["서비스"])}${d["업체"]&&!/^미기재/.test(d["업체"])&&!d["서비스"].includes(d["업체"])?` <span class="meta">${esc(d["업체"])}</span>`:""}<span class="tag">${esc(d["유형"])}</span></div><div class="meta ms">${src}${link}</div>${ctr(d)}</div></div>`}).join("")}</div>`}).join("");
  const cov=covered(sel), all=MASTER[sel], have=all.filter(x=>cov.has(x)), empty=all.filter(x=>!cov.has(x));
  const cnt=x=>rows().filter(d=>d["시도"]===sel&&d.counts&&d.units.includes(x)).length;
  const label=filter==="전체"?"전체 서비스":filter;
  const box = `<div class="cov">
    <div class="covrow"><div class="covh">들어간 곳 <b>${have.length}</b></div><div class="echips">${have.length?`<button class="echip yes all" data-q="" aria-pressed="${!q}">${esc(sel)} 전체</button>`+have.map(x=>`<button class="echip yes" data-q="${esc(x)}" aria-pressed="${q===x}">${esc(x)}<span class="n">${cnt(x)}</span></button>`).join(""):'<span class="none">없음</span>'}</div></div>
    <div class="covrow"><div class="covh">빈 곳 <b>${empty.length}</b></div><div class="echips">${empty.length?empty.map(x=>`<span class="echip no">${esc(x)}</span>`).join(""):'<span class="none">없음</span>'}</div></div>
    ${hasWide(sel)?'<p class="covnote">이 시·도에는 시·도 단위 서비스도 있습니다(아래 「광역 단위」).</p>':''}
  </div>`;
  document.getElementById("panel").innerHTML = `<button class="back" id="back">전국 보기</button><h2>${sel}</h2><div class="sub">${esc(label)} 기준, 시·군·구 ${all.length}곳 중 ${have.length}곳</div>${box}<div class="searchrow"><input class="search" id="q" placeholder="시·군·구나 서비스·업체 이름으로 찾기" value="${esc(q)}">${q?`<button class="clr" id="clr">${esc(sel)} 전체 보기</button>`:''}</div>${body||'<p class="sub">확인된 항목이 없습니다.</p>'}`;
  document.getElementById("back").onclick=()=>{sel=null;q="";KM&&KM.zoom(null);renderPanel()};
  document.querySelectorAll(".echip[data-q]").forEach(b=>b.onclick=()=>{q=(b.dataset.q===""||q===b.dataset.q)?"":b.dataset.q;renderPanel()});
  const c=document.getElementById("clr"); if(c) c.onclick=()=>{q="";renderPanel()};
  const inp=document.getElementById("q"); inp.oninput=()=>{q=inp.value.trim();renderPanel();const i=document.getElementById("q");i.focus();i.setSelectionRange(i.value.length,i.value.length)};
}
function render(){renderFilters();renderStats();renderMap();renderPanel()}
fetch("sgg.geo.json?v=20261028d").then(r=>r.json()).then(g=>{window.__GEO=g;renderMap()});
render();
</script></body></html>"""
open(dst, "w", encoding="utf-8").write(html.replace("__ASOF__", _ao["asof"]).replace("__LATEST__", _latest).replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__MASTER__", json.dumps(MASTER, ensure_ascii=False)))
print("ok", len(data))
