# -*- coding: utf-8 -*-
"""NACHTGLAS 1.01 — original score and sound design, synthesised from scratch.

Instruments are built from first principles: glass rims, struck bottles, a
detuned upright, a bowed cello, breath and one sub. Nothing is sampled and
nothing is quoted. Reverb is an FFT convolution against a synthetic hall, and
its send level is automated so that DER EINSTURZ — the collapse of all room
sound near the Loescher — actually happens in the mix.
"""
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from episode import build_timeline, SCENES

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(1893)


def mtof(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


N = {}
for _o in range(0, 9):
    for _i, _n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]):
        N[f"{_n}{_o}"] = mtof(12 * (_o + 1) + _i)


def env(n, a, d, s, r, sus=0.6):
    """Attack/decay/sustain/release envelope, lengths in seconds."""
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    a, d, r = max(1, a), max(1, d), max(1, r)
    sn = max(0, n - a - d - r)
    e = np.concatenate([
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, sus, d, endpoint=False),
        np.full(sn, sus),
        np.linspace(sus, 0, r),
    ])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def _t(dur):
    return np.arange(int(dur * SR)) / SR


# ------------------------------------------------------------ instruments ---
def glass(f, dur, amp=1.0, breathy=0.12):
    """Rubbed glass rim: near-pure, slow to speak, long to die."""
    t = _t(dur)
    sig = np.sin(2 * np.pi * f * t)
    sig += 0.24 * np.sin(2 * np.pi * f * 2.76 * t)
    sig += 0.10 * np.sin(2 * np.pi * f * 5.40 * t)
    sig += 0.05 * np.sin(2 * np.pi * f * 8.93 * t)
    sig *= 1 + 0.035 * np.sin(2 * np.pi * 4.7 * t)          # finger wobble
    n = len(t)
    if breathy:
        w = rng.normal(0, 1, n) * breathy * np.exp(-t * 9)
        sig += w
    return (sig * env(n, min(0.42, dur * .4), dur * .25, 0, dur * .45, 0.55) * amp).astype(np.float32)


def bottle(f, dur, amp=1.0):
    """Cut bottle struck with a felt beater."""
    t = _t(dur); n = len(t)
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t * 6.0)
           + 0.42 * np.sin(2 * np.pi * f * 2.41 * t) * np.exp(-t * 11.0)
           + 0.18 * np.sin(2 * np.pi * f * 4.07 * t) * np.exp(-t * 17.0))
    click = rng.normal(0, 1, n) * np.exp(-t * 260) * 0.30
    return ((sig + click) * env(n, 0.001, 0.02, 0, dur * .95, 0.9) * amp).astype(np.float32)


def piano(f, dur, amp=1.0, detune=0.0105):
    """Schoolroom upright, felt strip down, 18 cents flat and proud of it."""
    t = _t(dur); n = len(t)
    sig = np.zeros(n)
    for h, g in ((1, 1.0), (2, .38), (3, .17), (4, .09), (5, .045), (6, .02)):
        d = 1 + detune * (h - 1) * 0.5
        sig += g * (np.sin(2 * np.pi * f * h * d * t) + np.sin(2 * np.pi * f * h * t * (1 - detune * .35)))
        sig *= 1.0
    sig *= np.exp(-t * (1.7 + 0.55 * np.log2(max(f, 40) / 55.0)))
    sig += rng.normal(0, 1, n) * np.exp(-t * 420) * 0.22
    return (sig * env(n, 0.004, 0.05, 0, dur * .9, 0.8) * amp * 0.42).astype(np.float32)


