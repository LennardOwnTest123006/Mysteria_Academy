"""Render the NACHTGLAS wordmark to SVG and PNG."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import (GLYPHS, WORD, STROKE, ADVANCE, TRACKING, CAP,
                    word_polylines, word_width, crack_polyline, flame_anchor)
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "brand")
os.makedirs(BRAND, exist_ok=True)

GLASS = (191, 233, 222)      # #BFE9DE  pale nachtglas
GLASS_DEEP = (127, 227, 200)  # #7FE3C8
AMBER = (255, 176, 92)
INK = (8, 14, 18)

W = word_width()
PAD = 70


# ---------------------------------------------------------------- SVG --------
def fmt(pl):
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pl)


def build_svg():
    vw, vh = W + PAD * 2, CAP + PAD * 2
    body = []
    body.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw:.0f} {vh:.0f}" '
                f'width="{vw:.0f}" height="{vh:.0f}" role="img" aria-label="NACHTGLAS">')
    body.append("""  <defs>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"    stop-color="#DFF6EE"/>
      <stop offset="0.55" stop-color="#BFE9DE"/>
      <stop offset="1"    stop-color="#7FE3C8"/>
    </linearGradient>
    <filter id="bloom" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="emberglow" x="-300%" y="-300%" width="700%" height="700%">
      <feGaussianBlur stdDeviation="9" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="letters">""")
    for pl in word_polylines():
        body.append(f'      <path d="{fmt(pl)}" stroke="#fff" stroke-width="{STROKE}" '
                    f'fill="none" stroke-linecap="butt" stroke-linejoin="miter"/>')
    body.append("""    </clipPath>
  </defs>
  <rect width="100%" height="100%" fill="none"/>""")

    body.append(f'  <g transform="translate({PAD},{PAD})">')
    # wordmark
    body.append('    <g filter="url(#bloom)" fill="none" stroke="url(#glass)" '
                f'stroke-width="{STROKE}" stroke-linecap="butt" stroke-linejoin="miter">')
    for pl in word_polylines():
        body.append(f'      <path d="{fmt(pl)}"/>')
    body.append("    </g>")
    # fracture, clipped to the letters so it reads as a crack IN the glass
    crack = crack_polyline(W, CAP / 2)
    body.append('    <g clip-path="url(#letters)">')
    body.append(f'      <path d="{fmt(crack)}" fill="none" stroke="#04131A" '
                f'stroke-width="2.6" stroke-linecap="round"/>')
    body.append(f'      <path d="{fmt(crack)}" fill="none" stroke="#EAFFF8" '
                f'stroke-width="1.1" stroke-linecap="round" opacity="0.9"/>')
    body.append("    </g>")
    # the flame in the counter of the first A
    fx, fy = flame_anchor()
    body.append(f'    <g filter="url(#emberglow)">')
    body.append(f'      <path d="M {fx:.1f},{fy - 15:.1f} C {fx + 7:.1f},{fy - 6:.1f} '
                f'{fx + 6:.1f},{fy + 4:.1f} {fx:.1f},{fy + 7:.1f} C {fx - 6:.1f},{fy + 4:.1f} '
                f'{fx - 7:.1f},{fy - 6:.1f} {fx:.1f},{fy - 15:.1f} Z" fill="#FFB05C"/>')
    body.append(f'      <ellipse cx="{fx:.1f}" cy="{fy - 1:.1f}" rx="2.1" ry="4.2" fill="#FFF0D2"/>')
    body.append("    </g>")
    body.append("  </g>")
    body.append(f'  <text x="{vw/2:.0f}" y="{vh - 24:.0f}" text-anchor="middle" '
                f'font-family="Georgia,\'Times New Roman\',serif" font-size="19" '
                f'letter-spacing="3.4" fill="#7FA79E" font-style="italic">'
                f'Was das Licht vergisst, behält das Glas.</text>')
    body.append("</svg>")
    return "\n".join(body)


with open(os.path.join(BRAND, "nachtglas_logo.svg"), "w", encoding="utf-8") as f:
    f.write(build_svg())


# ---------------------------------------------------------------- PNG --------
def draw_wordmark(size, scale, origin, crack_t=1.0, flame=1.0, glow=1.0, color=GLASS):
    """Return an RGBA image of the wordmark drawn at `scale`."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = origin
    sw = max(1, int(round(STROKE * scale)))
    for pl in word_polylines(x0=0, y0=0, scale=scale):
        pts = [(ox + x, oy + y) for x, y in pl]
        d.line(pts, fill=color + (255,), width=sw, joint="curve")

    if glow > 0:
        halo = img.filter(ImageFilter.GaussianBlur(radius=3.5 * scale + 2))
        halo = Image.eval(halo.split()[3], lambda a: int(a * 0.42 * glow))
        base = Image.new("RGBA", size, GLASS_DEEP + (0,))
        base.putalpha(halo)
        img = Image.alpha_composite(base, img)

    if crack_t > 0:
        mask = Image.new("L", size, 0)
        md = ImageDraw.Draw(mask)
        for pl in word_polylines(x0=0, y0=0, scale=scale):
            md.line([(ox + x, oy + y) for x, y in pl], fill=255, width=sw, joint="curve")
        cl = Image.new("RGBA", size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        crack = [(ox + x * scale, oy + y * scale)
                 for x, y in crack_polyline(W, CAP / 2)]
        cut = max(2, int(len(crack) * crack_t))
        if cut >= 2:
            cd.line(crack[:cut], fill=(4, 19, 26, 190), width=max(1, int(2.2 * scale)), joint="curve")
            cd.line(crack[:cut], fill=(234, 255, 248, 230), width=max(1, int(1.3 * scale)), joint="curve")
        cl.putalpha(Image.composite(cl.split()[3], Image.new("L", size, 0), mask))
        img = Image.alpha_composite(img, cl)

    if flame > 0:
        fx, fy = flame_anchor()
        fx, fy = ox + fx * scale, oy + fy * scale
        fl = Image.new("RGBA", size, (0, 0, 0, 0))
        fd = ImageDraw.Draw(fl)
        r = 9.4 * scale * flame
        fd.ellipse([fx - r * 0.62, fy - r * 1.9, fx + r * 0.62, fy + r * 0.95],
                   fill=AMBER + (255,))
        fd.ellipse([fx - r * 0.28, fy - r * 1.0, fx + r * 0.28, fy + r * 0.42],
                   fill=(255, 240, 210, 255))
        halo = fl.filter(ImageFilter.GaussianBlur(radius=11 * scale))
        img = Image.alpha_composite(img, Image.alpha_composite(halo, fl))
    return img


def title_card(w=2560, h=1070, tagline=True):
    """2.39:1 title card on the Hollerbrunn night gradient."""
    bg = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        v = 1 - abs(t - 0.55) * 1.6
        v = max(0.0, v)
        d.line([(0, y), (w, y)], fill=(int(8 + 16 * v), int(16 + 30 * v), int(22 + 34 * v)))
    scale = (w * 0.72) / W
    ox = (w - W * scale) / 2
    oy = (h - CAP * scale) / 2 - h * 0.055
    mark = draw_wordmark((w, h), scale, (ox, oy))
    bg = Image.alpha_composite(bg.convert("RGBA"), mark).convert("RGB")
    if tagline:
        d = ImageDraw.Draw(bg)
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                                      int(h * 0.026))
        except OSError:
            font = ImageFont.load_default()
        txt = "WAS  DAS  LICHT  VERGISST,  BEHÄLT  DAS  GLAS."
        tw = d.textlength(txt, font=font)
        d.text(((w - tw) / 2, oy + CAP * scale + h * 0.10), txt,
               font=font, fill=(122, 167, 158))
    return bg


title_card().save(os.path.join(BRAND, "nachtglas_titlecard.png"), quality=95)
mark = draw_wordmark((int(W * 1.6) + 160, int(CAP * 1.6) + 160), 1.6, (80, 80))
mark.save(os.path.join(BRAND, "nachtglas_logo.png"))
print("wrote brand/nachtglas_logo.svg, nachtglas_logo.png, nachtglas_titlecard.png")
