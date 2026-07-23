#!/usr/bin/env python3
from __future__ import annotations
import json, os, secrets, smtplib, sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage
from http import HTTPStatus
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

DB=os.environ.get('NEWSLETTER_DB','/var/lib/nasekadan-newsletter/newsletter.sqlite3')
BASE=os.environ.get('NEWSLETTER_BASE_URL','https://nasekadan.cz')
FROM=os.environ.get('NEWSLETTER_FROM','info@nasekadan.cz')
SMTP_HOST=os.environ.get('SMTP_HOST','')
SMTP_PORT=int(os.environ.get('SMTP_PORT','587'))
SMTP_USER=os.environ.get('SMTP_USER','')
SMTP_PASSWORD=os.environ.get('SMTP_PASSWORD','')
SMTP_TLS=os.environ.get('SMTP_TLS','1')=='1'

def db():
 os.makedirs(os.path.dirname(DB),exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('''CREATE TABLE IF NOT EXISTS subscribers(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,status TEXT NOT NULL,token TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL,confirmed_at TEXT,unsubscribed_at TEXT,ip TEXT,user_agent TEXT)''')
 return c

def send_mail(to,subject,text):
 if not SMTP_HOST: raise RuntimeError('SMTP není nastaveno')
 m=EmailMessage();m['From']=FROM;m['To']=to;m['Subject']=subject;m.set_content(text)
 with smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=30) as s:
  if SMTP_TLS:s.starttls()
  if SMTP_USER:s.login(SMTP_USER,SMTP_PASSWORD)
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
   token=secrets.token_urlsafe(32);now=datetime.now(timezone.utc).isoformat();ip=env.get('HTTP_X_FORWARDED_FOR',env.get('REMOTE_ADDR','')).split(',')[0].strip();ua=env.get('HTTP_USER_AGENT','')[:500]
   c=db();c.execute('INSERT INTO subscribers(email,status,token,created_at,ip,user_agent) VALUES(?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET status="pending",token=excluded.token,created_at=excluded.created_at,confirmed_at=NULL,unsubscribed_at=NULL,ip=excluded.ip,user_agent=excluded.user_agent',(email,'pending',token,now,ip,ua));c.commit();c.close()
   link=f'{BASE}/api/newsletter/confirm?token={token}'
   send_mail(email,'Potvrďte odběr Naše Kadaň',f'Kliknutím potvrďte odběr týdenního přehledu Naše Kadaň:\n\n{link}\n\nPokud jste se nepřihlašovali, zprávu ignorujte.')
   return response(start,'200 OK',json.dumps({'ok':True,'message':'Na e-mail jsme poslali potvrzovací odkaz.'},ensure_ascii=False))
  except Exception as e:return response(start,'500 Internal Server Error',json.dumps({'ok':False,'message':'Přihlášení se nepodařilo. Zkuste to později.'},ensure_ascii=False))
 if path in ('/confirm','/unsubscribe'):
  token=parse_qs(env.get('QUERY_STRING','')).get('token',[''])[0]
  if not token:return response(start,'400 Bad Request','Chybí token.','text/plain; charset=utf-8')
  c=db();row=c.execute('SELECT email FROM subscribers WHERE token=?',(token,)).fetchone()
  if not row:c.close();return response(start,'404 Not Found','Odkaz není platný.','text/plain; charset=utf-8')
  now=datetime.now(timezone.utc).isoformat()
  if path=='/confirm':c.execute('UPDATE subscribers SET status="active",confirmed_at=?,unsubscribed_at=NULL WHERE token=?',(now,token));msg='Odběr je potvrzen. Děkujeme.'
  else:c.execute('UPDATE subscribers SET status="unsubscribed",unsubscribed_at=? WHERE token=?',(now,token));msg='Odběr byl zrušen.'
  c.commit();c.close();return response(start,'200 OK',f'<!doctype html><meta charset="utf-8"><title>Naše Kadaň</title><h1>{msg}</h1><p><a href="/">Zpět na Naše Kadaň</a></p>','text/html; charset=utf-8')
 return response(start,'404 Not Found',json.dumps({'ok':False}))

if __name__=='__main__':
 with make_server('127.0.0.1',8765,app) as s:s.serve_forever()
