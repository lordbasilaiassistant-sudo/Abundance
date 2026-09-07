"""The film's single timeline. Imported by both the Blender pass and the type pass
so the 3D and the typography can never drift out of sync.

30 fps. Five acts. Frame numbers are inclusive.
"""

FPS = 30
W, H = 1920, 1080

# ---------------------------------------------------------------- acts -------
A1 = (1, 420)        # THE DIVISOR      one light becomes 8.2 billion
A2 = (421, 1020)     # THE DIVISION     three resources, divided
A3 = (1021, 1440)    # THE SHAPE        the light does not spread evenly
A4 = (1441, 1860)    # THE VINTAGE      why the repo keeps changing
A5 = (1861, 2160)    # THE CLOSE

END = A5[1]
DURATION_S = END / FPS

# Each resource beat inside act 2 is 200 frames.
BEATS = [
    {"key": "food",        "start": 421, "end": 620},
    {"key": "water",       "start": 621, "end": 820},
    {"key": "electricity", "start": 821, "end": 1020},
]

# ------------------------------------------------------------- easing --------


def clamp(x, lo=0.0, hi=1.0):
    # array-safe: the 3D pass eases whole numpy arrays of per-point progress,
    # the type pass eases scalars. Both go through here.
    if hasattr(x, "clip"):
        return x.clip(lo, hi)
    return lo if x < lo else (hi if x > hi else x)


def span(f, a, b):
    """Normalised 0..1 position of frame f across [a, b]."""
    if b <= a:
        return 1.0
    return clamp((f - a) / float(b - a))


def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_quint(t):
    t = clamp(t)
    return 1.0 - (1.0 - t) ** 5


def ease_in_quad(t):
    t = clamp(t)
    return t * t


def ease_out_back(t, s=1.20):
    """Slight overshoot. Used sparingly - only where something lands."""
    t = clamp(t)
    return 1 + (s + 1) * ((t - 1) ** 3) + s * ((t - 1) ** 2)


def hold(f, a, b, rise, fall, ease=ease_out_cubic):
    """Fade a thing up over `rise` frames from a, hold, fade out over `fall` to b.

    Returns 0..1. Used for every typographic element so nothing pops.
    """
    if f < a or f > b:
        return 0.0
    # a zero-length rise/fall means "no fade on that side". Without these guards
    # span() sees b <= a, returns 1.0, and the whole hold collapses to zero.
    up = ease(span(f, a, a + rise)) if rise > 0 else 1.0
    dn = 1.0 - ease_in_quad(span(f, b - fall, b)) if fall > 0 else 1.0
    return min(up, dn)
