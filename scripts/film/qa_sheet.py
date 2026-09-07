"""Contact sheet of the finished film - the last visual gate before shipping.

Samples evenly across the composited frames so every act is represented, and
labels each tile with its frame number and act. Collisions, blown exposure and
dead frames are all obvious on one page in a way they never are frame by frame.

  py qa_sheet.py [--in comp] [--n 24] [--out qa.png]
"""
import argparse, glob, os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as T  # noqa: E402


def act_of(f):
    for name, (a, b) in (("1", T.A1), ("2", T.A2), ("3", T.A3),
                         ("4", T.A4), ("5", T.A5)):
        if a <= f <= b:
            return name
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=os.path.join(HERE, "comp"))
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(HERE, "qa.png"))
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.src, "c_*.png")))
    if not files:
        raise SystemExit("no frames in %s" % a.src)
    step = max(1, len(files) // a.n)
    picks = files[::step][:a.n]

    tw = 480
    th = int(tw * T.H / T.W)
    rows = (len(picks) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (a.cols * tw, rows * th), (16, 18, 22))
    d = ImageDraw.Draw(sheet)
    dark = 0
    for i, p in enumerate(picks):
        im = Image.open(p).convert("RGB")
        n = int(os.path.basename(p)[2:7])
        sheet.paste(im.resize((tw, th), Image.LANCZOS),
                    ((i % a.cols) * tw, (i // a.cols) * th))
        d.text(((i % a.cols) * tw + 8, (i // a.cols) * th + 6),
               "%05d  act %s" % (n, act_of(n)), fill=(0, 255, 130))
        if im.convert("L").resize((32, 18)).getextrema()[1] < 12:
            dark += 1
            print("  near-black frame: %d" % n)
    sheet.save(a.out)
    print("QA sheet %s  %d tiles  %d near-black" % (a.out, len(picks), dark))


if __name__ == "__main__":
    main()
