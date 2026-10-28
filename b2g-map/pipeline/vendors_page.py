"""서비스(업체·제품)별로 어느 시·군·구에 들어가 있는지: b2g-map/vendors.html"""
import json, re, sys, importlib.util
from collections import defaultdict
import os; BASE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("m", BASE + "/sgg_master.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
MASTER, OLD = m.SGG, m.OLD
data = json.load(open(BASE + "/data/regional.json", encoding="utf-8"))
_ao = json.load(open(BASE + "/data/asof.json", encoding="utf-8"))
_latest = max((c[0] for g in json.load(open(BASE + "/data/regional.json", encoding="utf-8")) for c in g.get("계약", [])), default="-")


LABEL_BRAND = {
    "워크온 걷기챌린지": "스왈라비", "효돌 돌봄로봇": "효돌", "다솜 돌봄로봇": "원더풀플랫폼",
    "AI 돌봄인형(미스터마인드)": "미스터마인드", "맬리브레인": "원메딕스", "기억하리": "펀웨이브",
    "모바일 AI 치매예방 플랫폼(하야트)": "하야트", "클로바 케어콜(네이버)": "네이버",
    "AI스피커 돌봄(SKT·행복커넥트)": "행복커넥트(SKT)", "대교 인지강화 프로그램(대면)": "대교",
    "슈퍼브레인(로완)": "로완", "기억담기 등 인지훈련 앱 구축(기억산책)": "기억산책(구 씨투몬스터)", "손목닥터9988": "서울시",
}
# 회사 -> (서비스명, 확인 방법) : 제품 = 앱 마켓·기사로 확인한 제품명, 계약명 = 나라장터 계약명에서 딴 이름
SVC = {
    "하야트": ("인지케어", "제품"), "두뇌싱긋교육개발원": ("두뇌자랑", "제품"), "펀웨이브": ("기억하리", "제품"),
    "기억산책(구 씨투몬스터)": ("브레인핏45, 기억담기", "제품"), "로완": ("슈퍼브레인", "제품"), "원메딕스": ("맬리브레인", "제품"),
    "대교": ("인지강화 토탈케어", "계약명"), "노리몰": ("뇌 청춘 건강 100세", "계약명"), "넥서스브레인컨설팅": ("치유농업 인지건강 프로그램", "계약명"),
    "이룸아이앤씨": ("스마트케어 기기", "계약명"), "도스트11": ("치매예방 프로그램", "계약명"), "놀깨교육": ("VR 인지재활", "계약명"),
    "라이넥스": ("인지재활훈련 장비", "계약명"), "에스엠티아이": ("체감형 ADL 인지재활 훈련 시스템", "계약명"),
    "에스와이이노테크": ("인지강화 VR 솔루션", "계약명"), "오이코스": ("스마트미러", "계약명"), "코트라스": ("코트라스 전산화 인지재활", "제품"),
    "어울": ("두뇌팡팡 오감놀이터", "계약명"), "브레인아카데미": ("경로당 ICT 인지훈련", "계약명"), "지앤에스인터내셔널": ("코트라스 D 납품", "계약명"),
    "앞선": ("전산화 인지재활 프로그램", "계약명"), "국가경제연구원": ("맞춤형 뇌건강 사업", "계약명"), "힐링업": ("인지재활 프로그램·장비 임대", "계약명"),
    "메디팜": ("그룹 인지재활 훈련 시스템", "계약명"),
    "SK케미칼": ("사운드마인드", "제품"), "에이블테라퓨틱스": ("스픽", "제품"), "행복커넥트(SKT)": ("AI스피커 돌봄, 두뇌톡톡", "제품"),
    "경기도": ("AI 간편치매체크", "제품"), "단양군 치매안심센터": ("웃음꽃 피오(치매안심 로봇)", "제품"),
    "스왈라비": ("워크온", "제품"), "효돌": ("효돌·효순이", "제품"), "원더풀플랫폼": ("다솜", "제품"), "미스터마인드": ("AI 돌봄인형", "제품"),
    "네이버": ("클로바 케어콜", "제품"), "서울시": ("손목닥터9988", "제품"),
}
def brand(g):
    s, v = g["서비스"], g["업체"] or ""
    if s in LABEL_BRAND: return LABEL_BRAND[s]
    txt = s + " " + v
    if re.search(r"오늘건강|정부사업|치매체크 앱 안내", txt): return None
    if "두뇌톡톡" in txt: return "행복커넥트(SKT)"
    if "사운드마인드" in txt: return "SK케미칼"
    if "스픽" in txt: return "에이블테라퓨틱스"
    if "기억담기" in txt or "브레인핏" in txt: return "기억산책(구 씨투몬스터)"
    if "간편치매체크" in txt: return "경기도"
    if "피오" in txt: return "단양군 치매안심센터"
    if "워크온" in txt: return "스왈라비"
    if "효돌" in txt: return "효돌"
    if "다솜" in txt or "원더풀플랫폼" in txt: return "원더풀플랫폼"
    if "미스터마인드" in txt: return "미스터마인드"
    if "행복커넥트" in txt: return "행복커넥트(SKT)"
    if re.search(r"클로바|케어콜", txt): return "네이버"
    if "맬리" in txt: return "원메딕스"
    if s == "치매예방 교구·교재 구매" or v == "다수 납품업체": return None
    if g["출처"] != "나라장터":
        if v and not v.startswith("미기재"): return v.split("·")[0].strip() if len(v) > 20 else v
        return re.split(r"\s*[\(（]", s)[0].strip()
    v2 = re.sub(r"주식회사|\(주\)|㈜|유한회사|사단법인|재단법인|\s+", "", v)
    return v2 or None

def units_of(sd, sg):
    sg = OLD.get(sd, {}).get(sg, sg)
    if sd == "세종": return ["세종시"]
    if sg == "광역": return []
    out = []
    for tok in re.split(r"[·/,]|\s+", sg):
        tok = tok.strip()
        hit = [x for x in MASTER.get(sd, []) if tok and (x == tok or x.startswith(tok))]
        if hit: out.append(hit[0])
    return sorted(set(out))

NOT_COG = r"실종|스마트\s*태그|안심밴드|CCTV|NVR|태블릿 PC|연구\s*용역|연구용역|원료|초등|코딩로봇|전문가 양성|인식개선|디지털타운|건강돌봄|주거환경|미션 성공물품"
def kind_of(name):
    if re.search(r"앱|어플|플랫폼|계정코드", name): return "앱·플랫폼"
    if re.search(r"교구|교재|재료|색칠북|컬러링북|워크북|꾸러미|용품|책자|물품|기억찾기", name): return "교구·재료"
    if re.search(r"장비|시스템|VR|기기|전산화|스마트미러|스마트케어|SET", name): return "인지재활 장비"
    if re.search(r"용역|프로그램", name): return "대면·위탁 프로그램"
    return "교구·재료"
B = {}
for g in data:
    b = brand(g)
    if not b: continue
    kinds = []
    if g["유형"] == "인지훈련·치매예방":
        if g["출처"] == "나라장터":
            g = dict(g); g["계약"] = [c for c in g["계약"] if not re.search(NOT_COG, c[1]) and kind_of(c[1]) != "교구·재료"]
            if not g["계약"]: continue
            kinds = [kind_of(c[1]) for c in g["계약"]]
        else:
            txt = g["서비스"]
            kinds = ["치매 검사" if re.search(r"체크|검사", txt) else "로봇·스피커" if re.search(r"로봇|스피커", txt) else "앱·플랫폼"]
    e = B.setdefault(b, dict(name=b, types=defaultdict(int), kinds=defaultdict(int), units=set(), wide=set(), amt=0, n=0, last="", items=[]))
    for k in kinds: e["kinds"][k] += 1
    e["types"][g["유형"]] += 1
    us = units_of(g["시도"], g["시군구"])
    if not us: e["wide"].add(g["시도"])
    for u in us: e["units"].add((g["시도"], u))
    region = g["시도"] + " " + (g["시군구"] if us or g["시군구"] != "광역" else "광역")
    if g["출처"] == "나라장터":
        for c in g["계약"]:
            e["amt"] += c[2]; e["n"] += 1; e["last"] = max(e["last"], c[0])
            e["items"].append([region, c[0], c[1], c[2], c[5], "나라장터"])
    else:
        e["last"] = max(e["last"], str(g["최근"])[:4])
        e["items"].append([region, str(g["최근"]), g["서비스"], 0, g["링크"], "기사"])
# 브레인핏45: 서울시가 만 45세 이상 시민 전체에 제공(손목닥터9988 연동) -> 서울 25개 구 전부로 본다
if "기억산책(구 씨투몬스터)" in B:
    for g in MASTER["서울"]: B["기억산책(구 씨투몬스터)"]["units"].add(("서울", g))
    B["기억산책(구 씨투몬스터)"]["wide"].discard("서울")
out = []
for b, e in B.items():
    t = max(e["types"], key=e["types"].get)
    e["items"].sort(key=lambda x: x[1], reverse=True)
    kd = max(e["kinds"], key=e["kinds"].get) if e["kinds"] else ""
    if "대교" in b: kd = "대면·위탁 프로그램"
    sv = SVC.get(b, ("", ""))
    out.append(dict(name=b, svc=sv[0], svcsrc=sv[1], type=t, kind=kd, ours=(b == "원메딕스"), comp=(t == "인지훈련·치매예방" and b != "원메딕스"), units=sorted(e["units"]), wide=sorted(e["wide"]), amt=e["amt"], n=e["n"], last=e["last"], items=e["items"]))
out.sort(key=lambda x: (-len(x["units"]) - len(x["wide"]), -x["amt"]))
print(len(out), [(o["name"], len(o["units"]), len(o["wide"])) for o in out[:15]])

ORDER = ["서울", "인천", "경기", "강원", "충북", "충남", "세종", "대전", "전북", "광주", "전남", "경북", "대구", "울산", "경남", "부산", "제주"]
html = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="인지훈련·치매예방 경쟁 서비스가 들어간 시·군·구를 회사별로 겹쳐 보는 지도">
<title>경쟁 서비스 지도</title>
<link rel="stylesheet" href="ui.css?v=20261028d">
<style>
.filters{margin-bottom:16px;display:grid;gap:12px}
.frow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tagrow{background:var(--surface-3);padding:4px;border-radius:var(--r-md);gap:4px}
.f{min-height:36px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:var(--r-pill);padding:8px 16px;font-size:var(--fs-sm);font-weight:600;cursor:pointer;transition:background-color var(--dur-micro) var(--ease),color var(--dur-micro) var(--ease)}
.f:hover{background:var(--surface-2)}
.f[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--surface)}
.tagrow .f.tag{flex:1 1 auto;min-height:40px;border:0;border-radius:10px;background:transparent;color:var(--ink-3);font-size:var(--fs-body)}
.tagrow .f.tag:hover{color:var(--ink)}
.tagrow .f.tag[aria-pressed="true"]{background:var(--surface);color:var(--ink);box-shadow:var(--shadow)}
.f.tag small{color:var(--ink-4);margin-left:4px;font-weight:500}
.f.ours[aria-pressed="true"]{background:var(--s0);border-color:var(--s0);color:var(--on-strong)}
.q{min-height:36px;border:1px solid var(--line);background:var(--surface-2);border-radius:var(--r-pill);padding:8px 16px;font-size:var(--fs-sm);color:var(--ink);min-width:0;flex:1 1 160px}
.q::placeholder{color:var(--ink-4)}
.main{display:grid;grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr);gap:16px;align-items:start}
@media (max-width:980px){.main{grid-template-columns:minmax(0,1fr)}}
.box{color:var(--ink);background:var(--surface);border-radius:var(--r-lg);box-shadow:var(--shadow);padding:20px}
.box h2{font-size:var(--fs-md);font-weight:700}
.rank{max-height:78vh;overflow:auto;margin:0 -8px;padding:0 8px}
.row{display:grid;grid-template-columns:20px minmax(0,1fr) auto;gap:12px;align-items:center;width:100%;text-align:left;background:none;border:0;border-top:1px solid var(--line);padding:16px 8px;border-radius:var(--r-md);cursor:pointer;transition:background-color var(--dur-micro) var(--ease)}
.row:first-child{border-top:0}
.row:hover{background:var(--surface-2)}
.row:active{background:var(--surface-3)}
.row>span{min-width:0}
.row .sw{width:18px;height:18px;border-radius:6px;box-shadow:inset 0 0 0 2px var(--line-2)}
.row[aria-pressed="true"] .sw{box-shadow:none}
.row .nm{font-weight:700;font-size:var(--fs-md);color:var(--ink)}
.sv{font-size:var(--fs-cap);font-weight:700;color:var(--brand);background:var(--brand-soft);border-radius:6px;padding:2px 8px;margin-left:8px;white-space:nowrap}
.sv.d{font-weight:600;color:var(--ink-3);background:var(--surface-2);box-shadow:inset 0 0 0 1px var(--line-2)}
.row .tp{font-size:var(--fs-cap);color:var(--ink-4);margin-left:8px;font-weight:500}
.row .mt{display:flex;font-size:var(--fs-sm);color:var(--ink-4);margin-top:2px}
.row .ct{text-align:right;font-size:var(--fs-cap);color:var(--ink-4);white-space:nowrap}
.row .ct b{display:block;font-size:var(--fs-lg);font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}
.bar{height:6px;border-radius:3px;background:var(--surface-3);margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:3px;background:var(--line-2)}
.sel h3{font-size:var(--fs-md);font-weight:700;margin:24px 0 4px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.sel h3 .swatch{width:12px;height:12px;border-radius:4px;display:inline-block}
.sel .meta{font-size:var(--fs-sm);color:var(--ink-3);margin-bottom:8px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 8px}
.chip{font-size:var(--fs-cap);border-radius:6px;padding:4px 8px;background:var(--surface-2);color:var(--ink-2);min-height:0;border:0;cursor:default;font-weight:500}
.chip b{font-weight:700;margin-right:4px}
.sel details{font-size:var(--fs-sm)}
.sel summary{cursor:pointer;color:var(--brand-2);font-weight:600;min-height:32px;display:flex;align-items:center}
.ci{border-top:1px solid var(--line);padding:12px 0;color:var(--ink-2)}
.ci .d{color:var(--ink-4);font-variant-numeric:tabular-nums}
.ci a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line-2);text-underline-offset:3px}
.ci a:hover{color:var(--brand-2)}
.ci b{font-variant-numeric:tabular-nums}
.toast{position:fixed;left:50%;bottom:24px;transform:translate(-50%,16px);background:var(--ink);color:var(--surface);padding:12px 20px;border-radius:var(--r-md);font-size:var(--fs-sm);font-weight:600;opacity:0;pointer-events:none;transition:opacity var(--dur-short) var(--ease),transform var(--dur-short) var(--ease);z-index:7;box-shadow:var(--shadow-pop)}
.toast.on{opacity:1;transform:translate(-50%,0)}
.empty{color:var(--ink-4);font-size:var(--fs-sm);padding:12px 0}
</style></head><body>
<header class="topbar"><div class="topbar-in"><a class="wordmark" href="status.html">맬리브레인 <span>B2G</span></a><nav class="tabsnav" aria-label="지도 메뉴"><a href="status.html">전체 현황</a><a href="vendors.html" aria-current="page">경쟁 서비스</a><a href="sales.html" class="soon">영업 지도<small>준비 중</small></a></nav></div></header>
<main class="page">
<div class="pagehead"><h1>경쟁 서비스 지도</h1><p>우리와 경쟁하는 인지훈련 서비스(앱, 인지재활 장비, 대면 프로그램)가 들어간 시·군·구입니다. 최대 8개까지 골라 우리와 겹쳐 볼 수 있습니다.</p><div class="asof"><span>데이터 기준 <b>__ASOF__</b></span><span>나라장터 최근 계약일 __LATEST__</span><a class="refresh" href="https://github.com/butblank-oss/meli.brain/actions/workflows/b2g-refresh.yml" target="_blank" rel="noopener" title="GitHub에서 Run workflow를 누르면 그 시점 기준으로 나라장터를 다시 불러와 3~5분 뒤 이 화면에 반영됩니다">최신 데이터 불러오기</a></div></div>
<div class="filters" id="filters"></div>
<div class="main">
  <section class="box"><h2>들어간 시·군·구 순위</h2><p class="hint">누르는 대로 지도에 더해지고(최대 8개), 다시 누르면 빠집니다.</p><div class="rank" id="rank"></div></section>
  <section class="box"><h2>지도</h2><p class="hint">진한 색은 시·군·구 계약, 옅은 색은 시·도 단위 계약, 검정은 고른 서비스가 겹친 곳입니다.</p><div id="kmap"></div><div class="legend" id="legend"></div><div class="sel" id="sel"></div></section>
