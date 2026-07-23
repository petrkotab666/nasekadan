#!/usr/bin/env python3
from __future__ import annotations
import json, os, secrets, smtplib, sqlite3, sys, traceback
from datetime import datetime, timezone
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


def log_error(label,exc):
 print(f'[{datetime.now(timezone.utc).isoformat()}] {label}: {type(exc).__name__}: {exc}',file=sys.stderr,flush=True)
 traceback.print_exc(file=sys.stderr)


def db():
 os.makedirs(os.path.dirname(DB),exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('''CREATE TABLE IF NOT EXISTS subscribers(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,status TEXT NOT NULL,token TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL,confirmed_at TEXT,unsubscribed_at TEXT,ip TEXT,user_agent TEXT)''')
 return c


def send_mail(to,subject,text):
 if not SMTP_HOST: raise RuntimeError('SMTP není nastaveno')
 m=EmailMessage();m['From']=FROM;m['To']=to;m['Subject']=subject;m.set_content(text)
 if SMTP_MODE in {'ssl','smtps','465'}:
  connection=smtplib.SMTP_SSL(SMTP_HOST,SMTP_PORT,timeout=SMTP_TIMEOUT)
 else:
  connection=smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=SMTP_TIMEOUT)
 with connection as s:
  if SMTP_MODE in {'1','true','yes','starttls','tls'}: s.starttls()
  if SMTP_USER: s.login(SMTP_USER,SMTP_PASSWORD)
  s.send_message(m)


def response(start,status,body,ctype='application/json; charset=utf-8'):
 data=body if isinstance(body,bytes) else body.encode('utf-8')
 start(status,[('Content-Type',ctype),('Content-Length',str(len(data))),('Cache-Control','no-store')]);return [data]


def app(env,start):
 path=env.get('PATH_INFO','');method=env.get('REQUEST_METHOD','GET')
 if path=='/health': return response(start,'200 OK',json.dumps({'ok':True}))
 if path=='/subscribe' and method=='POST':
  try:
   raw=env['wsgi.input'].read(int(env.get('CONTENT_LENGTH') or 0)).decode();data=json.loads(raw or '{}');email=str(data.get('email','')).strip().lower();consent=bool(data.get('consent'))
   if '@' not in email or len(email)>254 or not consent:return response(start,'400 Bad Request',json.dumps({'ok':False,'message':'Zkontrolujte e-mail a potvrďte souhlas.'},ensure_ascii=False))
   now=datetime.now(timezone.utc).isoformat();ip=env.get('HTTP_X_FORWARDED_FOR',env.get('REMOTE_ADDR','')).split(',')[0].strip();ua=env.get('HTTP_USER_AGENT','')[:500]
   c=db();existing=c.execute('SELECT status,token FROM subscribers WHERE email=?',(email,)).fetchone()
   if existing and existing[0]=='active':
    c.close();return response(start,'200 OK',json.dumps({'ok':True,'message':'Tento e-mail už je k newsletteru přihlášený.'},ensure_ascii=False))
   token=existing[1] if existing and existing[0]=='pending' else secrets.token_urlsafe(32)
   c.execute('INSERT INTO subscribers(email,status,token,created_at,ip,user_agent) VALUES(?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET status="pending",token=excluded.token,created_at=excluded.created_at,confirmed_at=NULL,unsubscribed_at=NULL,ip=excluded.ip,user_agent=excluded.user_agent',(email,'pending',token,now,ip,ua));c.commit();c.close()
   link=f'{BASE}/api/newsletter/confirm?token={token}'
   send_mail(email,'Potvrďte odběr Naše Kadaň',f'Kliknutím potvrďte odběr týdenního přehledu Naše Kadaň:\n\n{link}\n\nPokud jste se nepřihlašovali, zprávu ignorujte.')
   return response(start,'200 OK',json.dumps({'ok':True,'message':'Na e-mail jsme poslali potvrzovací odkaz.'},ensure_ascii=False))
  except smtplib.SMTPAuthenticationError as exc:
   log_error('SMTP_AUTH',exc)
   return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Odeslání selhalo: Seznam odmítl přihlášení ke schránce.'},ensure_ascii=False))
  except (TimeoutError,OSError,smtplib.SMTPException) as exc:
   log_error('SMTP_CONNECTION',exc)
   return response(start,'502 Bad Gateway',json.dumps({'ok':False,'message':'Poštovní server nyní neodpovídá. Zkuste to znovu za chvíli.'},ensure_ascii=False))
  except Exception as exc:
   log_error('SUBSCRIBE',exc)
   return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Přihlášení se nepodařilo. Zkuste to později.'},ensure_ascii=False))
 if path in ('/confirm','/unsubscribe'):
  token=parse_qs(env.get('QUERY_STRING','')).get('token',[''])[0]
  if not token:return response(start,'400 Bad Request','Chybí token.','text/plain; charset=utf-8')
  c=db();row=c.execute('SELECT email,status FROM subscribers WHERE token=?',(token,)).fetchone()
  if not row:c.close();return response(start,'404 Not Found','Odkaz není platný. Požádejte o nový potvrzovací e-mail.','text/plain; charset=utf-8')
  now=datetime.now(timezone.utc).isoformat()
  if path=='/confirm':
   if row[1]=='active':msg='Odběr už byl potvrzen.'
   else:c.execute('UPDATE subscribers SET status="active",confirmed_at=?,unsubscribed_at=NULL WHERE token=?',(now,token));msg='Odběr je potvrzen. Děkujeme.'
  else:c.execute('UPDATE subscribers SET status="unsubscribed",unsubscribed_at=? WHERE token=?',(now,token));msg='Odběr byl zrušen.'
  c.commit();c.close();return response(start,'200 OK',f'<!doctype html><meta charset="utf-8"><title>Naše Kadaň</title><h1>{msg}</h1><p><a href="/">Zpět na Naše Kadaň</a></p>','text/html; charset=utf-8')
 return response(start,'404 Not Found',json.dumps({'ok':False}))


if __name__=='__main__':
 with make_server('127.0.0.1',8765,app) as s:s.serve_forever()
