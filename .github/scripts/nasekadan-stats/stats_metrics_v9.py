#!/usr/bin/env python3
from __future__ import annotations

import re
import statistics
from typing import Any

import stats_metrics_v6 as v6
import stats_metrics_v7 as v7

LIMIT = 200


def _age(item: dict[str, Any]) -> tuple[float, str, float]:
    if item.get("historical"):
        return 999999.0, "bez data", 0.0
    published = item["published"]
    seconds = max(0.0, (v6.now_local() - published).total_seconds())
    days = seconds / 86400.0
    if seconds < 3600:
        label = "< 1 h"
    elif seconds < 86400:
        label = f"{max(1, round(seconds / 3600))} h"
    else:
        label = f"{max(1, round(days))} d"
    views = int(item.get("views", 0) or 0)
    return days, label, views / max(days, 1 / 24)


def _performance(rate: float, median_rate: float, historical: bool) -> tuple[str, str]:
    if historical:
        return "bez data", "neutral"
    baseline = max(median_rate, 0.01)
    if rate >= baseline * 2:
        return "výrazně silný", "hot"
    if rate >= baseline:
        return "nad mediánem", "good"
    if rate >= baseline * 0.5:
        return "běžný", "normal"
    return "slabší", "low"


def render_articles_200() -> str:
    items = v7.latest_published_articles(LIMIT)
    persisted = v6.read_persisted()
    pages = v6.normalize_counter(persisted.get("pages"))
    site_views = int((persisted.get("total") or {}).get("views", 0) or 0)

    prepared: list[dict[str, Any]] = []
    rates: list[float] = []
    for item in items:
        row = dict(item)
        row["views"] = int(pages.get(row["path"], row.get("views", 0)) or 0)
        row["age_days"], row["age_text"], row["rate"] = _age(row)
        if not row.get("historical"):
            rates.append(float(row["rate"]))
        prepared.append(row)

    median_rate = statistics.median(rates) if rates else 0.0
    total = sum(int(row["views"]) for row in prepared)
    average = total / len(prepared) if prepared else 0.0
    median_views = statistics.median([int(row["views"]) for row in prepared]) if prepared else 0.0
    max_views = max((int(row["views"]) for row in prepared), default=1) or 1

    rows: list[str] = []
    for original_rank, row in enumerate(prepared, 1):
        historical = bool(row.get("historical"))
        published = row["published"]
        published_text = "historický záznam" if historical else published.strftime("%d.%m.%Y %H:%M")
        published_date = "" if historical else published.strftime("%Y-%m-%d")
        published_ts = 0 if historical else int(published.timestamp())
        views = int(row["views"])
        rate = float(row["rate"])
        share_site = views / site_views * 100 if site_views else 0.0
        perf_text, perf_class = _performance(rate, median_rate, historical)
        bar = views / max_views * 100 if views else 0.0
        title = str(row["title"])
        path = str(row["path"])
        search = f"{title} {path}".lower()
        rows.append(
            f'<tr data-original-rank="{original_rank}" data-search="{v6.esc(search)}" '
            f'data-published="{published_ts}" data-published-date="{published_date}" '
            f'data-age="{float(row["age_days"]):.6f}" data-views="{views}" '
            f'data-rate="{rate:.6f}" data-share="{share_site:.6f}" data-historical="{1 if historical else 0}">'
            '<td class="rank js-rank"></td>'
            f'<td class="pub">{v6.esc(published_text)}</td>'
            f'<td class="age">{v6.esc(row["age_text"])}</td>'
            f'<td class="article"><a href="{v6.esc(path)}" target="_blank" rel="noopener"><b>{v6.esc(title)}</b></a><small>{v6.esc(path)}</small></td>'
            f'<td class="num views"><b>{v6.fmt(views)}</b><span class="vbar"><i style="width:{bar:.1f}%"></i></span></td>'
            f'<td class="num">{v6.fmt(rate)}</td>'
            '<td class="num js-selection">—</td>'
            f'<td class="num">{share_site:.1f} %</td>'
            f'<td><span class="perf {perf_class}">{v6.esc(perf_text)}</span></td>'
            '</tr>'
        )

    top = max(prepared, key=lambda row: int(row["views"]), default=None)
    top_text = "—" if not top else f'{top["title"]} · {v6.fmt(int(top["views"]))}'
    today = v6.now_local().strftime("%Y-%m-%d")

    return f'''
<section class="panel analytics200" id="poslednich-200-clanku">
  <div class="a200-head"><div><h2>Posledních 200 článků</h2>
  <p class="panel-note"><strong>Sloupec „Zobrazení celkem“ znamená součet od publikace článku.</strong>
  Filtry Dnes / 7 / 30 / 90 dní vybírají články podle data vydání, nikoli návštěvnost za toto období.
  Aktuálně je dostupných {len(prepared)} článků.</p></div>
  <button type="button" id="a200-export">Export CSV</button></div>
  <div class="a200-summary">
    <div><small>Článků ve výběru</small><strong id="a200-count">{len(prepared)}</strong><span>maximum 200</span></div>
    <div><small>Zobrazení ve výběru</small><strong id="a200-total">{v6.fmt(total)}</strong><span>celkem od publikace</span></div>
    <div><small>Průměr / článek</small><strong id="a200-average">{v6.fmt(average)}</strong><span>aktuální výběr</span></div>
    <div><small>Medián / článek</small><strong id="a200-median">{v6.fmt(median_views)}</strong><span>bez zkreslení špičkou</span></div>
    <div class="wide"><small>Nejsledovanější ve výběru</small><strong id="a200-top">{v6.esc(top_text)}</strong></div>
  </div>
  <div class="a200-tools">
    <label class="grow"><span>Hledat</span><input id="a200-search" type="search" placeholder="Název nebo adresa článku…"></label>
    <div><span>Počet</span><nav id="a200-limits"><button data-limit="25">25</button><button data-limit="50">50</button><button data-limit="100">100</button><button data-limit="200" class="active">200</button></nav></div>
    <div><span>Vydáno</span><nav id="a200-periods"><button data-period="all" class="active">Vše</button><button data-period="today">Dnes</button><button data-period="7">7 dní</button><button data-period="30">30 dní</button><button data-period="90">90 dní</button></nav></div>
    <label><span>Řazení</span><select id="a200-sort"><option value="newest">Nejnovější</option><option value="views">Nejvíce zobrazení</option><option value="rate">Nejvyšší tempo</option><option value="share">Nejvyšší podíl webu</option><option value="oldest">Nejstarší</option><option value="lowest">Nejméně zobrazení</option></select></label>
    <label class="check"><input id="a200-zero" type="checkbox"> Skrýt bez zobrazení</label>
  </div>
  <div class="table-wrap"><table id="articles-200"><thead><tr><th>#</th><th>Publikováno</th><th>Stáří</th><th>Článek</th><th class="num">Zobrazení celkem</th><th class="num">Průměr / den</th><th class="num">Podíl výběru</th><th class="num">Podíl webu</th><th>Výkon</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
  <p class="a200-note">Průměr za den je tempo vypočtené z celkových zobrazení a času od publikace. U nových článků se rychle mění. Výkon se porovnává s mediánem tempa dostupných článků.</p>
  <script>window.NK_A200_TODAY={today!r};</script>
</section>'''


