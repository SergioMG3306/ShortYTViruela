"""Escenas del Short «Voltaire y la lotería de 1729» (1080×1920 nativo)."""
import sys
sys.path.insert(0, '/home/claude/serie/voltaire')
from vt_art import *

FOT = '/home/claude/serie/voltaire/fotos/'

def ink_circle(img, cx, cy, rx, ry, k, col=VERM, a=1.0, th=6):
    if k <= 0 or a <= 0.003: return
    n = 80; m = int(n * min(1, k)) + 1
    pts = [(cx + rx * math.cos(-2.2 + 2 * math.pi * 1.08 * j / n) * (1 + 0.03 * math.sin(j * 0.7)), cy + ry * math.sin(-2.2 + 2 * math.pi * 1.08 * j / n)) for j in range(m)]
    if len(pts) > 1: over(img, mline([pts], th), col, a)

def x_of(s, sub, sz, fname='play'):
    """centro x del primer `sub` dentro de `s` dibujado centrado en 540."""
    f = font(fname, sz); i = s.index(sub)
    return 540 - f.getlength(s) / 2 + f.getlength(s[:i]) + f.getlength(sub) / 2

def arrow(img, x0, y0, x1, y1, a=1.0, col=GOLD, th=5, k=1.0):
    if a <= 0.003 or k <= 0: return
    xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
    over(img, mline([[(x0, y0), (xe, ye)]], th), col, a)
    ang = math.atan2(ye - y0, xe - x0); L = 26
    head = [(xe, ye), (xe - L * math.cos(ang - 0.45), ye - L * math.sin(ang - 0.45)), (xe - L * math.cos(ang + 0.45), ye - L * math.sin(ang + 0.45))]
    over(img, mpoly([head]), col, a)

def pop(t, t0, d=0.25):
    """escala de aparición con rebote."""
    x = prog(t, t0, t0 + d)
    return 0.0 if x <= 0 else (1 + 0.12 * math.sin(math.pi * x)) * eo(x)

def name_tag(img, t, s, x, y, t0, a=1.0, sz=40, col=GOLDL):
    if a <= 0.003 or t < t0 - 0.3: return
    w = text_w(s, sz, 'cas') + 60; al = a * ease((t - t0 + 0.3) / 0.3)
    plate(img, x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, al, sh=0.35)
    write(img, t, s, x, y, sz, col, t0, 18, al, 'cas')


# ===================================================== S0 · ¿sabías que...?
def s0(t):
    t_vo, t_fa, t_lo = tw(0, 'voltaire'), tw(0, 'fallo'), tw(0, 'loteria')
    img = math_bg(t)
    framed_photo(img, FOT + 'voltaire.jpg', t, -0.3, B[1] + 0.6, 1.0, 1.16, (0.50, 0.40), (0.50, 0.34), (200, 310, 880, 1080), 1.0, True, 0.45)
    eq = 'billetes  <  premios'
    write(img, t, eq, 540, 1250, 70, IVORY, t_fa - 0.15, 20, 1.0, 'playr')
    ink_circle(img, x_of(eq, '<', 70, 'playr'), 1250, 48, 42, ease(prog(t, t_lo - 0.1, t_lo + 0.35)))
    img = cam(img, lerp(1.0, 1.05, ease(prog(t, 0, B[1] + 0.6))), 0, 0, 540, 700)
    name_tag(img, t, 'Voltaire', 540, 1150, t_vo - 0.1, 1.0, 50)
    al = 1 - ease(prog(t, st1(0) + 0.2, st1(0) + 0.6))       # cabecera grande desde el primer fotograma
    if al > 0.003:
        plate(img, 70, 96, 1010, 250, al); text(img, '¿SABÍAS QUE...?', 540, 173, 80, GOLDL, al, 'play')
    return img


