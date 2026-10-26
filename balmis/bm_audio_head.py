import sys, json
sys.path.insert(0, '/home/claude/serie/balmis')
from bm_audio_lib import *
import bm_audio_lib as AL
EV = json.load(open('/home/claude/serie/balmis/events.json'))
def _e(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

# ---------- piezas nuevas
def riser(t0, t1, g=0.2, f0=60, f1=420, noise=0.35):
    n = int((t1 - t0) * SR); t = tt(n); x = np.linspace(0, 1, n) ** 2.2; f = f0 + (f1 - f0) * x; ph = 2 * np.pi * np.cumsum(f) / SR
    s = (np.sin(ph) + 0.5 * np.sin(1.5 * ph + 1)) * 0.6 + noise * bp(nz(n), 300, 5000) * x
    add((s * x ** 0.6 * g).astype(np.float32), t0, 0.0, 1.0, 0.25, True)
def reverse_hit(t_hit, dur=0.9, g=0.3):
    n = int(dur * SR); t = tt(n); s = bp(nz(n), 400, 7000) * (np.linspace(0, 1, n) ** 2.5); add((s * g).astype(np.float32), t_hit - dur, 0.0, 1.0, 0.3)
def glitch(t0, t1, g=0.3, dens=60):
    n = int(dens * (t1 - t0))
    for j in range(n):
        tj = t0 + (t1 - t0) * (j / max(n, 1)) ** 0.8 + rng.rand() * 0.01
        add(click(600 + rng.rand() * 5000, 0.004 + 0.01 * rng.rand(), g * (0.5 + 0.5 * rng.rand())), tj, rng.rand() * 1.6 - 0.8)
def sonar(t0, f=1050, g=0.3, dec=2.4, pan=0.0):
    n = int(dec * SR); t = tt(n); s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.0) * np.minimum(1, t / 0.01) + 0.35 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 5.5)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.7)
def chirp(t0, f0=1200, f1=3200, dur=0.07, g=0.2, pan=0.0):
    n = int(dur * SR); t = tt(n); f = f0 + (f1 - f0) * t / dur; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.01)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.2)
def step_snd(g=1.0, f=85):
    n = int(0.17 * SR); t = tt(n); s = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 30))) / SR) * np.exp(-t * 22) + 0.45 * bp(nz(n), 300, 2400) * np.exp(-t * 55) + 0.2 * lp(nz(n), 600) * np.exp(-t * 25)
    return (s * g).astype(np.float32)
def stomps(t0, t1, hz, g_fn, v_fn, spread=1.4):
    t = t0
    while t < t1:
        g = g_fn(t); nv = int(max(1, round(v_fn(t))))
        for v in range(nv): add(step_snd(g * (0.55 + 0.45 * rng.rand()), 65 + rng.rand() * 45), t + rng.randn() * 0.014, (rng.rand() - 0.5) * spread, 1.0, 0.10)
        t += 1.0 / hz
def tom(t0, f=95, g=0.5, pan=0.0):
    n = int(0.45 * SR); t = tt(n); s = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t * 20))) / SR) * np.exp(-t * 9) + 0.3 * bp(nz(n), 400, 2500) * np.exp(-t * 40)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.3)
def pluck(t0, f, g=0.18, dur=0.5, pan=0.0):
    n = int(dur * SR); t = tt(n); s = (2 * np.abs(2 * ((f * t) % 1) - 1) - 1) * 0.6 + 0.3 * np.sin(2 * np.pi * f * 2 * t); s = lp(s, 2200) * np.exp(-t * 7) * np.minimum(1, t / 0.003)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.35)
def drip(t0, g=0.14):
    n = int(0.14 * SR); t = tt(n); f = rng.uniform(1100, 2200) * np.exp(-t * rng.uniform(6, 14)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)
    add((s * g).astype(np.float32), t0, rng.rand() * 1.6 - 0.8, 1.0, 0.3)
def clop(t0, g=0.22, pan=0.0):
    n = int(0.12 * SR); t = tt(n); s = (np.sin(2 * np.pi * 720 * t) * 0.5 + bp(nz(n), 500, 3500) * 0.8) * np.exp(-t * 50)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.18)
