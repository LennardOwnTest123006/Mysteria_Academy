# NACHTGLAS

> **Was das Licht vergisst, behält das Glas.**

An original supernatural mystery adventure series for viewers **12 and over**.
Everything here is created from scratch: the title, the logo, the town, the five
leads, the mythology, the antagonist, the screenplay, the score and the sound design.
Nothing is adapted from, or references, any existing series, character or property.

---

## The show in three lines

In the German valley town of **Hollerbrunn**, 111 antique street lanterns have burned
every night for a hundred and thirty years, and nobody remembers why. When the council
starts swapping the old hand-blown glass for LED fittings, people begin to vanish — and
nobody notices, because the moment someone is taken, every memory of them goes out.
Five teenagers still remember, for one absurd reason: each of them has an old glassworks
marble in their pocket.

**Episode 1.01 — „Einhundertelf"** · 11:17 · four acts · all dialogue in German.

---

## What's in this repository

| Path | |
|---|---|
| **`docs/00_SERIENBIBEL.md`** | Series bible — premise, the five leads with full design and voice notes, Hollerbrunn, the Nachtglas mythology, the Löscher's six fixed rules, season-one spine |
| **`docs/01_EPISODE_101_DREHBUCH.md`** | The pilot screenplay, cold open through cliffhanger. All spoken dialogue in German; action and direction in English |
| **`docs/02_SHOTLIST_VISUAL_DIRECTION.md`** | The three lights, night-exterior grammar, the Löscher's animation rules, camera policy per sequence, the continuity lock list, shot count |
| **`docs/03_SOUND_DESIGN.md`** | „Der Einsturz" (the reverb-collapse signature), ambience beds, the lantern sound family, set-piece cues, foley list |
| **`docs/04_MUSIC_SCORE.md`** | The original score — glass, wood and breath — themes, harmonic language, and the full cue sheet |
| **`docs/05_TITLE_SEQUENCE.md`** | The 40-second main title, shot by shot |
| **`docs/06_PRODUCTION_NOTES.md`** | How the video in `out/` was actually made, and what a full production would add |
| **`brand/`** | The original NACHTGLAS wordmark — SVG, PNG, and the title card |
| **`render/`** | The Python that generates all of it |
| **`out/`** | The rendered episode |

---

## The rendered episode

**`out/nachtglas_101.mp4`** — the complete pilot as a **cinematic animatic**:
11 minutes 20, 1600×668 (2.39:1), 24 fps, with the **complete original score and sound
design** synthesised from scratch, and the full German dialogue carried as subtitles.

It is a real, continuous, single-file cut of the whole episode — the camera moves, the
lanterns go out one by one, the fog drifts, the reverb collapses when the Löscher is near
and slams back when the lantern relights. It is **not** a final 3-D render, and it has
**no voice track**: see `docs/06_PRODUCTION_NOTES.md` for exactly what is and isn't in it.

## Rebuilding it

```bash
pip install numpy pillow imageio-ffmpeg
python3 render/make_logo.py     # wordmark -> brand/
python3 render/audio.py         # score + sound design -> out/*.wav
python3 render/video.py         # picture -> out/*.mp4
python3 render/mux.py           # final single-file episode
```

`render/episode.py` is the single timeline both the picture and the sound are built
from, so they cannot drift apart.
