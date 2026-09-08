"""Abundance - the typography pass.

Composites the film's text over the rendered 3D frames. Kept separate from the
Blender pass so the writing can be re-cut without re-rendering a single frame.

Every figure drawn here comes from film_facts.json, which is computed from the
repo's own primary-source-cited dataset. Nothing is typed in by hand.

TYPE SCALE. Sized for someone watching in a half-screen window (~780px wide),
not for a 1920px frame. At that width the frame renders at ~40%, so a 16px
citation is 6px on screen - invisible. The floor here is 30px (~12px at
half-screen) and it is a floor, not a suggestion.

  py type_pass.py --in render --out comp [--frames 1,200,...] [--jobs 8]
"""
import json, math, os, sys, argparse
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as T  # noqa: E402

W, H = T.W, T.H
M = 132                      # left margin - the editorial column starts here

# ----------------------------------------------------------------- type -----
F_DIR = "C:/Windows/Fonts/"
SERIF, SERIF_B, SERIF_I = F_DIR + "constan.ttf", F_DIR + "constanb.ttf", F_DIR + "constani.ttf"
MONO, MONO_B = F_DIR + "consola.ttf", F_DIR + "consolab.ttf"

S_CITE = 30      # citations, source lines            (~12px at half-screen)
S_MONO = 32      # commit subjects, the ratio recap
S_LABEL = 32     # act-2 resource label, tracked out
S_UNIT = 44      # units and captions, serif italic
S_BODY = 50      # sub-statements
S_STAT = 72      # statements
S_BIG = 140      # the per-person result - the number the film is about
S_TOTAL = 108    # world totals
S_RATIO = 92     # the multiple
S_COUNT = 132    # act-1 divisor counter
S_TITLE = 124    # ABUNDANCE

_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]


# --------------------------------------------------------------- palette ----
INK = (243, 240, 234)        # primary warm off-white
SUB = (196, 205, 214)        # secondary cool grey
CITE = (156, 168, 180)       # citations - quiet, but still readable
RULE = (243, 240, 234)

with open(os.path.join(HERE, "film_facts.json"), encoding="utf-8") as fh:
    FX = json.load(fh)
DIV = {d["key"]: d for d in FX["divisions"]}


def hue255(key):
    return tuple(int(round(c * 255)) for c in DIV[key]["hue"])


# ------------------------------------------------------------- drawing ------
def text(d, xy, s, f, colour, a, tracking=0.0, anchor="ls"):
    """Draw with an explicit alpha and optional letter tracking."""
    if a <= 0.004 or not s:
        return
    col = (colour[0], colour[1], colour[2], max(0, min(255, int(round(a * 255)))))
    if tracking == 0:
        d.text(xy, s, font=f, fill=col, anchor=anchor)
        return
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2.0
    elif anchor[0] == "r":
        x -= total
    for ch, wch in zip(s, widths):
        d.text((x, y), ch, font=f, fill=col, anchor="l" + anchor[1])
        x += wch + tracking


def rule(d, x0, x1, y, a, colour=RULE, weight=2):
    if a <= 0.004:
        return
    d.rectangle([x0, y, x1, y + weight - 1],
                fill=(colour[0], colour[1], colour[2], int(round(a * 0.55 * 255))))


def rise(f, a, b, rise_n, fall_n, dist=16):
    """Returns (alpha, y-offset). Text drifts up as it arrives - never a pop."""
    al = T.hold(f, a, b, rise_n, fall_n)
    dy = (1.0 - T.ease_out_cubic(T.span(f, a, a + rise_n))) * dist
    return al, dy


def commas(n):
    return "{:,}".format(int(round(n)))


def short(s, n=44):
    """Citations are full source names in the dataset; on screen they have to
    fit the column at film type size. Cut at the parenthetical, then trim."""
    s = s.split(" (")[0].strip().rstrip(",")
    return s if len(s) <= n else s[:n - 1].rstrip(" ,;") + "\u2026"


