#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "newsletter/server.py"
SITE = ROOT / "site.js"
TUSIMICE_ARTICLE = ROOT / "clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html"
TUSIMICE_DRAFT = ROOT / ".github/drafts/jaderne-tusimice-smr-voda-doprava-eia-2026.html"
GREENERY_PREP = ROOT / "scripts/prepare_greenery_publication_20260801.py"
VERSION = "20260801-poll-system-v3"
START = "# BEGIN POLL_RESULTS_API"
END = "# END POLL_RESULTS_API"

SERVER_API = r'''# BEGIN POLL_RESULTS_API
def valid_poll_token(value,max_length=80):
 token=str(value or '').strip().lower()
 return token if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,%d}'%(max_length-1),token) else ''


def poll_cookie(env):
 raw=str(env.get('HTTP_COOKIE') or '')
 for part in raw.split(';'):
  name,sep,value=part.strip().partition('=')
  if sep and name=='nk_poll_device' and re.fullmatch(r'[A-Za-z0-9_-]{20,120}',value):return value
 return ''


def poll_cookie_header(value):
 return ('Set-Cookie',f'nk_poll_device={value}; Path=/; Max-Age=31536000; SameSite=Lax; Secure; HttpOnly')


def migrate_legacy_poll_votes(c):
 try:
  rows=c.execute("SELECT path,day,visitor_hash,created_at FROM pageviews WHERE path LIKE '/anketa/%/%'").fetchall()
  for path,day,old_hash,created_at in rows:
   parts=str(path or '').strip('/').split('/')
   if len(parts)!=3 or parts[0]!='anketa':continue
   poll_id=valid_poll_token(parts[1]);choice=valid_poll_token(parts[2],40)
   if not poll_id or not choice:continue
   legacy_raw=f'legacy|{day}|{old_hash}'
   legacy_hash=hashlib.sha256(legacy_raw.encode()).hexdigest()[:32]
   c.execute('INSERT OR IGNORE INTO poll_votes(poll_id,choice,visitor_hash,created_at) VALUES(?,?,?,?)',(poll_id,choice,legacy_hash,created_at or datetime.now(timezone.utc).isoformat()))
  c.commit()
 except Exception as exc:
  log_error('POLL_MIGRATION',exc)


def poll_visitor_hash(env,poll_id,device):
 if device:
  raw=f'{ANALYTICS_SECRET}|poll-cookie|{poll_id}|{device}'
 else:
  raw=f'{ANALYTICS_SECRET}|poll-fallback|{poll_id}|{client_ip(env)}|{env.get("HTTP_USER_AGENT","")[:180]}'
 return hashlib.sha256(raw.encode()).hexdigest()[:32]


def poll_results_payload(c,poll_id,selected=''):
 rows=c.execute('SELECT choice,COUNT(*) FROM poll_votes WHERE poll_id=? GROUP BY choice ORDER BY choice',(poll_id,)).fetchall()
 counts={str(choice):int(count) for choice,count in rows}
 total=sum(counts.values())
 percentages={choice:(round(count*100/total,1) if total else 0) for choice,count in counts.items()}
 payload={'ok':True,'pollId':poll_id,'total':total,'counts':counts,'percentages':percentages,'updatedAt':datetime.now(timezone.utc).isoformat()}
 if selected:payload['selected']=selected
 return payload


def poll_results(env,start):
 try:
  poll_id=valid_poll_token(parse_qs(env.get('QUERY_STRING','')).get('poll',[''])[0])
  if not poll_id:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Chybí platné ID ankety.'},ensure_ascii=False))
  device=poll_cookie(env);c=db();selected=''
  if device:
   vhash=poll_visitor_hash(env,poll_id,device)
   row=c.execute('SELECT choice FROM poll_votes WHERE poll_id=? AND visitor_hash=?',(poll_id,vhash)).fetchone()
   if row:selected=str(row[0])
  payload=poll_results_payload(c,poll_id,selected);c.close()
  return response(start,'200 OK',json.dumps(payload,ensure_ascii=False))
 except Exception as exc:
  log_error('POLL_RESULTS',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Výsledky se nepodařilo načíst.'},ensure_ascii=False))


def poll_vote(env,start):
 try:
  data=read_json(env);poll_id=valid_poll_token(data.get('pollId'));choice=valid_poll_token(data.get('choice'),40)
  if not poll_id or not choice:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Neplatný hlas.'},ensure_ascii=False))
  device=poll_cookie(env);extra=[]
  if not device:
   device=secrets.token_urlsafe(32);extra=[poll_cookie_header(device)]
  now=datetime.now(timezone.utc).isoformat();vhash=poll_visitor_hash(env,poll_id,device);c=db()
  existing=c.execute('SELECT choice FROM poll_votes WHERE poll_id=? AND visitor_hash=?',(poll_id,vhash)).fetchone()
  accepted=existing is None;selected=choice if accepted else str(existing[0])
  if accepted:
   c.execute('INSERT INTO poll_votes(poll_id,choice,visitor_hash,created_at) VALUES(?,?,?,?)',(poll_id,choice,vhash,now));c.commit()
  payload=poll_results_payload(c,poll_id,selected);payload['accepted']=accepted;c.close()
  return response(start,'200 OK',json.dumps(payload,ensure_ascii=False),extra=extra)
 except sqlite3.IntegrityError:
  return response(start,'409 Conflict',json.dumps({'ok':False,'message':'Hlas už byl zaznamenán.'},ensure_ascii=False))
 except Exception as exc:
  log_error('POLL_VOTE',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Hlas se nepodařilo uložit.'},ensure_ascii=False))
# END POLL_RESULTS_API'''