def bird(t0, g=0.06):
    k = rng.randint(2, 5); t_ = t0
    for j in range(k): chirp(t_, rng.uniform(2800, 4200), rng.uniform(3200, 5200), rng.uniform(0.05, 0.10), g, rng.rand() * 1.4 - 0.7); t_ += rng.uniform(0.08, 0.16)

# ---------- máquina de escribir, fotos y sellos
for (text, t0, cps) in EV['tn']:
    typing(t0, len(text), cps, 0.42 if cps >= 14 else 0.38)
for (name, t0, t1) in EV['ph']:
    pan = 0.0
    shutter(t0, 0.7, pan); n_ = int(0.17 * SR); add(bp(nz(n_), 500, 6000) * (np.linspace(0, 1, n_) ** 2) * 0.22, t0, pan, 1.0, 0.1)
    add(thud(0.75, 0.5), t0 + 0.16, pan, 1.0, 0.2); add(bp(nz(int(0.07 * SR)), 700, 6000) * np.exp(-tt(int(0.07 * SR)) * 45) * 0.6, t0 + 0.16, pan, 1.0)
for (text, t0) in EV['sp']:
    stampthud(t0 + 0.14, 0.8)


# ================= piezas nuevas para Cervantes
def boom(t0, g=0.4, pan=0.0, dist=0.0):
    n = int(2.2 * SR); t = tt(n); f = 38 + 50 * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) + 0.9 * lp(nz(n), 420 - 220 * dist) * np.exp(-t * (4.5 - 2 * dist)) + (1 - dist) * 0.5 * bp(nz(n), 900, 5000) * np.exp(-t * 40)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.45 + 0.3 * dist)
def crack(t0, g=0.6, pan=0.0):
    n = int(0.9 * SR); t = tt(n)
    s = 1.2 * bp(nz(n), 1200, 9000) * np.exp(-t * 70) + 0.8 * lp(nz(n), 600) * np.exp(-t * 12) + np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.5)
def clang(t0, f=380, g=0.3, pan=0.0, dec=2.5):
    n = int(dec * SR); t = tt(n); s = np.zeros(n, np.float32)
    for k, (m, a) in enumerate(((1.0, 1.0), (2.32, 0.6), (3.86, 0.4), (5.41, 0.25), (6.9, 0.15))):
        s += a * np.sin(2 * np.pi * f * m * t + k) * np.exp(-t * (2.2 + 1.6 * k) * 2.5 / dec)
    s = s * np.minimum(1, t / 0.002) + 0.4 * bp(nz(n), 2000, 9000) * np.exp(-t * 80)
    add((s * g * 0.5).astype(np.float32), t0, pan, 1.0, 0.4)
def chains(t0, dur=0.8, g=0.2, pan=0.0):
    k = int(dur * 22)
    for j in range(k): clang(t0 + dur * (j / k) + rng.rand() * 0.03, rng.uniform(1800, 3600), g * rng.uniform(0.4, 1.0), pan + rng.rand() * 0.4 - 0.2, 0.25)
def coins(t0, n=12, g=0.15, dur=0.9):
    for j in range(n): clang(t0 + dur * (j / n) ** 1.4 + rng.rand() * 0.02, rng.uniform(2600, 4800), g * rng.uniform(0.5, 1.0), rng.rand() * 1.0 - 0.5, 0.35)
def wind(t0, t1, g=0.12):
    n = int((t1 - t0) * SR); t = tt(n)
    s = lp(nz(n), 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t) ** 2) + 0.25 * bp(nz(n), 900, 2600) * (0.3 + 0.7 * np.sin(2 * np.pi * 0.09 * t + 1) ** 4)
    add((s * swell(n, 1.0, 1.0) * g).astype(np.float32), t0, 0.0, 1.0, 0.05, True)
def gallop(t0, t1, g=0.22, pan0=-0.6, pan1=0.2):
    t = t0
    while t < t1:
        p = pan0 + (pan1 - pan0) * (t - t0) / max(1e-3, t1 - t0)
        for dt in (0.0, 0.09, 0.19): clop(t + dt, g * rng.uniform(0.7, 1.0), p)
        t += 0.42
