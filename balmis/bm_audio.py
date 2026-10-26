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
# ================= cues de Balmis (se concatena tras bm_audio_head.py)
def W(si, p, n=0): return tw(si, p, n)
def pen(t0, dur=0.3, g=0.14):
    n = int(dur * SR); t = tt(n); s = bp(nz(n), 2500, 8000) * np.sin(np.pi * t / dur) ** 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t))
    add((s * g).astype(np.float32), t0, 0.1, 1.0, 0.15)
def chime(t0, f=880, g=0.12):
    bell(t0, f, g); bell(t0 + 0.02, f * 1.5, g * 0.45)
def sparkle(t0, g=0.08, n=5, f0=1760):
    for j in range(n): bell(t0 + j * 0.045 + rng.rand() * 0.01, f0 * (1 + 0.12 * j), g * (1 - 0.12 * j))
def ship_bell(t0, g=0.14):
    for j in range(2): clang(t0 + j * 0.42, 620, g, -0.3, 2.4)
def glass_crack(t0, g=0.35):
    clang(t0, 2900, g * 0.6, 0.1, 0.6); crack(t0 + 0.02, g * 0.5, 0.1)
    for j in range(8): add(click(rng.uniform(3000, 8000), 0.003, g * 0.5 * rng.uniform(0.4, 1.0)), t0 + 0.03 + rng.rand() * 0.25, rng.rand() * 0.6 - 0.3)
def hull_creaks(t0, t1, g=0.16, per=1.3):
    tk = t0
    while tk < t1: creak(tk + rng.rand() * 0.3, g * rng.uniform(0.6, 1.0)); tk += per * rng.uniform(0.7, 1.3)
def gulls(t0, n=3, g=0.05):
    for j in range(n):
        tk = t0 + j * rng.uniform(0.5, 0.9)
        for q in range(rng.randint(2, 4)): chirp(tk + q * 0.13, rng.uniform(1700, 2100), rng.uniform(2300, 2700), rng.uniform(0.09, 0.14), g, rng.rand() * 1.2 - 0.6)

# ---------- música (drones por escena, ducking automático bajo la voz)
subdrone(0.0, B[1] + 1.0, 36.7, 0.16, 0.3, 2); drone([73.4, 110.0, 146.8], 0.0, B[1] + 1.0, 0.05, 700, 0.3, 2)
subdrone(B[1] - 0.5, B[2] + 1.0, 34.6, 0.16, 2, 2); drone([69.3, 103.8, 164.8], B[1] - 0.5, B[2] + 1.0, 0.05, 600, 2, 2)
subdrone(B[2] - 0.5, B[3] + 1.0, 36.7, 0.14, 2, 2); drone([73.4, 110.0, 146.8, 185.0], B[2] - 0.5, B[3] + 1.0, 0.045, 800, 2, 2)
subdrone(B[3] - 0.5, B[4] + 1.0, 32.7, 0.15, 2, 2); drone([65.4, 98.0, 130.8, 164.8], B[3] - 0.5, B[4] + 1.0, 0.045, 850, 2, 2)
subdrone(B[4] - 0.5, B[6] + 1.0, 36.7, 0.15, 2, 2); drone([73.4, 110.0, 146.8, 220.0], B[4] - 0.5, B[6] + 1.0, 0.045, 950, 2, 2)
subdrone(B[6] - 0.5, B[7] + 1.0, 30.9, 0.15, 2, 2); drone([61.7, 92.5, 123.5, 185.0], B[6] - 0.5, B[7] + 1.0, 0.045, 700, 2, 2)
subdrone(B[7] - 0.5, TEND + 0.4, 36.7, 0.15, 2, 4); drone([73.4, 110.0, 146.8, 185.0, 220.0], B[7] - 0.5, TEND + 0.4, 0.05, 900, 2, 4)

# ---------- S0 · gancho: la corbeta en el océano
riser(0.0, 1.0, 0.20, 60, 480, 0.4)
waves(0.0, B[1] + 1.2, 0.30, 800); wind(0.0, B[1] + 1.0, 0.12)
hull_creaks(0.3, B[1], 0.18, 1.1)
thunder(0.25, 0.22, -0.4)
sparkle(W(0, 'vacuna') - 0.05, 0.07)
whoosh(W(0, 'dentro') - 0.4, 0.8, 0.12, 300, 4000); chime(W(0, 'dentro') + 0.05, 660, 0.06)
boom(W(0, '22') - 0.02, 0.32, 0.0, 0.3); add(thud(0.6, 0.8), W(0, '22'), 0.0, 1.0, 0.3)
for j in range(6): bell(W(0, '22') + 0.05 + 0.08 * j, 1046 * (1 + 0.1 * j), 0.035)

