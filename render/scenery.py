# -*- coding: utf-8 -*-
"""NACHTGLAS — procedural location plates.

Each painter returns a high-resolution plate plus metadata (lantern positions,
the ground line figures stand on, and where the shop window is). The frame
renderer crops into the plate for camera moves, so a plate is painted once per
location and reused for the whole episode.
"""
import math, random
from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---- palette ---------------------------------------------------------------
SKY_T, SKY_B = (9, 14, 21), (30, 46, 58)
DAY_T, DAY_B = (150, 162, 172), (196, 200, 198)
DAWN_T, DAWN_B = (44, 62, 84), (146, 158, 162)
INK = (5, 9, 13)
FOGC = (42, 58, 70)
AMBER = (255, 178, 96)
LEDW = (228, 240, 255)
GLASS = (127, 227, 200)
WARM_INT = (58, 44, 32)


def vgrad(size, top, bot, y0=0.0, y1=1.0):
    w, h = size
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = min(1.0, max(0.0, (y / h - y0) / max(1e-6, y1 - y0)))
        d.line([(0, y), (w, y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return img


def ridgeline(d, w, y, amp, color, seed, steps=90, bottom=None):
    r = random.Random(seed)
    pts, yy = [], y
    for i in range(steps + 1):
        x = w * i / steps
        yy += r.uniform(-amp, amp)
        yy = max(y - amp * 5, min(y + amp * 5, yy))
        pts.append((x, yy))
    pts += [(w, bottom or y + 4000), (0, bottom or y + 4000)]
    d.polygon(pts, fill=color)


def facade(img, x0, y0, x1, y1, color, seed, lit=0.18, warm=(210, 170, 110),
           cols=4, rows=5):
    """A building block with a scatter of lit windows, each with real bloom."""
    d = ImageDraw.Draw(img)
    r = random.Random(seed)
    d.rectangle([x0, y0, x1, y1], fill=color)
    ww = (x1 - x0) / (cols * 2 + 1)
    hh = (y1 - y0) / (rows * 2 + 1)
    rects = []
    for c in range(cols):
        for ro in range(rows):
            if r.random() < lit:
                wx = x0 + ww * (1 + c * 2)
                wy = y0 + hh * (1 + ro * 2)
                rects.append((wx, wy, wx + ww, wy + hh, r.uniform(0.55, 1.0)))
    if rects:
        pad = int(max(ww, hh) * 1.6) + 8
        bx0 = int(min(r_[0] for r_ in rects) - pad)
        by0 = int(min(r_[1] for r_ in rects) - pad)
        bx1 = int(max(r_[2] for r_ in rects) + pad)
        by1 = int(max(r_[3] for r_ in rects) + pad)
        bw, bh = max(1, bx1 - bx0), max(1, by1 - by0)
        bloom = Image.new("RGB", (bw, bh), (0, 0, 0))
        bd = ImageDraw.Draw(bloom)
        for wx, wy, wx2, wy2, g in rects:
            bd.rectangle([wx - bx0, wy - by0, wx2 - bx0, wy2 - by0],
                         fill=tuple(int(warm[i] * g) for i in range(3)))
        bloom = bloom.filter(ImageFilter.GaussianBlur(max(3, ww * 0.55)))
        img.paste(ImageChops.add(img.crop((bx0, by0, bx1, by1)), bloom), (bx0, by0))
        for wx, wy, wx2, wy2, g in rects:
            d.rectangle([wx, wy, wx2, wy2], fill=tuple(int(warm[i] * g) for i in range(3)))


def lamp_post(d, x, ybase, h, color=INK, arm=0):
    d.line([(x, ybase), (x, ybase - h)], fill=color, width=max(2, int(h * 0.018)))
    d.line([(x - h * 0.055, ybase - h), (x + h * 0.055, ybase - h)],
           fill=color, width=max(2, int(h * 0.016)))
    d.polygon([(x - h * 0.05, ybase - h), (x + h * 0.05, ybase - h),
               (x + h * 0.032, ybase - h * 1.075), (x - h * 0.032, ybase - h * 1.075)],
              fill=color)


# ---------------------------------------------------------------- plates ----
def plate(loc, W, H):
    """Return (RGB plate, meta)."""
    fn = globals().get("_p_" + loc)
    if fn is None:
        fn = _p_street
    return fn(W, H)


def _p_valley(W, H):
    img = vgrad((W, H), SKY_T, (34, 50, 64), 0, 0.72)
    d = ImageDraw.Draw(img)
    # moon haze
    d.ellipse([W * .70, H * .06, W * .80, H * .22], fill=(46, 64, 80))
    ridgeline(d, W, H * .42, 6, (16, 24, 33), 11, bottom=H)
    ridgeline(d, W, H * .52, 5, (11, 18, 25), 22, bottom=H)
    lamps = []
    r = random.Random(5)
    # the ring of lanterns, seen from above as a necklace round the valley floor
    for i in range(46):
        a = math.pi * (0.06 + 0.88 * i / 45)
        x = W * .5 + math.cos(a) * W * .40 * (1 + r.uniform(-.04, .04))
        y = H * .74 + math.sin(a) * H * .19 * (1 + r.uniform(-.05, .05))
        lamps.append((x, y, H * .012))
    ridgeline(d, W, H * .60, 4, (8, 13, 19), 33, bottom=H)
    for i in range(120):                                    # rooftops
        x = r.uniform(0, W); y = r.uniform(H * .66, H * .95)
        w2 = r.uniform(W * .012, W * .035)
        d.polygon([(x, y), (x + w2, y - w2 * .5), (x + w2 * 2, y)], fill=(9, 14, 20))
    return img, dict(lamps=lamps, base=H * .88, aerial=True)


def _p_bypass(W, H):
    img = vgrad((W, H), SKY_T, (28, 42, 54), 0, 0.62)
    d = ImageDraw.Draw(img)
    ridgeline(d, W, H * .48, 7, (12, 19, 27), 7, bottom=H)
    d.polygon([(W * .10, H), (W * .44, H * .58), (W * .56, H * .58), (W * .95, H)],
              fill=(17, 20, 24))                            # road
    d.line([(W * .50, H * .60), (W * .50, H)], fill=(38, 42, 44), width=int(W * .004))
    lamps = []
    for i in range(6):
        t = i / 5.0
        x = W * (.60 + .26 * t)
        y = H * (.62 + .30 * t)
        h = H * (.10 + .30 * t)
        lamp_post(d, x, y, h)
        lamps.append((x, y - h * 1.02, h * .10))
    lamps = lamps[::-1]
    return img, dict(lamps=lamps, base=H * .90)


def _p_uhlen(W, H, dawn=False):
    img = vgrad((W, H), DAWN_T if dawn else SKY_T,
                DAWN_B if dawn else (26, 40, 52), 0, .58)
    d = ImageDraw.Draw(img)
    wall = (14, 20, 27) if not dawn else (36, 46, 55)
    facade(img, -W * .05, H * .02, W * .30, H, wall, 3, lit=.10 if not dawn else .03)
    facade(img, W * .74, H * .00, W * 1.05, H, wall, 4, lit=.12 if not dawn else .03)
    facade(img, W * .28, H * .16, W * .44, H * .86, (11, 16, 22), 5, lit=.07, cols=3, rows=4)
    facade(img, W * .58, H * .14, W * .76, H * .88, (11, 16, 22), 6, lit=.07, cols=3, rows=4)
    d.polygon([(W * .18, H), (W * .455, H * .60), (W * .545, H * .60), (W * .86, H)],
              fill=(20, 23, 27) if not dawn else (60, 64, 66))
    for i in range(7):                                       # cobble hint
        t = i / 6
        d.line([(W * (.455 - .27 * t), H * (.60 + .40 * t)),
                (W * (.545 + .31 * t), H * (.60 + .40 * t))],
               fill=(26, 30, 34) if not dawn else (68, 72, 74), width=2)
    lamps = []
    for i in range(6):
        t = i / 5.0
        side = -1 if i % 2 == 0 else 1
        x = W * (.5 + side * (.055 + .30 * t))
        y = H * (.615 + .35 * t)
        h = H * (.09 + .33 * t)
        lamp_post(d, x, y, h)
        lamps.append((x, y - h * 1.02, h * .105))
    lamps = lamps[::-1]                                      # index 0 = nearest
    # Blumen Hesse, the shop window
    wx0, wy0, wx1, wy1 = W * .055, H * .50, W * .225, H * .84
    d.rectangle([wx0, wy0, wx1, wy1], fill=(16, 26, 30) if not dawn else (52, 62, 66))
    d.rectangle([wx0, wy0, wx1, wy1], outline=(30, 40, 44), width=3)
    return img, dict(lamps=lamps, base=H * .90, mirror=(wx0, wy0, wx1, wy1))


def _p_dawn(W, H):
    return _p_uhlen(W, H, dawn=True)


def _p_street(W, H):
    img = vgrad((W, H), SKY_T, (28, 42, 54), 0, .60)
    d = ImageDraw.Draw(img)
    facade(img, -W * .04, H * .10, W * .34, H, (13, 19, 26), 9, lit=.11)
    facade(img, W * .66, H * .06, W * 1.04, H, (13, 19, 26), 10, lit=.11)
    facade(img, W * .34, H * .28, W * .66, H * .80, (10, 15, 21), 12, lit=.08, cols=5, rows=3)
    d.rectangle([0, H * .80, W, H], fill=(19, 22, 26))
    lamps = []
    for i, x in enumerate((.14, .40, .62, .88)):
        h = H * .40
        lamp_post(d, W * x, H * .84, h)
        lamps.append((W * x, H * .84 - h * 1.02, h * .11))
    lamps += lamps[:2]
    wx0, wy0, wx1, wy1 = W * .70, H * .46, W * .90, H * .78
    d.rectangle([wx0, wy0, wx1, wy1], fill=(16, 26, 30), outline=(30, 40, 44), width=3)
    return img, dict(lamps=lamps, base=H * .88, mirror=(wx0, wy0, wx1, wy1))


def _p_markt(W, H):
    img = vgrad((W, H), DAY_T, DAY_B, 0, .55)
    d = ImageDraw.Draw(img)
    facade(img, -W * .03, H * .10, W * .36, H * .78, (96, 100, 104), 21, lit=0)
    facade(img, W * .64, H * .06, W * 1.03, H * .78, (88, 92, 98), 22, lit=0)
    facade(img, W * .36, H * .24, W * .64, H * .74, (104, 106, 108), 23, lit=0)
    d.rectangle([0, H * .74, W, H], fill=(118, 118, 116))
    for i in range(24):                                      # cobbles
        d.line([(0, H * (.74 + .011 * i)), (W, H * (.74 + .011 * i))],
               fill=(110, 110, 108), width=2)
    # the iron-and-glass bandstand
    d.polygon([(W * .42, H * .70), (W * .50, H * .52), (W * .58, H * .70)], fill=(70, 76, 78))
    for x in (.43, .47, .53, .57):
        d.line([(W * x, H * .70), (W * x, H * .84)], fill=(70, 76, 78), width=4)
    # cherry-picker
    d.line([(W * .74, H * .86), (W * .74, H * .40)], fill=(190, 120, 30), width=int(W * .008))
    d.rectangle([W * .70, H * .34, W * .79, H * .42], outline=(190, 120, 30), width=4)
    lamps = []
    for x in (.18, .30, .66, .82):
        h = H * .30
        lamp_post(d, W * x, H * .78, h, color=(62, 66, 70))
        lamps.append((W * x, H * .78 - h * 1.02, h * .10))
    lamps += lamps[:2]
    return img, dict(lamps=lamps, base=H * .84, day=True)


def _p_class(W, H):
    img = Image.new("RGB", (W, H), (30, 34, 36))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H * .72], fill=(34, 39, 41))
    d.rectangle([0, H * .72, W, H], fill=(24, 26, 26))
    for k, x in enumerate((.05, .39, .73)):                  # tall rain-lit windows
        d.rectangle([W * x, H * .08, W * (x + .21), H * .68], fill=(74, 88, 96))
        d.rectangle([W * x, H * .08, W * (x + .21), H * .30], fill=(86, 100, 108))
        d.rectangle([W * x, H * .08, W * (x + .21), H * .68], outline=(20, 23, 25), width=6)
        d.line([(W * (x + .105), H * .08), (W * (x + .105), H * .68)],
               fill=(20, 23, 25), width=5)
        r = random.Random(70 + k)
        for _ in range(140):                                 # rain on the glass
            rx = r.uniform(W * x, W * (x + .21)); ry = r.uniform(H * .08, H * .68)
            d.line([(rx, ry), (rx - 2, ry + r.uniform(10, 30))], fill=(112, 128, 136), width=1)
    for row in range(3):                                     # desks and chairs
        y = H * (.70 + row * .105)
        for c in range(5):
            x = W * (.04 + c * .195) + row * W * .012
            d.rectangle([x, y, x + W * .135, y + H * .045], fill=(96, 78, 56))
            d.rectangle([x + W * .01, y + H * .045, x + W * .125, y + H * .075],
                        fill=(30, 32, 32))
    lamps = [(W * .24, H * .035, H * .05), (W * .58, H * .035, H * .05),
             (W * .86, H * .035, H * .05)]
    return img, dict(lamps=lamps, base=H * .84, interior=True, day=True)


def _p_kiosk(W, H):
    img = Image.new("RGB", (W, H), (30, 24, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(36, 28, 22))
    for r_ in range(5):                                      # shelves of stock
        y = H * (.12 + r_ * .15)
        d.rectangle([W * .04, y, W * .44, y + H * .11], fill=(52, 42, 32))
        rr = random.Random(90 + r_)
        for c in range(9):
            x = W * .05 + c * W * .043
            d.rectangle([x, y + H * .01, x + W * .033, y + H * .10],
                        fill=(rr.randint(44, 104), rr.randint(34, 82), rr.randint(24, 62)))
    d.rectangle([W * .52, H * .06, W * .96, H * .62], fill=(64, 78, 84))   # window to the street
    d.rectangle([W * .52, H * .06, W * .96, H * .62], outline=(24, 20, 16), width=6)
    d.rectangle([0, H * .66, W, H], fill=(46, 36, 28))       # counter
    d.ellipse([W * .60, H * .12, W * .68, H * .20], fill=(180, 150, 100))  # hanging bulb
    return img, dict(lamps=[(W * .64, H * .16, H * .10)], base=H * .78, interior=True, warm=True)


def _p_back(W, H):
    img = Image.new("RGB", (W, H), (26, 24, 22))
    d = ImageDraw.Draw(img)
    r = random.Random(31)
    for i in range(16):                                      # crates
        x = r.uniform(0, W * .9); y = r.uniform(H * .45, H * .85)
        s = r.uniform(W * .06, W * .13)
        d.rectangle([x, y, x + s, y + s * .7], fill=(58, 48, 36), outline=(34, 28, 22), width=3)
    d.ellipse([W * .46, H * .04, W * .54, H * .12], fill=(210, 180, 120))
    d.rectangle([W * .18, H * .58, W * .82, H * .74], fill=(60, 54, 44))   # the crate table
    d.rectangle([W * .30, H * .56, W * .70, H * .64], fill=(196, 190, 172))  # the map
    return img, dict(lamps=[(W * .50, H * .08, H * .16)], base=H * .84, interior=True, warm=True)


def _p_tanke(W, H):
    img = vgrad((W, H), SKY_T, (26, 36, 46), 0, .5)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H * .70, W, H], fill=(34, 34, 34))
    d.rectangle([W * .08, H * .18, W * .92, H * .28], fill=(46, 48, 50))   # canopy
    for x in (.14, .86):
        d.line([(W * x, H * .28), (W * x, H * .78)], fill=(46, 48, 50), width=int(W * .012))
    for x in (.34, .62):                                     # pumps
        d.rectangle([W * x, H * .52, W * (x + .07), H * .78], fill=(52, 54, 56))
    d.rectangle([W * .18, H * .34, W * .44, H * .70], fill=(64, 70, 74))   # shop
    lamps = [(W * .30, H * .245, H * .13), (W * .70, H * .245, H * .13)]
    return img, dict(lamps=lamps, base=H * .82, sodium=True)