# ------------------------------------------------------------- washes -------
_BANDS = {}


def band(y0, y1, feather=170, strength=0.74):
    """A feathered horizontal wash behind centred text (acts 1 and 5)."""
    key = (y0, y1, feather, strength)
    if key not in _BANDS:
        col = Image.new("L", (1, H))
        px = col.load()
        for y in range(H):
            if y0 <= y <= y1:
                v = 1.0
            elif y < y0:
                v = max(0.0, 1.0 - (y0 - y) / float(feather))
            else:
                v = max(0.0, 1.0 - (y - y1) / float(feather))
            px[0, y] = int(255 * (v ** 1.6) * strength)
        s = Image.new("RGBA", (W, H), (4, 6, 11, 255))
        s.putalpha(col.resize((W, H)))
        _BANDS[key] = s
    return _BANDS[key]


_SCRIM = None


def scrim():
    """A dark wash under the left-hand editorial column (acts 2-4).

    Two-dimensional on purpose. A pure horizontal gradient was not enough: the
    threshold bar and its citations sit low in frame, where the lit field is
    near-white, so the wash also has to deepen toward the bottom.
    """
    global _SCRIM
    if _SCRIM is None:
        import numpy as np
        # horizontal: flat across the column, then released back to the field
        x = np.arange(W, dtype=np.float64)
        hx = np.where(x < W * 0.52, 1.0,
                      np.clip(1.0 - (x - W * 0.52) / (W * 0.43), 0, 1) ** 1.3)
        # vertical: light over the dark sky, full over the bright field
        y = np.arange(H, dtype=np.float64)
        vy = 0.52 + 0.48 * np.clip(y / (H * 0.62), 0, 1) ** 1.25
        a = (255 * 0.88 * vy[:, None] * hx[None, :]).astype(np.uint8)
        s = Image.new("RGBA", (W, H), (4, 6, 11, 255))
        s.putalpha(Image.fromarray(a, mode="L"))
        _SCRIM = s
    return _SCRIM


# ================================================================ act 1 ======
def act1(d, f):
    if f > T.A1[1] + 6:
        return
    a, dy = rise(f, 52, 166, 34, 40)
    text(d, (W / 2, 660 + dy), "One.", font(SERIF, 84), INK, a, tracking=3.0,
         anchor="ms")

    a2, dy2 = rise(f, 176, T.A1[1] + 6, 40, 34)
    if a2 > 0:
        p = T.ease_out_quint(T.span(f, 180, 352))
        val = 1 + (FX["population"] - 1) * p
        shown = commas(val if val < 1e6 else round(val / 1e6) * 1e6)
        text(d, (W / 2, 452 + dy2), shown, font(SERIF, S_COUNT), INK, a2,
             tracking=1.0, anchor="ms")

    a3, dy3 = rise(f, 232, T.A1[1] + 6, 34, 34)
    text(d, (W / 2, 524 + dy3), "people alive, mid-2024", font(SERIF_I, S_UNIT),
         SUB, a3, anchor="ms")
    a4, _ = rise(f, 262, T.A1[1] + 6, 34, 34)
    text(d, (W / 2, 576), FX["population_src"], font(MONO, S_CITE), CITE, a4,
         tracking=1.4, anchor="ms")

    a5, dy5 = rise(f, 320, T.A1[1] + 6, 40, 30)
    text(d, (W / 2, 706 + dy5), "This is the number we divide by.",
         font(SERIF, S_STAT), INK, a5, anchor="ms")