SITE_BLOCK = r'''  // Ankety Naše Kadaň: samostatné ukládání hlasů a veřejné průběžné výsledky.
  const pollVoteEndpoint = '/api/newsletter/poll/vote';
  const pollResultsEndpoint = '/api/newsletter/poll/results';

  if (!document.getElementById('nk-poll-results-style')) {
    const style = document.createElement('style');
    style.id = 'nk-poll-results-style';
    style.textContent = `
      .poll-results{display:block;margin-top:20px;padding-top:18px;border-top:1px solid #d9e0e3}
      .poll-results-head{display:flex;justify-content:space-between;gap:16px;align-items:baseline;margin-bottom:13px;color:#20313a}
      .poll-results-head strong{font:800 20px Georgia,serif}
      .poll-results-total{font-size:13px;color:#667780;font-weight:800}
      .poll-result-row{margin:0 0 13px}
      .poll-result-meta{display:flex;justify-content:space-between;gap:14px;margin-bottom:5px;font-size:14px;line-height:1.4}
      .poll-result-label{color:#20313a;font-weight:800}
      .poll-result-value{color:#667780;white-space:nowrap;font-weight:800}
      .poll-result-track{height:11px;overflow:hidden;border-radius:999px;background:#e7ecee}
      .poll-result-fill{height:100%;width:0;border-radius:inherit;background:#9f2626;transition:width .35s ease}
      .poll-results-status{margin:8px 0 0!important;color:#73818a;font-size:12px!important}
      .poll-results-error{color:#8e2525!important}
    `;
    document.head.appendChild(style);
  }

  document.querySelectorAll('[data-poll-id]').forEach((section) => {
    if (section.dataset.pollBound === '2') return;
    section.dataset.pollBound = '2';
    const pollId = section.getAttribute('data-poll-id') || 'poll';
    const storageKey = `nk-poll-${pollId}`;
    const buttons = Array.from(section.querySelectorAll('[data-poll-vote]'));
    const message = section.querySelector('.poll-message');
    const options = section.querySelector('.poll-options');
    let sending = false;
    const choices = buttons.map((button) => ({key: button.getAttribute('data-poll-vote') || '',label: (button.textContent || '').trim()})).filter((item) => item.key);

    const results = document.createElement('div');
    results.className = 'poll-results';
    results.setAttribute('aria-live', 'polite');
    results.innerHTML = `<div class="poll-results-head"><strong>Průběžné výsledky</strong><span class="poll-results-total" data-poll-total>Načítáme…</span></div>${choices.map((item) => `<div class="poll-result-row" data-poll-result="${item.key}"><div class="poll-result-meta"><span class="poll-result-label">${item.label}</span><span class="poll-result-value">0 hlasů · 0 %</span></div><div class="poll-result-track"><div class="poll-result-fill"></div></div></div>`).join('')}<p class="poll-results-status">Načítáme aktuální počet hlasů…</p>`;
    if (options) options.after(results); else section.appendChild(results);

    const setMessage = (value, type = 'success') => {
      if (!message) return;
      message.textContent = value;
      message.style.background = type === 'error' ? '#fff0f0' : '#eaf4ed';
      message.style.color = type === 'error' ? '#8e2525' : '#245d36';
      message.classList.add('show');
    };
    const setLocked = (vote) => {
      buttons.forEach((button) => {
        button.disabled = true;
        const selected = button.getAttribute('data-poll-vote') === vote;
        button.style.borderColor = selected ? '#9f2626' : '';
        button.style.background = selected ? '#fff4f4' : '';
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
    };
    const setUnlocked = () => buttons.forEach((button) => {button.disabled=false;button.style.borderColor='';button.style.background='';button.setAttribute('aria-pressed','false');});
    const voteWord = (count) => count === 1 ? 'hlas' : (count >= 2 && count <= 4 ? 'hlasy' : 'hlasů');

    const renderResults = (payload) => {
      const counts = payload && payload.counts ? payload.counts : {};
      const percentages = payload && payload.percentages ? payload.percentages : {};
      const total = Number(payload && payload.total) || 0;
      const totalEl = results.querySelector('[data-poll-total]');
      if (totalEl) totalEl.textContent = `${total} ${voteWord(total)} celkem`;
      choices.forEach((item) => {
        const count = Number(counts[item.key]) || 0;
        const percent = Number.isFinite(Number(percentages[item.key])) ? Number(percentages[item.key]) : (total > 0 ? Math.round((count / total) * 1000) / 10 : 0);
        const row = results.querySelector(`[data-poll-result="${item.key}"]`);
        if (!row) return;
        const value = row.querySelector('.poll-result-value');
        const fill = row.querySelector('.poll-result-fill');
        if (value) value.textContent = `${count} ${voteWord(count)} · ${String(percent).replace('.', ',')} %`;
        if (fill) fill.style.width = `${Math.max(0,Math.min(100,percent))}%`;
      });
      const status = results.querySelector('.poll-results-status');
      if (status) {status.classList.remove('poll-results-error');status.textContent = total > 0 ? 'Výsledky se aktualizují průběžně.' : 'Zatím nebyl odevzdán žádný hlas.';}
      // POLL_SERVER_AUTHORITATIVE_V3: cookie a databáze jsou jediný zdroj pravdy.
      if (payload && payload.selected) {
        try { localStorage.setItem(storageKey, payload.selected); } catch (_) {}
        setLocked(payload.selected);
        setMessage('Děkujeme, váš hlas už byl zaznamenán.');
      } else {
        // Starší nefunkční anketa mohla uložit pouze localStorage bez serverového hlasu.
        // Takový záznam nesmí blokovat nové hlasování.
        try { localStorage.removeItem(storageKey); } catch (_) {}
        setUnlocked();
        if (message && /Ověřujeme dřívější hlas|už byl zaznamenán/.test(message.textContent || '')) {
          message.classList.remove('show');
        }
      }
    };

    const loadResults = async () => {
      try {
        const response = await fetch(`${pollResultsEndpoint}?poll=${encodeURIComponent(pollId)}&t=${Date.now()}`, {method:'GET',cache:'no-store',credentials:'same-origin'});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        if (!payload || payload.ok !== true) throw new Error('invalid_payload');
        renderResults(payload);
      } catch (_) {
        const status = results.querySelector('.poll-results-status');
        if (status) {status.textContent='Výsledky se nyní nepodařilo načíst. Hlasování můžete zkusit znovu za chvíli.';status.classList.add('poll-results-error');}
        const totalEl = results.querySelector('[data-poll-total]');
        if (totalEl) totalEl.textContent='Dočasně nedostupné';
      }
    };

    // Lokální záznam je pouze nápověda; tlačítka uzamkne až potvrzení serveru.
    try {
      if (localStorage.getItem(storageKey)) setMessage('Ověřujeme dřívější hlas…');
    } catch (_) {}
    loadResults();

    buttons.forEach((button) => {
      button.addEventListener('click', async (event) => {
        event.preventDefault();event.stopImmediatePropagation();
        if (sending) return;
        // Hlas vždy posíláme serveru. Duplicitní hlas bezpečně odmítne databáze podle cookie.
        const vote=button.getAttribute('data-poll-vote');if(!vote)return;
        sending=true;setLocked(vote);setMessage('Odesíláme váš hlas…');
        try{
          const response=await fetch(pollVoteEndpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pollId,choice:vote}),keepalive:true,credentials:'same-origin'});
          const payload=await response.json().catch(()=>null);
          if(!response.ok||!payload||payload.ok!==true)throw new Error(`HTTP ${response.status}`);
          const selected=payload.selected||vote;try{localStorage.setItem(storageKey,selected);}catch(_){}
          setLocked(selected);setMessage(payload.accepted===false?'Z tohoto zařízení už byl hlas zaznamenán. Zobrazujeme aktuální výsledky.':'Děkujeme, váš hlas byl zaznamenán.');renderResults(payload);
        }catch(_){setUnlocked();setMessage('Hlas se nyní nepodařilo odeslat. Zkuste to prosím znovu.','error');await loadResults();}
        sending=false;
      }, true);
    });
    window.setInterval(() => {if(!document.hidden)loadResults();},20000);
  });

'''


