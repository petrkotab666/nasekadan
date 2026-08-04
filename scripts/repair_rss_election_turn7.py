#!/usr/bin/env python3
from __future__ import annotations

from email.utils import parsedate_to_datetime
from pathlib import Path
import re
from xml.etree import ElementTree as ET

RSS = Path(__file__).resolve().parents[1] / "rss.xml"
URL = "https://nasekadan.cz/clanky/komunalni-volby-kadan-kandidaty-lhuta-2026.html"
PIN_URL = "https://nasekadan.cz/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html"
TITLE = "Lhůta pro kandidátky skončila. V Kadani se rýsuje souboj ODS, nové skupiny a ANO"
DESCRIPTION = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily celé sestavy, ANO oznámilo podání a Piráti představují své kandidáty."
)
IMAGE = "https://nasekadan.cz/social/komunalni-volby-kadan-kandidaty-lhuta-2026.png"


def item_link(block: str) -> str:
    match = re.search(r"<link>(.*?)</link>", block, flags=re.S)
    return match.group(1).strip() if match else ""


def item_date(block: str):
    match = re.search(r"<pubDate>(.*?)</pubDate>", block, flags=re.S)
    if not match:
        raise RuntimeError(f"Položka RSS bez pubDate: {item_link(block) or 'bez odkazu'}")
    return parsedate_to_datetime(match.group(1).strip())


def main() -> None:
    text = RSS.read_text(encoding="utf-8")
    election_item = f'''    <item>
      <title>{TITLE}</title>
      <description><![CDATA[{DESCRIPTION}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>Tue, 04 Aug 2026 18:46:00 +0200</pubDate>
      <category>Kadaň</category>
      <category>Komunální volby 2026</category>
      <category>Politika</category>
      <category>Volby</category>
      <szn:image><szn:url>{IMAGE}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>'''

    matches = list(re.finditer(r"\s*<item>.*?</item>\s*", text, flags=re.S))
    if not matches:
        raise RuntimeError("RSS neobsahuje žádné položky.")

    prefix = text[: matches[0].start()].rstrip() + "\n"
    suffix = "\n" + text[matches[-1].end() :].lstrip()

    by_link: dict[str, str] = {}
    for match in matches:
        block = match.group(0).strip()
        link = item_link(block)
        if not link:
            raise RuntimeError("RSS obsahuje položku bez odkazu.")
        # Při případné historické duplicitě ponecháme první nalezenou položku.
        by_link.setdefault(link, "    " + block.lstrip())

    # Volební článek doplníme z kanonických metadat a případnou starou verzi nahradíme.
    by_link[URL] = election_item

    blocks = sorted(by_link.values(), key=item_date, reverse=True)
    text = prefix + "\n".join(blocks) + suffix
    text = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        "<lastBuildDate>Tue, 04 Aug 2026 18:46:00 +0200</lastBuildDate>",
        text,
        count=1,
    )
    RSS.write_text(text, encoding="utf-8", newline="\n")

    root = ET.parse(RSS).getroot()
    items = root.findall("./channel/item")
    links = [node.findtext("link") or "" for node in items]
    dates = [parsedate_to_datetime(node.findtext("pubDate") or "") for node in items]
    if not links or links[0] != URL:
        raise RuntimeError(f"Nejnovější volební článek není první: {links[:5]}")
    if len(links) != len(set(links)) or links.count(URL) != 1:
        raise RuntimeError("RSS obsahuje duplicitní odkazy.")
    if dates != sorted(dates, reverse=True):
        raise RuntimeError("RSS není seřazené chronologicky sestupně.")
    if PIN_URL in links and links.index(PIN_URL) == 0:
        raise RuntimeError("Připnutý článek byl chybně přesunut na začátek RSS.")
    print(f"RSS chronologicky opraveno: {len(items)} položek, první {links[0]}")


if __name__ == "__main__":
    main()
