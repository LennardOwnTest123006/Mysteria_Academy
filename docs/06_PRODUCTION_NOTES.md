# NACHTGLAS 1.01 — Production Notes

## What the rendered file is

`out/nachtglas_101.mp4` is the **complete first episode as a cinematic animatic**:
one continuous 11:20 cut, 1440×602 (2.39:1), 24 fps, every scene of the screenplay in order,
with the finished score and sound design and the full German dialogue on screen.

Everything in it was generated from scratch by the code in `render/`:

| | |
|---|---|
| **Picture** | Procedural location plates (`render/scenery.py`) painted once per location at 1.55x frame size, so camera moves are real crops through an oversized plate rather than post-hoc zooms. Layered building silhouettes, perspective roads, lit windows with true Gaussian bloom. |
| **Camera** | The shot list's own language: push-ins, pull-backs, pans, cranes, a descent for the cold open, an orbit for the war room, and hand-held reserved for the Uhlengasse. Every shot eases; even "static" shots breathe. |
| **Light** | Lantern glow sprites with a visible glow ring and a 0.4 Hz flicker, extinguished one lamp at a time from the timeline's `lamps_out`. The ring closing in Act 4 lights eleven lamps in 1.4 s. |
| **Atmosphere** | Two independently drifting pre-blurred fog layers, masked by a ground gradient so fog pools low; a soft vignette; a show LUT that crushes the toe and keeps the blacks blue; per-frame film grain from six rotating tiles. |
| **Blocking** | Silhouette figures with a per-character rim-light colour, built from one parametric body so the five leads are *identical in every frame they appear in* — continuity by construction. The Löscher has his own sprite and obeys his rule: he only ever changes position across a cut or a blink. |
| **The marble vision** | Optical, in-shot: seams of pale blue-green light travelling lamp to lamp, the taken rendered solid rather than ghostly, a green-cyan tint and a circular falloff. |
| **Score** | `render/audio.py` — glass-rim harmonics, struck bottles, an 18-cent-flat upright, bowed cello, low strings, breath choir and one sub, all synthesised from first principles. The main theme is in 7/8 and lands on its tonic exactly twice. |
| **Sound design** | Ambience beds per location (the kiosk fridge really does hum a flat B♭), the lantern sound family, moped, flare, marble, breathing. |
| **Der Einsturz** | The signature is real, not described: an FFT-convolution hall whose send level is automated to zero whenever the Löscher is near, and slammed back to 135 % when lantern 47 relights. On headphones the room genuinely disappears and comes back. |

## What it is not

Three things a full production would add, which cannot be produced here:

1. **No 3-D render.** There is no generative image or video model in this environment,
   so the picture is a graphic animatic — silhouette and light — rather than the
   physically-based 3-D described in `docs/02_SHOTLIST_VISUAL_DIRECTION.md`. The shot
   list, lighting bible, continuity lock list and the Löscher's animation rules are
   written to be handed to an animation team as-is.
2. **No voice track.** There is no speech synthesis here, and the brief explicitly rules
   out robotic AI voices — a scratch track from a text-to-speech engine would be worse
   than none. All German dialogue is therefore on screen as subtitles, timed at
   17 characters per second, which is the pace the lines would be performed at. Casting
   notes for all five leads (register, rhythm, and how each one sounds when frightened)
   are in the series bible.
3. **No lip sync**, for the same reason.

## Runtime

The screenplay as first drafted ran about seventeen minutes. It was cut to land inside
the 8–12 minute target: roughly sixty dialogue beats came out, mostly repeated
statements and speeches that were split across three lines where two carried the idea.
The four-act structure, every story beat, every character and the cliffhanger are intact,
and the episode is tighter for it. Final runtime **11:17** plus a three-second end card.

## The one timeline

`render/episode.py` holds all 302 shots — location, camera, staging, lighting state,
supernatural effects and the German line. Both `video.py` and `audio.py` read it, which
is why the music cue changes on the act break, the reverb collapses on the same frame the
lamp goes out, and the ring-closing chord lands on the frame the light comes on.
