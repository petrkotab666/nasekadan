#!/usr/bin/env python3
"""Kanonická pojistka úplné viditelnosti publikovaných článků.

Tento vstupní bod nesmí obsahovat ani volat žádný jednorázový historický deploy.
Vždy pouze znovu sestaví titulku a stránkovaný archiv ze skutečných článkových
souborů pomocí obecného generátoru ``enforce_article_visibility``.
"""
from __future__ import annotations

from enforce_article_visibility import main


if __name__ == "__main__":
    main()
