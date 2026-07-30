#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
OUT = Path('social/koupaliste-kadan-50-let-niagara-2026.png')


def font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


img = Image.new('RGB', (W, H), '#e9f4f7')
pixels = img.load()
for y in range(H):
    vertical = y / (H - 1)
    for x in range(W):
        horizontal = x / (W - 1)
        pixels[x, y] = (
            int(232 - 24 * vertical - 16 * horizontal),
            int(247 - 34 * vertical - 15 * horizontal),
            int(250 - 23 * vertical + 3 * horizontal),
        )

draw = ImageDraw.Draw(img)
sun = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sun_draw = ImageDraw.Draw(sun)
sun_draw.ellipse((900, -150, 1330, 280), fill=(255, 211, 78, 110))
img = Image.alpha_composite(img.convert('RGBA'), sun.filter(ImageFilter.GaussianBlur(36)))
draw = ImageDraw.Draw(img)

draw.rounded_rectangle((785, 100, 1135, 520), radius=38, fill=(255, 255, 255, 235), outline=(29, 95, 121, 255), width=5)
draw.rectangle((805, 355, 1115, 495), fill=(27, 153, 202, 255))
for y in range(370, 490, 22):
    draw.arc((805, y - 13, 1115, y + 20), 0, 180, fill=(187, 236, 250, 255), width=4)

draw.line((850, 165, 850, 355), fill=(32, 71, 88, 255), width=12)
draw.line((920, 165, 920, 355), fill=(32, 71, 88, 255), width=12)
draw.line((842, 170, 930, 170), fill=(32, 71, 88, 255), width=12)
for y in range(205, 345, 32):
    draw.line((850, y, 920, y), fill=(32, 71, 88, 255), width=5)

for offset, color in [(0, (218, 48, 62, 255)), (52, (255, 183, 32, 255))]:
    points = [(870 + offset, 180), (970 + offset, 205), (1000 + offset, 260), (980 + offset, 315), (925 + offset, 355), (900 + offset, 390)]
    draw.line(points, fill=(255, 255, 255, 255), width=38, joint='curve')
    draw.line(points, fill=color, width=28, joint='curve')

for center_x in (825, 1080):
    draw.ellipse((center_x - 12, 310, center_x + 12, 334), fill=(255, 255, 255, 255))
    draw.line((center_x, 334, center_x, 374), fill=(255, 255, 255, 255), width=7)
    draw.line((center_x, 345, center_x - 18, 360), fill=(255, 255, 255, 255), width=6)
    draw.line((center_x, 345, center_x + 18, 360), fill=(255, 255, 255, 255), width=6)

draw.rounded_rectangle((42, 38, 760, 592), radius=32, fill=(8, 31, 47, 244))
draw.text((82, 70), 'NAŠE KADAŇ', font=font(31, True), fill='white')
draw.rectangle((82, 116, 650, 124), fill=(180, 35, 47, 255))
draw.rounded_rectangle((82, 148, 330, 198), radius=10, fill=(180, 35, 47, 255))
draw.text((103, 158), 'MĚSTO · VOLNÝ ČAS', font=font(21, True), fill='white')

lines = ['KADAŇSKÉ', 'KOUPALIŠTĚ', 'SLAVÍ 50 LET']
y = 225
for index, line in enumerate(lines):
    draw.text((82, y), line, font=font(57 if index < 2 else 52, True), fill='white')
    y += 68

draw.text((84, 438), 'NOVÁ NIAGARA', font=font(29, True), fill=(255, 203, 50, 255))
draw.text((84, 481), 'Co nabízí areál a co stále není jasné?', font=font(26, True), fill=(222, 240, 247, 255))
draw.rounded_rectangle((82, 535, 680, 578), radius=8, fill=(236, 241, 244, 255))
draw.text((103, 544), 'ČTĚTE NA NASEKADAN.CZ', font=font(22, True), fill=(20, 52, 68, 255))
draw.rounded_rectangle((690, 531, 743, 582), radius=10, fill=(180, 35, 47, 255))
draw.text((700, 542), 'NK', font=font(23, True), fill='white')

OUT.parent.mkdir(parents=True, exist_ok=True)
img.convert('RGB').save(OUT, 'PNG', optimize=True)
print(f'{OUT}: {OUT.stat().st_size} B')