# ===================================================== S1 · París, los bonos y la lotería
def s1(t):
    t_pa, t_bo, t_pe, t_go, t_lo, t_so = st0(1), st0(2), tw(2, 'perdido'), st0(3), tw(3, 'loteria'), st0(4)
    T1, T2, T3 = t_bo - 0.3, t_go - 0.25, t_so - 0.15
    img = math_bg(t)
    am = 1 - ease(prog(t, T1 - 0.3, T1 + 0.2))
    if am > 0.003:
        framed_photo(img, FOT + 'turgot.jpg', t, B[1] - 0.6, T1 + 0.3, 1.0, 1.55, (0.50, 0.50), (0.47, 0.50), (40, 330, 1040, 1115), am, False, 0.40)
    ab = win(t, T1 - 0.1, T2 - 0.1, 0.4, 0.4)
    if ab > 0.003:
        blit(img, bond_sprite('1.000 libras'), 540, 540, ab, 1.40 * max(0.01, pop(t, T1 - 0.1)))
        value_chart(img, 150, 820, 930, 1210, ease(prog(t, t_pe - 0.3, st1(2) + 0.3)), ab)
    ad = win(t, T2 - 0.1, T3 + 0.3, 0.4, 0.4)
    if ad > 0.003: drum(img, 540, 640, 360, t, ad, 1.0)
    ao = ease(prog(t, T3 - 0.1, T3 + 0.4))
    if ao > 0.003:
        blit(img, bond_sprite('1.000 libras'), 280, 720, ao, 1.12 * max(0.01, pop(t, T3 - 0.1)))
        arrow(img, 535, 720, 640, 720, ao, GOLD, 7, ease(prog(t, T3 + 0.2, T3 + 0.6)))
        blit(img, ticket_sprite('lotería'), 840, 720, ao * ease(prog(t, T3 + 0.5, T3 + 0.8)), 1.15 * max(0.01, pop(t, T3 + 0.5)))
    img = cam(img, lerp(1.0, 1.04, ease(prog(t, B[1] - 0.6, B[2] + 0.6))), 0, 0, 540, 760)
    header(img, t, 'PARÍS, 1729', t_pa - 0.05, T1 - 0.3, 68)
    header(img, t, 'LOS BONOS DE LA CIUDAD', t_bo - 0.05, T2 - 0.3, 58)
    header(img, t, 'LA LOTERÍA', t_lo - 0.15, T3 - 0.3, 68)
    header(img, t, 'SOLO LOS DUEÑOS DE BONOS', t_so - 0.05, B[2] - 0.2, 54)
    if am > 0.01: text(img, 'PLAN DE TURGOT (1739) · WIKIMEDIA COMMONS', 540, 1185, 22, IVORY, 0.75 * am, 'casr', track=1)
    return img


# ===================================================== S2 · la regla del billete
def grid_pos(i, x0=600, y0=500, cell=40):
    r, c = divmod(i, 10); return x0 + c * cell, y0 + r * cell * 0.72

