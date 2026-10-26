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
