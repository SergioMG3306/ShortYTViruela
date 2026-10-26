import os; os.environ['PAL_DIR'] = '/home/claude/serie/voltaire'
import sys; sys.path.insert(0, '/home/claude/serie/cervantes')
import sys, wave, math
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
sys.path.insert(0, '/home/claude/serie/voltaire')
import cv_lib as P
from cv_lib import B, TEND, ST, prog, ease, tw, st0, st1
SR = 44100; rng = np.random.RandomState(11)
N = int((TEND + 0.5) * SR)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def nz(n): return rng.randn(n).astype(np.float32)
def tt(n): return np.arange(n, dtype=np.float32) / SR
def sine(f, n, ph=0.0): return np.sin(2 * np.pi * f * tt(n) + ph).astype(np.float32)
def swell(n, a, r):
    e = np.ones(n, np.float32); a = max(1, min(int(a * SR), n // 2)); r = max(1, min(int(r * SR), n // 2)); e[:a] = np.linspace(0, 1, a) ** 1.5; e[n - r:] = np.linspace(1, 0, r) ** 1.5; return e
L = np.zeros(N, np.float32); R = np.zeros(N, np.float32); SL = np.zeros(N, np.float32); SR_ = np.zeros(N, np.float32)
AMB = np.zeros((2, N), np.float32)         # capas ambientales (se atenúan con la voz)
def add(sig, t0, pan=0.0, g=1.0, send=0.0, amb=False):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(0, -i); j = min(N, i + len(sig)); s = sig[a:j - i] * g
    th = (pan + 1) * math.pi / 4; gl, gr = math.cos(th), math.sin(th); i0 = max(i, 0)
    tgt = AMB if amb else None
    if amb: AMB[0, i0:j] += s * gl; AMB[1, i0:j] += s * gr
    else: L[i0:j] += s * gl; R[i0:j] += s * gr
    if send: SL[i0:j] += s * gl * send; SR_[i0:j] += s * gr * send

# ---------- voz (cálida, cercana)
w = wave.open('/home/claude/serie/voltaire/voz.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
v = np.concatenate([v, np.zeros(max(0, N - len(v)), np.float32)])[:N]
v = hp(v, 70); v = v + 0.55 * lp(v, 200) + 0.06 * bp(v, 2200, 5200); v = lp(v, 9500)
e = np.sqrt(np.convolve(v * v, np.ones(1323) / 1323, 'same') + 1e-9); v *= np.clip((e + 1e-3) / 0.1, 0.01, 10) ** -0.38
v = v / np.abs(v).max() * 0.80
ir = (rng.randn(int(0.45 * SR)) * np.exp(-np.arange(int(0.45 * SR)) / SR / 0.11)).astype(np.float32); ir = hp(ir, 250)
wr = fftconvolve(v, ir)[:N]; v = v + 0.07 * wr / np.abs(wr).max() * np.abs(v).max()
VOZ = v.copy()
env = np.sqrt(np.convolve(VOZ * VOZ, np.ones(2205) / 2205, 'same') + 1e-12); env = np.clip(env / 0.10, 0, 1); sm = np.zeros(N, np.float32); cur = 0.0
at, rl = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.5 * SR))
for i in range(0, N, 441):
    m = env[i:i + 441].max(); k = at if m > cur else rl; cur += (m - cur) * (1 - (1 - k) ** 441); sm[i:i + 441] = cur
DUCK = 1 - 0.65 * sm

# ---------- piezas sonoras
def thud(g=1.0, dur=0.7):
    n = int(dur * SR); t = tt(n); f = 52 + 70 * np.exp(-t * 28); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return ((s + 0.5 * bp(nz(n), 900, 4500) * np.exp(-t * 90) + 0.25 * lp(nz(n), 400) * np.exp(-t * 18)) * g).astype(np.float32)
def beatpair(g=1.0):
    n = int(0.55 * SR); t = tt(n); a = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 20); b = np.zeros(n, np.float32); k = int(0.19 * SR); b[k:] = (np.sin(2 * np.pi * 44 * t[:n - k]) * np.exp(-t[:n - k] * 24)) * 0.7
    return ((a + b) * g).astype(np.float32)
def heart(t0, t1, b0, b1, g):
    t = t0
    while t < t1:
        bpm = b0 + (b1 - b0) * (t - t0) / max(1e-3, t1 - t0); add(beatpair(g * (0.7 + 0.3 * (t - t0) / max(1e-3, t1 - t0))), t, 0, 1.0, 0.15); t += 60.0 / bpm
def click(f0=3500, dur=0.004, g=1.0):
    n = int(dur * SR + 40); s = bp(nz(n), f0 * 0.6, min(f0 * 1.8, 18000)) * np.exp(-tt(n) / (dur * 0.35)); return (s * g).astype(np.float32)
def tick(f=900, g=1.0):
    n = int(0.09 * SR); t = tt(n); return ((np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * 0.6 + bp(nz(n), 2500, 7000) * np.exp(-t * 400)) * g).astype(np.float32)
