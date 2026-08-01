#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "newsletter/server.py"
SITE = ROOT / "site.js"
ARTICLE = ROOT / "clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html"
VERSION = "20260801-poll-results-1"


def patch_server() -> None:
    text = SERVER.read_text(encoding="utf-8")
    if "# BEGIN POLL_RESULTS_API" in text:
        return

    text = text.replace(
        "import hashlib,json,os,secrets,smtplib,sqlite3,sys,traceback",
        "import hashlib,json,os,re,secrets,smtplib,sqlite3,sys,traceback",
        1,
    )

    old_db_tail = """ c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_day ON pageviews(day)')
 c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_path ON pageviews(path)')
 return c
"""
    new_db_tail = """ c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_day ON pageviews(day)')
 c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_path ON pageviews(path)')
 c.execute('''CREATE TABLE IF NOT EXISTS poll_votes(id INTEGER PRIMARY KEY,poll_id TEXT NOT NULL,choice TEXT NOT NULL,visitor_hash TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(poll_id,visitor_hash))''')
 c.execute('CREATE INDEX IF NOT EXISTS idx_poll_votes_poll ON poll_votes(poll_id)')
 migrate_legacy_poll_votes(c)
 return c
"""
    if old_db_tail not in text:
        raise SystemExit("Nelze najít konec inicializace databáze")
    text = text.replace(old_db_tail, new_db_tail, 1)

    api = r'''
# BEGIN POLL_RESULTS_API
def valid_poll_token(value,max_length=80):
 token=str(value or '').strip().lower()
 return token if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,%d}'%(max_length-1),token) else ''


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


def poll_visitor_hash(env,poll_id):
 raw=f'{ANALYTICS_SECRET}|poll|{poll_id}|{client_ip(env)}|{env.get("HTTP_USER_AGENT","")[:180]}'
 return hashlib.sha256(raw.encode()).hexdigest()[:32]


def poll_results_payload(c,poll_id):
 rows=c.execute('SELECT choice,COUNT(*) FROM poll_votes WHERE poll_id=? GROUP BY choice ORDER BY choice',(poll_id,)).fetchall()
 counts={str(choice):int(count) for choice,count in rows}
 return {'ok':True,'pollId':poll_id,'total':sum(counts.values()),'counts':counts}


def poll_results(env,start):
 try:
  poll_id=valid_poll_token(parse_qs(env.get('QUERY_STRING','')).get('poll',[''])[0])
  if not poll_id:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Chybí platné ID ankety.'},ensure_ascii=False))
  c=db();payload=poll_results_payload(c,poll_id);c.close()
  return response(start,'200 OK',json.dumps(payload,ensure_ascii=False))
 except Exception as exc:
  log_error('POLL_RESULTS',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False},ensure_ascii=False))


def poll_vote(env,start):
 try:
  data=read_json(env)
  poll_id=valid_poll_token(data.get('pollId'));choice=valid_poll_token(data.get('choice'),40)
  if not poll_id or not choice:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Neplatný hlas.'},ensure_ascii=False))
  now=datetime.now(timezone.utc).isoformat();vhash=poll_visitor_hash(env,poll_id);c=db()
  existing=c.execute('SELECT choice FROM poll_votes WHERE poll_id=? AND visitor_hash=?',(poll_id,vhash)).fetchone()
  accepted=existing is None
  selected=choice if accepted else str(existing[0])
  if accepted:
   c.execute('INSERT INTO poll_votes(poll_id,choice,visitor_hash,created_at) VALUES(?,?,?,?)',(poll_id,choice,vhash,now));c.commit()
  payload=poll_results_payload(c,poll_id);payload.update({'accepted':accepted,'selected':selected});c.close()
  return response(start,'200 OK',json.dumps(payload,ensure_ascii=False))
 except Exception as exc:
  log_error('POLL_VOTE',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False},ensure_ascii=False))
# END POLL_RESULTS_API

'''
    marker = "\ndef smtp_configured():"
    if marker not in text:
        raise SystemExit("Nelze najít místo pro API ankety")
    text = text.replace(marker, "\n" + api + "def smtp_configured():", 1)

    old_routes = """ if path=='/analytics/pageview' and method=='POST':return analytics_pageview(env,start)
 if path=='/analytics/summary' and method=='GET':return analytics_summary(start)
"""
    new_routes = """ if path=='/analytics/pageview' and method=='POST':return analytics_pageview(env,start)
 if path=='/analytics/summary' and method=='GET':return analytics_summary(start)
 if path=='/poll/results' and method=='GET':return poll_results(env,start)
 if path=='/poll/vote' and method=='POST':return poll_vote(env,start)
"""
    if old_routes not in text:
        raise SystemExit("Nelze najít směrování analytiky")
    text = text.replace(old_routes, new_routes, 1)
    SERVER.write_text(text, encoding="utf-8")