def scratch(t0, dur=1.2, g=0.12):
    n = int(dur * SR); t = tt(n); e = np.zeros(n, np.float32); k = 0
    while k < n:
        l = int(rng.uniform(0.05, 0.16) * SR); e[k:k + l] = np.sin(np.linspace(0, np.pi, len(e[k:k + l]))) * rng.uniform(0.5, 1.0); k += l + int(rng.uniform(0.02, 0.08) * SR)
    add((bp(nz(n), 2500, 8000) * e * g).astype(np.float32), t0, 0.15, 1.0, 0.15)
def murmur(t0, t1, g=0.08):
    n = int((t1 - t0) * SR); t = tt(n); s = np.zeros(n, np.float32)
    for k in range(6): s += bp(nz(n), rng.uniform(250, 500), rng.uniform(900, 1500)) * (0.3 + 0.7 * np.abs(np.sin(2 * np.pi * rng.uniform(2, 5) * t + k)))
    add((s / 6 * swell(n, 0.8, 0.8) * g).astype(np.float32), t0, 0.0, 1.0, 0.2, True)
def oars(t0, t1, g=0.10, per=1.6):
    t = t0
    while t < t1:
        n = int(0.7 * SR); tq = tt(n); s = bp(nz(n), 300, 2400) * np.sin(np.pi * tq / tq[-1]) ** 3
        add((s * g).astype(np.float32), t, rng.rand() * 0.6 - 0.3, 1.0, 0.1)
        if rng.rand() < 0.4: creak(t + 0.2, g * 0.6)
        t += per
def steps(t0, n, hz, g=0.22, pan0=0.0, pan1=0.0, f=95):
    for j in range(n): add(step_snd(g * rng.uniform(0.8, 1.0), f + rng.rand() * 20), t0 + j / hz, pan0 + (pan1 - pan0) * j / max(1, n - 1), 1.0, 0.1)
def war_drums(t0, t1, bpm=100, g=0.3):
    t = t0; k = 0; b = 60.0 / bpm
    while t < t1:
        pat = (1.0, 0.0, 0.6, 0.6)[k % 4]
        if pat: tom(t, 90 if k % 4 == 0 else 120, g * pat, -0.2 if k % 2 else 0.2)
        t += b / 2; k += 1
ANDA = [(146.8, 174.6, 220.0), (130.8, 164.8, 196.0), (116.5, 146.8, 174.6), (110.0, 138.6, 164.8)]
def lute(t0, t1, bpm=84, g=0.09):
    b = 60.0 / bpm; t = t0; k = 0
    while t < t1:
        ch = ANDA[(k // 8) % 4]; pat = [0, 1, 2, 1, 0, 2, 1, 2][k % 8]; f = ch[pat] * (2 if k % 8 in (2, 5) else 1)
        fade = min(1.0, (t - t0) / 1.5, (t1 - t) / 1.5)
        pluck(t, f, g * max(0.0, fade), 0.6, -0.25 + 0.5 * (pat / 2)); 
        if k % 8 == 0: pluck(t, ch[0] / 2, g * 0.8 * max(0.0, fade), 1.2, 0.0)
        t += b / 2; k += 1

def W(si, p, n=0): return tw(si, p, n)


# ================= piezas líquidas y de madera
def roar(t0, t1, g=0.3, fc=260, a_in=0.05, a_out=2.5, pan=0.0):
    n = int((t1 - t0) * SR); t = tt(n)
    am = lp(np.abs(nz(n)), 18); am = am / (np.abs(am).max() + 1e-9)
    s = 1.0 * lp(nz(n), fc) + 0.55 * bp(nz(n), 400, 2600) * (0.4 + 0.6 * am) + 0.18 * bp(nz(n), 3000, 8000) * (0.3 + 0.7 * am)
    s = s * swell(n, a_in, a_out)
    add((s * g * 1.3).astype(np.float32), t0, pan, 1.0, 0.2, True)
def gush(t0, g=0.6, dur=1.6, pan=0.0):
    n = int(dur * SR); t = tt(n); fc = 5000 * np.exp(-t * 3) + 200
    s = np.zeros(n, np.float32); x = nz(n)
    for k, (a_, b_) in enumerate(((150, 600), (600, 2000), (2000, 7000))):
        s += bp(x, a_, b_) * np.exp(-t * (1.2 + k * 1.5)) * (1.2 - 0.3 * k)
    s *= np.minimum(1, t / 0.01)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.4)
def splash(t0, g=0.25, pan=0.0):
    n = int(0.5 * SR); t = tt(n); s = bp(nz(n), 300, 5000) * np.exp(-t * 9) * np.minimum(1, t / 0.005)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.25)
    for j in range(6): add(click(rng.uniform(1500, 5000), 0.006, g * 0.3), t0 + 0.05 + rng.rand() * 0.4, pan + rng.rand() * 0.4 - 0.2)
