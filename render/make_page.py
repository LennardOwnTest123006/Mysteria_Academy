# -*- coding: utf-8 -*-
"""Generate the NACHTGLAS presentation page (logo + lantern ring drawn from
the same geometry the production assets use)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import (word_polylines, word_width, crack_polyline, flame_anchor,
                    svg_path, STROKE, CAP)

# ---- wordmark, from the real letterform geometry ---------------------------
W = word_width()
paths = "\n".join(f'      <path d="{svg_path(pl)}"/>' for pl in word_polylines())
crack = " L ".join(f"{x:.1f},{y:.1f}" for x, y in crack_polyline(W, CAP / 2))
fx, fy = flame_anchor()

LOGO = f'''<svg class="mark" viewBox="-14 -16 {W + 28:.0f} {CAP + 32:.0f}"
       role="img" aria-label="NACHTGLAS">
  <defs>
    <linearGradient id="gl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#E4F7F0"/><stop offset=".55" stop-color="#BFE9DE"/>
      <stop offset="1" stop-color="#7FE3C8"/>
    </linearGradient>
    <filter id="bl" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="cp">
{paths.replace('<path d=', '<path stroke="#fff" stroke-width="' + str(STROKE) + '" fill="none" d=')}
    </clipPath>
  </defs>
  <g filter="url(#bl)" fill="none" stroke="url(#gl)" stroke-width="{STROKE}"
     stroke-linecap="butt" stroke-linejoin="miter">
{paths}
  </g>
  <g clip-path="url(#cp)">
    <path d="M {crack}" fill="none" stroke="#04131A" stroke-width="2.6"/>
    <path d="M {crack}" fill="none" stroke="#EAFFF8" stroke-width="1.1" opacity=".85"/>
  </g>
  <ellipse cx="{fx:.0f}" cy="{fy - 2:.0f}" rx="4.6" ry="9" fill="#FFB25C"/>
  <ellipse cx="{fx:.0f}" cy="{fy - 2:.0f}" rx="1.9" ry="4" fill="#FFF0D2"/>
</svg>'''

# ---- the lantern ring: 111 real dots, 9 dark, and the unaccounted 112th ----
REMOVED = {8, 9, 10, 11, 12, 13, 14, 15, 46}          # eight at the Marktplatz + no. 47
dots = []
for i in range(111):
    a = -math.pi / 2 + 2 * math.pi * i / 111
    r = 168 + 13 * math.sin(i * 0.9) + 7 * math.cos(i * 2.3)
    x, y = 220 + math.cos(a) * r * 1.30, 200 + math.sin(a) * r * 0.86
    if i in REMOVED:
        dots.append(f'<circle class="d off" cx="{x:.1f}" cy="{y:.1f}" r="3.4"/>')
    else:
        dots.append(f'<circle class="d on" cx="{x:.1f}" cy="{y:.1f}" r="3.1" '
                    f'style="--k:{i * 0.037:.2f}s"/>')
RING = "\n      ".join(dots)

CAST = [
    ("JUNO WENDT", "15", "#D66A36",
     "Rust-orange corduroy jacket, claw clip, a multitool on a red carabiner.",
     "Warm alto, fast, dry. Ends sentences early.",
     "Her mother is the technician taking the lanterns down."),
    ("TAREK SAHIN", "15", "#DAB046",
     "Mustard rain jacket, never zipped. Round glasses that catch every practical light.",
     "Higher, quick, breathy. Talks through fear.",
     "His little brother copies everything he does, including the dangerous parts."),
    ("NELL VARGA", "16", "#6CA880",
     "Surplus parka to mid-thigh, hood up outdoors. Charcoal in the creases of her right hand.",
     "Low, slow, flat. Then unguarded, and it lands like weather.",
     "She thought she was ill. She was relieved to find out it was a monster."),
    ("BASTIAN ROHDE", "14", "#688CD0",
     "Chlorine-bleached club hoodie, an orange headlamp pushed up on his forehead.",
     "Bright, loud, earnest. Says exactly the wrong true thing.",
     "The woman signing off on the lantern replacement is his mother."),
    ("KONSTANTIN MEIWALD", "17", "#8C9EB0",
     "Work jacket, name patch worn illegible. A moped with the right mirror taped on.",
     "Deep, quiet, unhurried. Uses full stops.",
     "Everyone in town already decided who he is. He stopped arguing."),
]
cast_html = "\n".join(f'''    <li class="cast-row" style="--rim:{c}">
      <div class="cast-id"><h3>{n}</h3><span class="age">{a}</span></div>
      <dl class="cast-fields">
        <div><dt>Look</dt><dd>{look}</dd></div>
        <div><dt>Voice</dt><dd>{voice}</dd></div>
        <div><dt>Wound</dt><dd>{wound}</dd></div>
      </dl>
    </li>''' for n, a, c, look, voice, wound in CAST)

RULES = [
 "He moves only through unlit ground. Any light is a wall.",
 "Nachtglas light he cannot cross at all. LED light only slows him — it holds him about as well as a fence holds weather.",
 "A person carrying Nachtglas keeps their memories. They remember the taken.",
 "The taken are not gone. They are held in reflection, and they can see out.",
 "To bring someone back, relight the lantern they were taken beside, with original Nachtglas in the fitting.",
 "The ring of 111 lanterns is not a fence. It is a lid.",
]
rules_html = "\n".join(
    f'      <li><span class="rn">{i+1}</span><p>{r}</p></li>' for i, r in enumerate(RULES))

ACTS = [
 ("KALTÖFFNUNG", "00:00 – 01:10", "Hollerbrunn from the valley rim, a necklace of amber "
  "around a sleeping town. Kosta stops his moped at the top of the Uhlengasse and watches "
  "six lanterns go out toward him, one every two seconds, the way a fuse burns."),
 ("AKT EINS", "01:47 – 04:04", "The council takes down the ninth old lantern. Juno pockets "
  "a chipped globe. At 18:52 Elif Toprak walks home through the gap where the sixth lamp "
  "should be — and by morning her desk is gone and the register has twenty-nine names."),
 ("AKT ZWEI", "04:04 – 07:01", "Five people who still remember her find each other, because "
  "all five have an old glassworks marble in their pocket. Paragraph nine of the 1894 town "
  "charter forbids the lanterns from ever being dark together. Plotted on a map they are "
  "not a lighting plan. They are a ring."),
 ("AKT DREI", "07:01 – 09:12", "Pepe Sahin, nine, goes out to see the Laternenmann. The five "
  "build a corridor of light down the Uhlengasse — phones, a headlamp, a moped main beam, "
  "a road flare — and get within five metres before the flare is drunk."),
 ("AKT VIER", "09:12 – 11:17", "They don't fight him. They wire an 1893 globe to a moped "
  "battery and put lantern 47 back on. The light runs lamp to lamp and the ring shuts like "
  "a heavy door. Then Juno lifts her marble to the relit lamp one last time."),
]
acts_html = "\n".join(f'''    <li class="act">
      <div class="act-head"><span class="tc">{tc}</span><h3>{t}</h3></div>
      <p>{d}</p>
    </li>''' for t, tc, d in ACTS)

CUES = [
 ("1M1", "Hollerbrunn, 23:38", "00:00", "Glass rims from black. Subtracts to nothing as the lanterns die."),
 ("MT", "NACHTGLAS — Main Title", "01:10", "The only time in the episode the theme plays complete."),
 ("1M3", "Der Heimweg", "03:05", "Solo cello, one note per bar. Stops at the collapse."),
 ("2M2", "Hundertelf", "05:20", "Bottles and low strings, accelerating. Never resolves."),
 ("3M1", "Sieben Minuten", "07:20", "Loses an instrument every four bars. Stops mid-bar."),
 ("4M2", "Sein Bruder", "10:05", "The first major chord in the episode."),
 ("4M3", "Einhundertzwölf", "10:50", "Glass choir, breath choir, one sub-bass D. Hard cut."),
]
cues_html = "\n".join(
    f"      <tr><td class='m'>{c}</td><td>{t}</td><td class='m tc'>{tc}</td><td>{n}</td></tr>"
    for c, t, tc, n in CUES)

HTML = f'''<title>Nachtglas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Antonio:wght@300;500;700&family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --ground:#070C10; --ground-2:#0C141A; --raised:#111C23;
  --ink:#DDE8E6; --ink-2:#9CB2AE; --ink-3:#63797A;
  --amber:#FFB25C; --amber-dim:#8A5F2E;
  --glass:#7FE3C8; --glass-dim:#2E6A63;
  --line:#1A2830; --line-2:#243640;
  --display:"Antonio","Oswald","Arial Narrow",sans-serif;
  --body:"Spectral",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
  --wrap:1080px;
}}
* {{ box-sizing:border-box; }}
body {{
  background:var(--ground); color:var(--ink); font-family:var(--body);
  font-size:17px; line-height:1.72; margin:0;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:var(--wrap); margin:0 auto; padding:0 28px; }}
p {{ max-width:66ch; }}

/* ---------- hero ---------- */
.hero {{
  position:relative; overflow:hidden; padding:76px 0 54px;
  background:
    radial-gradient(120% 78% at 50% 6%, #12222B 0%, rgba(7,12,16,0) 62%),
    radial-gradient(60% 40% at 50% 100%, rgba(255,178,92,.07) 0%, rgba(7,12,16,0) 70%),
    var(--ground);
  border-bottom:1px solid var(--line);
}}
.mark {{ display:block; width:min(100%,760px); margin:0 auto; height:auto; }}
.tag {{
  text-align:center; font-family:var(--mono); font-size:.72rem;
  letter-spacing:.34em; text-transform:uppercase; color:var(--ink-3);
  margin:30px 0 0;
}}
.strip {{
  margin:44px auto 0; max-width:900px; display:grid; gap:1px;
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  background:var(--line); border:1px solid var(--line);
}}
.strip div {{ background:var(--ground-2); padding:15px 18px; }}
.strip dt {{
  font-family:var(--mono); font-size:.62rem; letter-spacing:.2em;
  text-transform:uppercase; color:var(--ink-3); margin:0 0 5px;
}}
.strip dd {{ margin:0; font-family:var(--display); font-size:1.18rem; font-weight:500;
  letter-spacing:.02em; color:var(--ink); line-height:1.25; }}
.strip dd.hot {{ color:var(--amber); }}

/* ---------- sections ---------- */
section {{ padding:74px 0; border-bottom:1px solid var(--line); }}
.eyebrow {{
  font-family:var(--mono); font-size:.66rem; letter-spacing:.28em;
  text-transform:uppercase; color:var(--glass-dim); margin:0 0 14px;
}}
h2 {{
  font-family:var(--display); font-weight:500; font-size:clamp(1.9rem,4.2vw,2.9rem);
  letter-spacing:.015em; line-height:1.06; margin:0 0 22px; text-wrap:balance;
  color:var(--ink);
}}
.lede {{ font-size:1.22rem; line-height:1.62; color:var(--ink); max-width:60ch; }}
.lede em {{ color:var(--amber); font-style:italic; }}

/* ---------- ring ---------- */
.ring-grid {{ display:grid; gap:40px; grid-template-columns:1fr; align-items:center; }}
@media (min-width:880px) {{ .ring-grid {{ grid-template-columns:1.15fr .85fr; }} }}
.ring {{ width:100%; height:auto; display:block; }}
.ring .d.on {{ fill:var(--amber); animation:flick 5.5s ease-in-out infinite; animation-delay:var(--k); }}
.ring .d.off {{ fill:none; stroke:var(--line-2); stroke-width:1.2; }}
.ring .ghost {{ fill:none; stroke:var(--glass); stroke-width:1.4; stroke-dasharray:3 4; }}
@keyframes flick {{ 0%,100%{{opacity:.95}} 45%{{opacity:.66}} 70%{{opacity:1}} }}
@media (prefers-reduced-motion:reduce) {{ .ring .d.on {{ animation:none; }} }}
.legend {{ list-style:none; padding:0; margin:0; display:grid; gap:16px; }}
.legend li {{ display:grid; grid-template-columns:26px 1fr; gap:14px; align-items:start; }}
.legend b {{ font-family:var(--mono); font-weight:500; font-size:.78rem; letter-spacing:.06em; }}
.swatch {{ width:14px; height:14px; border-radius:50%; margin-top:7px; }}
.sw-on {{ background:var(--amber); box-shadow:0 0 12px rgba(255,178,92,.6); }}
.sw-off {{ border:1.4px solid var(--line-2); }}
.sw-ghost {{ border:1.4px dashed var(--glass); }}
.legend p {{ margin:2px 0 0; color:var(--ink-2); font-size:.95rem; line-height:1.6; }}

/* ---------- cast ---------- */
.cast {{ list-style:none; padding:0; margin:0; display:grid; gap:1px; background:var(--line); border-block:1px solid var(--line); }}
.cast-row {{
  background:var(--ground-2); padding:26px 26px 26px 30px;
  border-left:3px solid var(--rim);
  display:grid; gap:8px 34px; grid-template-columns:1fr;
}}
@media (min-width:800px) {{ .cast-row {{ grid-template-columns:230px 1fr; }} }}
.cast-id {{ display:flex; align-items:baseline; gap:12px; }}
.cast-id h3 {{
  font-family:var(--display); font-weight:500; font-size:1.42rem; letter-spacing:.02em;
  margin:0; color:var(--rim); line-height:1.15;
}}
.age {{ font-family:var(--mono); font-size:.78rem; color:var(--ink-3); }}
.cast-fields {{ margin:0; display:grid; gap:10px; }}
.cast-fields div {{ display:grid; grid-template-columns:64px 1fr; gap:14px; }}
.cast-fields dt {{
  font-family:var(--mono); font-size:.62rem; letter-spacing:.16em; text-transform:uppercase;
  color:var(--ink-3); padding-top:5px;
}}
.cast-fields dd {{ margin:0; color:var(--ink-2); font-size:1rem; line-height:1.6; }}

/* ---------- rules ---------- */
.villain {{ display:grid; gap:44px; grid-template-columns:1fr; }}
@media (min-width:900px) {{ .villain {{ grid-template-columns:.9fr 1.1fr; }} }}
.rules {{ list-style:none; padding:0; margin:0; counter-reset:r; display:grid; gap:2px; }}
.rules li {{
  display:grid; grid-template-columns:38px 1fr; gap:16px; align-items:start;
  padding:15px 18px; background:var(--ground-2);
}}
.rn {{
  font-family:var(--mono); font-size:.8rem; color:var(--glass);
  border:1px solid var(--glass-dim); border-radius:2px;
  width:26px; height:26px; display:grid; place-items:center; margin-top:2px;
}}
.rules p {{ margin:0; color:var(--ink-2); font-size:1rem; line-height:1.62; }}
.villain figure {{ margin:0; }}
.villain blockquote {{
  margin:0 0 22px; padding:0 0 0 20px; border-left:2px solid var(--glass-dim);
  font-size:1.16rem; font-style:italic; color:var(--ink); line-height:1.6;
}}

/* ---------- acts ---------- */
.acts {{ list-style:none; padding:0; margin:0; display:grid; gap:0; }}
.act {{ padding:26px 0 26px 30px; border-left:1px solid var(--line-2); position:relative; }}
.act::before {{
  content:""; position:absolute; left:-5px; top:34px; width:9px; height:9px;
  border-radius:50%; background:var(--amber); box-shadow:0 0 10px rgba(255,178,92,.55);
}}
.act:last-child::before {{ background:var(--glass); box-shadow:0 0 10px rgba(127,227,200,.55); }}
.act-head {{ display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; margin-bottom:8px; }}
.act-head h3 {{
  font-family:var(--display); font-weight:500; font-size:1.34rem; letter-spacing:.09em;
  margin:0; color:var(--ink);
}}
.tc {{ font-family:var(--mono); font-size:.76rem; color:var(--amber-dim); font-variant-numeric:tabular-nums; }}
.act p {{ margin:0; color:var(--ink-2); }}

/* ---------- table ---------- */
.tablewrap {{ overflow-x:auto; border:1px solid var(--line); }}
table {{ border-collapse:collapse; width:100%; min-width:620px; }}
th, td {{ text-align:left; padding:12px 16px; border-bottom:1px solid var(--line); font-size:.95rem; }}
th {{
  font-family:var(--mono); font-size:.62rem; letter-spacing:.18em; text-transform:uppercase;
  color:var(--ink-3); background:var(--ground-2); border-bottom:1px solid var(--line-2);
}}
td {{ color:var(--ink-2); }}
td.m {{ font-family:var(--mono); font-size:.82rem; color:var(--ink); }}
td.tc {{ color:var(--amber-dim); font-variant-numeric:tabular-nums; }}
tr:last-child td {{ border-bottom:none; }}

.two {{ display:grid; gap:40px; grid-template-columns:1fr; }}
@media (min-width:860px) {{ .two {{ grid-template-columns:1fr 1fr; }} }}
h4 {{ font-family:var(--mono); font-size:.66rem; letter-spacing:.22em; text-transform:uppercase;
  color:var(--glass-dim); margin:0 0 12px; }}
.two p {{ color:var(--ink-2); margin:0 0 14px; }}

/* ---------- close ---------- */
.close {{ border-bottom:none; text-align:center; padding:96px 0 110px;
  background:radial-gradient(70% 60% at 50% 40%, #0B161C 0%, var(--ground) 70%); }}
.close .mouthed {{
  font-family:var(--display); font-weight:300; font-size:clamp(2rem,6vw,3.6rem);
  color:var(--glass); letter-spacing:.03em; margin:0 0 10px; text-wrap:balance;
}}
.close .attrib {{ font-family:var(--mono); font-size:.68rem; letter-spacing:.24em;
  text-transform:uppercase; color:var(--ink-3); margin:0 0 54px; }}
.count {{ font-family:var(--display); font-weight:700; font-size:clamp(3.4rem,13vw,8rem);
  letter-spacing:.04em; color:var(--amber); line-height:1; margin:0; }}
.count small {{ display:block; font-family:var(--mono); font-weight:400; font-size:.66rem;
  letter-spacing:.3em; color:var(--ink-3); margin-top:18px; text-transform:uppercase; }}
footer {{ padding:34px 0 60px; text-align:center; }}
footer p {{ max-width:none; font-family:var(--mono); font-size:.68rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin:0; }}
:focus-visible {{ outline:2px solid var(--amber); outline-offset:3px; }}
</style>

<header class="hero">
  <div class="wrap">
    {LOGO}
    <p class="tag">Was das Licht vergisst, behält das Glas</p>
    <dl class="strip">
      <div><dt>Genre</dt><dd>Mystery<br>Adventure</dd></div>
      <div><dt>Freigabe</dt><dd class="hot">Ab 12</dd></div>
      <div><dt>Staffel 1</dt><dd>8 Folgen</dd></div>
      <div><dt>Pilotlänge</dt><dd>11:17</dd></div>
      <div><dt>Sprache</dt><dd>Deutsch</dd></div>
    </dl>
  </div>
</header>

<section>
  <div class="wrap">
    <p class="eyebrow">Serie</p>
    <h2>Eine Stadt, die vergisst</h2>
    <p class="lede">In the valley town of <em>Hollerbrunn</em>, 111 antique street lanterns
    have burned every night for a hundred and thirty years, and nobody remembers why. When
    the council starts swapping the old hand-blown glass for LED fittings, people begin to
    vanish — and nobody notices, because the moment someone is taken, every memory of them
    goes out like a filament.</p>
    <p>Five teenagers still remember, for one absurd reason: each of them carries a marble
    of old glassworks scrap in their pocket. Children in Hollerbrunn have dug them out of
    the Nebelgraben for a century and traded them in the schoolyard like currency. Almost
    every child in town has one. Almost every adult threw theirs away. That is the entire
    reason five teenagers can save a town and six thousand adults cannot.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Der Laternenring · Stadtsatzung §9</p>
    <h2>Kein Beleuchtungsplan. Ein Kreis.</h2>
    <div class="ring-grid">
      <svg class="ring" viewBox="0 0 440 400" role="img"
           aria-label="The 111 lanterns of Hollerbrunn plotted as a closed ring, nine of them dark, with a 112th unaccounted for.">
        <ellipse cx="220" cy="200" rx="150" ry="96" fill="none" stroke="#141F26" stroke-width="1"/>
        <text x="220" y="196" text-anchor="middle" fill="#3B4E52"
              font-family="IBM Plex Mono, monospace" font-size="9" letter-spacing="2.6">GLASHÜTTE</text>
        <text x="220" y="210" text-anchor="middle" fill="#2C3D42"
              font-family="IBM Plex Mono, monospace" font-size="8" letter-spacing="2.2">AM BRANDHANG</text>
      {RING}
        <circle class="ghost" cx="408" cy="36" r="7"/>
        <text x="394" y="20" text-anchor="end" fill="#4E7C77"
              font-family="IBM Plex Mono, monospace" font-size="9" letter-spacing="1.4">Nr. 112 ?</text>
      </svg>
      <ul class="legend">
        <li><span class="swatch sw-on"></span><div><b>102 brennen</b>
          <p>Original-Nachtglas von 1893. Solange sie brennen, kommt er nicht durch.</p></div></li>
        <li><span class="swatch sw-off"></span><div><b>9 abgeschraubt</b>
          <p>Acht am Marktplatz, und Nummer 47 in der Uhlengasse — genau da, wo Elif Toprak
          verschwindet. Die Lichtoffensive Hollerbrunn 2030 spart sechzig Prozent Energie.</p></div></li>
        <li><span class="swatch sw-ghost"></span><div><b>1 unauffindbar</b>
          <p>Der Originalplan von 1894 zählt einhundertundzwölf. Auf keiner modernen Karte,
          in keinem Inventar. Das ist die Staffel.</p></div></li>
      </ul>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Die Fünf</p>
    <h2>Fünf Leute, im Dunkeln, die nicht weggehen</h2>
  </div>
  <ul class="cast">
{cast_html}
  </ul>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Antagonist</p>
    <h2>Der Löscher</h2>
    <div class="villain">
      <figure>
        <blockquote>He does not walk toward you. He is simply closer each time you blink.</blockquote>
        <p style="color:var(--ink-2)">Two metres forty. A coat that reads as poured black glass.
        Where a face should be there is a smooth oval pane in which you see your own
        reflection, dimmer than you are and a third of a second late. In his left hand,
        a lantern with no flame — and when its small door opens, the light in the street
        visibly bends toward it, the way smoke bends.</p>
        <p style="color:var(--ink-2)">He never runs. He never touches anyone. He takes the
        light <em>in</em> a person — their warmth, their presence, the fact of them — and what
        remains is a reflection, standing in every window and puddle, mouthing words nobody
        hears.</p>
      </figure>
      <ol class="rules">
{rules_html}
      </ol>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Folge 1.01</p>
    <h2>Einhundertelf</h2>
    <p class="lede">Hollerbrunn wird heller. Neue Lampen, bessere Birnen, sechzig Prozent
    weniger Energie. Aber in der Nacht, in der die neunte alte Laterne abgeschraubt wird,
    geht Elif Toprak die Uhlengasse entlang nach Hause und kommt nicht an — und am nächsten
    Morgen kennen nur noch fünf Leute in der Stadt ihren Namen.</p>
    <ul class="acts">
{acts_html}
    </ul>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Musik &amp; Ton</p>
    <h2>Glas, Holz und Atem</h2>
    <div class="two">
      <div>
        <h4>Das Ensemble</h4>
        <p>34 gestimmte Gläser mit nassem Finger gespielt, ein Gestell aus 16 geschnittenen
        Flaschen mit Filzschlegeln, ein Schulklavier 18 Cent zu tief, ein Solocello, sechs
        tiefe Streicher als Boden, ein Atemchor und ein einziger Subbass. Kein Blech, kein
        Schlagzeug, keine Flächen.</p>
        <p>Das Hauptthema steht im 7/8 und landet in der ganzen Folge genau zweimal auf
        seinem Grundton.</p>
      </div>
      <div>
        <h4>Der Löscher hat kein Motiv</h4>
        <p>Er nimmt sie weg. Ist er in der Nähe, verliert die laufende Musik alle vier Takte
        ein Instrument — Gläser, dann Flaschen, dann Klavier, dann Streicher — bis nur noch
        ein Ton übrig ist und dann Raumton. Bis Akt drei hat das Publikum Angst davor, dass
        ein Instrument geht.</p>
        <h4 style="margin-top:22px">Der Einsturz</h4>
        <p>Kein Geräusch, sondern ein Entzug: der gesamte Hall geht in 1,2 Sekunden auf null.
        Die Welt verliert ihre Größe. Wenn Laterne 47 wieder angeht, kommt er nicht zurück —
        er schlägt zurück.</p>
      </div>
    </div>
    <div class="tablewrap" style="margin-top:34px">
      <table>
        <thead><tr><th>Cue</th><th>Titel</th><th>TC</th><th>Notiz</th></tr></thead>
        <tbody>
{cues_html}
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="close">
  <div class="wrap">
    <p class="eyebrow" style="color:var(--ink-3)">Cliffhanger</p>
    <p class="mouthed">„Ihr habt eine vergessen."</p>
    <p class="attrib">Elif Toprak · lautlos · im Licht von Laterne 47</p>
    <p class="count">112<small>Nachtlaternen der Stadt Hollerbrunn · Originalplan 1894</small></p>
  </div>
</section>

<footer>
  <div class="wrap"><p>Nachtglas · Originalserie · Alle Figuren, Orte und Musik sind frei erfunden</p></div>
</footer>
'''

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "out", "nachtglas_page.html")
open(out, "w", encoding="utf-8").write(HTML)
print("wrote page,", len(HTML), "bytes")