def _p_torhaus(W, H):
    img = vgrad((W, H), SKY_T, (24, 36, 46), 0, .5)
    d = ImageDraw.Draw(img)
    d.rectangle([W * .16, H * .18, W * .84, H], fill=(20, 26, 30))         # the gatehouse
    d.polygon([(W * .12, H * .20), (W * .50, H * .04), (W * .88, H * .20)], fill=(16, 21, 25))
    lamps = []
    for i, (x, y) in enumerate([(.26, .34), (.44, .34), (.62, .34), (.74, .34),
                                (.30, .60), (.50, .60), (.70, .60)]):
        d.rectangle([W * (x - .05), H * (y - .09), W * (x + .05), H * (y + .09)],
                    fill=(214, 178, 116), outline=(12, 16, 20), width=4)
        lamps.append((W * x, H * y, H * .11))
    d.rectangle([W * .46, H * .74, W * .58, H], fill=(12, 16, 20))         # door
    return img, dict(lamps=lamps, base=H * .92, house=True)


def _p_peperoom(W, H):
    img = Image.new("RGB", (W, H), (20, 22, 26))
    d = ImageDraw.Draw(img)
    d.rectangle([W * .18, H * .12, W * .82, H * .78], fill=(30, 44, 56))   # window
    d.rectangle([W * .18, H * .12, W * .82, H * .78], outline=(14, 16, 20), width=8)
    d.line([(W * .50, H * .12), (W * .50, H * .78)], fill=(14, 16, 20), width=6)
    d.rectangle([W * .18, H * .55, W * .82, H * .60], fill=(24, 34, 42))   # street below
    lamps = [(W * .30, H * .40, H * .07), (W * .62, H * .38, H * .07),
             (W * .44, H * .44, H * .06)]
    r = random.Random(8)
    for _ in range(24):                                                    # glow-stars
        sx, sy, ss = r.uniform(0, W), r.uniform(0, H * .10), r.uniform(3, 7)
        d.ellipse([sx, sy, sx + ss, sy + ss], fill=(58, 74, 62))
    return img, dict(lamps=lamps, base=H * .88, interior=True)