</div>
<ul class="foot">
<li><b>서비스명</b>: 초록 칸은 앱 마켓과 기사로 확인한 제품명, 회색 칸은 제품명을 못 찾아 나라장터 계약명에서 딴 이름입니다.</li>
<li><b>브레인핏45</b>: 서울시가 만 45세 이상 시민 전체에 제공하는 앱(손목닥터9988 연동)이라 서울 25개 구 전체로 표시했습니다. 개발사는 주식회사 기억산책(구 씨투몬스터)입니다.</li>
<li>출처: 나라장터 계약정보(2024.1~2026.10)와 기사, 공식자료. 업체명은 계약 상대방 기준이라 같은 제품을 대리점이 납품한 경우 다른 업체로 잡힐 수 있습니다. 경계: vuski/admdongkor 행정동 경계를 2026년 시·군·구로 합침.</li>
</ul>
</main>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="kmap.js?v=20261028d"></script>
<script>
const V=__DATA__, ORDER=__ORDER__;
const TYPES=["전체","인지훈련·치매예방","걸음·건강관리","AI돌봄·안부","돌봄로봇","스마트경로당"];
const PAL=["var(--s1)","var(--s2)","var(--s3)","var(--s4)","var(--s5)","var(--s6)","var(--s7)","var(--s8)"];
const MAXP=PAL.length; const slot={};
function assign(n){const used=new Set(Object.values(slot));for(let i=0;i<MAXP;i++){if(!used.has(i)){slot[n]=i;return true}}return false}
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const man=n=>!n?"-":n>=1e8?(n/1e8).toFixed(1).replace(/\.0$/,"")+"억 원":Math.round(n/1e4).toLocaleString()+"만 원";
let mode="comp", type="전체", kind="앱·플랫폼", showOne=false, q="", KM=null;
const byName=Object.fromEntries(V.map(v=>[v.name,v]));
const OURS=V.find(v=>v.ours);
const COMP=V.filter(v=>v.comp), OTHER=V.filter(v=>!v.comp&&!v.ours);
const KORD=["앱·플랫폼","인지재활 장비","대면·위탁 프로그램","치매 검사","로봇·스피커"];
const KINDS=[...KORD.filter(k=>COMP.some(v=>v.kind===k)),...[...new Set(COMP.map(v=>v.kind).filter(k=>k&&!KORD.includes(k)))],"전체"];
let picked=COMP.filter(v=>v.kind==="앱·플랫폼").slice(0,8).map(v=>v.name), showOurs=!!OURS;
picked.forEach(n=>assign(n));
const color=n=>OURS&&n===OURS.name?"var(--s0)":PAL[slot[n]??picked.indexOf(n)];
function flash(m){const t=document.getElementById("toast");t.textContent=m;t.classList.add("on");clearTimeout(flash.t);flash.t=setTimeout(()=>t.classList.remove("on"),2600)}
function shown(){return [...(showOurs&&OURS?[OURS.name]:[]),...picked]}
function list(){
  if(mode==="comp") return COMP.filter(v=>(kind==="전체"||v.kind===kind)&&(!q||v.name.includes(q)));
  return OTHER.filter(v=>(type==="전체"||v.type===type)&&(showOne||v.units.length+v.wide.length>=2||picked.includes(v.name))&&(!q||v.name.includes(q)));
}
function filters(){
  const el=document.getElementById("filters");
  const TAGS=TYPES.filter(t=>t!=="전체");
  const main=TAGS.map(t=>{const n=t==="인지훈련·치매예방"?COMP.length:OTHER.filter(v=>v.type===t).length;
    return `<button class="f tag ${t==="인지훈련·치매예방"?"primary":""}" data-t="${t}" aria-pressed="${(mode==="comp"&&t==="인지훈련·치매예방")||(mode==="other"&&t===type)}">${t} <small>${n}</small></button>`}).join("");
  const sub = mode==="comp"
    ? KINDS.map(t=>`<button class="f" data-k="${t}" aria-pressed="${t===kind}">${t}</button>`).join("")+(OURS?`<button class="f ours" id="ours" aria-pressed="${showOurs}">우리(원메딕스 맬리브레인) 같이 보기</button>`:"")
    : `<button class="f" id="one" aria-pressed="${showOne}">1곳만 들어간 곳도 보기</button>`+(OURS?`<button class="f ours" id="ours" aria-pressed="${showOurs}">우리(원메딕스 맬리브레인) 같이 보기</button>`:"");
  el.innerHTML=`<div class="frow tagrow">${main}</div><div class="frow">${sub}<input class="q" id="q" placeholder="업체·서비스 이름 찾기" value="${esc(q)}"></div>`;
  el.querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>{const t=b.dataset.t; const m=t==="인지훈련·치매예방"?"comp":"other";
    if(m===mode&&(m==="comp"||t===type)) return; mode=m; type=t; q="";
    if(m==="comp") kind="앱·플랫폼"; picked=(m==="comp"?COMP.filter(v=>v.kind==="앱·플랫폼"):OTHER.filter(v=>v.type===t)).slice(0,m==="comp"?8:1).map(v=>v.name); for(const k in slot) delete slot[k]; picked.forEach(n=>assign(n)); render()});
  el.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{kind=b.dataset.k;render()});
  const o=el.querySelector("#one"); if(o) o.onclick=()=>{showOne=!showOne;render()};
  const u=el.querySelector("#ours"); if(u) u.onclick=()=>{showOurs=!showOurs;render()};
  const i=el.querySelector("#q"); i.oninput=()=>{q=i.value.trim();rank()};
}
function rank(){
  const ls=list(), mx=Math.max(1,...ls.map(v=>v.units.length+v.wide.length));
  document.getElementById("rank").innerHTML=ls.map(v=>{const on=picked.includes(v.name);
    const tag=mode==="comp"?v.kind:v.type;
    return `<button class="row" data-n="${esc(v.name)}" aria-pressed="${on}"><span class="sw" style="${on?`background:${color(v.name)}`:""}"></span>
    <span><span class="nm">${esc(v.name)}</span>${v.svc?`<span class="sv ${v.svcsrc==="계약명"?"d":""}" title="${v.svcsrc==="계약명"?"제품명을 확인하지 못해 계약명에서 딴 이름":"서비스명"}">${esc(v.svc)}</span>`:""}<span class="tp">${esc(tag)}</span><div class="mt ms">${v.n?`<span>계약 ${v.n}건</span><span>${man(v.amt)}</span><span>최근 ${esc(v.last)}</span>`:`<span>기사·공식자료</span><span>${esc(v.last)}</span>`}</div><div class="bar"><i style="width:${(v.units.length+v.wide.length)/mx*100}%;${on?`background:${color(v.name)}`:""}"></i></div></span>
    <span class="ct"><b>${v.units.length}곳</b>${v.wide.length?`시·도 단위 ${v.wide.length}곳 더`:""}</span></button>`}).join("")||'<p class="empty">해당하는 서비스가 없습니다.</p>';
  document.querySelectorAll(".row").forEach(b=>b.onclick=()=>{const n=b.dataset.n;
    if(picked.includes(n)){ picked=picked.filter(x=>x!==n); delete slot[n]; }
    else if(picked.length>=MAXP){ flash(`한 번에 ${MAXP}개까지 볼 수 있습니다. 하나를 빼고 다시 골라 주세요.`); return; }
    else { assign(n); picked.push(n) }
    rank();sel();KM&&KM.paint()});
}
function hits(sd,sgg){return shown().filter(n=>byName[n].units.some(u=>u[0]===sd&&u[1]===sgg))}
function wides(sd){return shown().filter(n=>byName[n].wide.includes(sd))}
function sel(){
  document.getElementById("legend").innerHTML=shown().map(n=>`<span><i style="background:${color(n)}"></i>${esc(n)}</span>`).join("")+(shown().length>1?`<span><i style="background:var(--ov)"></i>겹침</span>`:"");
  document.getElementById("sel").innerHTML=shown().length?shown().map(n=>{const v=byName[n];
    const bySd={}; v.units.forEach(([sd,g])=>(bySd[sd] ||= []).push(g));
    return `<h3><span class="swatch" style="background:${color(n)}"></span>${esc(n)}${v.svc?` <span class="sv ${v.svcsrc==="계약명"?"d":""}">${esc(v.svc)}</span>`:""}${v.ours?" (우리)":""}</h3><div class="meta ms"><span>${esc(v.comp||v.ours?v.kind:v.type)}</span><span>시·군·구 ${v.units.length}곳</span>${v.wide.length?`<span>시·도 단위 ${v.wide.map(esc).join(", ")}</span>`:""}${v.n?`<span>계약 ${v.n}건, ${man(v.amt)}</span>`:""}</div>
    <div class="chips">${ORDER.filter(sd=>bySd[sd]).map(sd=>`<span class="chip"><b>${sd}</b> ${bySd[sd].map(esc).join(", ")}</span>`).join("")}</div>
    <details><summary>계약·기사 ${v.items.length}건 보기</summary>${v.items.map(it=>`<div class="ci"><span class="d">${esc(it[1])}</span> ${esc(it[0])}<br>${it[4]?`<a href="${esc(it[4])}" target="_blank" rel="noopener">${esc(it[2])}</a>`:esc(it[2])} ${it[3]?`<b>${man(it[3])}</b>`:`<span class="d">${esc(it[5])}</span>`}</div>`).join("")}</details>`}).join(""):'<p class="empty">왼쪽에서 서비스를 고르세요.</p>';
}
function mapInit(){
  KM=KMap.create(document.getElementById("kmap"),{geo:window.__GEO,order:ORDER,
    fill:(sd,sgg)=>{const h=hits(sd,sgg); if(h.length>1) return {fill:"var(--ov)"}; if(h.length) return {fill:color(h[0])};
      const w=wides(sd); if(w.length) return {fill:`color-mix(in srgb,${color(w[0])} 22%,var(--surface))`}; return {fill:"var(--none)"}},
    sdTip:sd=>{const c=shown().map(n=>`${esc(n)}: ${byName[n].units.filter(u=>u[0]===sd).length}곳${byName[n].wide.includes(sd)?" (시·도 단위 포함)":""}`);return `<b>${sd}</b>${c.length?"<br>"+c.join("<br>"):""}<br><span style="opacity:.75">눌러서 확대</span>`},
    tip:(sd,sgg)=>{const all=V.filter(v=>v.units.some(u=>u[0]===sd&&u[1]===sgg)).map(v=>v.name);const h=hits(sd,sgg);
      return `<b>${esc(sd)} ${esc(sgg)}</b>${h.length?"<br>고른 서비스: "+h.map(esc).join(", "):""}<br><span style="opacity:.8">이곳 전체: ${all.length?all.slice(0,6).map(esc).join(", ")+(all.length>6?` 외 ${all.length-6}`:""):"없음"}</span>`}});
}
function render(){filters();rank();sel();KM&&KM.paint()}
render();
fetch("sgg.geo.json?v=20261028d").then(r=>r.json()).then(g=>{window.__GEO=g;mapInit()});
</script></body></html>"""
html = html.replace("__ASOF__", _ao["asof"]).replace("__LATEST__", _latest).replace("__DATA__", json.dumps(out, ensure_ascii=False)).replace("__ORDER__", json.dumps(ORDER, ensure_ascii=False))
open(sys.argv[1], "w", encoding="utf-8").write(html)
print("ok", len(html))