def patch_site() -> None:
    text = SITE.read_text(encoding="utf-8")
    start = text.find("  // Ankety jsou obsluhované z externího skriptu")
    end = text.find("  // U článků se statickými reklamami", start)
    if start < 0 or end < 0:
        raise SystemExit("Nelze najít blok ankety v site.js")

    block = r'''  // Ankety jsou obsluhované z externího skriptu, aby fungovaly i při blokování inline JavaScriptu.
  // Hlas se ukládá samostatně a veřejné průběžné výsledky se načítají ze serveru.
  const pollVoteEndpoint = '/api/newsletter/poll/vote';
  const pollResultsEndpoint = '/api/newsletter/poll/results';

  if (!document.getElementById('nk-poll-results-style')) {
    const style = document.createElement('style');
    style.id = 'nk-poll-results-style';
    style.textContent = `
      .poll-results{margin-top:20px;padding-top:18px;border-top:1px solid #d9e0e3}
      .poll-results[hidden]{display:none}
      .poll-results-head{display:flex;justify-content:space-between;gap:16px;align-items:baseline;margin-bottom:13px;color:#20313a}
      .poll-results-head strong{font:800 20px Georgia,serif}
      .poll-results-total{font-size:13px;color:#667780;font-weight:700}
      .poll-result-row{margin:0 0 13px}
      .poll-result-meta{display:flex;justify-content:space-between;gap:14px;margin-bottom:5px;font-size:14px;line-height:1.4}
      .poll-result-label{color:#20313a;font-weight:800}
      .poll-result-value{color:#667780;white-space:nowrap}
      .poll-result-track{height:10px;overflow:hidden;border-radius:999px;background:#e7ecee}
      .poll-result-fill{height:100%;width:0;border-radius:inherit;background:#9f2626;transition:width .35s ease}
      .poll-results-status{margin:8px 0 0!important;color:#73818a;font-size:12px!important}
    `;
    document.head.appendChild(style);
  }

  document.querySelectorAll('[data-poll-id]').forEach((section) => {
    if (section.dataset.pollBound === '1') return;
    section.dataset.pollBound = '1';

    const pollId = section.getAttribute('data-poll-id') || 'poll';
    const storageKey = `nk-poll-${pollId}`;
    const buttons = Array.from(section.querySelectorAll('[data-poll-vote]'));
    const message = section.querySelector('.poll-message');
    const options = section.querySelector('.poll-options');
    let sending = false;

    const choices = buttons.map((button) => ({
      key: button.getAttribute('data-poll-vote') || '',
      label: (button.textContent || '').trim(),
    })).filter((item) => item.key);

    const results = document.createElement('div');
    results.className = 'poll-results';
    results.hidden = true;
    results.setAttribute('aria-live', 'polite');
    results.innerHTML = `
      <div class="poll-results-head">
        <strong>Průběžné výsledky</strong>
        <span class="poll-results-total" data-poll-total></span>
      </div>
      ${choices.map((item) => `
        <div class="poll-result-row" data-poll-result="${item.key}">
          <div class="poll-result-meta">
            <span class="poll-result-label">${item.label}</span>
            <span class="poll-result-value">0 hlasů · 0 %</span>
          </div>
          <div class="poll-result-track"><div class="poll-result-fill"></div></div>
        </div>
      `).join('')}
      <p class="poll-results-status">Načítáme aktuální výsledky…</p>
    `;
    if (options) options.after(results);
    else section.appendChild(results);

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
        if (button.getAttribute('data-poll-vote') === vote) {
          button.style.borderColor = '#9f2626';
          button.style.background = '#fff4f4';
        }
      });
    };

    const setUnlocked = () => {
      buttons.forEach((button) => {
        button.disabled = false;
        button.style.borderColor = '';
        button.style.background = '';
      });
    };

    const voteWord = (count) => count === 1 ? 'hlas' : (count >= 2 && count <= 4 ? 'hlasy' : 'hlasů');

    const renderResults = (payload) => {
      const counts = payload && payload.counts ? payload.counts : {};
      const total = Number(payload && payload.total) || 0;
      const totalEl = results.querySelector('[data-poll-total]');
      if (totalEl) totalEl.textContent = `${total} ${voteWord(total)} celkem`;
      choices.forEach((item) => {
        const count = Number(counts[item.key]) || 0;
        const percent = total > 0 ? Math.round((count / total) * 100) : 0;
        const row = results.querySelector(`[data-poll-result="${item.key}"]`);
        if (!row) return;
        const value = row.querySelector('.poll-result-value');
        const fill = row.querySelector('.poll-result-fill');
        if (value) value.textContent = `${count} ${voteWord(count)} · ${percent} %`;
        if (fill) fill.style.width = `${percent}%`;
      });
      const status = results.querySelector('.poll-results-status');
      if (status) status.textContent = total > 0 ? 'Výsledky se aktualizují průběžně.' : 'Zatím nebyl odevzdán žádný hlas.';
      results.hidden = false;
    };

    const loadResults = async () => {
      try {
        const response = await fetch(`${pollResultsEndpoint}?poll=${encodeURIComponent(pollId)}&t=${Date.now()}`, {
          method: 'GET', cache: 'no-store', credentials: 'same-origin',
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        renderResults(await response.json());
      } catch (_) {
        const status = results.querySelector('.poll-results-status');
        if (status) status.textContent = 'Výsledky se nyní nepodařilo načíst.';
        results.hidden = false;
      }
    };

    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        setLocked(saved);
        setMessage('Děkujeme, váš hlas už byl zaznamenán.');
      }
    } catch (_) {}

    loadResults();

    buttons.forEach((button) => {
      button.addEventListener('click', async (event) => {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (sending) return;
        let saved = '';
        try { saved = localStorage.getItem(storageKey) || ''; } catch (_) {}
        if (saved) {
          setLocked(saved);
          setMessage('Děkujeme, váš hlas už byl zaznamenán.');
          await loadResults();
          return;
        }
        const vote = button.getAttribute('data-poll-vote');
        if (!vote) return;
        sending = true;
        setLocked(vote);
        setMessage('Odesíláme váš hlas…');
        try {
          const response = await fetch(pollVoteEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pollId, choice: vote }),
            keepalive: true,
            credentials: 'same-origin',
          });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const payload = await response.json();
          const selected = payload.selected || vote;
          try { localStorage.setItem(storageKey, selected); } catch (_) {}
          setLocked(selected);
          setMessage(payload.accepted === false
            ? 'Z tohoto zařízení už byl hlas zaznamenán. Zobrazujeme aktuální výsledky.'
            : 'Děkujeme, váš hlas byl zaznamenán.');
          renderResults(payload);
        } catch (_) {
          setUnlocked();
          setMessage('Hlas se nyní nepodařilo odeslat. Zkuste to prosím znovu.', 'error');
          await loadResults();
        }
        sending = false;
      }, true);
    });

    window.setInterval(() => {
      if (!document.hidden) loadResults();
    }, 30000);
  });

'''
    SITE.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    text = text.replace(
        "Hlasujte podle informací, které jsou nyní veřejně dostupné. Výsledky čtenářské ankety později zveřejníme.",
        "Hlasujte podle informací, které jsou nyní veřejně dostupné. Průběžné výsledky se zobrazují hned pod možnostmi.",
        1,
    )
    text, site_count = re.subn(
        r'<script src="/site\.js(?:\?v=[^"]+)?" defer></script>',
        f'<script src="/site.js?v={VERSION}" defer></script>',
        text,
        count=1,
    )
    text, analytics_count = re.subn(
        r'<script src="/analytics\.js(?:\?v=[^"]+)?" defer></script>',
        f'<script src="/analytics.js?v={VERSION}" defer></script>',
        text,
        count=1,
    )
    if site_count != 1 or analytics_count != 1:
        raise SystemExit("Nelze verzovat skripty v článku")
    ARTICLE.write_text(text, encoding="utf-8")


def main() -> None:
    patch_server()
    patch_site()
    patch_article()
    print("Živé výsledky ankety byly připraveny.")


if __name__ == "__main__":
    main()