# ================================================================ act 2 ======
def act2(d, f):
    for b in T.BEATS:
        s, e = b["start"], b["end"]
        if not (s - 8 <= f <= e + 8):
            continue
        x = DIV[b["key"]]
        hue = hue255(b["key"])

        # the numerator: what the world makes
        a, dy = rise(f, s + 8, e + 6, 30, 26)
        text(d, (M, 168 + dy), x["label"], font(MONO_B, S_LABEL), hue, a, tracking=9.0)
        rule(d, M, M + 380, 192 + dy, a, hue)

        a1, dy1 = rise(f, s + 16, e + 6, 34, 26)
        total_big, total_sub = x["total_txt"].split(" ", 1)
        text(d, (M, 300 + dy1), total_big, font(SERIF, S_TOTAL), INK, a1)
        wpx = d.textlength(total_big, font=font(SERIF, S_TOTAL))
        text(d, (M + wpx + 20, 300 + dy1), total_sub, font(SERIF_I, S_UNIT), SUB, a1)

        a2, _ = rise(f, s + 34, e + 6, 30, 26)
        text(d, (M, 352), short(x["src"]), font(MONO, S_CITE), CITE, a2, tracking=1.3)

        # the operation
        a3, dy3 = rise(f, s + 74, e + 6, 30, 26)
        text(d, (M, 448 + dy3), "\u00f7  " + FX["population_txt"],
             font(SERIF, 62), SUB, a3, tracking=1.0)

        # the result, against the published minimum need
        a4, dy4 = rise(f, s + 118, e + 6, 36, 26)
        text(d, (M, 590 + dy4), x["have_txt"], font(SERIF, S_BIG), INK, a4)
        wr = d.textlength(x["have_txt"], font=font(SERIF, S_BIG))
        text(d, (M + wr + 24, 590 + dy4), x["unit"], font(SERIF_I, S_UNIT), SUB, a4)

        # threshold bar: full width is each person's actual share, the tick marks
        # the published minimum. At 287x the tick sits hard left - the honest picture.
        a5 = T.hold(f, s + 138, e + 6, 34, 26)
        if a5 > 0:
            bx0, bx1, by = M, M + 880, 660
            grow = T.ease_out_cubic(T.span(f, s + 138, s + 190))
            d.rectangle([bx0, by, bx0 + (bx1 - bx0) * grow, by + 12],
                        fill=(*hue, int(a5 * 235)))
            frac = min(1.0, x["need"] / x["have"])
            tx = bx0 + (bx1 - bx0) * frac
            d.rectangle([tx - 2, by - 22, tx + 2, by + 34],
                        fill=(*INK, int(a5 * 235)))
            # at 287x the tick sits within a few px of the left margin, so the
            # centred label would run off-frame - clamp it back inside
            lw = d.textlength("minimum need", font=font(MONO, S_CITE))
            lx = max(tx, M + lw / 2.0)
            text(d, (lx, by + 74), "minimum need", font(MONO, S_CITE), SUB, a5,
                 tracking=1.2, anchor="ms")
            text(d, (lx, by + 112), x["need_txt"], font(MONO, S_CITE), CITE, a5,
                 tracking=1.2, anchor="ms")
            text(d, (bx1 + 46, by + 34), x["ratio_txt"], font(SERIF_B, S_RATIO),
                 hue, a5)
            text(d, (M, by + 168), short(x["need_src"], 40), font(MONO, S_CITE),
                 CITE, a5 * 0.9, tracking=1.2)
        if x["caveat"]:
            a6 = T.hold(f, s + 158, e + 6, 30, 26)
            text(d, (M, 890), x["caveat"], font(SERIF_I, 38), CITE, a6)


