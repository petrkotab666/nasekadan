#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,secrets,smtplib,sqlite3,sys,traceback
from datetime import datetime,timezone,timedelta
from email.message import EmailMessage
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

DB=os.environ.get('NEWSLETTER_DB','/var/lib/nasekadan-newsletter/newsletter.sqlite3')
BASE=os.environ.get('NEWSLETTER_BASE_URL','https://nasekadan.cz')
FROM=os.environ.get('NEWSLETTER_FROM','info@nasekadan.cz')
SMTP_HOST=os.environ.get('SMTP_HOST','')
SMTP_PORT=int(os.environ.get('SMTP_PORT','587'))
SMTP_USER=os.environ.get('SMTP_USER','')
SMTP_PASSWORD=os.environ.get('SMTP_PASSWORD','')
SMTP_MODE=os.environ.get('SMTP_TLS','1').strip().lower()
SMTP_TIMEOUT=int(os.environ.get('SMTP_TIMEOUT','12'))
ANALYTICS_SECRET=os.environ.get('ANALYTICS_SECRET','nasekadan-change-me')


class SMTPConfigurationError(RuntimeError):
 pass


def log_error(label,exc):
 print(f'[{datetime.now(timezone.utc).isoformat()}] {label}: {type(exc).__name__}: {exc}',file=sys.stderr,flush=True)
 traceback.print_exc(file=sys.stderr)


def db():
 os.makedirs(os.path.dirname(DB),exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('''CREATE TABLE IF NOT EXISTS subscribers(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,status TEXT NOT NULL,token TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL,confirmed_at TEXT,unsubscribed_at TEXT,ip TEXT,user_agent TEXT)''')
 c.execute('''CREATE TABLE IF NOT EXISTS pageviews(id INTEGER PRIMARY KEY,path TEXT NOT NULL,title TEXT,referrer TEXT,day TEXT NOT NULL,visitor_hash TEXT NOT NULL,created_at TEXT NOT NULL)''')
 c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_day ON pageviews(day)')
 c.execute('CREATE INDEX IF NOT EXISTS idx_pageviews_path ON pageviews(path)')
 c.execute('''CREATE TABLE IF NOT EXISTS poll_votes(id INTEGER PRIMARY KEY,poll_id TEXT NOT NULL,choice TEXT NOT NULL,visitor_hash TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(poll_id,visitor_hash))''')
 c.execute('CREATE INDEX IF NOT EXISTS idx_poll_votes_poll ON poll_votes(poll_id)')
 migrate_legacy_poll_votes(c)
 return c



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

def smtp_configured():
 return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_mail(to,subject,text):
 if not SMTP_HOST: raise SMTPConfigurationError('SMTP server není nastavený')
 if not SMTP_USER: raise SMTPConfigurationError('SMTP uživatel není nastavený')
 if not SMTP_PASSWORD: raise SMTPConfigurationError('SMTP heslo není nastavené')
 m=EmailMessage();m['From']=FROM;m['To']=to;m['Subject']=subject;m.set_content(text)
 connection=smtplib.SMTP_SSL(SMTP_HOST,SMTP_PORT,timeout=SMTP_TIMEOUT) if SMTP_MODE in {'ssl','smtps','465'} else smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=SMTP_TIMEOUT)
 with connection as s:
  if SMTP_MODE in {'1','true','yes','starttls','tls'}:s.starttls()
  s.login(SMTP_USER,SMTP_PASSWORD)
  s.send_message(m)


