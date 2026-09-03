# -*- coding: utf-8 -*-
"""NACHTGLAS 1.01 — picture renderer.

Paints the episode as a cinematic animatic: procedural location plates, real
camera moves cropped out of oversized plates, lantern glow that goes out lamp
by lamp, drifting volumetric fog, silhouette blocking with per-character rim
light, the marble-vision optical treatment, German subtitles and film grain.
Frames are piped straight into ffmpeg.
"""
import os, sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from episode import build_timeline, CHARS
import scenery
from glyphs import word_polylines, word_width, crack_polyline, flame_anchor, STROKE, CAP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1440, 602            # 2.39:1
FPS = 24
PW, PH = int(W * 1.55), int(H * 1.55)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_SUB = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 27)
F_SPK = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 27)
F_CAP = ImageFont.truetype(FONT_DIR + "DejaVuSerif.ttf", 23)
F_SLUG = ImageFont.truetype(FONT_DIR + "DejaVuSansMono.ttf", 17)
F_ACT = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 46)
F_TAG = ImageFont.truetype(FONT_DIR + "DejaVuSerif.ttf", 20)

def _CONTRAST(im):
    """Show LUT: lift the highlights, crush the toe, keep the blacks blue."""
    return im.point(_LUT_R + _LUT_G + _LUT_B)


def _mk_lut(gain, lift):
    out = []
    for v in range(256):
        x = v / 255.0
        x = (x - 0.055) / 0.945
        x = max(0.0, x)
        y = x ** 0.92
        y = y * gain + lift
        out.append(min(255, max(0, int(y * 255))))
    return out


_LUT_R = _mk_lut(1.10, 0.004)
_LUT_G = _mk_lut(1.08, 0.008)
_LUT_B = _mk_lut(1.05, 0.020)

AMBER = (255, 178, 96)
GLASSC = (127, 227, 200)
rnd = random.Random(1893)


# ------------------------------------------------------------- sprites ------
def glow_sprite(radius, color, intensity=1.0, falloff=2.1):
    """A soft light with a visible glow ring. Built once, pasted many times."""
    r = max(6, int(radius))
    size = r * 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y in range(size):
        dy = (y - r) / r
        for x in range(size):
            dx = (x - r) / r
            d = math.hypot(dx, dy)
            if d >= 1.0:
                continue
            a = (1.0 - d) ** falloff
            a = a * 0.85 + (1.0 - d) ** 8 * 0.9
            px[x, y] = (color[0], color[1], color[2], min(255, int(255 * a * intensity)))
    return img


_GLOW = {}


def glow(radius, color, intensity=1.0):
    key = (int(radius / 4) * 4, color, round(intensity, 1))
    if key not in _GLOW:
        _GLOW[key] = glow_sprite(key[0], color, intensity)
    return _GLOW[key]


def figure_sprite(build, h, accent):
    """Silhouette blocking with a coloured rim. Consistency for free."""
    h = max(24, int(h))
    w = int(h * 0.62)
    img = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))

    def body(d, col, ox=0, oy=0):
        cx = w / 2 + ox
        f = {"small": .96, "tall": .94, "parka": 1.16, "broad": 1.14,
             "heavy": 1.20, "child": 1.0, "adult": 1.02, "loescher": .70}.get(build, 1.0)
        hr = h * (0.058 if build != "child" else 0.070)
        hy = oy + h * 0.072
        sy = oy + h * (0.165 if build != "child" else 0.185)
        py = oy + h * (0.505 if build != "child" else 0.535)
        sw2 = h * 0.118 * f
        pw2 = h * 0.086 * f
        d.line([(cx, hy + hr * .6), (cx, sy)], fill=col, width=max(2, int(h * .030)))
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=col)
        d.polygon([(cx - sw2, sy), (cx + sw2, sy), (cx + pw2, py), (cx - pw2, py)], fill=col)
        lw = max(3, int(h * .072))
        d.line([(cx - pw2 * .48, py), (cx - pw2 * .58, oy + h)], fill=col, width=lw)
        d.line([(cx + pw2 * .48, py), (cx + pw2 * .62, oy + h)], fill=col, width=lw)
        aw = max(2, int(h * .040))
        d.line([(cx - sw2 * .92, sy + h * .015), (cx - sw2 * 1.02, py + h * .045)],
               fill=col, width=aw)
        d.line([(cx + sw2 * .92, sy + h * .015), (cx + sw2 * 1.00, py + h * .045)],
               fill=col, width=aw)

    d = ImageDraw.Draw(img)
    r_off = max(2, int(h * 0.016))
    body(d, accent + (215,), ox=-r_off, oy=-r_off)   # rim light, offset up-left
    body(d, (6, 9, 12, 255))
    return img