def _p_bauhof(W, H):
    img = vgrad((W, H), SKY_T, (24, 34, 44), 0, .5)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H * .72, W, H], fill=(30, 32, 34))
    for x in range(0, W, int(W * .022)):                     # chain-link fence
        d.line([(x, H * .30), (x, H * .78)], fill=(48, 54, 58), width=2)
    d.line([(0, H * .30), (W, H * .30)], fill=(56, 62, 66), width=5)
    d.rectangle([W * .30, H * .40, W * .74, H * .74], fill=(46, 50, 54))   # the van
    d.rectangle([W * .30, H * .42, W * .44, H * .56], fill=(70, 80, 88))
    for i in range(3):                                                     # crates in straw
        d.rectangle([W * (.34 + i * .12), H * .60, W * (.44 + i * .12), H * .72],
                    fill=(72, 60, 42), outline=(36, 30, 22), width=3)
    lamps = [(W * .10, H * .26, H * .10)]
    return img, dict(lamps=lamps, base=H * .84)


def _p_lantern(W, H):
    img = vgrad((W, H), SKY_T, (26, 38, 50), 0, .55)
    d = ImageDraw.Draw(img)
    facade(img, -W * .1, 0, W * .34, H, (14, 20, 27), 41, lit=.06)
    facade(img, W * .72, 0, W * 1.1, H, (14, 20, 27), 42, lit=.06)
    d.rectangle([0, H * .84, W, H], fill=(20, 23, 27))
    lamp_post(d, W * .50, H * .88, H * .74)                  # the pole, close
    lamps = [(W * .50, H * .88 - H * .755, H * .085)]
    for k in range(5):
        lamps.append((W * (.14 + .18 * k), H * .30, H * .03))
    return img, dict(lamps=lamps, base=H * .90)


def _p_window(W, H):
    img = Image.new("RGB", (W, H), (12, 18, 22))
    d = ImageDraw.Draw(img)
    d.rectangle([W * .10, H * .08, W * .90, H * .92], fill=(18, 28, 33))
    d.rectangle([W * .10, H * .08, W * .90, H * .92], outline=(34, 44, 48), width=10)
    for i in range(6):                                       # chrysanthemum buckets
        x = W * (.16 + i * .12)
        d.rectangle([x, H * .74, x + W * .07, H * .88], fill=(30, 40, 44))
        d.ellipse([x - W * .01, H * .66, x + W * .08, H * .76], fill=(44, 56, 58))
    return img, dict(lamps=[], base=H * .92,
                     mirror=(W * .10, H * .08, W * .90, H * .92), closeup=True)
