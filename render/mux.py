# -*- coding: utf-8 -*-
"""Mux the rendered picture and the score/sound-design mix into the episode."""
import os, subprocess, sys
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
pic = os.path.join(OUT, "nachtglas_101_picture.mp4")
wav = os.path.join(OUT, "nachtglas_101_mix.wav")
final = os.path.join(OUT, "nachtglas_101.mp4")

for f in (pic, wav):
    if not os.path.exists(f):
        sys.exit(f"missing {f}")

ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-i", pic, "-i", wav,
       "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
       # EBU R128: broadcast loudness, with the episode's dynamics kept intact
       "-af", "loudnorm=I=-19:TP=-2:LRA=14",
       "-map", "0:v:0", "-map", "1:a:0", "-shortest",
       "-movflags", "+faststart",
       "-metadata", "title=NACHTGLAS 1.01 - Einhundertelf",
       "-metadata", "artist=NACHTGLAS",
       "-metadata", "comment=Original supernatural mystery series pilot. Age rating 12+.",
       final]
print(" ".join(cmd[:1]), "…")
subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"episode: {final}  ({os.path.getsize(final)/1e6:.1f} MB)")

probe = subprocess.run([ff, "-i", final], capture_output=True, text=True).stderr
for line in probe.splitlines():
    if "Duration" in line or "Stream #" in line:
        print("  " + line.strip())
