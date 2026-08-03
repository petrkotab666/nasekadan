#!/usr/bin/env python3
"""Opravený vstupní bod auditu sociálních štítků.

Původní modul zůstává kvůli kompatibilitě, ale jeho výpočet jasu používal
16bitová celá čísla. Násobení barevných kanálů proto přetékalo a světlý text
nebyl rozpoznán. Tento vstupní bod nahrazuje pouze výpočet světelné masky
32bitovou variantou a poté používá veškerou původní logiku, argumenty i report.
"""

from __future__ import annotations

import sys

import numpy as np

import normalize_social_badges as core


def light_mask_32bit(array: np.ndarray) -> np.ndarray:
    rgb = array[..., :3].astype(np.int32)
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    luma = (rgb[..., 0] * 299 + rgb[..., 1] * 587 + rgb[..., 2] * 114) // 1000
    return (luma >= 125) & (maximum >= 150) & ((maximum - minimum) <= 145)


core.light_mask = light_mask_32bit


if __name__ == "__main__":
    sys.exit(core.main())