_FIG = {}


def figure(key, h):
    k = (key, int(h / 6) * 6)
    if k not in _FIG:
        _FIG[k] = figure_sprite(CHARS[key]["build"], k[1], CHARS[key]["col"])
    return _FIG[k]


def loescher_sprite(h):
    """Two metres forty. He is never animated in locomotion."""
    h = max(40, int(h))
    w = int(h * 0.42)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w / 2
    d.polygon([(cx - w * .16, h * .13), (cx + w * .16, h * .13),
               (cx + w * .40, h), (cx - w * .40, h)], fill=(3, 5, 7, 255))
    d.ellipse([cx - w * .155, h * .01, cx + w * .155, h * .17], fill=(9, 13, 17, 255))
    d.ellipse([cx - w * .11, h * .035, cx + w * .11, h * .145], fill=(17, 24, 30, 255))
    d.line([(cx + w * .30, h * .30), (cx + w * .46, h * .52)], fill=(3, 5, 7, 255),
           width=max(2, int(w * .06)))
    lx, ly = cx + w * .46, h * .52                       # the Leerlaterne
    s = h * .055
    d.rectangle([lx - s, ly, lx + s, ly + s * 2.1], outline=(14, 18, 22, 255),
                width=max(2, int(s * .32)))
    return img


_LO = {}


def loescher(h):
    k = int(h / 8) * 8
    if k not in _LO:
        _LO[k] = loescher_sprite(k)
    return _LO[k]