def cello(f, dur, amp=1.0):
    """Bowed, with a slow vibrato that arrives late, like a real player's."""
    t = _t(dur); n = len(t)
    vib = 1 + 0.0045 * np.sin(2 * np.pi * 5.1 * t) * np.clip((t - 0.35) * 1.6, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    sig = sum((1.0 / h) * np.sin(ph * h) for h in (1, 2, 3, 4, 5, 6, 7, 8))
    b = np.exp(-np.arange(n) / (SR * 0.06))                  # bow noise, decaying
    sig += rng.normal(0, 1, n) * 0.05 * b
    ker = np.exp(-np.linspace(0, 5, 24)); ker /= ker.sum()
    out = np.convolve(sig, ker, mode="same")
    return (out * env(n, 0.16, 0.2, 0, min(0.5, dur * .4), 0.78) * amp * 0.5).astype(np.float32)


def marimba(f, dur, amp=1.0):
    t = _t(dur); n = len(t)
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
           + 0.3 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t * 16))
    return (sig * env(n, 0.002, 0.03, 0, dur * .9, .85) * amp * 0.8).astype(np.float32)


def musicbox(f, dur, amp=1.0):
    t = _t(dur); n = len(t)
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t * 4.5)
           + 0.45 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 8)
           + 0.22 * np.sin(2 * np.pi * f * 5.1 * t) * np.exp(-t * 14))
    return (sig * env(n, 0.001, 0.02, 0, dur * .95, .9) * amp * 0.55).astype(np.float32)


def subnote(f, dur, amp=1.0):
    t = _t(dur); n = len(t)
    sig = np.tanh(np.sin(2 * np.pi * f * t) * 1.6) * 0.7 + 0.2 * np.sin(2 * np.pi * f * 2 * t)
    return (sig * env(n, 0.09, 0.3, 0, dur * .5, .8) * amp).astype(np.float32)


def strings_low(f, dur, amp=1.0):
    """Six players used as a floor, never as a melody."""
    t = _t(dur); n = len(t); sig = np.zeros(n)
    for k in range(6):
        det = 1 + rng.normal(0, 0.0022)
        ph = 2 * np.pi * f * det * t + rng.uniform(0, 6.28)
        sig += sum((1.0 / h ** 1.4) * np.sin(ph * h) for h in (1, 2, 3, 4))
    sig /= 6
    return (sig * env(n, 0.5, 0.4, 0, min(1.4, dur * .45), .8) * amp * 0.35).astype(np.float32)


def breath_voice(dur, amp=1.0, pitch=220.0):
    """Unpitched close-miked breath. The taken speak like this."""
    n = int(dur * SR); t = _t(dur)
    nz = rng.normal(0, 1, n)
    k = 700
    ker = np.exp(-np.linspace(0, 6, k)) * np.cos(2 * np.pi * pitch * np.arange(k) / SR)
    nz = np.convolve(nz, ker, mode="same") / (k ** 0.5)
    return (nz * env(n, dur * .35, dur * .2, 0, dur * .45, .7) * amp * 2.4).astype(np.float32)


# ------------------------------------------------------------------ noise ---
def _noise(n):
    return rng.normal(0, 1, n).astype(np.float32)