def s2(t):
    t_bi = tw(5, 'billete'); t_6 = st0(6); t_una = tw(6, 'una'); t_7 = st0(7); t_cien = tw(7, 'cien'); t_8 = st0(8); t_mis = tw(8, 'misma')
    t_9 = st0(9); t_gr = tw(9, 'grande'); t_com = tw(9, 'comprabas'); t_c100 = tw(9, 'cien'); t_peq = tw(9, 'pequenos')
    img = math_bg(t)
    eq = 'billete = bono ÷ 1.000'
    write(img, t, eq, 540, 352, 76, IVORY, t_bi - 0.05, 13)
    over(img, mline([[(200, 410), (200 + 680 * ease(prog(t, t_bi + 1.4, t_bi + 1.9)), 410)]], 3), GOLD, 0.9)
    # fase A · dos bonos, dos billetes
    aA = 1 - ease(prog(t, t_8 - 0.25, t_8 + 0.25))
    if aA > 0.003:
        blit(img, bond_sprite('1.000 libras'), 280, 620, aA, 1.05 * max(0.01, pop(t, t_6 - 0.15)))
        arrow(img, 280, 790, 280, 870, aA, GOLD, 6, ease(prog(t, t_una - 0.5, t_una - 0.2)))
        blit(img, bond_sprite('100.000 libras', 440, 300), 800, 620, aA, 1.05 * max(0.01, pop(t, t_7 - 0.15)))
        arrow(img, 800, 790, 800, 870, aA, GOLD, 6, ease(prog(t, t_cien - 0.5, t_cien - 0.2)))
    # billetes (se quedan y se mueven)
    up = ease(prog(t, t_8 - 0.2, t_8 + 0.4))
    yA = lerp(1010, 660, up); yB = lerp(1010, 660, up); xB = lerp(800, 800, up)
    aTA = ease(prog(t, t_una - 0.25, t_una)) * (1 - ease(prog(t, t_9 - 0.3, t_9 + 0.1)))
    if aTA > 0.003: blit(img, ticket_sprite('1 libra'), 280, yA, aTA, 1.25 * max(0.01, pop(t, t_una - 0.25)))
    aTB = ease(prog(t, t_cien - 0.25, t_cien))
    mvB = ease(prog(t, t_9 - 0.3, t_9 + 0.3))
    if aTB > 0.003: blit(img, ticket_sprite('100 libras'), lerp(xB, 230, mvB), yB, aTB, lerp(1.25, 1.05, mvB) * max(0.01, pop(t, t_cien - 0.25)))
    # fase B · misma probabilidad
    aB = ease(prog(t, t_8 + 0.1, t_8 + 0.4)) * (1 - ease(prog(t, t_9 - 0.3, t_9 + 0.1)))
    if aB > 0.003:
        text(img, '=', 540, 660, 120, GOLDL, aB, 'play')
        write(img, t, 'misma probabilidad', 540, 950, 84, GOLDL, t_mis - 0.1, 18, aB, 'casi', glowk=0.25)
    # fase C · un billete grande = cien pequeños
    if t > t_gr - 0.3:
        aC = ease(prog(t, t_gr - 0.3, t_gr))
        text(img, '=', 448, 660, 110, GOLDL, aC, 'play')
        n = int(100 * prog(t, t_com - 0.1, t_peq + 0.25))
        for i in range(n):
            x, y = grid_pos(i, 538, 500, 50)
            blit(img, ticket_sprite('1', 46, 30, True), x, y, 1.0, 1.0)
        if n > 0:
            text(img, '%d' % n, 763, 905, 76, GOLDL, aC, 'play')
            text(img, 'billetes de 1 libra', 763, 970, 40, IVORY, aC, 'casi')
        write(img, t, '1 grande = 100 pequeños', 540, 1140, 80, GOLDL, t_c100 - 0.15, 18, 1.0, 'play', glowk=0.2)
    img = cam(img, lerp(1.0, 1.03, ease(prog(t, B[2] - 0.6, B[3] + 0.6))), 0, 0, 540, 700)
    header(img, t, 'LA REGLA', st0(5) - 0.05, B[3] - 0.2, 68)
    return img


# ===================================================== S3 · el premio, las cuentas y el fallo
COINS = [(np.random.RandomState(50 + j).rand(), j) for j in range(56)]
def coin_rain(img, t, t0, t1, a=1.0, x0=140, x1=940, ytop=300, ybot=1230):
    """monedas que caen y se amontonan en un montón centrado."""
    for (r, j) in COINS:
        ts = t0 + (t1 - t0) * (j / len(COINS)) ** 0.8
        if t < ts: continue
        k = min(1, (t - ts) / 0.55)
        tx = x0 + (x1 - x0) * (0.5 + (r - 0.5) * (0.35 + 0.5 * (1 - j / len(COINS))))
        ty = ybot - 40 - 34 * (j % 9) * (1 - abs(tx - 540) / 620)
        y = lerp(ytop - 120, ty, k ** 2)
        blit(img, coin_sprite(46, 0.6), tx, y, a)

def stack_tickets(img, x, y, n=6, a=1.0):
    for j in range(n): blit(img, ticket_sprite('', 170, 98, True), x - 22 + (j % 3) * 22, y - 34 - j * 13, a, 1.0, -8 + j * 5)

