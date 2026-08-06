#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_gymnastika_kadan_20260806 as publication


def main() -> int:
    if not publication.ARTICLE.is_file():
        raise RuntimeError(f"Chybí hotový článek: {publication.ARTICLE}")
    if not publication.SOCIAL.is_file() or publication.SOCIAL.stat().st_size < 10000:
        raise RuntimeError(f"Chybí hotová sociální grafika: {publication.SOCIAL}")

    # Grafika i článek jsou již součástí hlavní větve. Tento krok proto
    # neimportuje ani neinstaluje Pillow a pouze bezpečně dopočítá textové
    # publikační kanály z aktuálního úplného seznamu článků.
    publication.rebuild_surfaces()
    publication.rebuild_integrity_manifest()
    publication.upsert_registry()
    publication.validate()
    print("Textové kanály článku Gymnastiky Kadaň byly úspěšně přegenerovány.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
