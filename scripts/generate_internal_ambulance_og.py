#!/usr/bin/env python3
from __future__ import annotations

import struct
import zlib
from pathlib import Path

WIDTH = 1200
HEIGHT = 630
OUT = Path("og/interni-ambulance-nemocnice-kadan-20260725-v1.png")

FONT = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01111","10000","10000","10111","10001","10001","01111"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","10010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],
    ".": ["00000","00000","00000","00000","00000","00110","00110"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    "/": ["00001","00010","00010","00100","01000","01000","10000"],
    ":": ["00000","00110","00110","00000","00110","00110","00000"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
}

pixels = bytearray(WIDTH * HEIGHT * 3)


def set_px(x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        index = (y * WIDTH + x) * 3
        pixels[index:index + 3] = bytes(color)


def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    x0, x1 = max(0, x0), min(WIDTH, x1)
    y0, y1 = max(0, y0), min(HEIGHT, y1)
    row = bytes(color) * max(0, x1 - x0)
    for y in range(y0, y1):
        index = (y * WIDTH + x0) * 3
        pixels[index:index + len(row)] = row


def circle(cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
    radius_squared = radius * radius
    for y in range(max(0, cy - radius), min(HEIGHT, cy + radius + 1)):
        dy = y - cy
        span = int((radius_squared - dy * dy) ** 0.5)
        rect(cx - span, y, cx + span + 1, y + 1, color)


def line(x0: int, y0: int, x1: int, y1: int, thickness: int, color: tuple[int, int, int]) -> None:
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for step in range(steps + 1):
        x = round(x0 + dx * step / steps)
        y = round(y0 + dy * step / steps)
        circle(x, y, max(1, thickness // 2), color)


def draw_text(
    x: int,
    y: int,
    text: str,
    scale: int,
    color: tuple[int, int, int],
    spacing: int | None = None,
) -> None:
    gap = scale if spacing is None else spacing
    cursor = x
    for character in text.upper():
        glyph = FONT.get(character, FONT[" "])
        for glyph_y, row in enumerate(glyph):
            for glyph_x, bit in enumerate(row):
                if bit == "1":
                    rect(
                        cursor + glyph_x * scale,
                        y + glyph_y * scale,
                        cursor + (glyph_x + 1) * scale,
                        y + (glyph_y + 1) * scale,
                        color,
                    )
        cursor += 5 * scale + gap


for y in range(HEIGHT):
    for x in range(WIDTH):
        horizontal = x / (WIDTH - 1)
        vertical = y / (HEIGHT - 1)
        set_px(
            x,
            y,
            (
                int(17 + 17 * horizontal + 10 * vertical),
                int(39 + 26 * horizontal + 7 * vertical),
                int(53 + 31 * horizontal + 9 * vertical),
            ),
        )

circle(80, 50, 230, (24, 53, 70))
circle(1080, 600, 300, (33, 63, 78))
for offset in range(-100, 1200, 80):
    line(offset, 630, offset + 400, 230, 2, (40, 72, 86))

rect(0, 0, 24, HEIGHT, (166, 35, 45))
rect(24, 0, 31, HEIGHT, (225, 174, 85))

rect(77, 112, 438, 536, (10, 25, 34))
rect(66, 101, 427, 525, (235, 239, 238))
rect(66, 101, 427, 145, (202, 210, 208))
rect(104, 210, 390, 472, (248, 248, 244))
rect(88, 190, 406, 220, (174, 43, 51))
rect(135, 160, 359, 198, (250, 250, 247))

for window_y in (244, 306, 368):
    for window_x in (132, 196, 260, 324):
        rect(window_x, window_y, window_x + 38, window_y + 34, (64, 104, 119))
        rect(window_x + 4, window_y + 4, window_x + 34, window_y + 30, (171, 204, 212))

rect(226, 406, 282, 472, (39, 70, 84))
rect(232, 412, 276, 472, (138, 184, 196))
circle(247, 128, 53, (173, 38, 48))
rect(233, 91, 261, 165, (255, 255, 255))
rect(210, 114, 284, 142, (255, 255, 255))
rect(89, 488, 404, 548, (173, 38, 48))
draw_text(111, 504, "27. 7. - 14. 8.", 4, (255, 255, 255), spacing=4)

draw_text(505, 84, "NASE KADAN", 4, (226, 177, 90), spacing=5)
rect(505, 124, 1130, 130, (173, 38, 48))
draw_text(505, 176, "INTERNI", 8, (255, 255, 255), spacing=8)
draw_text(505, 250, "AMBULANCE", 8, (255, 255, 255), spacing=8)
draw_text(507, 348, "DOCASNE UZAVRENA", 4, (226, 177, 90), spacing=5)
draw_text(507, 405, "27. 7. - 14. 8. 2026", 5, (242, 244, 241), spacing=5)
rect(505, 470, 1130, 474, (82, 115, 126))
draw_text(507, 501, "PRAKTICKE INFORMACE PRO PACIENTY", 3, (205, 220, 222), spacing=4)
rect(1045, 570, 1130, 596, (173, 38, 48))
draw_text(1057, 575, "NK", 2, (255, 255, 255), spacing=3)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


raw = bytearray()
stride = WIDTH * 3
for y in range(HEIGHT):
    raw.append(0)
    raw.extend(pixels[y * stride:(y + 1) * stride])

png = (
    b"\x89PNG\r\n\x1a\n"
    + png_chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    + png_chunk(b"IEND", b"")
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_bytes(png)
print(f"Vytvořen {OUT} ({OUT.stat().st_size} B)")
