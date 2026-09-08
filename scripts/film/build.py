"""Build the Abundance film end to end.

  py build.py                       # every pass, resumable
  py build.py --spot 40,575,1330    # a handful of frames, for judging the look
  py build.py --from type           # skip straight to the typography pass

Resumable: the 3D pass only renders frames that are not already on disk, so an
interrupted run costs nothing but the frames it had not reached.
"""
import argparse, os, subprocess, sys, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as T  # noqa: E402

BLENDER = os.environ.get(
    "BLENDER_EXE",
    os.path.expanduser("~/blender/blender-4.2.9-windows-x64/blender.exe"))
RENDER = os.path.join(HERE, "render")
COMP = os.path.join(HERE, "comp")
OUT = os.path.join(HERE, "abundance.mp4")


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd[:6]), "..." if len(cmd) > 6 else "",
          flush=True)
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        raise SystemExit("FAILED (%d): %s" % (r.returncode, cmd[0]))
    return r


def have(d, prefix):
    return {int(os.path.basename(p)[len(prefix):len(prefix) + 5])
            for p in glob.glob(os.path.join(d, prefix + "?????.png"))}


def contiguous(nums):
    """Compress a set of frame numbers into [start, end] runs."""
    out, cur = [], None
    for n in sorted(nums):
        if cur and n == cur[1] + 1:
            cur[1] = n
        else:
            cur = [n, n]
            out.append(cur)
    return out


def render_3d(frames, shards, samples):
    todo = sorted(set(frames) - have(RENDER, "f_"))
    if not todo:
        print("3D pass: nothing to do (%d frames present)" % len(frames))
        return
    print("3D pass: %d frames to render" % len(todo))
    runs = contiguous(todo)
    # hand each shard a slice of the work; EEVEE serialises on the GPU, so more
    # shards past a handful buys nothing
    flat = [n for r in runs for n in range(r[0], r[1] + 1)]
    chunk = max(1, (len(flat) + shards - 1) // shards)
    procs = []
    for i in range(0, len(flat), chunk):
        part = flat[i:i + chunk]
        log = open(os.path.join(HERE, "logs", "build_%05d.log" % part[0]), "w")
        procs.append((subprocess.Popen(
            [BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "scene.py"),
             "--", "--frames", ",".join(str(x) for x in part),
             "--out", RENDER, "--samples", str(samples)],
            stdout=log, stderr=subprocess.STDOUT), log, part[0], len(part)))
    bad = 0
    for p, log, first, n in procs:
        rc = p.wait()
        log.close()
        print("  shard @%d (%d frames) rc=%d" % (first, n, rc))
        bad += (rc != 0)
    if bad:
        raise SystemExit("%d render shard(s) failed - see logs/" % bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot", default="", help="comma-separated frames only")
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--from", dest="start_at", default="facts",
                    choices=["facts", "3d", "type", "encode"])
    a = ap.parse_args()

    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    os.makedirs(RENDER, exist_ok=True)
    os.makedirs(COMP, exist_ok=True)
    frames = ([int(x) for x in a.spot.split(",") if x.strip()]
              if a.spot else list(range(1, T.END + 1)))
    order = ["facts", "3d", "type", "encode"]
    todo = order[order.index(a.start_at):]

    if not os.path.exists(BLENDER):
        raise SystemExit("no Blender at %s (set BLENDER_EXE)" % BLENDER)

    if "facts" in todo:
        run([sys.executable, os.path.join(HERE, "facts.py")])
        # master the score if a raw one is present and no master exists yet
        raw = os.path.join(HERE, "score.wav")
        mastered = os.path.join(HERE, "score-master.wav")
        if os.path.exists(raw) and not os.path.exists(mastered):
            run([sys.executable, os.path.join(HERE, "master_audio.py"),
                 raw, mastered])
    if "3d" in todo:
        render_3d(frames, a.shards, a.samples)
    if "type" in todo:
        run([sys.executable, os.path.join(HERE, "type_pass.py"),
             "--in", RENDER, "--out", COMP, "--jobs", str(a.jobs)]
            + (["--frames", ",".join(str(f) for f in frames)] if a.spot else []))
    if "encode" in todo and not a.spot:
        run([BLENDER, "-b", "--factory-startup", "-P",
             os.path.join(HERE, "encode.py"), "--", "--in", COMP, "--out", OUT])
        run([sys.executable, os.path.join(HERE, "verify_container.py"), OUT])
    print("BUILD OK")


if __name__ == "__main__":
    main()
