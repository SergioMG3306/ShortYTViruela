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
