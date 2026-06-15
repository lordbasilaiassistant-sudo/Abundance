#!/usr/bin/env python3
"""Generate the 1200x630 OpenGraph card for letter.html.

A distinct share card so a forwarded letter shows its own message, not the
arithmetic card. Run once; commit og-letter.png.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG     = (14, 15, 18)
LINE   = (38, 41, 50)
FG     = (233, 236, 241)
FG2    = (170, 177, 189)
FG3    = (107, 114, 128)
ACCENT = (95, 208, 161)


def f(family, size):
    for path in (family + ".ttf", family + ".TTF", f"C:/Windows/Fonts/{family}.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


font_serif_lg = f("georgiab", 82)
font_serif    = f("georgia",  34)
font_mono_sm  = f("consola",  18)
font_sans     = f("segoeui",  26)
font_sans_sm  = f("segoeui",  20)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rectangle((24, 24, W - 24, H - 24), outline=LINE, width=1)
# accent rail, echoing the site's blockquote styling
d.rectangle((24, 24, 30, H - 24), fill=ACCENT)

d.text((64, 58), "ABUNDANCE  ·  AN OPEN LETTER  ·  CC0", fill=FG3, font=font_mono_sm)

# Headline
d.text((62, 104), "To whoever can", fill=FG, font=font_serif_lg)
d.text((62, 196), "end this.", fill=ACCENT, font=font_serif_lg)

# Body — the hooks, at explicit positions so nothing collides with the footer
body = [
    (302, "The world already produces enough — the shortfall is", FG2),
    (338, "distribution, and distribution is a choice.", FG2),
    (394, "Closing the poverty gap costs less than one year's rise in", FG),
    (430, "military spending. People as capable as you have already", FG),
    (466, "chosen it — and a fairer world is better even at the top.", FG),
]
for y, text, color in body:
    d.text((64, y), text, fill=color, font=font_sans)

d.line((64, H - 92, W - 64, H - 92), fill=LINE, width=1)
d.text((64, H - 72), "every claim cited  ·  no tracking  ·  public domain", fill=FG3, font=font_mono_sm)
d.text((64, H - 46), "lordbasilaiassistant-sudo.github.io/Abundance/letter.html", fill=FG, font=font_sans_sm)

out = Path(__file__).resolve().parent.parent / "og-letter.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes)")