# ================================================================ act 3 ======
def act3(d, f):
    s = T.A3[0]
    if not (s - 8 <= f <= T.A3[1] + 8):
        return

    a, dy = rise(f, s + 14, s + 210, 34, 30)
    text(d, (M, 244 + dy), "Enough, on every measure we can compare.",
         font(SERIF, S_STAT), INK, a)

    a1, dy1 = rise(f, s + 60, s + 210, 34, 30)
    # built from the dataset, never retyped, so it cannot drift from the numbers
    recap = "   \u00b7   ".join("%s %s" % (x["label"].title(), x["ratio_txt"])
                                for x in FX["divisions"])
    text(d, (M, 322 + dy1), recap, font(MONO, S_MONO), INK, a1, tracking=1.6)

    # the turn
    a2, dy2 = rise(f, s + 150, s + 340, 36, 30)
    text(d, (M, 452 + dy2), "The light does not spread.", font(SERIF, S_STAT),
         INK, a2)

    # who the arithmetic does not reach
    for i, sf in enumerate(FX["shortfalls"]):
        st = s + 196 + i * 34
        a3, dy3 = rise(f, st, s + 336, 30, 34)
        y = 588 + i * 88
        num = commas(sf["n"])
        text(d, (M, y + dy3), num, font(SERIF, S_STAT), INK, a3)
        wn = d.textlength(num, font=font(SERIF, S_STAT))
        text(d, (M + wn + 24, y + dy3), sf["label"], font(SERIF_I, S_BODY), SUB, a3)
        text(d, (M + 830, y + dy3 - 8), short(sf["src"], 34), font(MONO, 26),
             CITE, a3 * 0.85, tracking=1.1)

    # the cause is a position, not a shortage - stated without a false ratio
    a4, dy4 = rise(f, s + 352, T.A3[1] - 20, 34, 30)
    text(d, (M, 640 + dy4), "%s of household wealth." % FX["wealth_txt"],
         font(SERIF_I, S_BODY), SUB, a4)
    text(d, (M, 706 + dy4), "%s of it above the $1m line." % FX["wealth_above1m_txt"],
         font(SERIF_I, S_BODY), SUB, a4)
    a5, _ = rise(f, s + 366, T.A3[1] - 20, 30, 30)
    text(d, (M, 756), FX["wealth_src"], font(MONO, S_CITE), CITE, a5, tracking=1.2)

    a6, dy6 = rise(f, T.A3[1] - 140, T.A3[1] + 8, 40, 34)
    text(d, (W / 2, 940 + dy6), "Scarcity is a shape, not a quantity.",
         font(SERIF_B, S_STAT), INK, a6, anchor="ms")


# ================================================================ act 4 ======
def act4(d, f):
    s = T.A4[0]
    if not (s - 8 <= f <= T.A4[1] + 8):
        return

    a, dy = rise(f, s + 16, s + 210, 34, 30)
    text(d, (M, 268 + dy), "Every number here has a vintage.",
         font(SERIF, S_STAT), INK, a)
    a1, dy1 = rise(f, s + 56, s + 210, 34, 30)
    text(d, (M, 346 + dy1), "A figure with no date is a rumour.",
         font(SERIF_I, S_BODY), SUB, a1)

    # real commit subjects, read from git by facts.py - the receipts for
    # "we keep updating". Never hand-typed: the film must not attribute a line
    # this repo did not actually commit.
    for i, ln in enumerate(FX["commit_lines"]):
        st = s + 150 + i * 42
        a2, dy2 = rise(f, st, T.A4[1] - 46, 28, 34, dist=12)
        y = 500 + i * 66
        text(d, (M, y + dy2), "commit", font(MONO, 26), CITE, a2 * 0.8, tracking=1.4)
        text(d, (M + 150, y + dy2), ln, font(MONO, S_MONO), INK, a2)

    a3, dy3 = rise(f, s + 330, T.A4[1] + 8, 34, 30)
    text(d, (M, 830 + dy3), "%d cited facts.   %d with a primary source.   %d commits."
         % (FX["cited_fact_count"], FX["sourced_fact_count"], FX["commits"]),
         font(SERIF, 58), INK, a3)

    a4, dy4 = rise(f, s + 372, T.A4[1] + 8, 34, 30)
    text(d, (M, 906 + dy4), "\u201cIf a claim has no link, it is not in the repo.\u201d",
         font(SERIF_I, S_BODY), SUB, a4)
    a5, _ = rise(f, s + 392, T.A4[1] + 8, 30, 30)
    text(d, (M, 950), "README.md", font(MONO, S_CITE), CITE, a5, tracking=1.2)

    a6, dy6 = rise(f, T.A4[1] - 132, T.A4[1] + 8, 38, 30)
    text(d, (M, 1032 + dy6), "That is why the repo keeps changing.",
         font(SERIF_B, 66), INK, a6)