def groan(t0, dur=1.4, g=0.3, f0=70, pan=0.0):
    n = int(dur * SR); t = tt(n); f = f0 * (1 + 0.25 * np.sin(2 * np.pi * 0.7 * t) + 0.1 * rng.randn() + 0.4 * t / dur)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    s = bp(saw * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * t))), 80, 900) * np.sin(np.pi * t / dur) ** 1.5
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.3)
def scrape(t0, dur=0.35, g=0.25):
    n = int(dur * SR); t = tt(n); s = bp(nz(n), 1500, 7000) * np.sin(np.pi * t / dur) * (0.5 + 0.5 * np.sin(2 * np.pi * 60 * t))
    add((s * g).astype(np.float32), t0, 0.2, 1.0, 0.2)
def bricks(t0, dur=1.6, g=0.5):
    n = int(dur * SR); t = tt(n); add((lp(nz(n), 900) * np.exp(-t * 2.2) * g * 0.6).astype(np.float32), t0, 0.0, 1.0, 0.3)
    for j in range(26): add(thud(g * rng.uniform(0.25, 0.7), 0.35), t0 + dur * rng.rand() ** 1.6, rng.rand() * 1.4 - 0.7, 1.0, 0.25)
def knock(t0, g=0.3, pan=0.0):
    n = int(0.25 * SR); t = tt(n); s = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30) + 0.5 * bp(nz(n), 400, 2500) * np.exp(-t * 60)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.2)
def hiss(t0, g=0.08):
    n = int(0.5 * SR); t = tt(n); add((bp(nz(n), 3000, 9000) * np.exp(-t * 7) * g).astype(np.float32), t0, rng.rand() * 0.6 - 0.3, 1.0, 0.1)
def pour(t0, t1, g=0.2):
    n = int((t1 - t0) * SR); t = tt(n); s = bp(nz(n), 300, 2500) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 6 * t))) * swell(n, 0.3, 0.6)
    add((s * g).astype(np.float32), t0, 0.0, 1.0, 0.2)
    tk = t0
    while tk < t1: bubble(tk, 0.10); tk += rng.uniform(0.06, 0.16)
def bubblewhoosh(tc, g=0.25):
    whoosh(tc - 0.7, 1.4, g * 0.6, 200, 3000)
    for j in range(40): bubble(tc - 0.6 + 1.2 * rng.rand(), g * 0.5)


def W(si, p, n=0): return tw(si, p, n)
def thunder(t0, g=0.4, pan=0.0):
    n = int(3.0 * SR); t = tt(n); s = lp(nz(n), 300) * np.exp(-t * 1.2) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3 * t))) + 0.6 * bp(nz(n), 600, 4000) * np.exp(-t * 12)
    add((s * g).astype(np.float32), t0, pan, 1.0, 0.5)
def rain(t0, t1, g=0.08):
    n = int((t1 - t0) * SR); add((bp(nz(n), 2000, 9000) * swell(n, 0.8, 0.8) * g).astype(np.float32), t0, 0.0, 1.0, 0.05, True)
def fire(t0, t1, g=0.12):
    tk = t0
    while tk < t1: add(click(rng.uniform(1500, 6000), 0.004, g * rng.uniform(0.3, 1.0)), tk, rng.rand() * 1.0 - 0.5); tk += rng.exponential(0.035)
    n = int((t1 - t0) * SR); add((lp(nz(n), 500) * swell(n, 0.4, 0.4) * g * 0.6).astype(np.float32), t0, 0.0, 1.0, 0.1, True)
