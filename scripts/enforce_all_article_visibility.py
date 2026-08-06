#!/usr/bin/env python3
"""Jednorázový publikační most pro opravený článek o Apoleně Švábíkové.

Proudový deploy obchází zaplněný serverový /tmp. Po úspěšném veřejném
ověření se tento soubor sám obnoví na kanonickou verzi.
"""
from __future__ import annotations

from deploy_current_apolena_streamed import main


if __name__ == "__main__":
    main()