# ---------- S1 · la viruela, Jenner, el viaje
whoosh(B[1] - 0.6, 1.0, 0.10, 300, 3500); paper(B[1] + 0.1, 1.2, 0.30)
heart(B[1] + 0.2, st0(2) - 0.3, 58, 64, 0.17)
for j in range(3): add(thud(0.42, 0.6), W(1, 'tres') + 0.12 * (j + 1), -0.3 + 0.3 * j, 1.0, 0.2)
whoosh(st0(2) - 0.8, 0.9, 0.12, 300, 4000); shutter(st0(2) - 0.3, 0.5)
bell(st0(2) + 0.05, 392, 0.09); bell(st0(2) + 0.05, 587, 0.05)
chime(W(2, 'descubrio') + 0.1, 784, 0.07)
T_V1 = st0(3) + 0.6
whoosh(T_V1 - 0.5, 0.9, 0.12, 200, 3500); waves(T_V1 - 0.3, B[2] + 0.8, 0.12, 700)
tk = T_V1
while tk < W(3, 'largo'): add(tick(1200, 0.05), tk, 0.0); tk += 0.16
glass_crack(W(3, 'largo') - 0.1, 0.35); add(thud(0.5, 0.7), W(3, 'largo') + 0.05, 0.0, 1.0, 0.3)

# ---------- S2 · llevarla viva
whoosh(B[2] - 0.6, 1.0, 0.12, 300, 4500); paper(B[2] + 0.2, 1.0, 0.30)
T_K = st0(5) + 0.45
whoosh(T_K - 0.4, 0.8, 0.10, 200, 3000)
waves(T_K - 0.3, B[3] + 0.8, 0.08, 500); hull_creaks(T_K, B[3] + 0.5, 0.15, 1.2)
chime(W(5, 'dos') + 0.05, 880, 0.09); chime(W(5, 'dos') + 0.17, 1046, 0.07)
t_dd = W(6, 'despues')
for j in range(9): add(tick(900 + 40 * j, 0.10), t_dd - 0.35 + j * 0.08, 0.0)
whoosh(W(6, 'liquido') - 0.05, 1.2, 0.07, 1500, 7000); sparkle(W(6, 'liquido') + 0.2, 0.05, 4, 2093)
chime(W(6, 'otros') + 0.1, 988, 0.09); chime(W(6, 'otros') + 0.2, 1175, 0.07)
per = (st1(7) + 0.1 - st0(7)) / 9.0
for p in range(9): bell(st0(7) + (p + 1) * per, 784 * (2 ** (p / 12.0 * 2)), 0.06); add(click(5000, 0.004, 0.12), st0(7) + p * per + 0.03, -0.4 + 0.1 * p)
whoosh(st0(7) - 0.2, 1.6, 0.08, 400, 5000)

# ---------- S3 · la salida de A Coruña
whoosh(B[3] - 0.6, 1.0, 0.12, 300, 4000)
waves(B[3] - 0.3, st0(9) + 1.0, 0.22, 900); wind(B[3] - 0.3, st0(9) + 1.0, 0.08)
ship_bell(st0(8) + 0.1, 0.12); gulls(B[3] + 0.3, 3, 0.04); hull_creaks(st0(8), st0(9), 0.14, 1.4)
T_BAL = st0(9) + 0.45
whoosh(T_BAL - 0.5, 0.8, 0.10, 300, 4000); shutter(T_BAL - 0.15, 0.45); paper(T_BAL, 1.0, 0.25)
bell(W(9, 'francisco') + 0.05, 523, 0.07); bell(W(9, 'francisco') + 0.05, 784, 0.04)
T_KID = st0(10) - 0.05
whoosh(T_KID - 0.4, 0.8, 0.10, 200, 3500); waves(T_KID - 0.3, st0(11), 0.10, 600)
for j in range(22): add(tick(700 + 30 * j, 0.09), W(10, '22') - 0.15 + 0.055 * j, -0.6 + 1.2 * (j % 11) / 10.0)
add(thud(0.4, 0.6), W(10, '22') + 1.06, 0.0, 1.0, 0.2)
T_ZEN = st0(11) - 0.15
whoosh(T_ZEN - 0.5, 0.9, 0.10, 300, 4000); shutter(T_ZEN - 0.15, 0.45)
bell(W(11, 'isabel') + 0.05, 659, 0.08); bell(W(11, 'isabel') + 0.05, 988, 0.04)

# ---------- S4 · la ruta (globo)
whoosh(B[4] - 0.6, 1.2, 0.12, 200, 3000); riser(B[4] - 0.2, st0(12) - 0.1, 0.10, 80, 400, 0.4)
waves(B[4], B[5] + 4.0, 0.10, 700); hull_creaks(B[4] + 0.3, B[5] + 4.0, 0.10, 1.6)
for i_, w_ in enumerate([W(12, 'canarias'), W(12, 'puerto'), W(12, 'venezuela'), W(14, 'cuba'), W(14, 'mexico'), W(15, 'filipinas'), W(16, 'china')]):
    sonar(w_ - 0.03, 660 * (2 ** (i_ * 2 / 12.0)), 0.11, 1.8, -0.3 + 0.1 * i_)
whoosh(st0(13) - 0.2, 1.2, 0.10, 200, 3000)
sonar(W(13, 'salvany') - 0.05, 523, 0.10, 2.0, -0.4); pen(W(13, 'salvany') + 0.1, 1.2, 0.08)
whoosh(st0(14) - 0.2, 1.0, 0.10, 200, 3000)
whoosh(st0(15) + 0.2, 2.4, 0.13, 150, 2500)
add(thud(0.5, 0.7), W(15, '26') - 0.05, 0.0, 1.0, 0.25)
whoosh(W(15, 'filipinas') - 0.8, 1.0, 0.10, 300, 3500)