def response(start,status,body,ctype='application/json; charset=utf-8',extra=None):
 data=body if isinstance(body,bytes) else body.encode('utf-8')
 headers=[('Content-Type',ctype),('Content-Length',str(len(data))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]
 if extra:headers.extend(extra)
 start(status,headers);return [data]


def read_json(env,max_size=8192):
 length=min(int(env.get('CONTENT_LENGTH') or 0),max_size)
 return json.loads(env['wsgi.input'].read(length).decode() or '{}')


def valid_email(value):
 email=str(value or '').strip().lower()
 return email if '@' in email and len(email)<=254 else ''


def client_ip(env):
 return env.get('HTTP_X_FORWARDED_FOR',env.get('REMOTE_ADDR','')).split(',')[0].strip()


def visitor_hash(env,day):
 raw=f'{ANALYTICS_SECRET}|{day}|{client_ip(env)}|{env.get("HTTP_USER_AGENT","")[:180]}'
 return hashlib.sha256(raw.encode()).hexdigest()[:24]


def clean_path(value):
 path=str(value or '/').strip()
 if not path.startswith('/'):path='/'+path
 path=path.split('?')[0].split('#')[0][:300]
 return path if path else '/'


def analytics_pageview(env,start):
 try:
  data=read_json(env);path=clean_path(data.get('path'))
  if path.startswith('/api/') or path.startswith('/navstevnost/'):return response(start,'204 No Content',b'')
  now=datetime.now(timezone.utc);day=now.date().isoformat()
  title=str(data.get('title') or '')[:250];ref=str(data.get('referrer') or '')[:250]
  c=db();c.execute('INSERT INTO pageviews(path,title,referrer,day,visitor_hash,created_at) VALUES(?,?,?,?,?,?)',(path,title,ref,day,visitor_hash(env,day),now.isoformat()))
  cutoff=(now-timedelta(days=180)).isoformat();c.execute('DELETE FROM pageviews WHERE created_at<?',(cutoff,));c.commit();c.close()
  return response(start,'204 No Content',b'')
 except Exception as exc:
  log_error('ANALYTICS_PAGEVIEW',exc);return response(start,'204 No Content',b'')


def analytics_summary(start):
 try:
  today=datetime.now(timezone.utc).date().isoformat();cutoff=(datetime.now(timezone.utc).date()-timedelta(days=29)).isoformat()
  c=db();total=c.execute('SELECT COUNT(*) FROM pageviews').fetchone()[0]
  today_views=c.execute('SELECT COUNT(*) FROM pageviews WHERE day=?',(today,)).fetchone()[0]
  unique_today=c.execute('SELECT COUNT(DISTINCT visitor_hash) FROM pageviews WHERE day=?',(today,)).fetchone()[0]
  top=[{'path':row[0],'views':row[1]} for row in c.execute('SELECT path,COUNT(*) views FROM pageviews WHERE day>=? GROUP BY path ORDER BY views DESC LIMIT 12',(cutoff,)).fetchall()]
  c.close();return response(start,'200 OK',json.dumps({'total':total,'today':today_views,'uniqueToday':unique_today,'topPages':top},ensure_ascii=False))
 except Exception as exc:
  log_error('ANALYTICS_SUMMARY',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False}))


