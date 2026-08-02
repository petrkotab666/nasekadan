from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'.github/drafts/cisarsky-den-kadan-historie-2026.html').read_text(encoding='utf-8')
script=(ROOT/'scripts/publish_cisarsky_den_20260804.py').read_text(encoding='utf-8')
assert 'Císařský den v Kadani' in source
assert 'noindex,nofollow,noarchive' in source
assert 'Kadaň znovu vítá císaře' in script
assert '10:00–22:00' in script
assert all(t in script for t in ('14:00','14:30','18:00'))
assert 'Hru spustíme 12. srpna v 18:00' in script
assert 'href="/hry/prijezd-karla-iv/"' not in script
assert 'vstup zdarma' not in script.lower()
assert '2026, 8, 4, 18, 0' in script
assert '--dry-run' in script and 'EXPECTED_GENERATED' in script
assert re.search(r'index,follow,max-image-preview:large',script)
print('Statická kontrola publikačního balíčku prošla.')
