#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = Path("og/interni-ambulance-nemocnice-kadan-20260725-v2.png")

img = Image.new("RGB", (W, H))
pixels = img.load()
for y in range(H):
    for x in range(W):
        t = x / (W - 1)
        u = y / (H - 1)
        pixels[x, y] = (
            int(18 + 22 * t + 8 * u),
            int(39 + 37 * t + 10 * u),
            int(53 + 43 * t + 12 * u),
        )

draw = ImageDraw.Draw(img)
draw.ellipse((-130, -170, 330, 290), fill=(24, 55, 72))
draw.ellipse((930, 380, 1370, 820), fill=(39, 72, 88))
for offset in range(-100, 1300, 90):
    draw.line((offset, H, offset + 420, 210), fill=(48, 82, 96), width=2)

draw.rectangle((0, 0, 24, H), fill=(169, 35, 45))
draw.rectangle((24, 0, 31, H), fill=(225, 177, 90))

draw.rounded_rectangle((65, 86, 440, 548), radius=20, fill=(237, 241, 240))
draw.rectangle((65, 86, 440, 145), fill=(200, 209, 208))
draw.rectangle((92, 180, 413, 220), fill=(169, 35, 45))
draw.rectangle((122, 230, 383, 475), fill=(248, 248, 244))
for wy in (260, 330, 400):
    for wx in (145, 215, 285, 355):
        draw.rounded_rectangle((wx, wy, wx + 38, wy + 36), radius=3, fill=(168, 205, 214))
        draw.rectangle((wx + 5, wy + 5, wx + 33, wy + 31), fill=(83, 125, 140))
draw.rectangle((239, 415, 292, 475), fill=(54, 92, 106))
draw.rectangle((246, 422, 285, 475), fill=(152, 193, 203))
draw.ellipse((190, 103, 315, 228), fill=(173, 38, 48))
draw.rectangle((236, 126, 269, 205), fill="white")
draw.rectangle((212, 149, 293, 182), fill="white")
draw.rounded_rectangle((88, 492, 416, 548), radius=10, fill=(173, 38, 48))

font_dir = Path("/usr/share/fonts/truetype/dejavu")
bold = str(font_dir / "DejaVuSans-Bold.ttf")
regular = str(font_dir / "DejaVuSans.ttf")
f_brand = ImageFont.truetype(bold, 28)
f_title = ImageFont.truetype(bold, 67)
f_sub = ImageFont.truetype(bold, 33)
f_date = ImageFont.truetype(bold, 27)
f_small = ImageFont.truetype(regular, 23)
f_badge = ImageFont.truetype(bold, 20)

draw.text((112, 505), "27. 7. – 14. 8. 2026", font=f_date, fill="white")
draw.text((500, 72), "NAŠE KADAŇ", font=f_brand, fill=(226, 177, 90))
draw.rectangle((500, 116, 1125, 122), fill=(173, 38, 48))
draw.text((500, 165), "INTERNÍ", font=f_title, fill="white")
draw.text((500, 242), "AMBULANCE", font=f_title, fill="white")
draw.text((502, 350), "DOČASNĚ UZAVŘENA", font=f_sub, fill=(226, 177, 90))
draw.text((502, 405), "Od 27. července do 14. srpna 2026", font=f_date, fill=(242, 244, 241))
draw.line((502, 470, 1125, 470), fill=(92, 127, 140), width=4)
draw.text((502, 500), "Praktické informace pro pacienty", font=f_small, fill=(211, 225, 227))
draw.rounded_rectangle((1040, 562, 1125, 600), radius=8, fill=(173, 38, 48))
draw.text((1065, 568), "NK", font=f_badge, fill="white")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"Vytvořen {OUT} ({W} × {H} px, {OUT.stat().st_size} B)")
