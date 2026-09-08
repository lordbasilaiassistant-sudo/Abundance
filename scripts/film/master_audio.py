"""Master the score for a film with no voice under it.

score-v3.mjs normalises its peak to 0.66 (-3.6 dBFS) deliberately, to leave
headroom for a voiceover. This film has no voice, so that headroom is just
quiet. This lifts loudness (RMS, which is what "more emphasised" actually
means) with a soft saturator rather than raw gain, so the swells still breathe
and nothing clips.

  py master_audio.py score.wav score-master.wav [--rms -14.5] [--ceiling 0.90]
"""
import argparse, struct, sys, wave
import numpy as np


def read_wav(p):
    with wave.open(p, "rb") as w:
        assert w.getsampwidth() == 2, "expected 16-bit"
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return a.reshape(-1, ch), sr


def write_wav(p, a, sr):
    q = np.clip(a, -1.0, 1.0)
    i = np.where(q < 0, q * 32768.0, q * 32767.0).astype("<i2")
    with wave.open(p, "wb") as w:
        w.setnchannels(a.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(i.tobytes())


def db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def process(a, gain, ceiling):
    """Soft saturation: linear for quiet material, asymptotic near the ceiling,
    then peak-normalised to the ceiling."""
    y = ceiling * np.tanh(gain * a / ceiling)
    pk = np.abs(y).max()
    if pk > 0:
        y *= ceiling / pk
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--rms", type=float, default=-14.5, help="target RMS dBFS")
    ap.add_argument("--ceiling", type=float, default=0.90)
    a = ap.parse_args()

    x, sr = read_wav(a.src)
    rms_in, pk_in = np.sqrt((x ** 2).mean()), np.abs(x).max()

    # search the drive that lands on the target loudness - measured, not guessed
    lo, hi = 1.0, 12.0
    for _ in range(48):
        mid = (lo + hi) / 2
        y = process(x, mid, a.ceiling)
        if db(np.sqrt((y ** 2).mean())) < a.rms:
            lo = mid
        else:
            hi = mid
    y = process(x, (lo + hi) / 2, a.ceiling)

    rms_out, pk_out = np.sqrt((y ** 2).mean()), np.abs(y).max()
    write_wav(a.dst, y, sr)

    # a limiter that flattens the dynamics has destroyed the swells, so check
    win = sr * 2
    def spread(sig):
        m = sig[:len(sig) // win * win].reshape(-1, win, sig.shape[1])
        r = np.sqrt((m ** 2).mean(axis=(1, 2)))
        return db(r.max()) - db(r.min())

    print("in    peak %6.1f dB   rms %6.1f dB   2s-spread %5.1f dB"
          % (db(pk_in), db(rms_in), spread(x)))
    print("out   peak %6.1f dB   rms %6.1f dB   2s-spread %5.1f dB"
          % (db(pk_out), db(rms_out), spread(y)))
    print("gain  %+.1f dB loudness, drive %.2fx" % (db(rms_out) - db(rms_in), (lo + hi) / 2))
    if db(pk_out) > -0.3:
        sys.exit("peak too hot")
    if spread(y) < spread(x) * 0.55:
        sys.exit("dynamics crushed: the section swells are the point")
    print("WROTE", a.dst)


if __name__ == "__main__":
    main()
