#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_monitoring_registry import canonical_url, fold  # noqa: E402
from monitor_kadansko_unified import (  # noqa: E402
    local_matches,
    meaningful_title,
    normalized_title,
    semantic_title_key,
    source_terms,
)


class MonitoringFiltersTest(unittest.TestCase):
    def test_canonical_url_removes_volatile_parameters(self) -> None:
        self.assertEqual(
            canonical_url("https://www.2zskadan.cz/download/37576/?tmstv=1785546498&utm_source=x"),
            "https://www.2zskadan.cz/download/37576",
        )

    def test_download_counter_does_not_change_title(self) -> None:
        self.assertEqual(
            normalized_title("Rozpočet školy 2026 (staženo 1291790× )"),
            "Rozpočet školy 2026",
        )

    def test_navigation_titles_are_suppressed(self) -> None:
        source = {"rules": {"ignoreTitlePatterns": [r"^prezentace$"]}, "requiresLocalMatch": False}
        self.assertFalse(meaningful_title("Přeskočit na obsah", source))
        self.assertFalse(meaningful_title("Prezentace", source))

    def test_person_name_is_suppressed_for_broad_media(self) -> None:
        source = {"rules": {}, "requiresLocalMatch": True}
        self.assertFalse(meaningful_title("Jan Beneš", source))

    def test_prunerov_fire_passes_local_match(self) -> None:
        registry = {"coverage": {"scopeMunicipalities": ["Kadaň", "Klášterec nad Ohří"]}}
        terms = source_terms(registry)
        item = {"title": "Požár lesa u Prunéřova", "description": "Zasahovalo osm jednotek", "url": "https://example.cz/prunerov"}
        self.assertIn("prunerov", local_matches(item, terms))

    def test_unrelated_hrensko_event_does_not_match(self) -> None:
        registry = {"coverage": {"scopeMunicipalities": ["Kadaň", "Klášterec nad Ohří"]}}
        terms = source_terms(registry)
        item = {"title": "Sucho v Hřensku", "description": "Kamenice má nízký průtok", "url": "https://example.cz/hrensko"}
        self.assertEqual(local_matches(item, terms), [])

    def test_semantic_title_ignores_publisher_suffix(self) -> None:
        self.assertEqual(
            semantic_title_key("Požár lesa u Prunéřova - Chomutovský deník"),
            semantic_title_key("Požár lesa u Prunéřova"),
        )

    def test_supplement_contains_all_orp_municipalities(self) -> None:
        payload = json.loads((ROOT / "data" / "monitoring-supplemental-sources.json").read_text(encoding="utf-8"))
        municipalities = [x["name"] for x in payload["scope"]["municipalities"]]
        self.assertEqual(len(municipalities), 19)
        self.assertIn("Kadaň", municipalities)
        self.assertIn("Loučná pod Klínovcem", municipalities)
        self.assertIn("Račetice", municipalities)

    def test_fold_diacritics(self) -> None:
        self.assertEqual(fold("Úřední deska"), "uredni deska")


if __name__ == "__main__":
    unittest.main()