def ensure_imports(text: str) -> str:
    text = text.replace("import hashlib,json,os,secrets,smtplib,sqlite3,sys,traceback", "import hashlib,json,os,re,secrets,smtplib,sqlite3,sys,traceback", 1)
    return text


def patch_server() -> None:
    text = ensure_imports(SERVER.read_text(encoding="utf-8"))
    if "CREATE TABLE IF NOT EXISTS poll_votes" not in text:
        marker = " c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_path ON pageviews(path)')\n"
        addition = marker + " c.execute('''CREATE TABLE IF NOT EXISTS poll_votes(id INTEGER PRIMARY KEY,poll_id TEXT NOT NULL,choice TEXT NOT NULL,visitor_hash TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(poll_id,visitor_hash))''')\n c.execute('CREATE INDEX IF NOT EXISTS idx_poll_votes_poll ON poll_votes(poll_id)')\n migrate_legacy_poll_votes(c)\n"
        if marker not in text: raise RuntimeError("Nelze najít inicializaci databáze.")
        text = text.replace(marker, addition, 1)
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), SERVER_API, text, count=1, flags=re.S)
    else:
        marker = "\ndef smtp_configured():"
        if marker not in text: raise RuntimeError("Nelze vložit API ankety.")
        text = text.replace(marker, "\n" + SERVER_API + "\n\ndef smtp_configured():", 1)
    routes = " if path=='/analytics/summary' and method=='GET':return analytics_summary(start)\n"
    if "path=='/poll/results'" not in text:
        if routes not in text: raise RuntimeError("Nelze doplnit směrování ankety.")
        text = text.replace(routes, routes + " if path=='/poll/results' and method=='GET':return poll_results(env,start)\n if path=='/poll/vote' and method=='POST':return poll_vote(env,start)\n", 1)
    SERVER.write_text(text, encoding="utf-8")


