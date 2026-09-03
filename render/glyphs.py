"""NACHTGLAS wordmark — original letterform geometry.

Letters are constructed on an 11-unit grid (11, because there are 111 lanterns).
Every glyph is a list of polylines in a 0..60 x 0..100 em box; arcs are sampled
so that the SVG export and the PIL/video renderer share exactly one source of truth.
"""
import math

STROKE = 13.0
ADVANCE = 60.0
TRACKING = 22.0
CAP = 100.0


def _arc(cx, cy, r, a0, a1, steps=220):
    """Polyline sampling an arc. Angles in degrees, y-down screen space."""
    return [
        (cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
         cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
        for i in range(steps + 1)
    ]


GLYPHS = {
    "N": [[(0, 100), (0, 0), (60, 100), (60, 0)]],
    "A": [[(2, 100), (24, 0), (36, 0), (58, 100)], [(12, 71), (48, 71)]],
    "C": [_arc(30, 50, 28, -50, -310)],
    "H": [[(0, 0), (0, 100)], [(60, 0), (60, 100)], [(0, 50), (60, 50)]],
    "T": [[(0, 6.5), (60, 6.5)], [(30, 6.5), (30, 100)]],
    "G": [_arc(30, 50, 28, -50, -270), [(30, 78), (58, 78), (58, 50), (38, 50)]],
    "L": [[(0, 0), (0, 100), (56, 100)]],
    "S": [_arc(30, 28, 22, -30, -270), _arc(30, 72, 22, -90, 150)],
}

WORD = "NACHTGLAS"


def word_polylines(word=WORD, x0=0.0, y0=0.0, scale=1.0):
    """All polylines of the wordmark, laid out and transformed."""
    out, pen = [], x0
    for ch in word:
        for pl in GLYPHS[ch]:
            out.append([(x0 + (pen - x0 + px) * scale, y0 + py * scale) for px, py in pl])
        pen += ADVANCE + TRACKING
    return out


def word_width(word=WORD):
    return len(word) * ADVANCE + (len(word) - 1) * TRACKING


def crack_polyline(width, y_center, amplitude=1.0, seed=7):
    """The hairline fracture that travels through the wordmark."""
    import random
    rng = random.Random(seed)
    pts, x = [], -20.0
    y = y_center + 18 * amplitude
    while x < width + 20:
        pts.append((x, y))
        x += rng.uniform(14, 46)
        y += rng.uniform(-11, 9) * amplitude
        y = max(y_center - 32 * amplitude, min(y_center + 30 * amplitude, y))
    pts.append((width + 20, y_center - 20 * amplitude))
    return pts


# The flame sits in the counter of the SECOND A (index 7 in NACHTGLAS: N A C H T G L A S)
def flame_anchor(word=WORD, index=1):
    """Centre point of the counter of the A at `index` (default: the first A)."""
    return (index * (ADVANCE + TRACKING) + 30.0, 85.0)


def svg_path(pl):
    """Format a polyline as SVG path data.

    Axis-aligned polylines (the H, the T, both A crossbars) have a zero-width or
    zero-height bounding box, and renderers drop those when a filter is in play.
    A 0.02-unit nudge on the last point is invisible and keeps every glyph.
    """
    pts = [list(p) for p in pl]
    if len({round(p[0], 4) for p in pts}) == 1:
        pts[-1][0] += 0.02
    if len({round(p[1], 4) for p in pts}) == 1:
        pts[-1][1] += 0.02
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
