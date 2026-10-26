import sys, json
sys.path.insert(0, '/home/claude/serie/voltaire')
from vt_audio_lib import *
import vt_audio_lib as AL
EV = json.load(open('/home/claude/serie/voltaire/events.json'))
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
# ================= cues del Short de Voltaire (se concatena tras vt_audio_head.py)
import sys as _sys; _sys.path.insert(0, '/home/claude/serie/voltaire')
import vt_lib as _V
B = list(_V.B)
EVV = json.load(open('/home/claude/serie/voltaire/events.json'))
def W(si, p, n=0): return tw(si, p, n)

# ---------- instrumentos
def harpsi(t0, f, g=0.05, pan=0.0, dur=1.6):
    """clave: armónicos con caída rápida y ataque de púa."""
    n = int(dur * SR); t = tt(n); s = np.zeros(n, np.float32)
    for k in range(1, 9):
        s += (1.0 / k ** 0.75) * np.sin(2 * np.pi * f * k * (1 + 0.0006 * k * k) * t + k) * np.exp(-t * (2.2 + 1.4 * k))
    s = s * np.minimum(1, t / 0.002) + 0.25 * bp(nz(n), 2000, 7000) * np.exp(-t * 120)
    add((lp(s, 6500) * g).astype(np.float32), t0, pan, 1.0, 0.35, True)

NOTE = dict(D2=73.42, E2=82.41, F2=87.31, G2=98.0, A2=110.0, Bb2=116.54, C3=130.81, Cs3=138.59, D3=146.83, E3=164.81, F3=174.61, G3=196.0,
            A3=220.0, Bb3=233.08, C4=261.63, Cs4=277.18, D4=293.66, E4=329.63, F4=349.23, Fs3=185.0, Fs4=369.99, G4=392.0, A4=440.0)
def arp(t0, t1, chords, bpm=96, g=0.045, step=0.5):
    """arpegio barroco en corcheas: cada acorde dura 2 tiempos (4 notas)."""
    b = 60.0 / bpm * step; t = t0; k = 0
    while t < t1 - 0.05:
        ch = chords[(k // 4) % len(chords)]; pat = [0, 1, 2, 3][k % 4] if (k // 4) % 2 == 0 else [3, 2, 1, 2][k % 4]
        fade = min(1.0, (t - t0) / 0.8, (t1 - t) / 0.8)
        harpsi(t, NOTE[ch[pat]], g * max(0.0, fade), (-0.3 + 0.2 * pat))
        if k % 4 == 0: harpsi(t, NOTE[ch[0]] / 2, g * 0.8 * max(0.0, fade), 0.0, 2.2)
        t += b; k += 1

DM = ('D3', 'F3', 'A3', 'D4'); GM = ('G2', 'Bb2', 'D3', 'G3'); AM = ('A2', 'Cs3', 'E3', 'A3'); BB = ('Bb2', 'D3', 'F3', 'Bb3')
FM = ('F2', 'A2', 'C3', 'F3'); C7 = ('C3', 'E3', 'G3', 'Bb3'); DMAJ = ('D3', 'Fs3', 'A3', 'D4')

def quill_snd(t0, dur, g=0.10):
    n = int(dur * SR) + 1; t = tt(n)
    strokes = np.abs(np.sin(2 * np.pi * rng.uniform(5.5, 7.5) * t)) ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 1.7 * t + rng.rand() * 6))
    s = bp(nz(n), 2800, 9000) * strokes * swell(n, 0.03, 0.08)
    for j in range(int(dur * 9)): s[int(rng.rand() * (n - 200)):][:120] += bp(nz(120), 3000, 9000) * 0.6
    add((s * g).astype(np.float32), t0, 0.15, 1.0, 0.12)

def clink(t0, g=0.06, pan=None):
    f = rng.uniform(2300, 4200); n = int(0.5 * SR); t = tt(n); s = np.zeros(n, np.float32)
    for k, (m, a) in enumerate(((1.0, 1.0), (1.48, 0.6), (2.12, 0.4), (2.9, 0.25))): s += a * np.sin(2 * np.pi * f * m * t + k) * np.exp(-t * (14 + 8 * k))
    s += 0.5 * bp(nz(n), 3000, 9000) * np.exp(-t * 90)
    add((s * g).astype(np.float32), t0, rng.rand() * 1.2 - 0.6 if pan is None else pan, 1.0, 0.25)