def fog_layer(seed, scale=1.0):
    """Pre-blurred noise used as drifting volumetric fog."""
    small = Image.new("L", (120, 50))
    r = random.Random(seed)
    small.putdata([r.randint(0, 255) for _ in range(120 * 50)])
    big = small.resize((PW * 2, PH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(26))
    return big


_FOG = None


def fog():
    global _FOG
    if _FOG is None:
        _FOG = [fog_layer(1), fog_layer(2)]
    return _FOG


_SHADOW = {}


def shadow(w_, h_):
    """A soft dark oval - the Loescher takes light out of the frame around him."""
    k = (int(w_ / 16) * 16, int(h_ / 16) * 16)
    if k not in _SHADOW:
        a = Image.new("L", k, 0)
        ImageDraw.Draw(a).ellipse([k[0] * .12, k[1] * .06, k[0] * .88, k[1] * .94], fill=105)
        _SHADOW[k] = a.filter(ImageFilter.GaussianBlur(max(6, k[0] // 9)))
    return _SHADOW[k]


_GROUND = None


def ground_mask():
    """Fog belongs on the ground, not over the sky."""
    global _GROUND
    if _GROUND is None:
        m = Image.new("L", (1, H))
        m.putdata([int(255 * min(1.0, max(0.06, (y / H - 0.18) / 0.55) ** 1.3))
                   for y in range(H)])
        _GROUND = m.resize((W, H))
    return _GROUND


_VMASK = None


def vision_mask():
    global _VMASK
    if _VMASK is None:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([W * .06, -H * .16, W * .94, H * 1.16], fill=255)
        _VMASK = m.filter(ImageFilter.GaussianBlur(70))
    return _VMASK


_VIGN = None


def vignette():
    global _VIGN
    if _VIGN is None:
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.ellipse([-W * .30, -H * .42, W * 1.30, H * 1.42], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(90))
        v = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        v.putalpha(ImageChops.invert(m).point(lambda a: int(a * 0.62)))
        _VIGN = v
    return _VIGN


_GRAIN = None


def grain_tiles():
    global _GRAIN
    if _GRAIN is None:
        _GRAIN = []
        for k in range(6):
            r = random.Random(400 + k)
            g = Image.new("L", (W // 2, H // 2))
            g.putdata([r.randint(122, 133) for _ in range(W // 2 * H // 2)])
            _GRAIN.append(g.resize((W, H), Image.BILINEAR).convert("RGB"))
    return _GRAIN


# -------------------------------------------------------------- camera ------
def crop_box(cam, u, seed=0):
    """Return the crop rectangle in plate space for progress u in [0,1]."""
    ar = W / H
    cx, cy, z = 0.5, 0.5, 0.985
    e = u * u * (3 - 2 * u)                       # ease in/out
    if cam == "push":
        z = 0.99 - 0.115 * e
    elif cam == "pull":
        z = 0.875 + 0.115 * e
    elif cam == "pan_r":
        z, cx = 0.90, 0.40 + 0.20 * e
    elif cam == "pan_l":
        z, cx = 0.90, 0.60 - 0.20 * e
    elif cam == "crane":
        z, cy = 0.95 - 0.12 * e, 0.60 - 0.26 * e
    elif cam == "descend":
        z, cy = 1.0 - 0.06 * e, 0.28 + 0.34 * e
    elif cam == "orbit":
        z, cx = 0.90, 0.5 + 0.10 * math.sin(u * math.pi * 1.2)
    elif cam == "handheld":
        z = 0.92
    else:                                         # static still breathes
        z = 0.985 - 0.012 * e
    cw = PW * z
    ch = cw / ar
    if ch > PH:
        ch = PH; cw = ch * ar
    if cam == "handheld":
        r = random.Random(seed)
        f = seed * 0.0
        cx += 0.010 * math.sin(u * 41.0 + seed) + 0.004 * math.sin(u * 97.0 + seed * 2)
        cy += 0.009 * math.sin(u * 33.0 + seed * 3) + 0.004 * math.sin(u * 71.0 + seed)
    x0 = min(max(0, cx * PW - cw / 2), PW - cw)
    y0 = min(max(0, cy * PH - ch / 2), PH - ch)
    return (int(x0), int(y0), int(x0 + cw), int(y0 + ch))


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines


def subtitle_sprite(speaker, text, whisper=False, shout=False, mouthed=False, vo=False):
    img = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = CHARS.get(speaker, {}).get("col", (200, 200, 200))
    col = tuple(min(255, int(c * 1.35 + 40)) for c in col)
    name = speaker
    if vo:
        name += " (O.S.)"
    if mouthed:
        name += " (lautlos)"
    body = (238, 244, 246)
    if whisper:
        body = (188, 200, 204)
    if shout:
        body = (255, 252, 244)
    lines = wrap(text, F_SUB, W * 0.74)
    y = 8
    nw = d.textlength(name, font=F_SPK)
    d.text(((W - nw) / 2, y), name, font=F_SPK, fill=col)
    y += 34
    for ln in lines:
        lw = d.textlength(ln, font=F_SUB)
        d.text(((W - lw) / 2 + 2, y + 2), ln, font=F_SUB, fill=(0, 0, 0, 170))
        d.text(((W - lw) / 2, y), ln, font=F_SUB, fill=body)
        y += 34
    return img.crop((0, 0, W, min(150, y + 8)))


def caption_sprite(text):
    img = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 6
    for ln in wrap(text, F_CAP, W * 0.68):
        lw = d.textlength(ln, font=F_CAP)
        d.text(((W - lw) / 2 + 2, y + 2), ln, font=F_CAP, fill=(0, 0, 0, 160))
        d.text(((W - lw) / 2, y), ln, font=F_CAP, fill=(178, 196, 198))
        y += 30
    return img.crop((0, 0, W, y + 6))


# --------------------------------------------------------- title cards ------
def wordmark(size, scale, origin, crack_t=1.0, flame=0.0, col=(191, 233, 222), alpha=255):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = origin
    sw = max(1, int(round(STROKE * scale)))
    for pl in word_polylines(x0=0, y0=0, scale=scale):
        d.line([(ox + x, oy + y) for x, y in pl], fill=col + (alpha,), width=sw, joint="curve")
    if crack_t > 0:
        mask = Image.new("L", size, 0)
        md = ImageDraw.Draw(mask)
        for pl in word_polylines(x0=0, y0=0, scale=scale):
            md.line([(ox + x, oy + y) for x, y in pl], fill=255, width=sw, joint="curve")
        cl = Image.new("RGBA", size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        pts = [(ox + x * scale, oy + y * scale) for x, y in crack_polyline(word_width(), CAP / 2)]
        cut = max(2, int(len(pts) * crack_t))
        cd.line(pts[:cut], fill=(4, 19, 26, 200), width=max(1, int(2.2 * scale)), joint="curve")
        cd.line(pts[:cut], fill=(234, 255, 248, 220), width=max(1, int(1.2 * scale)), joint="curve")
        cl.putalpha(ImageChops.multiply(cl.split()[3], mask))
        img = Image.alpha_composite(img, cl)
    if flame > 0:
        fx, fy = flame_anchor()
        fx, fy = ox + fx * scale, oy + fy * scale
        r = 9.0 * scale * flame
        fl = Image.new("RGBA", size, (0, 0, 0, 0))
        fd = ImageDraw.Draw(fl)
        fd.ellipse([fx - r * .62, fy - r * 1.9, fx + r * .62, fy + r * .95], fill=AMBER + (255,))
        fd.ellipse([fx - r * .28, fy - r * 1.0, fx + r * .28, fy + r * .42], fill=(255, 240, 210, 255))
        img = Image.alpha_composite(img, fl)
    return img


def render_title(fx, u):
    """The 40-second main title, as one continuous move."""
    fr = Image.new("RGB", (W, H), (4, 6, 8))
    d = ImageDraw.Draw(fr)
    stage = fx.get("t", "gather")
    cx, cy = W / 2, H * 0.47

    if stage in ("gather", "globe", "face", "cool", "fog"):
        if stage == "gather":
            r = H * (0.035 + 0.30 * u)
            col = (255, int(150 + 40 * u), 60)
        elif stage == "globe":
            r = H * (0.34 + 0.05 * u); col = (255, 186, 96)
        elif stage == "face":
            r = H * 0.38; col = (250, 196, 120)
        elif stage == "cool":
            k = u
            r = H * 0.38
            col = (int(255 - 128 * k), int(190 + 20 * k), int(96 + 104 * k))
        else:
            r = H * 0.38; col = GLASSC
        fr.paste(glow(int(r * 2.3), col, 0.55),
                 (int(cx - r * 2.3), int(cy - r * 2.3)), glow(int(r * 2.3), col, 0.55))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * .32) for c in col))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(2, int(r * .05)))
        d.ellipse([cx - r * .62, cy - r * .66, cx - r * .40, cy - r * .48],
                  fill=tuple(min(255, int(c * .45 + 30)) for c in col))
        if stage == "gather":
            d.line([(cx, cy - r), (cx, -20)], fill=(70, 60, 52), width=int(H * .022))
        if stage == "face":
            who = fx.get("who", "JUNO")
            fh = int(r * 3.1)
            sp = figure(who, fh)
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).ellipse([cx - r * .94, cy - r * .94, cx + r * .94, cy + r * .94],
                                      fill=255)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            px = int(cx - sp.width / 2 + (u - 0.5) * r * 0.9)
            lay.paste(sp, (px, int(cy - fh * .18)), sp)
            lay.putalpha(ImageChops.multiply(lay.split()[3], m))
            fr = Image.alpha_composite(fr.convert("RGBA"), lay).convert("RGB")
            d = ImageDraw.Draw(fr)
            nm = who
            nw = d.textlength(nm, font=F_SPK)
            a = int(255 * min(1, math.sin(u * math.pi) * 1.6))
            d.text(((W - nw) / 2, cy + r + 26), nm, font=F_SPK,
                   fill=(CHARS[who]["col"][0] + 60, CHARS[who]["col"][1] + 60,
                         CHARS[who]["col"][2] + 60))
        if stage == "fog":
            for k in range(6):
                lx = cx - r * .6 + k * r * .24
                ly = cy + r * .1 - k * r * .05
                if k < 6 - int(u * 6):
                    g = glow(int(r * .16), AMBER, .9)
                    fr.paste(g, (int(lx - r * .16), int(ly - r * .16)), g)

    elif stage in ("crack", "hold", "endcard"):
        ww = word_width()
        scale = (W * 0.70) / ww
        ox, oy = (W - ww * scale) / 2, H * 0.40
        ct = u if stage == "crack" else 1.0
        fl = 0.0 if stage == "crack" else min(1.0, u * 2.2)
        if stage == "endcard":
            ct, fl = 1.0, 1.0
        mk = wordmark((W, H), scale, (ox, oy), crack_t=ct, flame=fl)
        halo = mk.filter(ImageFilter.GaussianBlur(16))
        fr = Image.alpha_composite(fr.convert("RGBA"), halo)
        fr = Image.alpha_composite(fr, mk).convert("RGB")
        if stage in ("hold", "endcard"):
            d = ImageDraw.Draw(fr)
            tag = "WAS  DAS  LICHT  VERGISST,  BEHÄLT  DAS  GLAS."
            tw = d.textlength(tag, font=F_TAG)
            a = min(1.0, u * 2.0)
            d.text(((W - tw) / 2, oy + CAP * scale + 46), tag, font=F_TAG,
                   fill=(int(122 * a), int(167 * a), int(158 * a)))
    return fr


# ----------------------------------------------------------- the frame -----
_PLATES = {}


def get_plate(loc):
    if loc not in _PLATES:
        _PLATES[loc] = scenery.plate(loc, PW, PH)
    return _PLATES[loc]


def render_frame(shot, u, fi):
    fx = shot["fx"]
    if shot["loc"] == "title":
        fr = render_title(fx, u)
    else:
        plate, meta = get_plate(shot["loc"])
        cam = fx.get("cam", "static")
        box = crop_box(cam, u, seed=shot["idx"])
        sx, sy = W / (box[2] - box[0]), H / (box[3] - box[1])
        fr = plate.crop(box).resize((W, H), Image.BILINEAR)

        def px(x, y):
            return ((x - box[0]) * sx, (y - box[1]) * sy)

        lamps = meta["lamps"]
        outs = set(fx.get("lamps_out", []))
        night = not meta.get("day")
        lamps_in = fx.get("lamps_in")
        ring = fx.get("ring")
        blackout = fx.get("flash") == "black"

        # ---- lantern light: islands, going out one by one
        if night and not blackout:
            for i, (lx, ly, lr) in enumerate(lamps):
                on = 1.0
                if i in outs:
                    on = 0.0
                if lamps_in:
                    on = min(1.0, max(0.0, (u * 6.0) - i * 0.8))
                if ring:
                    on = min(1.0, max(0.0, u * 4.0 - i * 0.25))
                if on <= 0.01:
                    continue
                flick = 1.0 + 0.045 * math.sin(fi * 0.11 + i * 2.3)
                col = AMBER if not meta.get("sodium") else (255, 160, 70)
                if meta.get("house"):
                    col = (255, 196, 120)
                gx, gy = px(lx, ly)
                r = max(8, lr * sx * 3.1)
                g = glow(int(r), col, 0.95 * on * flick)
                fr.paste(g, (int(gx - r), int(gy - r)), g)
                c = glow(int(max(5, lr * sx * 0.9)), (255, 236, 205), 1.0 * on)
                fr.paste(c, (int(gx - c.width / 2), int(gy - c.height / 2)), c)

        # ---- practical sources
        fl = fx.get("flash")
        if fl == "engine":                              # a beam, not a blob
            cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(cone).polygon(
                [(W * .50, H * .70), (W * .17, H), (W * .83, H)], fill=(206, 220, 238, 40))
            fr = Image.alpha_composite(fr.convert("RGBA"),
                                       cone.filter(ImageFilter.GaussianBlur(26))).convert("RGB")
            g = glow(int(W * .13), (236, 244, 252), .70)
            fr.paste(g, (int(W * .5 - g.width / 2), int(H * .70 - g.height / 2)), g)
        elif fl == "flare":
            fk = 0.75 + 0.25 * math.sin(fi * 0.9)
            g = glow(int(W * .30), (255, 92, 60), .8 * fk)
            fr.paste(g, (int(W * .34 - g.width / 2), int(H * .60 - g.height / 2)), g)
        elif fl == "die":
            k = max(0.0, 1.0 - u * 1.5)
            g = glow(int(W * .30 * (0.4 + 0.6 * k)), (255, 92, 60), .8 * k)
            fr.paste(g, (int(W * .34 - g.width / 2), int(H * .60 - g.height / 2)), g)
        elif fl == "torch":
            for k in range(5):
                if u * 5 > k:
                    g = glow(int(W * .07), (226, 238, 252), .55)
                    fr.paste(g, (int(W * (.34 + .08 * k) - g.width / 2),
                                 int(H * .58 - g.height / 2)), g)

        # ---- fog
        if night or meta.get("day"):
            fl1, fl2 = fog()
            d1 = int((fi * 0.55) % (fl1.width - W))
            d2 = int((fi * 0.24) % (fl2.width - W))
            k = 0.16 if meta.get("day") else (0.30 if not fx.get("collapse") else 0.40)
            for src, dx_, kk in ((fl1, d1, k), (fl2, d2, k * 0.6)):
                m = src.crop((dx_, 0, dx_ + W, H)).point(lambda a: int(a * kk))
                m = ImageChops.multiply(m, ground_mask())      # fog pools at ground level
                fr.paste(Image.new("RGB", (W, H), scenery.FOGC), (0, 0), m)

        # ---- blocking
        base = meta["base"]
        for key, fxn, sc in fx.get("figs", []):
            hgt = H * 0.40 * sc * sy / (PH / H) * 1.55
            sp = figure(key, hgt)
            gx, gy = px(fxn * PW, base)
            fr.paste(sp, (int(gx - sp.width / 2), int(gy - sp.height)), sp)

        # ---- der Loescher
        lo = fx.get("lo")
        if lo is not None:
            lh = H * (0.62 if fx.get("lo_near") else 0.34) * sy / (PH / H) * 1.55
            sp = loescher(lh)
            if fx.get("lo_glass"):
                sp = sp.copy()
                al = sp.split()[3].point(lambda a: int(a * 0.42))
                sp.putalpha(al)
            gx, gy = px(lo * PW, base)
            fr.paste(sp, (int(gx - sp.width / 2), int(gy - sp.height)), sp)
            if not blackout:
                aur = shadow(int(sp.width * 1.7), int(sp.height * 1.1))
                fr.paste(Image.new("RGB", aur.size, (0, 0, 0)),
                         (int(gx - aur.width / 2), int(gy - aur.height * .92)), aur)

        # ---- the taken, in the glass
        mir = fx.get("mirror")
        if mir and meta.get("mirror"):
            mx0, my0, mx1, my1 = meta["mirror"]
            a0 = px(mx0, my0); a1 = px(mx1, my1)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            mh = (a1[1] - a0[1]) * (0.82 if mir != "PEPE" else 0.55)
            sp = figure_sprite(CHARS[mir]["build"], mh, GLASSC)
            tint = Image.new("RGBA", sp.size, GLASSC + (0,))
            tint.putalpha(sp.split()[3].point(lambda a_: int(a_ * 0.80)))
            lay.paste(tint, (int((a0[0] + a1[0]) / 2 - sp.width / 2), int(a1[1] - mh)), tint)
            lay = lay.filter(ImageFilter.GaussianBlur(2))
            fr = Image.alpha_composite(fr.convert("RGBA"), lay).convert("RGB")
            g = glow(int((a1[0] - a0[0]) * .7), GLASSC, .30)
            fr.paste(g, (int((a0[0] + a1[0]) / 2 - g.width / 2),
                         int((a0[1] + a1[1]) / 2 - g.height / 2)), g)

        # ---- marble vision: seams of light, and everyone who is already inside
        if fx.get("vision"):
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            pts = [px(l[0], l[1]) for l in lamps]
            for i in range(len(pts) - 1):
                ph = (fi * 0.03 + i * 0.6) % 1.0
                a = int(120 + 90 * math.sin(ph * 6.283))
                dl.line([pts[i], pts[i + 1]], fill=GLASSC + (a,), width=3)
            for cw in range(fx.get("crowd", 0)):
                r = random.Random(900 + cw)
                fxn = r.uniform(0.02, 0.98)
                depth = r.uniform(0.25, 1.0)
                hgt = H * 0.30 * depth
                sp = figure_sprite("adult", hgt, GLASSC)
                t2 = Image.new("RGBA", sp.size, GLASSC + (0,))
                t2.putalpha(sp.split()[3].point(lambda a_: int(a_ * (0.30 + 0.35 * depth))))
                yy = H * (0.62 + 0.30 * (1 - depth))
                lay.paste(t2, (int(fxn * W - sp.width / 2), int(yy - hgt)), t2)
            lay = lay.filter(ImageFilter.GaussianBlur(1.4))
            fr = Image.alpha_composite(fr.convert("RGBA"), lay).convert("RGB")
            tintl = Image.new("RGBA", (W, H), (34, 92, 84, 46))
            fr = Image.alpha_composite(fr.convert("RGBA"), tintl).convert("RGB")
            fr = Image.composite(fr, Image.new("RGB", (W, H), (3, 8, 9)), vision_mask())

        # ---- the blackout: five marbles and five pairs of eyes
        if blackout:
            fr = Image.new("RGB", (W, H), (2, 3, 4))
            if fx.get("marbles"):
                for k in range(5):
                    g = glow(int(W * .020), GLASSC, .40 + .16 * math.sin(fi * .2 + k))
                    fr.paste(g, (int(W * (.30 + .10 * k) - g.width / 2),
                                 int(H * (.60 + .02 * math.sin(k * 2.0)) - g.height / 2)), g)
            if fx.get("lo") is not None:
                sp = loescher(H * 0.72)
                dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                sp2 = sp.copy(); sp2.putalpha(sp.split()[3].point(lambda a_: int(a_ * 0.55)))
                dark.paste(sp2, (int(W * .5 - sp.width / 2), int(H * .16)), sp2)
                fr = Image.alpha_composite(fr.convert("RGBA"), dark).convert("RGB")

        if fx.get("bend"):
            fr = fr.transform((W, H), Image.AFFINE,
                              (1, 0.02 * math.sin(u * 3.0), -6, 0, 1, 0), Image.BILINEAR)

    # ---- vignette, grain, fades, text ------------------------------------
    fr = Image.alpha_composite(fr.convert("RGBA"), vignette()).convert("RGB")
    fr = _CONTRAST(fr)
    fr = ImageChops.add(fr, grain_tiles()[fi % 6], scale=1, offset=-127)

    fi_in = fx.get("fade_in")
    if fi_in and u * shot["dur"] < fi_in:
        k = (u * shot["dur"]) / fi_in
        fr = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), fr, k)

    d = ImageDraw.Draw(fr)
    if shot.get("act") and u < 0.9:
        a = min(1.0, math.sin(min(1.0, u / 0.9) * math.pi) * 2.2)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(215 * a)))
        fr = Image.alpha_composite(fr.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(fr)
        tw = d.textlength(shot["act"], font=F_ACT)
        d.text(((W - tw) / 2, H * .44), shot["act"], font=F_ACT,
               fill=tuple(int(c * a) for c in (198, 226, 218)))
    if shot.get("first") and shot.get("slug") and u * shot["dur"] < 3.4:
        a = min(1.0, 3.4 - u * shot["dur"])
        d.text((44, 36), shot["slug"], font=F_SLUG,
               fill=tuple(int(c * a) for c in (150, 176, 176)))

    if shot["kind"] == "d":
        sp = shot.setdefault("_sub", subtitle_sprite(
            shot["speaker"], shot["text"], fx.get("whisper"), fx.get("shout"),
            fx.get("mouthed"), fx.get("vo")))
        fr.paste(sp, (0, H - sp.height - 30), sp)
    elif shot.get("caption"):
        sp = shot.setdefault("_cap", caption_sprite(shot["caption"]))
        fr.paste(sp, (0, H - sp.height - 44), sp)
    return fr


def main():
    shots, total = build_timeline()
    nframes = int((total + 3.0) * FPS)   # hold the end card under the music tail
    out = os.path.join(ROOT, "out", "nachtglas_101_picture.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow",
           "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time
    t0 = time.time()
    si, fi = 0, 0
    for fi in range(nframes):
        t = fi / FPS
        while si + 1 < len(shots) and t >= shots[si]["t1"]:
            si += 1
        sh = shots[si]
        u = min(1.0, max(0.0, (t - sh["t0"]) / max(1e-6, sh["dur"])))
        if t > shots[-1]["t1"]:
            sh, u = shots[-1], 1.0
        proc.stdin.write(render_frame(sh, u, fi).tobytes())
        if fi % 480 == 0:
            el = time.time() - t0
            eta = el / max(1, fi) * (nframes - fi)
            print(f"  {fi:6d}/{nframes}  {t/60:5.2f} min  scene {sh['scene']:>2}  "
                  f"elapsed {el/60:.1f}m  eta {eta/60:.1f}m", flush=True)
    proc.stdin.close(); proc.wait()
    print("picture:", out, f"{os.path.getsize(out)/1e6:.1f} MB")
    return out


if __name__ == "__main__":
    main()
