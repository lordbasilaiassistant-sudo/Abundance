#!/usr/bin/env python3
"""Generate a 32x32 favicon.png. Re-run only if branding changes."""
from pathlib import Path
from PIL import Image, ImageDraw

BG     = (14, 15, 18)
ACCENT = (95, 208, 161)
FG     = (233, 236, 241)

img = Image.new("RGBA", (32, 32), BG)
d   = ImageDraw.Draw(img)
# A simple division-sign motif: top dot, bar, bottom dot — the math symbol.
d.ellipse((12, 5, 20, 13), fill=ACCENT)        # top
d.rectangle((6, 14, 26, 18), fill=FG)          # bar
d.ellipse((12, 19, 20, 27), fill=ACCENT)       # bottom

out = Path(__file__).resolve().parent.parent / "favicon.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out}")

# Also a 180x180 apple-touch
big = Image.new("RGBA", (180, 180), BG)
d2  = ImageDraw.Draw(big)
d2.ellipse((68, 28, 112, 72),  fill=ACCENT)
d2.rectangle((34, 78, 146, 102), fill=FG)
d2.ellipse((68, 108, 112, 152), fill=ACCENT)
big.save(Path(__file__).resolve().parent.parent / "apple-touch-icon.png", "PNG", optimize=True)
print("wrote apple-touch-icon.png")