def coin_pile(img, x, y, n=12, a=1.0):
    for j in range(n): blit(img, coin_sprite(34, 0.7), x - 80 + (j % 5) * 40 + (j // 5) * 17, y - 28 - (j // 5) * 25, a)

def s3(t):
    t_ad = st0(10); t_cada = tw(10, 'cada'); t_500 = tw(10, '500.000'); t_11 = st0(11); t_ch = tw(11, 'charles'); t_cu = tw(11, 'cuentas')
    t_12 = st0(12); t_co = tw(12, 'costaban'); t_me = tw(12, 'menos'); t_13 = st0(13); t_gs = tw(13, 'ganabas')
    T1 = t_11 - 0.2; T2 = t_12 - 0.2
    img = math_bg(t)
    aP = 1 - ease(prog(t, T1 - 0.3, T1 + 0.2))
    if aP > 0.003:
        coin_rain(img, t, t_ad - 0.2, st1(10) + 0.3, aP)
        write(img, t, 'cada mes', 540, 460, 70, IVORY, t_cada - 0.1, 14, aP, 'casi')
        write(img, t, '+ 500.000 libras', 540, 620, 116, GOLDL, t_500 - 0.15, 14, aP, 'play', glowk=0.3, shadow=0.6)
    aL = win(t, T1 - 0.2, T2, 0.4, 0.4)
    if aL > 0.003:
        framed_photo(img, FOT + 'condamine.jpg', t, T1 - 0.3, T2 + 0.3, 1.04, 1.12, (0.5, 0.5), (0.48, 0.47), (70, 330, 520, 780), aL, True, 0.25)
        text(img, 'Charles-Marie', 295, 885, 52, GOLDL, aL, 'cas'); text(img, 'de La Condamine', 295, 950, 52, GOLDL, aL, 'cas')
        text(img, 'matemático', 295, 1025, 46, IVORY, aL, 'casi')
        m = mpoly([[(590, 350), (1030, 365), (1020, 1090), (600, 1075)]]); shadow_m(img, m, 0.5 * aL, (8, 12), 12); over(img, m, PARCH, aL)
        tip = scribbles(img, 630, 430, 350, 13, prog(t, t_ch - 0.2, st1(11) + 0.4), aL, lh=48)
        if tip and t < st1(11) + 0.4: quill(img, tip[0], tip[1], aL, t)
    aS = ease(prog(t, T2 - 0.2, T2 + 0.3))
    if aS > 0.003:
        tilt = 9 * ease(prog(t, t_me - 0.2, t_me + 0.5)) + 0.6 * math.sin(t * 2.0) * (1 - ease(prog(t, t_me, t_me + 1.0)))
        nT = 3 + int(5 * ease(prog(t, t_13, t_gs)))
        balance(img, 540, 430, 360, tilt, aS, lambda im, x, y: stack_tickets(im, x, y, nT, aS), lambda im, x, y: coin_pile(im, x, y, 13, aS),
                ('todos los billetes', 'premios'), ease(prog(t, T2 + 0.1, T2 + 0.5)))
        eq = 'billetes  <  premios'
        write(img, t, eq, 540, 1100, 92, GOLDL, t_co - 0.1, 18, aS, 'play', glowk=0.2)
        write(img, t, 'ganabas seguro', 540, 1225, 70, IVORY, t_gs - 0.1, 16, aS, 'casi')
        seal(img, t, st1(13) + 0.05, 905, 1215, 64, '', aS)
    img = cam(img, lerp(1.0, 1.035, ease(prog(t, B[3] - 0.6, B[4] + 0.6))), 0, 0, 540, 700)
    header(img, t, 'EL PREMIO', t_ad - 0.05, T1 - 0.3, 68)
    header(img, t, 'LAS CUENTAS', t_cu - 0.35, T2 - 0.3, 68)
    header(img, t, 'EL FALLO', t_12 - 0.05, B[4] - 0.2, 68)
    if aL > 0.01: text(img, 'RETRATO DE LA CONDAMINE · WIKIMEDIA COMMONS', 295, 1080, 18, IVORY, 0.7 * aL, 'casr', track=1)
    return img


# ===================================================== S4 · el sindicato
MONTHS = ['ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE']
def s4(t):
    t_vo = st0(14); t_15 = st0(15); t_so = tw(15, 'socios'); t_bo = tw(15, 'bonos'); t_ba = tw(15, 'baratos'); t_ca = tw(15, 'casi'); t_bi = tw(15, 'billetes'); t_mes = tw(15, 'mes')
    img = math_bg(t)
    aA = 1 - ease(prog(t, t_15 - 0.1, t_15 + 0.4))
    if aA > 0.003:
        framed_photo(img, FOT + 'voltaire.jpg', t, B[4] - 0.5, t_15 + 0.4, 1.05, 1.12, (0.5, 0.36), (0.5, 0.34), (50, 330, 520, 960), aA, True, 0.45)
        framed_photo(img, FOT + 'condamine.jpg', t, B[4] - 0.5, t_15 + 0.4, 1.04, 1.08, (0.5, 0.5), (0.5, 0.48), (590, 430, 1030, 870), aA, True, 0.25)
        text(img, '+', 555, 650, 130, GOLDL, aA * ease(prog(t, t_vo + 0.3, t_vo + 0.6)), 'play', glowk=0.3)
        text(img, 'Voltaire', 285, 1050, 62, GOLDL, aA * ease(prog(t, t_vo - 0.2, t_vo + 0.1)), 'cas')
        text(img, 'La Condamine', 810, 960, 56, GOLDL, aA * ease(prog(t, t_vo + 0.4, t_vo + 0.7)), 'cas')
    aB = ease(prog(t, t_15 - 0.1, t_15 + 0.4))
    if aB > 0.003:
        for i in range(6):
            ti = t_15 + 0.1 * i
            s = pop(t, ti, 0.3)
            if s > 0: blit(img, socio_sprite(i, 340), 115 + i * 170, 560 + 5 * math.sin(t * 2 + i), aB, s)
        for j in range(7):
            ts = t_bo - 0.2 + 0.13 * j; k = ease(prog(t, ts, ts + 0.6))
            if 0 < k < 1: blit(img, bond_sprite('1.000 libras'), lerp(1180, 150 + j * 130, k), lerp(330 + 40 * j, 640, k), 1.0, 0.42, lerp(20, -10, k))
        # barra: parte de los billetes del sorteo
        x0, x1, y0, y1 = 110, 970, 870, 950
        ab = ease(prog(t, t_ca - 0.6, t_ca - 0.3))
        if ab > 0.003:
            text(img, 'billetes del sorteo', 540, 825, 46, IVORY, ab, 'casi')
            m = mpoly([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]); over(img, m, NAVY * 0.7, ab); over(img, mline([[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]], 3), GOLD, ab)
            fl = 0.96 * ease(prog(t, t_ca - 0.3, t_bi + 0.2))
            nm = int(max(0, (t - t_mes + 0.25) / 0.2)) if t > t_mes - 0.25 else -1
            if nm >= 0: fl = 0.96 * ease(min(1, ((t - t_mes + 0.25) % 0.2) / 0.12)) if nm < len(MONTHS) - 1 else 0.96
            if fl > 0: over(img, mpoly([[(x0 + 6, y0 + 6), (x0 + 6 + (x1 - x0 - 12) * fl, y0 + 6), (x0 + 6 + (x1 - x0 - 12) * fl, y1 - 6), (x0 + 6, y1 - 6)]]), GOLD, ab)
            write(img, t, 'casi todos', 540, 1030, 80, GOLDL, t_ca - 0.1, 16, ab, 'play', glowk=0.2)
            if nm >= 0:
                mo = MONTHS[min(nm, len(MONTHS) - 1)]
                plate(img, 330, 1120, 750, 1235, ab, sh=0.4); text(img, mo, 540, 1178, 56, GOLDL, ab, 'cas', track=4)
    img = cam(img, lerp(1.0, 1.035, ease(prog(t, B[4] - 0.6, B[5] + 0.6))), 0, 0, 540, 700)
    header(img, t, 'LOS SOCIOS', t_so - 0.15, B[5] - 0.2, 68)
    return img


# ===================================================== S5 · el juicio
def s5(t):
    t_16 = st0(16); t_ju = tw(16, 'juicio'); t_ro = tw(17, 'roto'); t_re = tw(17, 'regla'); t_qu = tw(17, 'quedaron')
    img = math_bg(t)
    tilt = 13 * math.sin(2.6 * (t - t_16)) * (1 - ease(prog(t, t_ro - 0.3, t_re + 0.3))) * ease(prog(t, B[5] - 0.3, t_16 + 0.4))
    def doc(im, x, y):
        blit(im, ticket_sprite('', 180, 112, True), x, y - 44, 1.0, 1.0, 4)
    balance(img, 540, 400, 330, tilt, 1.0, lambda im, x, y: coin_pile(im, x, y, 11), doc, ('', ''), 0.0)
    write(img, t, 'no habían roto ninguna regla', 540, 1020, 66, IVORY, t_ro - 0.3, 20, 1.0, 'casi')
    write(img, t, 'se quedaron con el dinero', 540, 1120, 70, GOLDL, t_qu - 0.15, 18, 1.0, 'play', glowk=0.2)
    seal(img, t, st1(17) + 0.05, 540, 1235, 60, 'V')
    img = cam(img, lerp(1.0, 1.04, ease(prog(t, B[5] - 0.6, B[6] + 0.6))), 0, 0, 540, 700)
    header(img, t, 'A JUICIO', t_ju - 0.25, B[6] - 0.2, 68)
    return img


# ===================================================== S6 · la fortuna
def s6(t):
    t_18 = st0(18); t_me = tw(18, 'medio'); t_19 = st0(19)
    img = math_bg(t)
    ag = 0.32 * (1 - ease(prog(t, t_19 - 0.3, t_19 + 0.3)))
    if ag > 0.003:
        ph = photo_kb(FOT + 'voltaire.jpg', t, B[6] - 0.5, t_19 + 0.3, 1.0, 1.15, (0.5, 0.35), (0.5, 0.30), 0.85)
        img = img * (1 - ag) + ph * ag
    cols = 8
    for c in range(cols):
        x = 145 + c * 113; hmax = 4 + int(9 * (0.6 + 0.4 * math.sin(c * 1.7)))
        n = int(hmax * ease(prog(t, t_18 - 0.1 + 0.07 * c, t_me + 0.6 + 0.07 * c)))
        for j in range(n): blit(img, coin_sprite(46, 0.75), x + (j % 2) * 3, 1240 - j * 17)
    am = 1 - ease(prog(t, t_19 - 0.3, t_19 + 0.1))
    write(img, t, 'medio millón', 540, 560, 128, GOLDL, t_me - 0.1, 14, am, 'play', glowk=0.35, shadow=0.6)
    write(img, t, 'de libras', 540, 705, 84, IVORY, t_me + 0.55, 14, am, 'casi')
    aF = ease(prog(t, t_19 - 0.3, t_19 + 0.2))
    if aF > 0.003:
        framed_photo(img, FOT + 'voltaire_grabado.png', t, t_19 - 0.3, B[7] + 0.6, 1.0, 1.10, (0.55, 0.50), (0.58, 0.45), (210, 340, 870, 878), aF, False, 0.55)
        text(img, 'VOLTAIRE EN SU MESA DE TRABAJO (GRABADO)', 540, 950, 20, IVORY, 0.7 * aF, 'casr', track=1)
    img = cam(img, lerp(1.0, 1.04, ease(prog(t, B[6] - 0.6, B[7] + 0.6))), 0, 0, 540, 800)
    return img


# ===================================================== S7 · cierre
def s7(t):
    t_q = st0(20); t_fa = tw(20, 'fallo'); t_su = tw(21, 'suscribete'); t_de = tw(21, 'descubrir'); t_co = tw(21, 'como')
    img = math_bg(t)
    a0 = ease(prog(t, B[7] - 0.4, B[7] + 0.3))
    text(img, 'billete = bono ÷ 1.000', 540, 390, 80, IVORY, a0, 'play')
    eq = 'billetes  <  premios'
    text(img, eq, 540, 570, 98, GOLDL, a0, 'play', glowk=0.2)
    ink_circle(img, x_of(eq, '<', 98), 570, 66, 60, ease(prog(t, t_fa - 0.2, t_fa + 0.3)))
    seal(img, t, st1(20) + 0.05, 540, 1215, 62, 'V')
    aq = ease(prog(t, t_q - 0.25, t_q)) * (1 - ease(prog(t, t_su - 0.4, t_su - 0.1)))
    if aq > 0.003:
        plate(img, 40, 750, 1040, 910, aq)
        write(img, t, '¿Tú habrías visto el fallo?', 540, 830, 66, GOLDL, t_q - 0.05, 22, aq, 'play')
    if t > t_su - 0.15:
        a = ease((t - t_su + 0.15) / 0.3)
        plate(img, 60, 740, 1020, 880, a, VERM * 0.9, GOLDL)
        write(img, t, 'SUSCRÍBETE', 540, 810, 82, IVORY, t_su, 14, a, 'play')
        if t > t_de - 0.15:
            a2 = ease((t - t_de + 0.15) / 0.3)
            plate(img, 60, 900, 1020, 1100, a2)
            write(img, t, 'para descubrir más historias', 540, 965, 54, IVORY, t_de - 0.05, 20, a2, 'casi')
            write(img, t, 'como esta', 540, 1040, 60, GOLDL, t_co - 0.05, 14, a2, 'play')
    img = cam(img, lerp(1.0, 1.03, ease(prog(t, B[7] - 0.6, TEND))), 0, 0, 540, 700)
    return img

SC = [s0, s1, s2, s3, s4, s5, s6, s7]
