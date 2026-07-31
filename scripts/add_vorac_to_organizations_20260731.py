#!/usr/bin/env python3
from pathlib import Path
import json

path = Path('data/organizations.json')
data = json.loads(path.read_text(encoding='utf-8'))
name = 'Kožní ambulance MUDr. Stanislava Voráče'
item = {
    'name': name,
    'description': 'Soukromá kožní a dermatovenerologická ambulance s pracovišti v Kadani a Klášterci nad Ohří; ordinační doby, dovolené a informace pro pacienty.',
    'address': 'Golovinova 1559, Kadaň; Sadová 528, Klášterec nad Ohří',
    'url': 'https://mudr-vorac.webnode.cz/'
}

group = next((g for g in data.get('groups', []) if g.get('name') == 'Zdravotní, sociální a komunitní služby'), None)
if group is None:
    raise SystemExit('Skupina zdravotních služeb v adresáři chybí.')

if not any(x.get('name') == name for x in group.get('items', [])):
    group.setdefault('items', []).append(item)
    group['items'].sort(key=lambda x: x.get('name', '').casefold())

data['updatedAt'] = '2026-07-31'
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

text = json.dumps(data, ensure_ascii=False)
assert name in text
assert 'https://mudr-vorac.webnode.cz/' in text
print('Kožní ambulance MUDr. Voráče je v adresáři organizací.')