CSS = '''
.analytics200{{scroll-margin-top:12px}}.a200-head{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}}.a200-head h2{{font-size:24px}}#a200-export{{border:0;border-radius:10px;padding:10px 14px;background:var(--accent);color:#fff;font:inherit;font-weight:750;cursor:pointer;white-space:nowrap}}.a200-summary{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:16px 0}}.a200-summary>div{{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:13px;min-width:0}}.a200-summary small{{display:block;color:var(--muted);font-size:12px}}.a200-summary strong{{display:block;font-size:23px;line-height:1.15;margin:4px 0;overflow:hidden;text-overflow:ellipsis}}.a200-summary span{{font-size:11px;color:var(--muted)}}.a200-summary .wide{{grid-column:span 2}}.a200-summary .wide strong{{font-size:15px;white-space:nowrap}}.a200-tools{{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin:15px 0}}.a200-tools label,.a200-tools>div{{display:flex;flex-direction:column;gap:5px}}.a200-tools label>span,.a200-tools>div>span{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:700}}.a200-tools .grow{{flex:1 1 270px}}.a200-tools input[type=search]{{width:100%}}.a200-tools select{{padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff;font:inherit}}.a200-tools nav{{display:flex;border:1px solid var(--line);border-radius:10px;overflow:hidden}}.a200-tools nav button{{border:0;border-right:1px solid var(--line);background:#fff;padding:9px 10px;font:inherit;cursor:pointer}}.a200-tools nav button:last-child{{border-right:0}}.a200-tools nav button.active{{background:var(--accent);color:#fff;font-weight:750}}.a200-tools .check{{flex-direction:row;align-items:center;padding:9px 0}}#articles-200 th{{position:sticky;top:0;z-index:2}}#articles-200 tr[hidden]{{display:none}}#articles-200 .pub,#articles-200 .age{{white-space:nowrap;color:var(--muted)}}#articles-200 .article{{min-width:290px}}#articles-200 .views{{min-width:120px}}.vbar{{display:block;height:4px;background:#eee9e2;border-radius:999px;margin-top:5px;overflow:hidden}}.vbar i{{display:block;height:100%;background:var(--accent)}}.perf{{display:inline-block;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:750;white-space:nowrap}}.perf.hot{{background:#f9ded8;color:#8c2c1d}}.perf.good{{background:#e3f1e6;color:#246b38}}.perf.normal{{background:#eee9e2;color:#5f5a53}}.perf.low{{background:#f2ece5;color:#7a6552}}.perf.neutral{{background:#ececec;color:#666}}.a200-note{{font-size:12px;color:var(--muted);margin:12px 0 0}}@media(max-width:900px){{.a200-summary{{grid-template-columns:1fr 1fr}}}}@media(max-width:600px){{.a200-head{{flex-direction:column}}.a200-tools{{align-items:stretch}}.a200-tools>div,.a200-tools label{{width:100%}}.a200-tools nav button{{flex:1;padding:9px 5px}}}}
'''.replace('{{', '{').replace('}}', '}')

