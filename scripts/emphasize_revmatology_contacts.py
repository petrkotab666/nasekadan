#!/usr/bin/env python3
from pathlib import Path

path = Path('clanky/nova-revmatologicka-ambulance-kadan-podzim-2026.html')
text = path.read_text(encoding='utf-8')

style = ".contact-box{background:#fff4ef;border:2px solid #9f2626;border-radius:18px;padding:22px 24px;margin:26px 0}.contact-box h2{margin:0 0 14px;font-size:28px}.contact-box p{margin:7px 0}.contact-box a{font-weight:800;color:#9f2626;text-decoration:underline;text-underline-offset:3px}"
if '.contact-box{' not in text:
    text = text.replace('.source-list{', style + '.source-list{', 1)

block = '''<section class="contact-box" data-revmatologie-contact>
<h2>Objednání a kontakt</h2>
<p><strong>Telefon:</strong> <a href="tel:+420739359468">739 359 468</a></p>
<p><strong>E-mail:</strong> <a href="mailto:revmakadan@centrum.cz">revmakadan@centrum.cz</a></p>
<p><strong>Adresa ambulance:</strong> kpt. Jaroše 609, Kadaň</p>
<p><strong>Lékaři:</strong> MUDr. Vlastimil Novotný a MUDr. Lenka Rokytová</p>
<p><strong>Nové pacienty přijímají už nyní.</strong> Přesný termín otevření a ordinační hodiny zatím zveřejněné nejsou.</p>
</section>'''

if 'data-revmatologie-contact' not in text:
    marker = '<div class="hero-visual">'
    text = text.replace(marker, block + '\n' + marker, 1)

text = text.replace('content="2026-07-29T20:47:00+02:00">\n<script type="application/ld+json">', 'content="2026-07-29T21:17:00+02:00">\n<script type="application/ld+json">', 1)
text = text.replace('"dateModified":"2026-07-29T20:47:00+02:00"', '"dateModified":"2026-07-29T21:17:00+02:00"')

path.write_text(text, encoding='utf-8', newline='\n')
print('Kontakty Revmatologie Kadaň byly zvýrazněny.')
