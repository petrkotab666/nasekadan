#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
from xml.etree import ElementTree as ET

RSS = Path(__file__).resolve().parents[1] / "rss.xml"
URL = "https://nasekadan.cz/clanky/komunalni-volby-kadan-kandidaty-lhuta-2026.html"
TITLE = "Lhůta pro kandidátky skončila. V Kadani se rýsuje souboj ODS, nové skupiny a ANO"
DESCRIPTION = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily celé sestavy, ANO oznámilo podání a Piráti představují své kandidáty."
)
IMAGE = "https://nasekadan.cz/social/komunalni-volby-kadan-kandidaty-lhuta-2026.png"


def main() -> None:
    text = RSS.read_text(encoding="utf-8")
    item = f'''    <item>
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
    </item>
'''
    text = re.sub(
        r"\s*<item>.*?<link>" + re.escape(URL) + r"</link>.*?</item>\s*",
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        "<lastBuildDate>Tue, 04 Aug 2026 18:46:00 +0200</lastBuildDate>",
        text,
        count=1,
    )
    marker = "    <item>"
    if marker not in text:
        raise RuntimeError("RSS neobsahuje položku pro bezpečné vložení.")
    text = text.replace(marker, item + marker, 1)
    RSS.write_text(text, encoding="utf-8", newline="\n")

    root = ET.parse(RSS).getroot()
    links = [node.findtext("link") for node in root.findall("./channel/item")]
    if not links or links[0] != URL or links.count(URL) != 1:
        raise RuntimeError(f"Neplatné pořadí nebo duplicita RSS: {links[:4]}")
    print(f"RSS opraveno: {links[0]}")


if __name__ == "__main__":
    main()