def seal_snd(t0, g=0.7):
    add(thud(g * 0.9, 0.7), t0, 0.0, 1.0, 0.3)
    n = int(0.25 * SR); t = tt(n); add((lp(nz(n), 1200) * np.exp(-t * 18) * g * 0.35).astype(np.float32), t0 + 0.01, 0.0, 1.0, 0.2)

def rattle(t0, t1, g=0.10, rate=7.0):
    n = int((t1 - t0) * SR); t = tt(n)
    am = np.clip(np.sin(2 * np.pi * rate * t + 3 * np.sin(2 * np.pi * 0.9 * t)), 0, 1) ** 2
    s = bp(nz(n), 900, 5000) * (0.3 + 0.7 * am) * swell(n, 0.3, 0.4)
    add((s * g).astype(np.float32), t0, 0.0, 1.0, 0.15)
    tk = t0
    while tk < t1: add(click(rng.uniform(1500, 4000), 0.005, g * 0.8), tk, rng.rand() * 0.8 - 0.4); tk += rng.uniform(0.03, 0.09)

def glide(t0, t1, f0, f1, g=0.05):
    n = int((t1 - t0) * SR); t = tt(n); f = f0 * (f1 / f0) ** (t / t[-1]); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * swell(n, 0.05, 0.3)
    add((s * g).astype(np.float32), t0, 0.0, 1.0, 0.4)

def clock(t0, t1, g=0.05):
    tk = t0; k = 0
    while tk < t1: add(tick(1500 if k % 2 else 1100, g), tk, 0.25 if k % 2 else -0.25); tk += 0.5; k += 1

# ---------- música: clave barroca + bordón (se atenúa bajo la voz)
subdrone(0.0, TEND + 0.4, 36.7, 0.10, 0.5, 3)
arp(0.0, B[1] + 0.3, [DM, AM], 84, 0.040)
arp(B[1], B[2] + 0.3, [DM, GM, AM, DM], 96, 0.042)
arp(B[2], B[3] + 0.3, [DM, BB, GM, AM], 104, 0.042)
arp(B[3], B[4] + 0.3, [FM, C7, DM, AM], 104, 0.042)
arp(B[4], B[5] + 0.3, [BB, FM, GM, AM], 112, 0.044)
arp(B[5], B[6] + 0.3, [DM, AM, DM, AM], 72, 0.040)
arp(B[6], B[7] + 0.3, [FM, BB, C7, FM], 100, 0.046)
arp(B[7], TEND - 1.2, [DM, GM, AM, DMAJ], 92, 0.044)
for f in (NOTE['D3'], NOTE['Fs3'], NOTE['A3'], NOTE['D4']): harpsi(TEND - 2.4, f, 0.05, 0.0, 2.4)

# ---------- pluma y lacres (eventos de las escenas)
for (s_, t0, dur) in EVV['pen']:
    quill_snd(t0, dur, 0.09 if s_.isupper() else 0.12)
for (l_, t0) in EVV['seal']:
    seal_snd(t0 + 0.15, 0.75); whoosh(t0 - 0.1, 0.3, 0.06, 800, 5000)

# ---------- transiciones
for bi in range(1, 8): whoosh(B[bi] - 0.45, 0.9, 0.09, 250, 4500)

# ---------- S0 · gancho
riser(0.0, 1.0, 0.14, 70, 420, 0.3)
bell(W(0, 'voltaire') - 0.05, 784, 0.06); bell(W(0, 'voltaire') - 0.05, 1175, 0.035)
bell(W(0, 'loteria') - 0.05, 1568, 0.05); for_c = [clink(W(0, 'loteria') + 0.05 * j, 0.04) for j in range(5)]

# ---------- S1 · París, bonos, lotería
paper(B[1] + 0.2, 1.0, 0.22)
T1 = st0(2) - 0.3; T2 = st0(3) - 0.25; T3 = st0(4) - 0.15
paper(T1, 1.0, 0.25); glide(W(2, 'perdido') - 0.3, st1(2) + 0.3, 520, 180, 0.05)
rattle(T2, T3 + 0.4, 0.09); for_c = [creak(T2 + 0.4 + 0.7 * j, 0.10) for j in range(4)]
bell(W(3, 'loteria') + 0.05, 1046, 0.07); bell(W(3, 'loteria') + 0.15, 1318, 0.05)
paper(T3 + 0.1, 0.8, 0.22); paper(T3 + 0.6, 0.6, 0.2)