# ================================================================ act 5 ======
def act5(d, f):
    s = T.A5[0]
    if f < s - 8:
        return

    # the statements must clear before the title arrives - same optical centre
    a, dy = rise(f, s + 20, s + 168, 40, 34)
    text(d, (W / 2, 356 + dy), "The arithmetic says it is possible.",
         font(SERIF, S_STAT), INK, a, anchor="ms")
    a1, dy1 = rise(f, s + 60, s + 176, 40, 34)
    text(d, (W / 2, 434 + dy1), "It does not say it is easy.",
         font(SERIF_I, S_BODY), SUB, a1, anchor="ms")

    a2, dy2 = rise(f, s + 190, T.END + 1, 48, 0, dist=20)
    text(d, (W / 2, 366 + dy2), "ABUNDANCE", font(SERIF, S_TITLE), INK, a2,
         tracking=20.0, anchor="ms")
    a3 = T.hold(f, s + 218, T.END + 1, 42, 0)
    rule(d, W / 2 - 300, W / 2 + 300, 412, a3)
    text(d, (W / 2, 480), "github.com/lordbasilaiassistant-sudo/Abundance",
         font(MONO, 34), SUB, a3, tracking=1.6, anchor="ms")

    a4 = T.hold(f, s + 246, T.END + 1, 42, 0)
    text(d, (W / 2, 556), "Every figure recomputed from data/essentials.json.",
         font(MONO, S_CITE), CITE, a4, tracking=1.3, anchor="ms")
    text(d, (W / 2, 600), "This film rebuilds when the data does.",
         font(MONO, S_CITE), CITE, a4, tracking=1.3, anchor="ms")


# ================================================================= main ======
def compose(job):
    f, src, dst = job
    p_in = os.path.join(src, "f_%05d.png" % f)
    if not os.path.exists(p_in):
        return "missing %d" % f
    base = Image.open(p_in).convert("RGBA")
    wash, amt = None, 0.0
    if T.A2[0] - 8 <= f <= T.A4[1] + 8:
        wash = scrim()
        amt = min(T.hold(f, T.A2[0] - 8, T.A4[1] + 8, 30, 30), 1.0)
    elif f <= T.A1[1] + 6:
        wash, amt = band(400, 760), T.hold(f, 150, T.A1[1] + 6, 70, 26)
    elif f >= T.A5[0] - 8:
        wash, amt = band(300, 640), T.hold(f, T.A5[0] - 8, T.END + 1, 50, 0)
    if wash is not None and amt > 0.004:
        sc = wash.copy()
        sc.putalpha(sc.getchannel("A").point(lambda v: int(v * amt)))
        base = Image.alpha_composite(base, sc)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    act1(d, f); act2(d, f); act3(d, f); act4(d, f); act5(d, f)
    out = Image.alpha_composite(base, layer).convert("RGB")
    out.save(os.path.join(dst, "c_%05d.png" % f), compress_level=3)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=os.path.join(HERE, "render"))
    ap.add_argument("--out", dest="dst", default=os.path.join(HERE, "comp"))
    ap.add_argument("--frames", default="")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.dst, exist_ok=True)
    frames = ([int(x) for x in a.frames.split(",") if x.strip()]
              if a.frames else list(range(1, T.END + 1)))
    jobs = [(f, a.src, a.dst) for f in frames]
    miss = 0
    with Pool(a.jobs) as p:
        for i, r in enumerate(p.imap_unordered(compose, jobs, chunksize=8)):
            if r:
                miss += 1
            if (i + 1) % 400 == 0:
                print("composed %d/%d" % (i + 1, len(jobs)), flush=True)
    print("TYPE_DONE frames=%d missing=%d -> %s" % (len(jobs), miss, a.dst))


if __name__ == "__main__":
    main()
