from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / '.github/drafts/cisarsky-den-kadan-historie-2026.html').read_text(encoding='utf-8')
script_path = ROOT / 'scripts/publish_cisarsky_den_20260804.py'
runner_path = ROOT / 'scripts/run_publish_cisarsky_den_20260804.py'
script = script_path.read_text(encoding='utf-8')

spec = importlib.util.spec_from_file_location('cisarsky_den_runner', runner_path)
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runner)
effective = runner.patch_source(script)

assert 'Císařský den v Kadani' in source
assert 'noindex,nofollow,noarchive' in source
assert 'Kadaň znovu vítá císaře' in effective
assert '10:00–22:00 · vstup zdarma' in effective
assert 'Vstup na Císařský den 2026 je zdarma.' in effective
assert all(t in effective for t in ('14:00', '14:30', '18:00'))
assert 'Hru spustíme 12. srpna v 18:00' in effective

# Teaser hry před 12. srpnem nesmí obsahovat aktivní odkaz.
teaser = re.search(r'<section class="game-cta">.*?</section>', effective, re.S)
assert teaser, 'Publikační skript neobsahuje očekávaný teaser hry.'
assert 'href="/hry/prijezd-karla-iv/"' not in teaser.group(0)

# Vstup zdarma je povinný údaj, zatímco předčasný odkaz hry zůstává zakázaný.
required = re.search(r'required=\[(.*?)\]', effective, re.S)
forbidden = re.search(r'forbidden=\[(.*?)\]', effective, re.S)
assert required and "'vstup zdarma'" in required.group(1)
assert forbidden and "'vstup zdarma'" not in forbidden.group(1)
assert "'href=\"/hry/prijezd-karla-iv/\"'" in forbidden.group(1)
assert 'VSTUP ZDARMA' in effective
assert '2026, 8, 4, 18, 0' in effective
assert '--dry-run' in effective and 'EXPECTED_GENERATED' in effective
assert re.search(r'index,follow,max-image-preview:large', effective)

print('Statická kontrola publikačního balíčku prošla.')
