#!/usr/bin/env python3
"""Generate the 1200x630 OpenGraph card for the Abundance site.

Run once; commit og.png. Re-run only if the headline math changes.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG     = (14, 15, 18)        # --bg
LINE   = (38, 41, 50)        # --line
FG     = (233, 236, 241)     # --fg
FG2    = (170, 177, 189)     # --fg-2
FG3    = (107, 114, 128)     # --fg-3
ACCENT = (95, 208, 161)      # --accent

# Windows system fonts
def f(family, size):
    candidates = [family + ".ttf", family + ".TTF",
                  f"C:/Windows/Fonts/{family}.ttf"]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()

font_serif      = f("georgia",  56)
font_serif_lg   = f("georgiab", 60)
font_mono_big   = f("consolab", 42)
font_mono       = f("consola",  22)
font_mono_sm    = f("consola",  18)
font_sans       = f("segoeui",  20)

img = Image.new("RGB", (W, H), BG)
d   = ImageDraw.Draw(img)

# Outer hairline
d.rectangle((24, 24, W-24, H-24), outline=LINE, width=1)

# Eyebrow
d.text((64, 60),
       "ABUNDANCE  ·  PRIMARY-SOURCED ARITHMETIC  ·  CC0",
       fill=FG3, font=font_mono_sm)

# Headline (two lines, mixed color)
d.text((64, 100),
       "The world already produces enough.",
       fill=FG, font=font_serif_lg)
d.text((64, 170),
       "The question is whether we admit it.",
       fill=ACCENT, font=font_serif_lg)

# Stat rows
rows = [
    ("FOOD",        "2,950 kcal / day",   "need 2,100",   "1.4×"),
    ("WATER",       "14,367 L / day",     "WHO basic 50", "287×"),
    ("ELECTRICITY", "3,763 kWh / year",   "min 1,000",    "3.8×"),
    ("GDP",         "$13,422 / year",     "poverty $1,095","12×"),
]

y = 300
LABEL_X  = 64
VALUE_X  = 280
VS_X     = 720
RATIO_X  = 1010

for label, value, vs, ratio in rows:
    d.text((LABEL_X, y + 8),  label, fill=FG3, font=font_mono_sm)
    d.text((VALUE_X, y),      value, fill=FG, font=font_mono_big)
    d.text((VS_X, y + 12),    "vs " + vs, fill=FG2, font=font_mono)
    d.text((RATIO_X, y - 2),  ratio, fill=ACCENT, font=font_mono_big)
    y += 62

# Footer rule + URL
d.line((64, H - 90, W - 64, H - 90), fill=LINE, width=1)
d.text((64, H - 70),
       "every number cited  ·  no tracking  ·  no analytics  ·  public domain",
       fill=FG3, font=font_mono_sm)
d.text((64, H - 44),
       "lordbasilaiassistant-sudo.github.io/Abundance",
       fill=FG, font=font_sans)

out = Path(__file__).resolve().parent.parent / "og.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes)")