def geiger(t0, t1, r0, r1, g=1.0):
    t = t0
    while t < t1:
        rate = r0 + (r1 - r0) * (t - t0) / (t1 - t0); t += rng.exponential(1.0 / max(rate, 0.1))
        if t < t1: add(click(2800 + rng.rand() * 2500, 0.0025 + rng.rand() * 0.0015, (0.5 + 0.5 * rng.rand()) * g), t, rng.rand() * 1.6 - 0.8, 1.0, 0.1)
def typing(t0, n, cps, g=0.5):
    for i in range(n):
        tk = t0 + i / cps + rng.rand() * 0.012; add(click(2200 + rng.rand() * 1800, 0.004, g * (0.7 + 0.3 * rng.rand())), tk, rng.rand() * 0.4 - 0.2)
    add(tick(1400, g * 0.45), t0 + n / cps + 0.05, 0.1)
def paper(tc, dur=1.4, g=0.5, low=False):
    n = int(dur * SR); t = tt(n); e = np.clip(np.sin(np.pi * t / dur), 0, None) ** 1.5
    s = bp(nz(n), 700 if not low else 250, 6500 if not low else 2200) * e
    cr = (rng.rand(n) < 0.0018).astype(np.float32) * nz(n); s += 0.9 * bp(cr, 1500, 9000) * 6
    add((s * g).astype(np.float32), tc - dur / 2, 0.0, 1.0, 0.12)
def stampthud(t0, g=0.8): add(thud(g), t0, 0.0, 1.0, 0.25); add(bp(nz(int(0.06 * SR)), 800, 5000) * np.exp(-tt(int(0.06 * SR)) * 55) * 0.5, t0, 0, 1.0)
def ping(t0, f=1250, g=0.4):
    n = int(2.2 * SR); t = tt(n); s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 3.2) * np.minimum(1, t / 0.006)
    add((s * g).astype(np.float32), t0, rng.rand() * 0.6 - 0.3, 1.0, 0.6)
def waves(t0, t1, g=0.3, fc=900):
    n = int((t1 - t0) * SR); t = tt(n)
    for pan, side in ((-0.7, 0), (0.7, 1)):
        s = lp(nz(n), fc) * (0.45 + 0.55 * np.sin(2 * np.pi * (0.11 + 0.02 * side) * t + side * 2.1) ** 2) + 0.18 * hp(lp(nz(n), 4500), 1500) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.11 * t + side * 2.1 + 0.6) ** 6)
        add((s * swell(n, 2, 2) * g).astype(np.float32), t0, pan, 1.0, 0.05, True)
def creak(t0, g=0.3):
    n = int(rng.uniform(0.35, 0.7) * SR); t = tt(n); f = 170 + 60 * np.sin(2 * np.pi * rng.uniform(3, 7) * t) + 80 * t; s = bp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + 0.5 * nz(n), 150, 1200)
    add((s * np.clip(np.sin(np.pi * t / t[-1]), 0, None) ** 2 * g).astype(np.float32), t0, rng.rand() - 0.5, 1.0, 0.1)
def bubble(t0, g=0.2):
    n = int(rng.uniform(0.04, 0.10) * SR); t = tt(n); f = rng.uniform(300, 700) * np.exp(t * rng.uniform(10, 18)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40); add((s * g).astype(np.float32), t0, rng.rand() * 1.6 - 0.8, 1.0, 0.2)
def shutter(t0, g=0.5, pan=0.0):
    add(click(3800, 0.005, g), t0, pan); add(click(1500, 0.009, g * 0.8), t0 + 0.055, pan); add(tick(2400, g * 0.25), t0 + 0.06, pan)
def bell(t0, f=1318, g=0.25):
    n = int(3.2 * SR); t = tt(n); s = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.76 * t) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 1.5) * np.minimum(1, t / 0.004); add((s * g).astype(np.float32), t0, 0.0, 1.0, 0.5)
def drone(freqs, t0, t1, amp, fc=800, ai=2.0, ao=2.5):
    n = int((t1 - t0) * SR); s = np.zeros(n, np.float32); t = tt(n)
    for f in freqs:
        for dt in (-0.004, 0, 0.004): s += (2 * ((f * (1 + dt) * t + rng.rand()) % 1) - 1)
    s = lp(s / (len(freqs) * 3), fc) * swell(n, ai, ao) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t)); add(s * amp, t0, 0.0, 1.0, 0.35, True)
def subdrone(t0, t1, f, amp, ai=3, ao=3):
    n = int((t1 - t0) * SR); t = tt(n); s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t + 1)) * swell(n, ai, ao) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.05 * t)); add((s * amp).astype(np.float32), t0, 0.0, 1.0, 0.1, True)
def whoosh(t0, dur, g, a=400, b=5000):
    n = int(dur * SR); t = tt(n); add((bp(nz(n), a, b) * np.clip(np.sin(np.pi * t / dur), 0, None) ** 2 * g).astype(np.float32), t0, rng.rand() - 0.5, 1.0, 0.2)