def patch_site() -> None:
    text = SITE.read_text(encoding="utf-8")
    start = text.find("  // Ankety jsou obsluhované z externího skriptu")
    if start < 0: start = text.find("  // Ankety Naše Kadaň:")
    end = text.find("  // U článků se statickými reklamami", start)
    if start < 0 or end < 0: raise RuntimeError("Nelze najít blok ankety v site.js.")
    SITE.write_text(text[:start] + SITE_BLOCK + text[end:], encoding="utf-8")


def remove_legacy_poll_script(text: str) -> str:
    pattern = re.compile(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', re.I | re.S)
    def clean(match: re.Match[str]) -> str:
        body = match.group(1)
        return "" if "/api/analytics/pageview" in body and "data-poll-vote" in body else match.group(0)
    return pattern.sub(clean, text)


def patch_article(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0: return
    text = remove_legacy_poll_script(path.read_text(encoding="utf-8"))
    text = text.replace("Výsledky čtenářské ankety později zveřejníme.", "Průběžné počty hlasů a procenta se zobrazují hned pod možnostmi.")
    text = text.replace("Funkční hlasování se připojí při zveřejnění článku.", "Po hlasování se ihned zobrazí aktuální počty hlasů a procenta.")
    replacement = f'<script src="/site.js?v={VERSION}" defer></script>'
    text, count = re.subn(r'<script src="/site\.js(?:\?v=[^"]+)?" defer></script>', replacement, text, count=1)
    if count == 0 and "</body>" in text: text = text.replace("</body>", replacement + "\n</body>", 1)
    path.write_text(text, encoding="utf-8")


def patch_greenery_prepare() -> None:
    text = GREENERY_PREP.read_text(encoding="utf-8")
    if "POLL_SYSTEM_V2" not in text:
        text = text.replace('EXPECTED = "Sedm centimetrů je smluvní minimum jedné konkrétní lokality"\n', f'EXPECTED = "Sedm centimetrů je smluvní minimum jedné konkrétní lokality"\nPOLL_VERSION = "{VERSION}"  # POLL_SYSTEM_V2\n', 1)
        needle = "    text = read_source()\n"
        insertion = '''    text = read_source()\n    legacy = re.compile(r'<script(?![^>]*\\bsrc=)[^>]*>(.*?)</script>', re.I | re.S)\n    text = legacy.sub(lambda m: '' if '/api/analytics/pageview' in m.group(1) and 'data-poll-vote' in m.group(1) else m.group(0), text)\n    text = text.replace('Funkční hlasování se připojí při zveřejnění článku.', 'Po hlasování se ihned zobrazí aktuální počty hlasů a procenta.')\n    site_tag = f'<script src="/site.js?v={POLL_VERSION}" defer></script>'\n    text, site_count = re.subn(r'<script src="/site\\.js(?:\\?v=[^"]+)?" defer></script>', site_tag, text, count=1)\n    if site_count == 0:\n        text = text.replace('</body>', site_tag + '\\n</body>', 1)\n'''
        if needle not in text: raise RuntimeError("Nelze upravit sestavení článku o sečení.")
        text = text.replace(needle, insertion, 1)
        text = text.replace('        "/api/analytics/pageview",\n', '        f"/site.js?v={POLL_VERSION}",\n', 1)
        validation = "    if \"noindex,nofollow\" in text:\n        raise RuntimeError(\"Veřejný článek zůstal noindex.\")\n"
        text = text.replace(validation, validation + "    if \"/api/analytics/pageview\" in text:\n        raise RuntimeError(\"Ve článku zůstal starý nefunkční skript ankety.\")\n", 1)
    GREENERY_PREP.write_text(text, encoding="utf-8")


def main() -> None:
    patch_server();patch_site();patch_article(TUSIMICE_ARTICLE);patch_article(TUSIMICE_DRAFT);patch_greenery_prepare()
    print(f"Hlasovací systém {VERSION} je připraven.")


if __name__ == "__main__":
    main()