def app(env,start):
 path=env.get('PATH_INFO','');method=env.get('REQUEST_METHOD','GET')
 if path=='/health':
  return response(start,'200 OK',json.dumps({
   'ok':True,
   'smtpConfigured':smtp_configured(),
   'smtpHost':SMTP_HOST or None,
   'smtpPort':SMTP_PORT,
   'smtpMode':SMTP_MODE,
   'smtpUserSet':bool(SMTP_USER),
   'smtpPasswordSet':bool(SMTP_PASSWORD),
  }))
 if path=='/analytics/pageview' and method=='POST':return analytics_pageview(env,start)
 if path=='/analytics/summary' and method=='GET':return analytics_summary(start)
 if path=='/poll/results' and method=='GET':return poll_results(env,start)
 if path=='/poll/vote' and method=='POST':return poll_vote(env,start)

 if path=='/subscribe' and method=='POST':
  try:
   data=read_json(env);email=valid_email(data.get('email'));consent=bool(data.get('consent'))
   if not email or not consent:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Zkontrolujte e-mail a potvrďte souhlas.'},ensure_ascii=False))
   now=datetime.now(timezone.utc).isoformat();ip=client_ip(env);ua=env.get('HTTP_USER_AGENT','')[:500]
   c=db();existing=c.execute('SELECT status,token FROM subscribers WHERE email=?',(email,)).fetchone()
   if existing and existing[0]=='active':c.close();return response(start,'200 OK',json.dumps({'ok':True,'message':'Tento e-mail už je k newsletteru přihlášený.'},ensure_ascii=False))
   token=existing[1] if existing and existing[0]=='pending' else secrets.token_urlsafe(32)
   c.execute('INSERT INTO subscribers(email,status,token,created_at,ip,user_agent) VALUES(?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET status="pending",token=excluded.token,created_at=excluded.created_at,confirmed_at=NULL,unsubscribed_at=NULL,ip=excluded.ip,user_agent=excluded.user_agent',(email,'pending',token,now,ip,ua));c.commit();c.close()
   link=f'{BASE}/api/newsletter/confirm?token={token}'
   send_mail(email,'Potvrďte odběr Naše Kadaň',f'Kliknutím potvrďte odběr týdenního přehledu Naše Kadaň:\n\n{link}\n\nPokud jste se nepřihlašovali, zprávu ignorujte.')
   return response(start,'200 OK',json.dumps({'ok':True,'message':'Na e-mail jsme poslali potvrzovací odkaz.'},ensure_ascii=False))
  except SMTPConfigurationError as exc:
   log_error('SMTP_CONFIG',exc);return response(start,'503 Service Unavailable',json.dumps({'ok':False,'message':'Newsletter zatím nemá na serveru nastavené heslo odesílací schránky.'},ensure_ascii=False))
  except smtplib.SMTPAuthenticationError as exc:
   log_error('SMTP_AUTH',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Odeslání selhalo: uložené heslo odesílací schránky Seznam není platné.'},ensure_ascii=False))
  except (TimeoutError,OSError,smtplib.SMTPException) as exc:
   log_error('SMTP_CONNECTION',exc);return response(start,'502 Bad Gateway',json.dumps({'ok':False,'message':'Poštovní server nyní neodpovídá. Zkuste to znovu za chvíli.'},ensure_ascii=False))
  except Exception as exc:
   log_error('SUBSCRIBE',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Přihlášení se nepodařilo. Zkuste to později.'},ensure_ascii=False))

 if path=='/unsubscribe-request' and method=='POST':
  generic={'ok':True,'message':'Pokud je e-mail v seznamu odběratelů, poslali jsme na něj odkaz pro zrušení odběru.'}
  try:
   email=valid_email(read_json(env).get('email'))
   if not email:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Zadejte platný e-mail.'},ensure_ascii=False))
   c=db();row=c.execute('SELECT token,status FROM subscribers WHERE email=?',(email,)).fetchone();c.close()
   if row and row[1] in {'active','pending'}:
    link=f'{BASE}/api/newsletter/unsubscribe?token={row[0]}';send_mail(email,'Zrušení odběru Naše Kadaň',f'Kliknutím na následující odkaz zrušíte odběr newsletteru Naše Kadaň:\n\n{link}')
   return response(start,'200 OK',json.dumps(generic,ensure_ascii=False))
  except Exception as exc:
   log_error('UNSUBSCRIBE_REQUEST',exc);return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Žádost se nepodařilo odeslat.'},ensure_ascii=False))

 if path in ('/confirm','/unsubscribe'):
  token=parse_qs(env.get('QUERY_STRING','')).get('token',[''])[0]
  if not token:return response(start,'400 Bad Request','Chybí token.','text/plain; charset=utf-8')
  c=db();row=c.execute('SELECT email,status FROM subscribers WHERE token=?',(token,)).fetchone()
  if not row:c.close();return response(start,'404 Not Found','Odkaz není platný.','text/plain; charset=utf-8')
  now=datetime.now(timezone.utc).isoformat()
  if path=='/confirm':
   if row[1]=='active':msg='Odběr už byl potvrzen.'
   else:c.execute('UPDATE subscribers SET status="active",confirmed_at=?,unsubscribed_at=NULL WHERE token=?',(now,token));msg='Odběr je potvrzen. Děkujeme.'
  else:
   if row[1]=='unsubscribed':msg='Odběr už byl zrušen.'
   else:c.execute('UPDATE subscribers SET status="unsubscribed",unsubscribed_at=? WHERE token=?',(now,token));msg='Odběr byl zrušen.'
  c.commit();c.close();return response(start,'200 OK',f'<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Naše Kadaň</title><link rel="stylesheet" href="/style.css"></head><body><main class="wrap section"><h1>{msg}</h1><p><a class="btn" href="/">Zpět na Naše Kadaň</a></p></main></body></html>','text/html; charset=utf-8')
 return response(start,'404 Not Found',json.dumps({'ok':False}))

if __name__=='__main__':
 with make_server('127.0.0.1',8765,app) as s:s.serve_forever()
