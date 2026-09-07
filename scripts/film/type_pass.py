"""Abundance - the typography pass.

Composites the film's text over the rendered 3D frames. Kept separate from the
Blender pass so the writing can be re-cut without re-rendering a single frame.

Every figure drawn here comes from film_facts.json, which is computed from the
repo's own primary-source-cited dataset. Nothing is typed in by hand.

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
_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]


# --------------------------------------------------------------- palette ----
INK = (242, 239, 233)        # primary warm off-white
SUB = (190, 200, 210)        # secondary cool grey
CITE = (146, 158, 170)       # citations - quiet, but still readable
RULE = (242, 239, 233)

with open(os.path.join(HERE, "film_facts.json"), encoding="utf-8") as fh:
    FX = json.load(fh)
DIV = {d["key"]: d for d in FX["divisions"]}


def hue255(key):
    h = DIV[key]["hue"]
    return tuple(int(round(c * 255)) for c in h)


# ------------------------------------------------------------- drawing ------
def text(d, xy, s, f, colour, a, tracking=0.0, anchor="ls"):
    """Draw with an explicit alpha and optional letter tracking."""
    if a <= 0.004 or not s:
        return
    col = (colour[0], colour[1], colour[2], max(0, min(255, int(round(a * 255)))))
    if tracking == 0:
        d.text(xy, s, font=f, fill=col, anchor=anchor)
        return
    # manual tracking: measure, then place glyph by glyph
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


def rule(d, x0, x1, y, a, colour=RULE, weight=1):
    if a <= 0.004:
        return
    d.rectangle([x0, y, x1, y + weight - 1],
                fill=(colour[0], colour[1], colour[2], int(round(a * 0.55 * 255))))


def rise(f, a, b, rise_n, fall_n, dist=14):
    """Returns (alpha, y-offset). Text drifts up as it arrives - never a pop."""
    al = T.hold(f, a, b, rise_n, fall_n)
    dy = (1.0 - T.ease_out_cubic(T.span(f, a, a + rise_n))) * dist
    return al, dy


def commas(n):
    return "{:,}".format(int(round(n)))


def short(s, n=54):
    """Citations are full source names in the dataset; on screen they have to
    fit the column. Cut at the parenthetical, then hard-trim."""
    s = s.split(" (")[0].strip().rstrip(",")
    return s if len(s) <= n else s[:n - 1].rstrip(" ,;") + "…"


_BANDS = {}


def band(y0, y1, feather=150, strength=0.70):
    """A feathered horizontal wash behind centred text.

    Acts 1 and 5 set their type over the middle of the frame, where the lit
    field is brightest. The left-column scrim is the wrong shape for them.
    """
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
    """A soft dark wash under the left-hand editorial column.

    The field's horizon is the brightest thing in the frame and it sits exactly
    where the citations and the threshold bar go. Without this the small type is
    unreadable for a third of the film.
    """
    global _SCRIM
    if _SCRIM is None:
        row = Image.new("L", (W, 1))
        px = row.load()
        for x in range(W):
            t = x / (W * 0.76)
            px[x, 0] = int(255 * (max(0.0, 1.0 - t) ** 1.45) * 0.80)
        s = Image.new("RGBA", (W, H), (4, 6, 11, 255))
        s.putalpha(row.resize((W, H)))
        _SCRIM = s
    return _SCRIM


# ================================================================ act 1 ======
def act1(d, f):
    if f > T.A1[1] + 6:
        return
    # "One." under the single light
    a, dy = rise(f, 52, 166, 34, 40)
    text(d, (W / 2, 640 + dy), "One.", font(SERIF, 62), INK, a, tracking=2.0,
         anchor="ms")

    # the divisor, counting up to the whole species
    a2, dy2 = rise(f, 176, T.A1[1] + 6, 40, 34)
    if a2 > 0:
        p = T.ease_out_quint(T.span(f, 180, 352))
        val = 1 + (FX["population"] - 1) * p
        # count in whole millions once it is past the early digits
        shown = commas(val if val < 1e6 else round(val / 1e6) * 1e6)
        text(d, (W / 2, 470 + dy2), shown, font(SERIF, 96), INK, a2,
             tracking=1.0, anchor="ms")

    a3, dy3 = rise(f, 232, T.A1[1] + 6, 34, 34)
    text(d, (W / 2, 522 + dy3), "people alive, mid-2024", font(SERIF_I, 30),
         SUB, a3, anchor="ms")
    a4, _ = rise(f, 262, T.A1[1] + 6, 34, 34)
    text(d, (W / 2, 566), FX["population_src"], font(MONO, 16), CITE, a4,
         tracking=1.4, anchor="ms")

    a5, dy5 = rise(f, 320, T.A1[1] + 6, 40, 30)
    text(d, (W / 2, 700 + dy5), "This is the number we divide by.",
         font(SERIF, 40), INK, a5, anchor="ms")


# ================================================================ act 2 ======
def act2(d, f):
    for b in T.BEATS:
        s, e = b["start"], b["end"]
        if not (s - 8 <= f <= e + 8):
            continue
        x = DIV[b["key"]]
        hue = hue255(b["key"])

        # The whole column lives in the top 60% of frame: below that the field
        # is the brightest thing on screen and small type cannot survive on it.

        # --- the numerator: what the world makes -------------------------
        a, dy = rise(f, s + 8, e + 6, 30, 26)
        text(d, (M, 178 + dy), x["label"], font(MONO_B, 21), hue, a, tracking=7.0)
        rule(d, M, M + 300, 196 + dy, a, hue)

        a1, dy1 = rise(f, s + 16, e + 6, 34, 26)
        total_big, total_sub = x["total_txt"].split(" ", 1)
        text(d, (M, 276 + dy1), total_big, font(SERIF, 80), INK, a1)
        wpx = d.textlength(total_big, font=font(SERIF, 80))
        text(d, (M + wpx + 18, 276 + dy1), total_sub, font(SERIF_I, 31), SUB, a1)

        a2, _ = rise(f, s + 34, e + 6, 30, 26)
        text(d, (M, 316), short(x["src"]), font(MONO, 16), CITE, a2, tracking=1.3)

        # --- the operation ------------------------------------------------
        a3, dy3 = rise(f, s + 74, e + 6, 30, 26)
        text(d, (M, 404 + dy3), "\u00f7  " + FX["population_txt"],
             font(SERIF, 44), SUB, a3, tracking=1.0)

        # --- the result, against the published minimum need ---------------
        a4, dy4 = rise(f, s + 118, e + 6, 36, 26)
        text(d, (M, 516 + dy4), x["have_txt"], font(SERIF, 100), INK, a4)
        wr = d.textlength(x["have_txt"], font=font(SERIF, 100))
        text(d, (M + wr + 22, 516 + dy4), x["unit"], font(SERIF_I, 30), SUB, a4)

        # threshold bar: full width is what each person's share actually is,
        # the tick marks the published minimum. At 287x the tick sits hard left,
        # which is the honest picture.
        a5 = T.hold(f, s + 138, e + 6, 34, 26)
        if a5 > 0:
            bx0, bx1, by = M, M + 760, 572
            grow = T.ease_out_cubic(T.span(f, s + 138, s + 190))
            d.rectangle([bx0, by, bx0 + (bx1 - bx0) * grow, by + 9],
                        fill=(*hue, int(a5 * 235)))
            frac = min(1.0, x["need"] / x["have"])
            tx = bx0 + (bx1 - bx0) * frac
            d.rectangle([tx - 1, by - 16, tx + 1, by + 25],
                        fill=(*INK, int(a5 * 235)))
            text(d, (tx, by + 52), "minimum need", font(MONO, 15), SUB, a5,
                 tracking=1.2, anchor="ms")
            text(d, (tx, by + 74), x["need_txt"], font(MONO, 15), CITE, a5,
                 tracking=1.2, anchor="ms")
            text(d, (bx1 + 40, by + 24), x["ratio_txt"], font(SERIF_B, 62),
                 hue, a5)
            text(d, (M, by + 112), short(x["need_src"], 46), font(MONO, 15),
                 CITE, a5 * 0.9, tracking=1.2)
        if x["caveat"]:
            a6 = T.hold(f, s + 158, e + 6, 30, 26)
            text(d, (M, 716), x["caveat"], font(SERIF_I, 23), CITE, a6)


# ================================================================ act 3 ======
def act3(d, f):
    s = T.A3[0]
    if not (s - 8 <= f <= T.A3[1] + 8):
        return

    a, dy = rise(f, s + 14, s + 200, 34, 30)
    text(d, (M, 232 + dy), "Enough, on every measure we can compare.",
         font(SERIF, 46), INK, a)

    a1, dy1 = rise(f, s + 60, s + 200, 34, 30)
    # built from the dataset, never retyped, so it cannot drift from the numbers
    recap = "   \u00b7   ".join("%s %s" % (x["label"].title(), x["ratio_txt"])
                                for x in FX["divisions"])
    text(d, (M, 300 + dy1), recap, font(MONO, 27), INK, a1, tracking=1.6)

    # the turn
    a2, dy2 = rise(f, s + 150, s + 330, 36, 30)
    text(d, (M, 430 + dy2), "The light does not spread.", font(SERIF, 54),
         INK, a2)

    # who the arithmetic does not reach
    for i, sf in enumerate(FX["shortfalls"]):
        st = s + 196 + i * 34
        a3, dy3 = rise(f, st, T.A3[1] - 40, 30, 34)
        y = 560 + i * 74
        text(d, (M, y + dy3), commas(sf["n"]), font(SERIF, 52), INK, a3)
        wn = d.textlength(commas(sf["n"]), font=font(SERIF, 52))
        text(d, (M + wn + 22, y + dy3), sf["label"], font(SERIF_I, 32), SUB, a3)
        text(d, (M + 700, y + dy3 - 4), sf["src"], font(MONO, 14), CITE, a3 * 0.85,
             tracking=1.1)

    # the cause is a position, not a shortage - stated without a false ratio
    a4, _ = rise(f, s + 300, T.A3[1] - 30, 34, 30)
    text(d, (M, 916), "%s of household wealth. %s of it above the $1m line."
         % (FX["wealth_txt"], FX["wealth_above1m_txt"]),
         font(SERIF_I, 27), SUB, a4)
    a5, _ = rise(f, s + 316, T.A3[1] - 30, 30, 30)
    text(d, (M, 948), FX["wealth_src"], font(MONO, 15), CITE, a5, tracking=1.2)

    a6, dy6 = rise(f, T.A3[1] - 150, T.A3[1] + 8, 40, 34)
    text(d, (W / 2, 1010 + dy6), "Scarcity is a shape, not a quantity.",
         font(SERIF_B, 48), INK, a6, anchor="ms")


# ================================================================ act 4 ======
def act4(d, f):
    s = T.A4[0]
    if not (s - 8 <= f <= T.A4[1] + 8):
        return

    a, dy = rise(f, s + 16, s + 210, 34, 30)
    text(d, (M, 244 + dy), "Every number here has a vintage.",
         font(SERIF, 50), INK, a)
    a1, dy1 = rise(f, s + 56, s + 210, 34, 30)
    text(d, (M, 306 + dy1), "A figure with no date is a rumour.",
         font(SERIF_I, 34), SUB, a1)

    # real commit subjects, read from git by facts.py - the receipts for
    # "we keep updating". Never hand-typed: the film must not attribute a line
    # this repo did not actually commit.
    lines = FX["commit_lines"]
    for i, ln in enumerate(lines):
        st = s + 150 + i * 42
        a2, dy2 = rise(f, st, T.A4[1] - 46, 28, 34, dist=10)
        y = 470 + i * 52
        text(d, (M, y + dy2), "commit", font(MONO, 14), CITE, a2 * 0.8, tracking=1.4)
        text(d, (M + 86, y + dy2), ln, font(MONO, 18), INK, a2)

    a3, dy3 = rise(f, s + 330, T.A4[1] + 8, 34, 30)
    text(d, (M, 760 + dy3), "%d cited facts.  %d with a primary source.  %d commits."
         % (FX["cited_fact_count"], FX["sourced_fact_count"], FX["commits"]),
         font(SERIF, 38), INK, a3)

    a4, dy4 = rise(f, s + 372, T.A4[1] + 8, 34, 30)
    text(d, (M, 830 + dy4), "\u201cIf a claim has no link, it is not in the repo.\u201d",
         font(SERIF_I, 32), SUB, a4)
    a5, _ = rise(f, s + 392, T.A4[1] + 8, 30, 30)
    text(d, (M, 866), "README.md", font(MONO, 15), CITE, a5, tracking=1.2)

    a6, dy6 = rise(f, T.A4[1] - 132, T.A4[1] + 8, 38, 30)
    text(d, (M, 980 + dy6), "That is why the repo keeps changing.",
         font(SERIF_B, 44), INK, a6)


# ================================================================ act 5 ======
def act5(d, f):
    s = T.A5[0]
    if f < s - 8:
        return

    # The closing statements must be fully gone before the title arrives - they
    # share the same optical centre, and the dome fills the lower two thirds, so
    # everything here lives in the upper sky.
    a, dy = rise(f, s + 20, s + 168, 40, 34)
    text(d, (W / 2, 322 + dy), "The arithmetic says it is possible.",
         font(SERIF, 52), INK, a, anchor="ms")
    a1, dy1 = rise(f, s + 60, s + 176, 40, 34)
    text(d, (W / 2, 388 + dy1), "It does not say it is easy.",
         font(SERIF_I, 36), SUB, a1, anchor="ms")

    a2, dy2 = rise(f, s + 190, T.END + 1, 48, 0, dist=18)
    text(d, (W / 2, 318 + dy2), "ABUNDANCE", font(SERIF, 92), INK, a2,
         tracking=15.0, anchor="ms")
    a3 = T.hold(f, s + 218, T.END + 1, 42, 0)
    rule(d, W / 2 - 230, W / 2 + 230, 356, a3)
    text(d, (W / 2, 408), "github.com/lordbasilaiassistant-sudo/Abundance",
         font(MONO, 22), SUB, a3, tracking=1.6, anchor="ms")

    a4 = T.hold(f, s + 246, T.END + 1, 42, 0)
    text(d, (W / 2, 470), "Every figure recomputed from data/essentials.json.",
         font(MONO, 16), CITE, a4, tracking=1.3, anchor="ms")
    text(d, (W / 2, 498), "This film rebuilds when the data does.",
         font(MONO, 16), CITE, a4, tracking=1.3, anchor="ms")


# ================================================================= main ======
def compose(job):
    f, src, dst = job
    p_in = os.path.join(src, "f_%05d.png" % f)
    if not os.path.exists(p_in):
        return "missing %d" % f
    base = Image.open(p_in).convert("RGBA")
    # acts 2-4 carry the left-hand column over the bright field; 1 and 5 are
    # centred over empty sky and need no wash.
    wash, amt = None, 0.0
    if T.A2[0] - 8 <= f <= T.A4[1] + 8:
        wash = scrim()
        amt = min(T.hold(f, T.A2[0] - 8, T.A4[1] + 8, 30, 30), 1.0)
    elif f <= T.A1[1] + 6:
        # only once the field is actually lit - the opening is already black
        wash, amt = band(430, 760), T.hold(f, 150, T.A1[1] + 6, 70, 26)
    elif f >= T.A5[0] - 8:
        wash, amt = band(268, 545), T.hold(f, T.A5[0] - 8, T.END + 1, 50, 0)
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
            if (i + 1) % 200 == 0:
                print("composed %d/%d" % (i + 1, len(jobs)), flush=True)
    print("TYPE_DONE frames=%d missing=%d -> %s" % (len(jobs), miss, a.dst))


if __name__ == "__main__":
    main()