# ---------- S2 · la regla
paper(st0(6) - 0.1, 0.8, 0.22); paper(W(6, 'una') - 0.2, 0.6, 0.2)
paper(st0(7) - 0.1, 0.8, 0.22); paper(W(7, 'cien') - 0.2, 0.6, 0.2)
chime_t = W(8, 'misma'); bell(chime_t, 880, 0.07); bell(chime_t + 0.02, 880 * 1.5, 0.04)
t0g, t1g = W(9, 'comprabas') - 0.1, W(9, 'pequenos') + 0.25
for j in range(25): add(tick(900 + 30 * j, 0.06), t0g + (t1g - t0g) * j / 25, -0.5 + j / 25)
bell(W(9, 'cien') + 0.1, 1175, 0.07)

# ---------- S3 · premio, cuentas, fallo
c0, c1 = st0(10) - 0.2, st1(10) + 0.3
for j in range(56):
    ts = c0 + (c1 - c0) * (j / 56.0) ** 0.8; clink(ts + 0.55, 0.05 * rng.uniform(0.6, 1.0))
bell(W(10, '500.000') + 0.1, 1318, 0.06); bell(W(10, '500.000') + 0.1, 1760, 0.04)
clock(st0(11) - 0.2, st0(12) - 0.2, 0.05)
creak(W(12, 'menos') - 0.1, 0.16); add(thud(0.4, 0.6), W(12, 'menos') + 0.35, 0.3, 1.0, 0.2)
for j in range(6): paper(st0(13) + 0.2 + 0.25 * j, 0.4, 0.10)
bell(W(13, 'ganabas') + 0.05, 1046, 0.07); bell(W(13, 'ganabas') + 0.05, 1318, 0.05); bell(W(13, 'ganabas') + 0.05, 1568, 0.04)

# ---------- S4 · socios
bell(st0(14) + 0.1, 659, 0.06); bell(st0(14) + 0.45, 988, 0.05)
for j in range(6): add(step_snd(0.12, 80 + 8 * j), st0(15) + 0.1 * j, -0.5 + 0.2 * j, 1.0, 0.1)
for j in range(7): paper(W(15, 'bonos') - 0.2 + 0.13 * j + 0.5, 0.35, 0.10)
glide(W(15, 'casi') - 0.3, W(15, 'billetes') + 0.2, 200, 600, 0.04)
for j in range(6): paper(W(15, 'mes') - 0.25 + 0.2 * j, 0.25, 0.12)

# ---------- S5 · juicio
for j in range(4): tom(st0(16) + 0.55 * j, 70, 0.20, 0.0)
tom(W(16, 'juicio'), 60, 0.28, 0.0)
creak(W(17, 'regla') - 0.2, 0.12)
for j in range(8): clink(W(17, 'quedaron') + 0.06 * j, 0.05)

# ---------- S6 · fortuna
t18 = st0(18); tme = W(18, 'medio')
for c in range(8):
    hmax = 4 + int(9 * (0.6 + 0.4 * math.sin(c * 1.7))); a_, b_ = t18 - 0.1 + 0.07 * c, tme + 0.6 + 0.07 * c
    last = 0
    for k in range(1, 400):
        tk = a_ + (b_ - a_) * k / 400.0; n_ = int(hmax * ((lambda x: x * x * (3 - 2 * x))(min(1, max(0, (tk - a_) / (b_ - a_))))))
        if n_ > last: clink(tk, 0.035); last = n_
bell(tme + 0.1, 1046, 0.08); bell(tme + 0.1, 1318, 0.06); bell(tme + 0.1, 1568, 0.05)
paper(st0(19) - 0.2, 0.9, 0.2)

# ---------- S7 · cierre
pen_t = W(20, 'fallo') - 0.2; quill_snd(pen_t, 0.5, 0.12)
t_su = W(21, 'suscribete'); bell(t_su - 0.05, 1568, 0.12); bell(t_su + 0.28, 2093, 0.10); bell(t_su + 0.28, 1046, 0.05)
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
wv = wave.open('/home/claude/serie/voltaire/vt_audio_raw.wav', 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
print('ok', round(float(np.sqrt((st ** 2).mean())), 3), 'voz rms', round(float(np.sqrt((VOZ ** 2).mean())), 3))