JS = r'''
(function(){const table=document.getElementById('articles-200');if(!table)return;const body=table.tBodies[0],rows=[...body.rows],search=document.getElementById('a200-search'),sort=document.getElementById('a200-sort'),zero=document.getElementById('a200-zero'),limits=[...document.querySelectorAll('#a200-limits button')],periods=[...document.querySelectorAll('#a200-periods button')],fmt=new Intl.NumberFormat('cs-CZ',{maximumFractionDigits:1});let limit=200,period='all';const n=(r,k)=>Number(r.dataset[k]||0),med=a=>{if(!a.length)return 0;const s=[...a].sort((x,y)=>x-y),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2},periodOk=r=>period==='all'||(r.dataset.historical!=='1'&&(period==='today'?r.dataset.publishedDate===window.NK_A200_TODAY:n(r,'age')<=Number(period))),cmp=(a,b)=>{if(sort.value==='views')return n(b,'views')-n(a,'views');if(sort.value==='rate')return n(b,'rate')-n(a,'rate');if(sort.value==='share')return n(b,'share')-n(a,'share');if(sort.value==='oldest')return(n(a,'published')||9e15)-(n(b,'published')||9e15);if(sort.value==='lowest')return n(a,'views')-n(b,'views');return n(b,'published')-n(a,'published')};function apply(){const q=search.value.trim().toLowerCase(),visible=[];rows.forEach(r=>{const ok=n(r,'originalRank')<=limit&&periodOk(r)&&(!q||r.dataset.search.includes(q))&&(!zero.checked||n(r,'views')>0);r.hidden=!ok;if(ok)visible.push(r)});visible.sort(cmp);[...visible,...rows.filter(r=>r.hidden)].forEach(r=>body.appendChild(r));visible.forEach((r,i)=>r.querySelector('.js-rank').textContent=i+1);const values=visible.map(r=>n(r,'views')),total=values.reduce((a,b)=>a+b,0);visible.forEach(r=>r.querySelector('.js-selection').textContent=total?(n(r,'views')/total*100).toFixed(1)+' %':'0,0 %');document.getElementById('a200-count').textContent=fmt.format(visible.length);document.getElementById('a200-total').textContent=fmt.format(total);document.getElementById('a200-average').textContent=fmt.format(visible.length?total/visible.length:0);document.getElementById('a200-median').textContent=fmt.format(med(values));const top=visible.reduce((a,r)=>!a||n(r,'views')>n(a,'views')?r:a,null);document.getElementById('a200-top').textContent=top?top.querySelector('.article b').textContent+' · '+fmt.format(n(top,'views')):'—'}limits.forEach(b=>b.onclick=()=>{limit=Number(b.dataset.limit);limits.forEach(x=>x.classList.toggle('active',x===b));apply()});periods.forEach(b=>b.onclick=()=>{period=b.dataset.period;periods.forEach(x=>x.classList.toggle('active',x===b));apply()});search.oninput=sort.onchange=zero.onchange=apply;document.getElementById('a200-export').onclick=()=>{const out=[['Pořadí','Publikováno','Stáří','Článek','Adresa','Zobrazení celkem','Průměr za den','Podíl výběru','Podíl webu','Výkon']];rows.filter(r=>!r.hidden).forEach((r,i)=>out.push([i+1,r.querySelector('.pub').textContent.trim(),r.querySelector('.age').textContent.trim(),r.querySelector('.article b').textContent.trim(),r.querySelector('.article small').textContent.trim(),n(r,'views'),n(r,'rate').toFixed(1),r.querySelector('.js-selection').textContent.trim(),n(r,'share').toFixed(1)+' %',r.querySelector('.perf').textContent.trim()]));const csv='\ufeff'+out.map(a=>a.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\r\n'),blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='nasekadan-poslednich-200-clanku.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)};apply()})();
'''


def install(base: Any) -> None:
    if getattr(v6, "_articles_200_v9_installed", False):
        return
    previous = v6.render

    def render_v9(render_base: Any) -> bytes:
        body = previous(render_base).decode("utf-8", "replace")
        body = re.sub(r'<section class="panel" id="poslednich-25-clanku">.*?</section>', '', body, count=1, flags=re.S)
        body = re.sub(r'<a class="badge neutral" href="#poslednich-25-clanku"[^>]*>.*?</a>', '', body, count=1, flags=re.S)
        section = render_articles_200()
        body = body.replace("</style>", CSS + "</style>", 1)
        marker = '<div class="badges">'
        link = '<a class="badge neutral" href="#poslednich-200-clanku" style="text-decoration:none">↓ Analýza 200 článků</a>'
        if marker in body:
            body = body.replace(marker, marker + link, 1)
        body = body.replace("</header>", "</header>" + section, 1)
        body = body.replace("</main></body></html>", f"<script>{JS}</script></main></body></html>", 1)
        return body.encode("utf-8")

    v6.render = render_v9
    v6.CACHE_AT = None
    v6.CACHE_BODY = b""
    v6._articles_200_v9_installed = True
