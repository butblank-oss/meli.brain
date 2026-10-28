/* 한국 시·군·구 지도 (의존성 없음). KMap.create(el, opts)
   opts: geo, fill(sd,sgg)->{fill,stroke?,cls?}, onSido(sd), onSgg(sd,sgg), tip(sd,sgg)->html */
(function () {
  const K = Math.cos(36 * Math.PI / 180), S = 1000;
  const px = ([lon, lat]) => [lon * K * S, -lat * S];
  function ringPath(r) { let d = ""; r.forEach((c, i) => { const [x, y] = px(c); d += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1); }); return d + "Z"; }
  function geomPath(g) { const polys = g.type === "Polygon" ? [g.coordinates] : g.coordinates; return polys.map(p => p.map(ringPath).join("")).join(""); }
  function bbox(g) {
    let a = [1e9, 1e9, -1e9, -1e9]; const polys = g.type === "Polygon" ? [g.coordinates] : g.coordinates;
    polys.forEach(p => p[0].forEach(c => { const [x, y] = px(c); a[0] = Math.min(a[0], x); a[1] = Math.min(a[1], y); a[2] = Math.max(a[2], x); a[3] = Math.max(a[3], y); }));
    return a;
  }
  // 전국 보기에서 이름이 겹치지 않게 잡은 라벨 위치(경도, 위도)
  const LBL = { "서울": [127.0, 37.5], "인천": [126.3, 37.5], "경기": [127.3, 38.02], "강원": [128.3, 37.65], "충남": [126.75, 36.5], "세종": [127.18, 36.66], "대전": [127.42, 36.3], "충북": [127.78, 36.85], "경북": [128.75, 36.4], "대구": [128.58, 35.86], "울산": [129.28, 35.56], "부산": [129.1, 35.18], "경남": [128.2, 35.3], "전북": [127.1, 35.72], "광주": [126.83, 35.16], "전남": [126.95, 34.78], "제주": [126.55, 33.38] };
  // 확대할 때 먼 섬 때문에 본토가 작아지지 않게 잡은 범위(서경, 남위, 동경, 북위)
  const ZOOM = { "인천": [126.33, 37.22, 126.82, 37.83] };
  const NS = "http://www.w3.org/2000/svg";
  const mk = (t, at) => { const e = document.createElementNS(NS, t); for (const k in at) e.setAttribute(k, at[k]); return e; };
  function create(el, o) {
    const geo = o.geo; el.innerHTML = "";
    const wrap = document.createElement("div"); wrap.className = "kmap";
    const svg = mk("svg", { role: "img", "aria-label": "한국 시·군·구 지도" });
    const gS = mk("g", {}), gD = mk("g", { "pointer-events": "none" }), gL = mk("g", { "pointer-events": "none" });
    svg.append(gS, gD, gL);
    const tip = document.createElement("div"); tip.className = "kmap-tip";
    const back = document.createElement("button"); back.className = "kmap-back"; back.textContent = "← 전국"; back.hidden = true;
    wrap.append(svg, tip, back); el.appendChild(wrap);
    const all = [1e9, 1e9, -1e9, -1e9], sdBox = {};
    geo.sido.forEach(f => { const b = bbox(f.geometry); sdBox[f.properties.sd] = b; all[0] = Math.min(all[0], b[0]); all[1] = Math.min(all[1], b[1]); all[2] = Math.max(all[2], b[2]); all[3] = Math.max(all[3], b[3]); });
    const paths = geo.sgg.map(f => {
      const p = mk("path", { d: geomPath(f.geometry), class: "kmap-sgg" });
      p.__f = f.properties; gS.appendChild(p); return p;
    });
    geo.sido.forEach(f => gD.appendChild(mk("path", { d: geomPath(f.geometry), class: "kmap-sido" })));
    let cur = null, vb = null;
    function setVB(b, pad) {
      const w = b[2] - b[0], h = b[3] - b[1], p = Math.max(w, h) * pad;
      vb = [b[0] - p, b[1] - p, w + 2 * p, h + 2 * p];
      svg.setAttribute("viewBox", vb.map(v => v.toFixed(1)).join(" "));
      svg.style.setProperty("--k", (vb[2] / 1000).toFixed(3));
    }
    function labels() {
      gL.innerHTML = "";
      const fs = vb[2] / (cur ? 34 : 30);
      if (!cur) {
        const f2 = vb[2] / 44;
        geo.sido.forEach(f => {
          const sd = f.properties.sd; const [x, y] = px(LBL[sd] || f.properties.pt);
          const lab = o.sdLabel ? o.sdLabel(sd) : sd; const [a, b] = Array.isArray(lab) ? lab : [lab, ""];
          const t = mk("text", { x, y, class: "kmap-lb sd", "font-size": f2 }); t.textContent = a; gL.appendChild(t);
          if (b) { const u = mk("text", { x, y: y + f2 * 1.05, class: "kmap-lb sub", "font-size": f2 * 0.78 }); u.textContent = b; gL.appendChild(u); }
        });
      } else {
        geo.sgg.filter(f => f.properties.sd === cur).forEach(f => {
          const [x, y] = px(f.properties.pt); const t = mk("text", { x, y, class: "kmap-lb", "font-size": fs });
          t.textContent = cur === "세종" ? "세종" : f.properties.sgg.replace(/(시|군|구)$/, "") || f.properties.sgg; gL.appendChild(t);
        });
      }
    }
    function paint() {
      paths.forEach(p => {
        const { sd, sgg } = p.__f; const c = o.fill(sd, sgg) || {};
        p.style.fill = c.fill || "var(--km-empty)";
        p.setAttribute("class", "kmap-sgg" + (c.cls ? " " + c.cls : "") + (cur && sd !== cur ? " out" : "") + (o.selected && o.selected() === sd + "|" + sgg ? " sel" : ""));
      });
    }
    function zoom(sd) {
      cur = sd || null; back.hidden = !cur;
      const zb = cur && ZOOM[cur] ? (() => { const [a, b] = px([ZOOM[cur][0], ZOOM[cur][3]]), [c, d] = px([ZOOM[cur][2], ZOOM[cur][1]]); return [a, b, c, d]; })() : null;
      setVB(cur ? (zb || sdBox[cur]) : all, cur ? 0.06 : 0.02); paint(); labels();
    }
    back.onclick = () => { zoom(null); o.onSido && o.onSido(null); };
    svg.addEventListener("click", e => {
      const p = e.target.closest(".kmap-sgg"); if (!p) return; const { sd, sgg } = p.__f;
      if (!cur || cur !== sd) { zoom(sd); o.onSido && o.onSido(sd); }
      else o.onSgg && o.onSgg(sd, sgg);
    });
    svg.addEventListener("mousemove", e => {
      const p = e.target.closest(".kmap-sgg"); if (!p) { tip.style.display = "none"; return; }
      const { sd, sgg } = p.__f; tip.innerHTML = o.tip ? o.tip(sd, sgg) : `${sd} ${sgg}`;
      const r = wrap.getBoundingClientRect(); tip.style.display = "block";
      let x = e.clientX - r.left + 12, y = e.clientY - r.top + 12;
      if (x + tip.offsetWidth > r.width) x = e.clientX - r.left - tip.offsetWidth - 12;
      tip.style.left = x + "px"; tip.style.top = y + "px";
    });
    svg.addEventListener("mouseleave", () => tip.style.display = "none");
    zoom(null);
    return { zoom, paint, relabel: labels, get current() { return cur; } };
  }
  window.KMap = { create };
})();