def _lp(x, cutoff):
    """Cheap FFT-domain one-pole-ish lowpass (fine for beds)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1.0 / (1.0 + (f / cutoff) ** 2)
    return np.fft.irfft(X, n).astype(np.float32)


def _hp(x, cutoff):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= (f / cutoff) ** 2 / (1.0 + (f / cutoff) ** 2)
    return np.fft.irfft(X, n).astype(np.float32)


def _bp(x, lo, hi):
    return _lp(_hp(x, lo), hi)


# ------------------------------------------------------------------ beds ----
_BED_CACHE = {}


def bed(kind, n):
    """Looping ambience beds, generated once and tiled."""
    key = (kind, )
    if key not in _BED_CACHE:
        L = int(SR * 12)
        x = _noise(L)
        if kind == "valley_night":
            b = _bp(x, 200, 2600) * 0.055 + _lp(_noise(L), 90) * 0.30
            drip = np.zeros(L, np.float32)
            for _ in range(26):
                i = rng.integers(0, L - 4000)
                d = np.exp(-np.arange(3000) / 260.0) * np.sin(
                    2 * np.pi * rng.uniform(900, 2200) * np.arange(3000) / SR)
                drip[i:i + 3000] += d.astype(np.float32) * rng.uniform(.02, .07)
            b += drip
        elif kind == "valley_day":
            b = _bp(x, 300, 4200) * 0.035 + _lp(_noise(L), 120) * 0.16
            for _ in range(9):                       # rooks
                i = rng.integers(0, L - 12000)
                t = np.arange(9000) / SR
                caw = (np.sin(2 * np.pi * (620 + 240 * np.exp(-t * 22)) * t)
                       * np.exp(-t * 7) * (rng.random() > .3))
                b[i:i + 9000] += caw.astype(np.float32) * 0.05
        elif kind == "room":
            b = _lp(x, 220) * 0.34 + _bp(_noise(L), 400, 1400) * 0.012
        elif kind == "kiosk":                        # the fridge hums a flat B-flat
            t = np.arange(L) / SR
            b = _lp(_noise(L), 200) * 0.28
            b += (0.030 * np.sin(2 * np.pi * 116.0 * t)
                  + 0.012 * np.sin(2 * np.pi * 232.0 * t)).astype(np.float32)
        elif kind == "school":
            t = np.arange(L) / SR
            b = _lp(_noise(L), 260) * 0.30 + _bp(_noise(L), 600, 3000) * 0.02
            b += (0.010 * np.sin(2 * np.pi * 100.0 * t)).astype(np.float32)
            for i in range(0, L, int(SR * 7)):       # radiator, 7-second cycle
                k = np.exp(-np.arange(1400) / 90.0) * np.sin(
                    2 * np.pi * 1800 * np.arange(1400) / SR)
                if i + 1400 < L:
                    b[i:i + 1400] += k.astype(np.float32) * 0.05
        elif kind == "forecourt":                    # 50 Hz fluorescent buzz
            t = np.arange(L) / SR
            b = _lp(_noise(L), 300) * 0.22 + _bp(_noise(L), 800, 5000) * 0.02
            b += (0.026 * np.sin(2 * np.pi * 100 * t) + 0.014 * np.sin(2 * np.pi * 200 * t)
                  + 0.008 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
        elif kind == "dead":                         # the Spiegelweiher: nothing
            b = _lp(x, 60) * 0.10
        else:
            b = _lp(x, 400) * 0.10
        # loop-safe crossfade
        xf = int(SR * 0.7)
        b[:xf] = b[:xf] * np.linspace(0, 1, xf) + b[-xf:] * np.linspace(1, 0, xf)
        _BED_CACHE[key] = b[:-xf].astype(np.float32)
    src = _BED_CACHE[key]
    reps = int(n / len(src)) + 2
    return np.tile(src, reps)[:n]


# ------------------------------------------------------------------- sfx ----
def lantern_hum(dur, amp=1.0):
    t = _t(dur); n = len(t)
    wob = 1 + 0.10 * np.sin(2 * np.pi * 0.4 * t)
    sig = (0.5 * np.sin(2 * np.pi * 100 * t) + 0.2 * np.sin(2 * np.pi * 200 * t)
           + 0.08 * np.sin(2 * np.pi * 300 * t)) * wob
    return (sig * amp * 0.11).astype(np.float32)


def lantern_ignite(amp=1.0):
    """Thermal tick-tick-tick of expanding cast iron, then the hum warms up."""
    out = np.zeros(int(SR * 1.5), np.float32)
    for k, off in enumerate((0.0, 0.14, 0.27)):
        i = int(off * SR)
        tick = (np.exp(-np.arange(900) / 60.0)
                * np.sin(2 * np.pi * (2400 - k * 300) * np.arange(900) / SR))
        out[i:i + 900] += tick.astype(np.float32) * 0.22
    warm = lantern_hum(1.2) * np.linspace(0, 1, int(SR * 1.2)) ** 2
    out[int(SR * .3):int(SR * .3) + len(warm)] += warm
    return out * amp


def glass_struck(f=1180.0, amp=1.0, dur=2.6):
    """A single struck wineglass. His only sound."""
    t = _t(dur); n = len(t)
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t * 1.5)
           + 0.3 * np.sin(2 * np.pi * f * 2.74 * t) * np.exp(-t * 3.2))
    sig[:400] += rng.normal(0, 1, 400) * np.exp(-np.arange(400) / 30.0) * 0.4
    return (sig * amp * 0.5).astype(np.float32)


def glass_descend(dur=4.0, amp=1.0):
    """The sound of light being drunk: a rim tone falling two semitones."""
    t = _t(dur)
    f = 880 * 2 ** (-2 * t / dur / 12) * np.exp(-t * 0.18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.3 * np.sin(ph * 2.76)
    return (sig * env(len(t), .6, .5, 0, dur * .4, .7) * amp * 0.3).astype(np.float32)


def moped(dur, amp=1.0, rev=1.0):
    t = _t(dur); n = len(t)
    f = 62 * rev * (1 + 0.03 * np.sin(2 * np.pi * 3.1 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.tanh(2.2 * (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)))
    sig += _bp(_noise(n), 300, 3000) * 0.30
    return (sig * amp * 0.10).astype(np.float32)


def flare(dur, amp=1.0, dying=False):
    n = int(dur * SR)
    hiss = _hp(_noise(n), 1400) * 1.2 + _bp(_noise(n), 300, 900) * 0.5
    e = np.ones(n, np.float32)
    e[:int(SR * .12)] = np.linspace(0, 1, int(SR * .12)) ** .4
    if dying:
        e *= np.linspace(1, 0, n) ** 1.6
        f = np.linspace(1.0, 0.35, n)                    # the flame bends, not stops
        hiss = _lp(hiss, 6000) * f
    return (hiss * e * amp * 0.075).astype(np.float32)


def thump(amp=1.0):
    """A heavy door closing. The ring shutting."""
    t = _t(2.2)
    f = 62 * np.exp(-t * 2.4) + 30
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.0)
    sig += _lp(_noise(len(t)), 160) * np.exp(-t * 9) * 0.7
    return (sig * amp * 0.55).astype(np.float32)


def sub_pressure(dur, amp=1.0):
    """22 Hz. Inaudible on a laptop. Deliberate."""
    t = _t(dur)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return (np.sin(2 * np.pi * 22 * t) * e * amp * 0.5).astype(np.float32)


def torch_click(amp=1.0):
    n = 1400
    s = _hp(_noise(n), 2200) * np.exp(-np.arange(n) / 70.0)
    return (s * amp * 0.5).astype(np.float32)


def marble_roll(amp=1.0):
    """The best prop in the show: a glass marble rolling to a stop on stone."""
    dur = 2.4; t = _t(dur); n = len(t)
    out = np.zeros(n, np.float32)
    tt, gap = 0.02, 0.055
    while tt < dur - 0.05:
        i = int(tt * SR)
        k = (np.exp(-np.arange(700) / 26.0)
             * np.sin(2 * np.pi * rng.uniform(2400, 3400) * np.arange(700) / SR))
        out[i:i + 700] += k.astype(np.float32) * (1 - tt / dur) * 0.35
        gap *= 1.10; tt += gap
    return out * amp


def breathing(dur, amp=1.0, rate=0.9, n_people=5):
    """Five people in the dark, refusing to leave."""
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    for k in range(n_people):
        r = rate * rng.uniform(0.75, 1.45)
        ph = rng.uniform(0, 1)
        tt = ph / r
        while tt < dur - 0.9:
            b = breath_voice(0.75, rng.uniform(.35, .8) * amp, pitch=rng.uniform(140, 320))
            i = int(tt * SR)
            m = min(len(b), n - i)
            out[i:i + m] += b[:m]
            tt += 1.0 / r
    return out


# ---------------------------------------------------------------- reverb ----
def make_ir(rt60=1.7, pre=0.018, seed=3):
    r = np.random.default_rng(seed)
    n = int(SR * rt60)
    ir = r.normal(0, 1, n) * np.exp(-np.arange(n) * (6.9 / (rt60 * SR)))
    ir = _lp(ir.astype(np.float32), 5200)
    for d, g in ((0.011, .5), (0.019, .38), (0.031, .29), (0.043, .22)):
        i = int(d * SR)
        ir[i:i + 500] += r.normal(0, 1, 500).astype(np.float32) * g * 0.5
    ir[:int(pre * SR)] = 0
    return (ir / (np.abs(ir).sum() ** 0.5 + 1e-9) * 0.55).astype(np.float32)


def convolve_oa(x, ir, block=1 << 17):
    """Overlap-add FFT convolution."""
    nfft = 1
    while nfft < block + len(ir):
        nfft <<= 1
    H = np.fft.rfft(ir, nfft)
    out = np.zeros(len(x) + len(ir), np.float32)
    for i in range(0, len(x), block):
        seg = x[i:i + block]
        y = np.fft.irfft(np.fft.rfft(seg, nfft) * H, nfft)[:len(seg) + len(ir)]
        out[i:i + len(y)] += y.astype(np.float32)
    return out[:len(x)]


# ------------------------------------------------------------- sequencer ----
EIGHTH = 0.30            # 7/8 at this pulse gives a 2.10 s bar


class Bus:
    def __init__(self, n):
        self.x = np.zeros(n, np.float32)

    def add(self, t, sig, g=1.0):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]; i = 0
        m = min(len(sig), len(self.x) - i)
        if m > 0:
            self.x[i:i + m] += sig[:m] * g


# NACHTGLAS main theme: five rising notes, the fifth one falling short.
THEME = [("D5", 3), ("F5", 2), ("A5", 2),
         ("C6", 3), ("A#5", 4),
         ("A5", 3), ("G5", 2), ("F5", 2),
         ("E5", 3), ("D5", 4)]
THEME_BASS = [("D2", 7), ("A#1", 7), ("G1", 7), ("A1", 7)]
JUNO_MOTIF = [("A4", 2), ("C5", 2), ("D5", 2), ("F5", 3)]
PEPE_BOX = [("F5", 2), ("A5", 2), ("C6", 2), ("A5", 2), ("F5", 2), ("G5", 2),
            ("A5", 2), ("F5", 2), ("D5", 2), ("F5", 2), ("E5", 3), ("C5", 4)]


def seq(bus, t0, notes, instr, amp=1.0, gap=1.0, eighth=EIGHTH, hold=1.0):
    t = t0
    for name, beats in notes:
        d = beats * eighth * gap
        bus.add(t, instr(N[name], d * hold + 0.35, amp))
        t += d
    return t


def ostinato(bus, t0, t1, amp=1.0, eighth=EIGHTH, accel=0.0, pitches=("D3", "A3", "D4")):
    """Struck bottles on the 3+2+2 accents. `accel` compresses the pulse."""
    t, k = t0, 0
    while t < t1:
        prog = (t - t0) / max(1e-6, t1 - t0)
        e = eighth * (1.0 - accel * prog)
        for off in (0, 3, 5):
            tt = t + off * e
            if tt < t1:
                bus.add(tt, bottle(N[pitches[(k + off) % len(pitches)]],
                                   1.0, amp * (1.0 if off == 0 else 0.55)))
        t += 7 * e; k += 1


def floor(bus, t0, t1, roots=("D2", "A#1"), amp=1.0):
    t, k = t0, 0
    while t < t1:
        d = min(4.2, t1 - t)
        bus.add(t, strings_low(N[roots[k % len(roots)]], d + 1.0, amp))
        t += d; k += 1


# ------------------------------------------------------------------ cues ----
def cue_cold_open(mus, t0, t1):
    """1M1 — glass rims from black, subtracting to nothing as the lanterns die."""
    t, i = t0, 0
    chords = [("D4", "A4"), ("D4", "A4"), ("C4", "G4"), ("A#3", "F4")]
    while t < t1 - 1.0:
        g = max(0.0, 1.0 - (t - t0) / (t1 - t0) * 0.75)
        for nm in chords[i % len(chords)]:
            mus.add(t, glass(N[nm], 6.0, 0.26 * g))
        t += 4.0; i += 1
    mus.add(t1 - 2.6, glass_struck(N["D5"], 0.45))


def cue_main_title(mus, t0, t1):
    """The only time in the episode the theme plays complete."""
    ostinato(mus, t0 + 2.1, t1 - 1.0, amp=0.34, accel=0.0)
    floor(mus, t0, t1 - 0.5, roots=("D2", "D2", "A#1", "A1"), amp=0.62)
    t = seq(mus, t0 + 4.2, THEME, glass, amp=0.40)
    seq(mus, t0 + 4.2, [(n, b) for n, b in THEME[:6]], piano, amp=0.16, hold=0.5)
    seq(mus, t + 0.3, JUNO_MOTIF, marimba, amp=0.26)
    mus.add(t1 - 2.2, subnote(N["D1"], 2.4, 0.30))
    mus.add(t1 - 1.9, glass_struck(N["D6"], 0.30))


def cue_municipal(mus, t0, t1):
    """1M2 — bright, dumb, municipal."""
    t, i = t0, 0
    pat = [("D5", 2), ("F5", 2), ("A5", 2), ("G5", 2), ("F5", 2), ("D5", 3)]
    while t < t1 - 1.0:
        t = seq(mus, t, pat, marimba, amp=0.20, eighth=0.26)
        i += 1
    floor(mus, t0, t1, roots=("D3", "A#2"), amp=0.22)


def cue_cello_walk(mus, t0, t1):
    """1M3 — solo cello, one note per bar, absolutely patient."""
    notes = ["D3", "F3", "E3", "D3", "A#2", "C3", "D3", "A2"]
    t, i = t0, 0
    while t < t1 - 1.5:
        mus.add(t, cello(N[notes[i % len(notes)]], 3.4, 0.30))
        t += 2.6; i += 1


def cue_question(mus, t0, t1):
    """1M4 — one bowed glass, rising, cut off unresolved."""
    d = max(1.4, t1 - t0)
    mus.add(t0, glass(N["A4"], d, 0.30))
    mus.add(t0 + d * 0.35, glass(N["C5"], d * 0.8, 0.24))
    mus.add(t0 + d * 0.62, glass(N["D5"], d * 0.6, 0.26))


def cue_piano_finding(mus, t0, t1):
    """2M1 — single notes finding each other."""
    notes = ["D4", "A4", "F4", "D5", "C5", "A4", "G4", "F4", "A4", "D5"]
    t, i = t0, 0
    while t < t1 - 1.0:
        mus.add(t, piano(N[notes[i % len(notes)]], 3.0, 0.24))
        t += 1.35 + (0.5 if i % 4 == 3 else 0.0); i += 1
    floor(mus, t0 + 3, t1, roots=("D2",), amp=0.26)


def cue_pulse(mus, t0, t1, amp=1.0, accel=0.10, subtract=False, theme=False):
    """2M2 / 3M1 — the pulse. When the Loescher is near, layers leave."""
    span = t1 - t0
    ostinato(mus, t0, t1, amp=0.30 * amp, accel=accel)
    if subtract:
        floor(mus, t0, t0 + span * 0.55, roots=("D2", "A#1"), amp=0.55 * amp)
        if theme:
            seq(mus, t0 + 1.0, THEME[:5], glass, amp=0.22 * amp)
    else:
        floor(mus, t0, t1, roots=("D2", "A#1", "G1"), amp=0.55 * amp)
        t = t0 + 2.0
        while t < t1 - 3.0:
            seq(mus, t, THEME[:3], glass, amp=0.20 * amp)
            t += 8.4


def cue_theme_quiet(mus, t0, t1):
    """4M1 — the main theme, properly, for the first time."""
    seq(mus, t0 + 0.6, THEME, glass, amp=0.34)
    floor(mus, t0 + 4, t1, roots=("D2", "A#1"), amp=0.5)
    ostinato(mus, t0 + 8.4, t1, amp=0.20)


def cue_theme_warm(mus, t0, t1):
    """4M2 — the first major chord in the entire episode."""
    seq(mus, t0 + 0.4, [("D4", 3), ("F4", 2), ("A4", 2), ("D5", 7)], cello, amp=0.40)
    floor(mus, t0, t1, roots=("D2", "F2"), amp=0.55)
    seq(mus, t0 + 6.0, THEME[:6], glass, amp=0.26)
    seq(mus, t0 + 3.0, PEPE_BOX[:8], musicbox, amp=0.18, eighth=0.26)


def cue_dawn(mus, t0, t1):
    notes = ["D4", "F4", "A4", "G4", "F4", "D4"]
    t, i = t0, 0
    while t < t1 - 1.0:
        mus.add(t, piano(N[notes[i % len(notes)]], 3.2, 0.20))
        t += 1.9; i += 1


def cue_final(mus, t0, t1):
    """4M3 — glass choir, breath choir, and one sub-bass D."""
    for k, nm in enumerate(("D4", "F4", "A4", "C5", "D5")):
        mus.add(t0 + k * 1.1, glass(N[nm], (t1 - t0) - k * 1.1, 0.22))
    for k in range(7):
        mus.add(t0 + 1.0 + k * 1.3, breath_voice(2.2, 0.16, pitch=180 + k * 40))
    mus.add(t1 - 7.0, subnote(N["D1"], 6.5, 0.55))
    mus.add(t1 - 6.9, strings_low(N["D2"], 6.5, 0.8))
    mus.add(t1 - 2.0, glass_struck(N["D6"], 0.42))


# ------------------------------------------------------------------ mix -----
BEDS = {"valley": "valley_night", "bypass": "valley_night", "uhlen": "valley_night",
        "street": "valley_night", "lantern": "valley_night", "window": "valley_night",
        "bauhof": "valley_night", "torhaus": "valley_night", "dawn": "valley_day",
        "markt": "valley_day", "class": "school", "kiosk": "kiosk", "back": "room",
        "tanke": "forecourt", "peperoom": "room", "title": None}

CUE_MAP = {                       # scene id -> cue builder
    1: cue_cold_open, 2: cue_cold_open, 0: cue_main_title, 3: cue_municipal,
    5: None, 6: cue_cello_walk, 7: cue_question, 8: cue_piano_finding,
    9: cue_piano_finding, 10: "pulse", 11: "pulse", 12: "pulse",
    13: "pulse_sub", 14: "pulse_sub", 15: "pulse_sub", 16: "pulse_sub",
    17: None, 18: cue_theme_quiet, 19: cue_theme_quiet, 20: None,
    21: "pulse_sub", 22: cue_theme_warm, 23: cue_dawn, 24: cue_final,
}


def render(out_wav):
    shots, total = build_timeline()
    total += 3.0
    n = int(total * SR)
    mus, amb, sfx = Bus(n), Bus(n), Bus(n)
    wet_env = np.ones(n, np.float32)          # reverb send automation

    # ---- scene spans
    spans = {}
    for s in shots:
        a, b = spans.get(s["scene"], (s["t0"], s["t1"]))
        spans[s["scene"]] = (min(a, s["t0"]), max(b, s["t1"]))

    # ---- music
    for sc, (a, b) in spans.items():
        cue = CUE_MAP.get(sc, None)
        if cue is None:
            continue
        if cue == "pulse":
            cue_pulse(mus, a, b, amp=0.9, accel=0.10)
        elif cue == "pulse_sub":
            cue_pulse(mus, a, b, amp=1.0, accel=0.18, subtract=True, theme=(sc == 21))
        else:
            cue(mus, a, b)

    # ---- beds, per shot
    for s in shots:
        kind = BEDS.get(s["loc"])
        if not kind:
            continue
        ns = int(s["dur"] * SR) + SR
        g = 0.55 if s["fx"].get("collapse") else 1.0
        amb.add(s["t0"], bed(kind, ns)[:ns], g)

    # ---- lantern hums, collapse automation, sfx
    prev_out = None
    for s in shots:
        fx, t0, dur = s["fx"], s["t0"], s["dur"]
        night = s["loc"] in ("valley", "bypass", "uhlen", "street", "lantern",
                             "window", "bauhof", "torhaus")
        if night:
            lit = 6 - len(fx.get("lamps_out", []))
            if lit > 0:
                sfx.add(t0, lantern_hum(dur + 0.5, 0.22 + 0.13 * lit))
        if fx.get("collapse"):
            i0, i1 = int(t0 * SR), int(s["t1"] * SR)
            ramp = int(min(1.2, dur * 0.5) * SR)
            wet_env[i0:i1] = 0.06
            if i0 > ramp:
                wet_env[i0 - ramp:i0] = np.linspace(1, 0.06, ramp)
            outs = set(fx.get("lamps_out", []))
            if prev_out is not None and outs > prev_out:
                sfx.add(t0 + 0.15, glass_descend(min(4.0, dur), 0.6))
        prev_out = set(fx.get("lamps_out", [])) if night else None

        fl = fx.get("flash")
        if fl == "engine":
            sfx.add(t0, moped(dur + 0.4, 0.85, rev=0.7))
        elif fl == "flare":
            sfx.add(t0, flare(dur + 0.3, 1.0))
        elif fl == "die":
            sfx.add(t0, flare(dur, 1.0, dying=True))
            sfx.add(t0, glass_descend(dur + 1.0, 1.1))
            sfx.add(t0 + dur * 0.7, marble_roll(0.7))
        elif fl == "torch":
            for k in range(5):
                sfx.add(t0 + 0.25 * k, torch_click(0.7))
        elif fl == "ignite":
            sfx.add(t0, lantern_ignite(1.0))
        elif fl == "black":
            sfx.add(t0, breathing(dur, 0.9, n_people=5))
            sfx.add(t0 + dur * 0.4, sub_pressure(dur * 0.6, 0.7))
        if fx.get("lamps_in"):
            for k in range(6):
                sfx.add(t0 + 0.18 * k, lantern_ignite(0.55))
        if fx.get("ring"):
            for k in range(11):                       # the ring closing
                sfx.add(t0 + 0.13 * k, glass_struck(N["D4"] * (1 + 0.055 * k), 0.30, 1.6))
            sfx.add(t0 + 1.5, thump(1.0))
            i1 = int(s["t1"] * SR)
            wet_env[int(t0 * SR):i1] = np.linspace(0.06, 1.35, i1 - int(t0 * SR))
        if fx.get("lo_glass"):
            sfx.add(t0 + 0.2, glass_struck(N["D5"], 0.75, 3.2))
        if fx.get("mirror"):
            for k in range(3):
                sfx.add(t0 + 0.6 + k * 1.4, breath_voice(1.1, 0.28, pitch=200 + 60 * k))
        if fx.get("lo") is not None and not fx.get("collapse"):
            sfx.add(t0, sub_pressure(dur, 0.35))
        if fx.get("marbles"):
            sfx.add(t0, glass(N["D6"], dur, 0.06))
        if s["loc"] == "bypass" and s["idx"] < 25 and fx.get("figs"):
            sfx.add(t0, moped(dur, 0.45, rev=0.55))

    # ---- reverb, with the send automated
    print("  convolving hall …")
    send = (amb.x * 0.85 + sfx.x * 0.7 + mus.x * 0.30).astype(np.float32)
    wet = convolve_oa(send, make_ir(1.8))
    del send
    mix = mus.x * 0.85 + amb.x * 0.9 + sfx.x + wet * (0.5 * wet_env)
    del wet
    mix = np.tanh(mix * 1.05) * 0.94
    peak = float(np.abs(mix).max()) or 1.0
    mix = (mix / peak * 0.90)

    st = np.empty((len(mix), 2), np.float32)
    st[:, 0] = mix; st[:, 1] = mix
    # gentle width: delay the right channel of the reverb-ish content by 11 samples
    st[11:, 1] = mix[:-11] * 0.97

    import wave
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return total


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    p = os.path.join(ROOT, "out", "nachtglas_101_mix.wav")
    print("rendering score + sound design …")
    d = render(p)
    print(f"  {p}  ({d/60:.0f}:{d%60:04.1f}, {os.path.getsize(p)/1e6:.1f} MB)")