# ---------- S5 · vuelta al mundo y Jenner
whoosh(st0(17) - 0.3, 3.2, 0.14, 120, 2200); riser(st0(17), st1(17) - 0.1, 0.10, 70, 380, 0.3)
bell(st1(17) + 0.25, 392, 0.10); bell(st1(17) + 0.25, 494, 0.07); bell(st1(17) + 0.25, 587, 0.06)
T_J5 = st1(17) + 0.75
whoosh(T_J5 - 0.5, 0.9, 0.10, 300, 4000); shutter(T_J5 - 0.15, 0.45); paper(T_J5 + 0.1, 1.0, 0.22)
pen(W(18, 'ejemplo') - 0.1, 0.9, 0.10); pen(W(18, 'filantropia'), 1.0, 0.10)
chime(W(18, 'noble') + 0.3, 784, 0.08)

# ---------- S6 · 2020
whoosh(B[6] - 0.6, 1.0, 0.12, 300, 4000)
war_drums(st0(19) + 0.2, st1(19) - 0.1, 96, 0.10)
for j in range(18): add(tick(1400, 0.05), W(19, 'ejercito') + j * (W(19, 'operacion') - W(19, 'ejercito')) / 18.0, -0.6 + 1.2 * rng.rand())
sonar(W(19, 'covid') - 0.05, 440, 0.10, 1.8)
whoosh(W(20, 'madrid') - 0.8, 1.0, 0.10, 200, 3000); sonar(W(20, 'madrid') - 0.05, 880, 0.12, 1.8)
T_H = W(20, 'nombre') - 0.2
whoosh(T_H - 0.4, 0.8, 0.10, 300, 4000); chime(W(20, 'isabel') - 0.05, 784, 0.09)
murmur(T_H, B[7] + 0.6, 0.04)

# ---------- S7 · cierre
whoosh(B[7] - 0.6, 1.0, 0.10, 300, 4000)
waves(B[7] - 0.3, TEND + 0.4, 0.07, 500); hull_creaks(B[7], TEND - 1.0, 0.10, 1.6)
tk = B[7] + 0.4
while tk < TEND - 1.5: bell(tk, rng.choice([1318, 1568, 1760, 2093]), 0.025); tk += rng.uniform(0.5, 0.9)
t_su = W(22, 'suscribete'); bell(t_su - 0.05, 1568, 0.14); bell(t_su + 0.28, 2093, 0.12); bell(t_su + 0.28, 1046, 0.05)
# ---------- mezcla final
def rev(x):
    n_ir = int(2.6 * SR); ir_ = (rng.randn(n_ir) * np.exp(-np.arange(n_ir) / SR / 0.75)).astype(np.float32); ir_ = lp(ir_, 5200); ir_ = np.concatenate([np.zeros(int(0.03 * SR), np.float32), ir_])
    y = fftconvolve(x, ir_)[:N]; return y / (np.abs(y).max() + 1e-9)
SL, SR_, L, R, AMB, VOZ, DUCK = AL.SL, AL.SR_, AL.L, AL.R, AL.AMB, AL.VOZ, AL.DUCK
wl = rev(SL); wr_ = rev(SR_)
amb = AMB * DUCK[None, :]
HK = 1 + 0.4 * np.clip((2.3 - tt(N)) / 0.3, 0, 1)
fxL = (L * (0.55 + 0.45 * DUCK) + amb[0]) * HK; fxR = (R * (0.55 + 0.45 * DUCK) + amb[1]) * HK
fxL = fxL + 0.30 * wl * np.abs(SL).max() * 6 * DUCK; fxR = fxR + 0.30 * wr_ * np.abs(SR_).max() * 6 * DUCK
mixL = VOZ * 1.2 + np.tanh(fxL * 1.2) / 1.2 * 0.80; mixR = VOZ * 1.2 + np.tanh(fxR * 1.2) / 1.2 * 0.80
mixL = np.tanh(mixL * 1.0) / np.tanh(1.0); mixR = np.tanh(mixR * 1.0) / np.tanh(1.0)
HG = 1 + 0.2 * np.clip((2.35 - tt(N)) / 0.35, 0, 1); mixL *= HG; mixR *= HG
pk = max(np.abs(mixL).max(), np.abs(mixR).max()); mixL *= 0.92 / pk; mixR *= 0.92 / pk
fade = np.clip(tt(N) / 0.25, 0, 1) * np.clip((TEND + 0.4 - tt(N)) / 2.2, 0, 1); mixL *= fade; mixR *= fade
st = np.stack([mixL, mixR], 1)[:int((TEND + 0.1) * SR)]
wv = wave.open('/home/claude/serie/balmis/bm_audio_raw.wav', 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
print('ok', round(float(np.sqrt((st ** 2).mean())), 3), 'voz rms', round(float(np.sqrt((VOZ ** 2).mean())), 3))
