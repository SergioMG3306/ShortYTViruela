import os, sys
os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
sys.path.insert(0, '/home/claude/serie/balmis'); sys.path.insert(0, '/home/claude/serie/vascos'); sys.path.insert(0, '/home/claude/serie/cervantes')
from cv_lib import *
from cv_lib import _f, _d
import cv_lib as L
L.FOTOS = '/home/claude/serie/balmis/fotos/'
from cv_scenes import tn, fadeio, win, white_flash, header, recre, tag, shake
from cv_art import mk, paint, outline, x_mark, _R
from cv_artbase import _L, _P, _C, _E, _fm, WOOD, BONE, GOLD
from cv_geomap import pulse
from vs_art import gull
import bm_art as A
import bm_globe as G
import bm_map as M

BLUE_T = C3(0.13, 0.30, 0.62)
FOT = '/home/claude/serie/balmis/fotos/'
TINT_V = C3(0.96, 0.60, 0.40); TINT_ES = C3(0.97, 0.62, 0.48)

# ------------------------------------------------------------------ utilidades (de ll_scenes)
LN = []
def oline(x0, y0, x1, y1, col, a=1.0, th=4): LN.append((x0, y0, x1, y1, col, a, th))
def draw_lines(fr):
    for (x0, y0, x1, y1, col, a, th) in LN:
        if a <= 0.01: continue
        m = np.zeros(fr.shape[:2], F32)
        cv2.line(m, (int(x0 * 32), int(y0 * 32)), (int(x1 * 32), int(y1 * 32)), 1.0, int(th * 2), cv2.LINE_AA, shift=4)
        m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None] * a
        fr[:] = fr * (1 - m) + np.asarray(col, F32) * m
    LN.clear()

def lerpk(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1: return v0 + (v1 - v0) * ease((t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]

def linek(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1: return v0 + (v1 - v0) * ((t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]

def logk(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1: return math.exp(lerp(math.log(v0), math.log(v1), ease((t - t0) / max(1e-6, t1 - t0))))
    return keys[-1][1]

def flash(img, t, t0, dur=0.4, k=0.6):
    d = t - t0
    if 0 <= d < dur: white_flash(img, k * (1 - d / dur) ** 2)

_PC = {}
def _load(path):
    if path not in _PC: _PC[path] = cv2.imread(path)[:, :, ::-1].astype(F32) / 255
    return _PC[path]

def photo_kb(path, t, t0, t1, z0, z1, c0, c1, sat=0.88):
    src = _load(path); hh, ww = src.shape[:2]
    k = ease(prog(t, t0, t1)); z = lerp(z0, z1, k); cx = lerp(c0[0], c1[0], k) * ww; cy = lerp(c0[1], c1[1], k) * hh
    s = max(W / ww, H / hh) * z
    M_ = np.float32([[s, 0, 270 - s * cx], [0, s, 400 - s * cy]])
    img = cv2.warpAffine(src, M_, (W, H), flags=cv2.INTER_AREA if s < 0.5 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    g = img.mean(2, keepdims=True); img = g + (img - g) * sat
    img *= np.clip(1.12 - 0.5 * _d ** 1.8, 0.45, 1)[..., None]
    return img

def photo_fit(path, t, t0, t1, z0, z1, c0, c1, crop=(0.04, 0.05, 0.96, 0.95), sat=0.85):
    """imagen apaisada de poca resolución: fondo desenfocado a pantalla completa + imagen ajustada al ancho con Ken Burns."""
    src = _load(path); hh, ww = src.shape[:2]
    x0, y0, x1, y1 = int(crop[0] * ww), int(crop[1] * hh), int(crop[2] * ww), int(crop[3] * hh); src = src[y0:y1, x0:x1]; hh, ww = src.shape[:2]
    if ('bg', path) not in _PC:
        s = max(W / ww, H / hh) * 1.1; b = cv2.resize(src, (int(ww * s) + 2, int(hh * s) + 2), interpolation=cv2.INTER_AREA)
        b = b[(b.shape[0] - H) // 2:(b.shape[0] - H) // 2 + H, (b.shape[1] - W) // 2:(b.shape[1] - W) // 2 + W]
        b = cv2.GaussianBlur(b, (0, 0), 14) * 0.45 + PAPER * 0.2; _PC[('bg', path)] = b.astype(F32)
    img = _PC[('bg', path)].copy()
    k = ease(prog(t, t0, t1)); z = lerp(z0, z1, k); cx = lerp(c0[0], c1[0], k) * ww; cy = lerp(c0[1], c1[1], k) * hh
    s = (W - 24) / ww * z
    M_ = np.float32([[s, 0, 270 - s * cx], [0, s, 400 - s * cy]])
    fg = cv2.warpAffine(src, M_, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    box = cv2.warpAffine(np.ones((hh, ww), F32), M_, (W, H), flags=cv2.INTER_LINEAR)
    shadow(img, box, 0.5, (5, 8), 8.0)
    g = fg.mean(2, keepdims=True); fg = g + (fg - g) * sat
    img = img * (1 - box[..., None]) + fg * box[..., None]
    img *= np.clip(1.12 - 0.5 * _d ** 1.8, 0.45, 1)[..., None]
    return img

def credit(text, a):
    ov(text, 270, 150, 11, CREAM, 0.85 * a, 'c', sh=0.6)

def counter(x, y, w, big, small, a, col=RED, bsz=62, ssz=18):
    if a <= 0.003: return
    rect(x - w / 2, y - 52, x + w / 2, y + 52, None, 0.95 * a, 0.35); ov(big, x, y - 10, bsz, col, a, 'c'); ov(small, x, y + 34, ssz, INK, a, 'c')

def mix(a, b, k):
    if a is None or k >= 1: return b
    if k <= 0: return a
    return a * (1 - k) + b * k


# ===================================================== S0 · ¿sabías que...?
def s0(t):
    t_va, t_de, t_22 = tw(0, 'vacuna'), tw(0, 'dentro'), tw(0, '22')
    img = A.storm_sea(t, 0.55, 0.55)
    x = lerp(180, 300, prog(t, 0, B[1] + 0.7)); y = 500 + 5 * math.sin(t * 1.6)
    cut = ease(prog(t, t_de - 0.25, t_de + 0.3))
    lit = [ease(prog(t, t_22 + 0.05 * j, t_22 + 0.05 * j + 0.2)) for j in range(22)]
    A.corbeta(img, x, y, 300, t, 1.0, 0.045 * math.sin(t * 1.3), 1, 1.0, cut, lit)
    if t > t_va - 0.1:
        k = ease(prog(t, t_va - 0.1, t_va + 0.3)) * (1 - cut)
        A.spark(img, x + 6, y - 6, t, k, 1.1)
    A.front_wave(img, t, 545, 9, 1.0)
    z = lerp(1.0, 1.10, ease(prog(t, 0, B[1] + 0.7)))
    img = Cam(z, 0, 0, x, y - 60).apply(img)
    # cabecera grande desde el primer fotograma (sin tecleo)
    al = 1 - ease(prog(t, st1(0) + 0.1, st1(0) + 0.5))
    if al > 0.003:
        rect(16, 30, 524, 142, None, 0.95 * al, 0.4); ov('¿SABÍAS QUE...?', 270, 86, 50, RED, al, 'c')
    if t > t_22 - 0.1:
        counter(438, 212, 170, '22', 'NIÑOS', ease((t - t_22 + 0.1) / 0.25))
    recre(t, 0.8 * (1 - ease(prog(t, B[1] - 0.3, B[1] + 0.2))), CREAM)
    return img


# ===================================================== S1 · la viruela, Jenner y el viaje imposible
def figure(img, x, y, s, col, a=1.0):
    m = mk(); _C(m, x, y - 26 * s, 7 * s); _P(m, [(x - 10 * s, y - 16 * s), (x + 10 * s, y - 16 * s), (x + 8 * s, y + 8 * s), (x - 8 * s, y + 8 * s)])
    paint(img, m, col, a)

def s1(t):
    t_vi = st0(1); t_3 = tw(1, 'tres'); t_96 = st0(2); t_je = tw(2, 'jenner'); t_pe = st0(3); t_vj = tw(3, 'viaje'); t_lg = tw(3, 'largo')
    T_J = t_96 - 0.25; T_V = t_pe + 0.6
    out = None
    if t < T_J + 0.35:
        img = photo_fit(FOT + 'codice_hq.png', t, B[1] - 0.7, T_J + 0.4, 1.0, 1.30, (0.50, 0.50), (0.68, 0.40))
        out = img
        if t < T_J + 0.1:
            al = 1 - ease(prog(t, T_J - 0.3, T_J + 0.1))
            header(t, 'LA VIRUELA', t_vi - 0.05, T_J - 0.3, 18)
            credit('CÓDICE FLORENTINO, LIBRO XII (SIGLO XVI) · VERSIÓN COLOREADA · WIKIMEDIA COMMONS', al)
            if t > t_3 - 0.3:
                a = ease((t - t_3 + 0.3) / 0.3) * al
                m = mk(); _P(m, [(48, 470), (492, 470), (492, 625), (48, 625)]); shadow(img, _fm(m), 0.35 * a, (5, 7), 6.0); paint(img, m, CREAM, 0.95 * a)
                for j in range(10):
                    red = t > t_3 + 0.12 * (j + 1) and j < 3
                    figure(img, 90 + j * 40, 600, 0.95, RED if red else INK * 1.6, a)
                ov('3 DE CADA 10', 270, 505, 34, RED, a, 'c', n=tn('3 DE CADA 10', t, t_3, 18))
    if T_J - 0.35 < t < T_V + 0.35:
        img = photo_kb(FOT + 'jenner.jpg', t, T_J - 0.35, T_V + 0.4, 1.22, 1.0, (0.55, 0.50), (0.51, 0.45))
        a = ease(prog(t, T_J - 0.35, T_J + 0.35)); flash(img, t, T_J - 0.05, 0.3, 0.3)
        out = mix(out, img, a)
        if t > T_J - 0.2:
            al = ease(prog(t, T_J - 0.2, T_J + 0.2)) * (1 - ease(prog(t, T_V - 0.3, T_V + 0.1)))
            header(t, '1796', t_96 + 0.05, T_V - 0.35, 14)
            credit('ERNEST BOARD, «EL DR. JENNER EN SU PRIMERA VACUNACIÓN, 1796» · WELLCOME COLLECTION, CC BY 4.0', al)
            tag(270, 560, 'EDWARD JENNER', t, t_je - 0.1, ease((t - t_je + 0.3) / 0.3) * al, INK, 24)
            sp('LA VACUNA', 50, RED, -6, 300, 470, st1(2) + 0.05, 0.97 * (1 - ease(prog(t, T_V - 0.3, T_V + 0.1))))
    if t > T_V - 0.35:
        lo = lerpk(t, [(T_V - 0.35, -30.0), (B[2] + 0.7, -40.0)])
        g = G.Globe(lo, 30.0, logk(t, [(T_V - 0.35, 300.0), (B[2] + 0.7, 360.0)]), 270, 410)
        img = G.render(g, [('Spain', TINT_ES, 0.55)])
        kv = 0.80 * ease(prog(t, T_V - 0.1, t_lg + 0.15))
        G.draw_route(img, g, G.R_ATL, 0.0, kv, RED, 1.0, 3, (9, 7), t * 30)
        lon, lat = G.at(G.R_ATL, kv); x, y, z = g.p(lon, lat)
        fail = ease(prog(t, t_lg - 0.15, t_lg + 0.3))
        A.vial(img, x, y - 46, 1.0, 1.0, 1 - 0.85 * ease(prog(kv, 0.15, 0.70)), fail, 8 * math.sin(t * 2.4))
        if fail > 0: x_mark(img, x, y - 46, 46, RED, fail, 8)
        a = ease(prog(t, T_V - 0.35, T_V + 0.35))
        out = mix(out, img, a)
        if t > T_V:
            header(t, 'UN VIAJE TAN LARGO', t_vj - 0.1, B[2] - 0.4, 22)
            cx, cy, _ = g.p(*G.CORUNA); tag(cx + 40, cy - 40, 'ESPAÑA', t, T_V, ease(prog(t, T_V, T_V + 0.3)), RED, 18)
            px, py, _ = g.p(*G.SANJUAN); tag(px - 10, py + 52, 'AMÉRICA', t, T_V + 0.2, ease(prog(t, T_V + 0.2, T_V + 0.5)), BLUE_T, 18)
    return out


# ===================================================== S2 · llevarla viva: de brazo a brazo
ROWS = [(30 + i * 48, 630, 92) for i in range(11)] + [(40 + (10 - i) * 46, 520, 70) for i in range(11)]  # orden de la cadena (serpentina)

def hold_scene(t, cam, lit, grow, sparks=(), lantern=True, idle=0.0):
    """bodega con los 22 niños; cam=(z, wx, wy) → (wx,wy) en pantalla (270,430). lit[i]: brillo de la vacuna; grow[i]: granos."""
    z, wx, wy = cam
    img = A.hold_bg()
    if lantern: A.lantern(img, 270, 262, t)
    img = Cam(z, 270 - wx, 430 - wy, wx, wy).apply(img)
    S = lambda x, y: (270 + (x - wx) * z, 430 + (y - wy) * z)
    arms = [None] * 22
    order = sorted(range(22), key=lambda i: ROWS[i][1])
    for i in order:
        x, y, h = ROWS[i]; X, Y = S(x, y)
        if X < -80 or X > W + 80: arms[i] = ((X, Y - h * z * 0.6), (X, Y - h * z * 0.6)); continue
        r, l = A.kid(img, X, Y, h * z, i, 1.0, t)
        arms[i] = (r, l)
        if grow[i] > 0: A.pustule(img, r[0], r[1], grow[i] * z, 1.0)
        if lit[i] > 0:
            glow_roi(img, r[0], r[1], 26 * z, C3(1.0, 0.72, 0.30), 0.55 * lit[i], 1.8)
            glow_roi(img, r[0], r[1], 7 * z, C3(1.0, 0.95, 0.8), 0.7 * lit[i], 1.5)
    for (i, j, k, side) in sparks:
        A.spark_trail(img, arms[i][0], arms[j][0], k, t, 1.0, 50 * z)
    if idle > 0:
        for n in range(5):
            ph = (t * 0.55 + n * 0.37) % 1.0; i = (n * 5 + int(t * 0.55 + n * 0.37) * 3) % 21
            A.spark_trail(img, arms[i][0], arms[i + 1][0], ph, t, idle * math.sin(math.pi * ph), 40 * z)
    return img

def chain_state(t):
    t_dos = tw(5, 'dos'); t_dd = tw(6, 'despues'); t_li = tw(6, 'liquido'); t_ot = tw(6, 'otros'); t_br = st0(7); t_e = st1(7) + 0.1
    lit = [0.0] * 22; grow = [0.0] * 22; sparks = []
    for i in (0, 1): lit[i] = ease(prog(t, t_dos + 0.05 + 0.12 * i, t_dos + 0.3 + 0.12 * i)); grow[i] = ease(prog(t, t_dd - 0.2, t_li - 0.1))
    k = prog(t, t_li - 0.05, t_ot + 0.05)
    if 0 < k < 1: sparks += [(0, 2, k, 0), (1, 3, k, 0)]
    for i in (2, 3): lit[i] = ease(prog(t, t_ot + 0.05, t_ot + 0.35))
    per = (t_e - t_br) / 9.0
    for p in range(2, 11):
        t0 = t_br + (p - 2) * per; kk = prog(t, t0, t0 + per * 1.1)
        if 0 < kk < 1: sparks += [(2 * p - 2, 2 * p, kk, 0), (2 * p - 1, 2 * p + 1, kk, 0)]
        for i in (2 * p, 2 * p + 1): lit[i] = ease(prog(t, t0 + per, t0 + per + 0.2))
    return lit, grow, sparks

def s2(t):
    t_so = st0(4); t_va = st0(5); t_dos = tw(5, 'dos'); t_dd = tw(6, 'despues'); t_br = st0(7)
    T_K = t_va + 0.45
    out = None
    if t < T_K + 0.35:
        img = photo_kb(FOT + 'mano.jpg', t, B[2] - 0.7, T_K + 0.4, 1.10, 1.0, (0.38, 0.50), (0.47, 0.50), 0.95)
        flash(img, t, t_so - 0.05, 0.3, 0.25)
        out = img
        if t < T_K + 0.1:
            al = 1 - ease(prog(t, T_K - 0.3, T_K + 0.1))
            header(t, 'LA SOLUCIÓN', t_so - 0.05, T_K - 0.35, 18)
            credit('LÁMINA DEL LIBRO DE EDWARD JENNER (1798) · DOMINIO PÚBLICO', al)
            sp('¡VIVA!', 60, RED, -7, 270, 560, st1(4) + 0.05, 0.97 * al)
    if t > T_K - 0.35:
        z = lerpk(t, [(T_K - 0.35, 2.45), (t_br - 0.3, 2.15), (st1(7) + 0.3, 1.15), (B[3] + 0.7, 1.12)])
        wx = lerpk(t, [(T_K - 0.35, 58.0), (t_dd, 70.0), (tw(6, 'otros') - 0.3, 108.0), (t_br - 0.3, 110.0), (st1(7) + 0.3, 270.0)])
        wy = lerpk(t, [(T_K - 0.35, 588.0), (t_br - 0.3, 590.0), (st1(7) + 0.3, 545.0)])
        lit, grow, sparks = chain_state(t)
        img = hold_scene(t, (z, wx, wy), lit, grow, sparks)
        a = ease(prog(t, T_K - 0.35, T_K + 0.35))
        out = mix(out, img, a)
        if t > T_K:
            recre(t, 0.8 * ease(prog(t, T_K, T_K + 0.4)), CREAM)
            if t > t_dos:
                ad = ease(prog(t, t_dos, t_dos + 0.3)) * (1 - ease(prog(t, t_br - 0.45, t_br - 0.1)))
                dn = 1 + int(round(9 * ease(prog(t, t_dd - 0.35, t_dd + 0.35))))
                if ad > 0.003:
                    rect(180, 40, 360, 124, None, 0.93 * ad, 0.35); ov('DÍA %d' % dn, 270, 82, 36, RED, ad, 'c')
            if t > t_br - 0.1:
                header(t, 'DE BRAZO A BRAZO', t_br, B[3] - 0.5, 22)
    return out


# ===================================================== S3 · la salida
def depart_scene(t, t0):
    img = A.sea_img(380, 0.55).copy()
    A.sea_waves(img, t, 380, 0.8, 60, 3)
    A.headland(img); A.tower(img, 92, 345, 0.62, 1.0, t, 0.6)
    for j in range(3): gull(img, (120 + 140 * j + t * (18 + 4 * j)) % (W + 60) - 30, 210 + 30 * j + 6 * math.sin(t * 0.8 + j), 0.9 - 0.15 * j, t, 0.9, j)
    k = prog(t, t0 - 1.0, t0 + 6.0)
    x = lerp(150, 400, ease(k)); y = 430 + 3 * math.sin(t * 1.5)
    A.corbeta(img, x, y, 230, t, 1.0, 0.03 * math.sin(t * 1.3), 1, 1.0)
    A.front_wave(img, t, 470, 6, 0.85, C3(0.30, 0.44, 0.50))
    return Cam(lerp(1.0, 1.08, k), lerp(0, -40, ease(k)), 0, 270, 420).apply(img)

DECK_POS = [(40 + i * 46, 572, 80) for i in range(11)] + [(30 + i * 48, 640, 100) for i in range(11)]
def deck_kids(t, t_22):
    img = A.deck_bg(t); n = 0
    for j in range(22):
        tp = t_22 - 0.15 + 0.055 * j
        if t < tp: continue
        n += 1; d = t - tp; s = 1.0 + 0.25 * math.sin(math.pi * min(1, d / 0.18)) * (d < 0.18)
        x, y, h = DECK_POS[j]
        A.kid(img, x, y, h * s, j + 3, min(1, d / 0.08), t)
    img = Cam(lerp(1.0, 1.06, prog(t, t_22 - 1, t_22 + 3)), 0, 0, 270, 560).apply(img)
    return img, n

def s3(t):
    t_30 = st0(8); t_co = tw(8, 'corbeta'); t_cor = tw(8, 'coruna'); t_me = tw(9, 'medico'); t_fr = tw(9, 'francisco')
    t_22 = tw(10, '22'); t_tr = tw(10, 'tres'); t_ze = tw(11, 'isabel'); t_re = tw(11, 'rectora')
    T_BAL = st0(9) + 0.45; T_KID = st0(10) - 0.05; T_ZEN = st0(11) - 0.15
    out = None
    if t < T_BAL + 0.35:
        out = depart_scene(t, t_30)
        if t < T_BAL + 0.1:
            al = 1 - ease(prog(t, T_BAL - 0.3, T_BAL + 0.1))
            header(t, '30 DE NOVIEMBRE DE 1803', t_30 - 0.05, T_BAL - 0.35, 24)
            tag(330, 560, 'CORBETA MARÍA PITA', t, t_co - 0.05, ease((t - t_co + 0.25) / 0.3) * al, INK, 20)
            tag(110, 220, 'A CORUÑA', t, t_cor - 0.1, ease((t - t_cor + 0.25) / 0.3) * al, RED, 20)
            sp('1803', 64, RED, -6, 400, 300, st1(8) + 0.05, 0.97 * al)
            recre(t, 0.8 * al, CREAM)
    if T_BAL - 0.35 < t < T_KID + 0.35:
        img = photo_kb(FOT + 'balmis.jpg', t, T_BAL - 0.35, T_KID + 0.4, 1.0, 1.16, (0.50, 0.46), (0.48, 0.38), 0.9)
        img = img * C3(1.0, 0.96, 0.88)
        a = ease(prog(t, T_BAL - 0.35, T_BAL + 0.35)); flash(img, t, T_BAL - 0.05, 0.3, 0.3)
        out = mix(out, img, a)
        if T_BAL - 0.2 < t < T_KID + 0.1:
            al = ease(prog(t, T_BAL - 0.2, T_BAL + 0.2)) * (1 - ease(prog(t, T_KID - 0.3, T_KID + 0.1)))
            credit('RETRATO DE FRANCISCO JAVIER DE BALMIS · WIKIMEDIA COMMONS', al)
            tag(270, 520, 'EL MÉDICO', t, t_me - 0.1, ease((t - t_me + 0.3) / 0.3) * al, INK, 18)
            tag(270, 574, 'FRANCISCO JAVIER DE BALMIS', t, t_fr - 0.05, ease((t - t_fr + 0.3) / 0.3) * al, RED, 22, None, 22)
    if T_KID - 0.35 < t < T_ZEN + 0.35:
        img, n = deck_kids(t, t_22)
        a = ease(prog(t, T_KID - 0.35, T_KID + 0.35))
        out = mix(out, img, a)
        if T_KID - 0.2 < t < T_ZEN + 0.1:
            al = ease(prog(t, T_KID - 0.2, T_KID + 0.2)) * (1 - ease(prog(t, T_ZEN - 0.3, T_ZEN + 0.1)))
            header(t, 'A BORDO', T_KID, T_ZEN - 0.35, 16)
            if n > 0: counter(270, 250, 270, '%d' % n, 'HUÉRFANOS', al * ease(prog(t, t_22 - 0.2, t_22)))
            tag(270, 360, 'DE 3 A 9 AÑOS', t, t_tr - 0.05, ease((t - t_tr + 0.3) / 0.3) * al, INK, 24)
            recre(t, 0.8 * al, CREAM)
    if t > T_ZEN - 0.35:
        img = photo_kb(FOT + 'zendal.jpg', t, T_ZEN - 0.35, B[4] + 0.7, 1.05, 1.25, (0.52, 0.44), (0.53, 0.34), 0.8)
        a = ease(prog(t, T_ZEN - 0.35, T_ZEN + 0.35)); flash(img, t, T_ZEN - 0.05, 0.3, 0.3)
        out = mix(out, img, a)
        if t > T_ZEN - 0.2:
            al = ease(prog(t, T_ZEN - 0.2, T_ZEN + 0.2))
            credit('MONUMENTO A ISABEL ZENDAL (A CORUÑA) · WIKIMEDIA COMMONS', al)
            tag(270, 540, 'ISABEL ZENDAL', t, t_ze - 0.05, ease((t - t_ze + 0.3) / 0.3) * al, RED, 30, None, 16)
            tag(270, 600, 'RECTORA DEL ORFANATO CORUÑÉS', t, t_re - 0.05, ease((t - t_re + 0.3) / 0.3) * al, INK, 17, None, 22)
    return out


# ===================================================== S4 + S5 · la ruta en el globo (escena continua)
def _kat(route, place):
    a, c = route; d = (a[:, 0] - place[0]) ** 2 + (a[:, 1] - place[1]) ** 2; return float(c[int(np.argmin(d))])
K_TEN = _kat(G.R_ATL, G.TENERIFE); K_SJ = _kat(G.R_ATL, G.SANJUAN); K_HAB = _kat(G.R_BALM, G.HABANA); K_ACA = _kat(G.R_PAC, G.ACAPULCO)
K_STH = _kat(G.R_RET, G.W_(G.STHELENA))

def RT():
    """instantes clave de la ruta (se calculan una vez)."""
    if 'rt' in _PC: return _PC['rt']
    d = dict(can=tw(12, 'canarias'), pr=tw(12, 'puerto'), ve=tw(12, 'venezuela'), sal=tw(13, 'salvany'), sud=tw(13, 'sudamerica'), e13=st1(13), s14=st0(14), bal=tw(14, 'balmis'),
             cu=tw(14, 'cuba'), mx=tw(14, 'mexico'), e14=st1(14), s15=st0(15), pa=tw(15, 'pacifico'), n26=tw(15, '26'), fi=tw(15, 'filipinas'), e15=st1(15),
             s16=st0(16), ch=tw(16, 'china'), e16=st1(16), s17=st0(17), e17=st1(17))
    _PC['rt'] = d; return d

def globe_cam(t):
    r = RT()
    keys_lon = [(B[4] - 0.7, -22.0), (B[4] + 0.4, -24.0), (r['can'], -30.0), (r['pr'], -50.0), (r['ve'] + 0.3, -64.0), (st0(13) + 0.3, -67.0), (r['e13'] + 0.1, -71.0),
                (r['s14'] + 0.2, -74.0), (r['e14'] + 0.1, -86.0), (r['s15'] + 0.3, -96.0), (r['pa'] + 0.4, -140.0), (r['fi'] - 0.1, -226.0), (r['s16'], -236.0),
                (r['e16'] + 0.2, -243.0), (r['s17'] + 0.1, -244.0), (r['e17'] - 0.2, -352.0), (r['e17'] + 1.6, -372.0)]
    keys_lat = [(B[4] - 0.7, 34.0), (r['can'], 28.0), (r['pr'], 21.0), (r['ve'] + 0.3, 14.0), (st0(13) + 0.3, 10.0), (r['e13'] + 0.1, -1.0), (r['s14'] + 0.2, 6.0),
                (r['e14'] + 0.1, 17.0), (r['s15'] + 0.3, 17.0), (r['pa'] + 0.4, 15.0), (r['fi'] - 0.1, 15.0), (r['e16'] + 0.2, 19.0), (r['s17'] + 0.1, 15.0),
                (r['e17'] - 0.2, 8.0), (r['e17'] + 1.6, 14.0)]
    keys_R = [(B[4] - 0.7, 430.0), (r['can'], 440.0), (r['pr'], 520.0), (r['ve'] + 0.3, 760.0), (st0(13) + 0.3, 760.0), (r['e13'] + 0.1, 560.0), (r['s14'] + 0.2, 600.0),
              (r['e14'] + 0.1, 720.0), (r['s15'] + 0.3, 700.0), (r['pa'] + 0.4, 330.0), (r['fi'] - 0.1, 470.0), (r['s16'], 600.0), (r['e16'] + 0.2, 660.0),
              (r['s17'] + 0.1, 420.0), (r['e17'] - 0.2, 255.0), (r['e17'] + 1.6, 245.0)]
    return G.Globe(lerpk(t, keys_lon), lerpk(t, keys_lat), logk(t, keys_R), 270, 400)

def route_k(t):
    r = RT()
    kA = lerpk(t, [(B[4] + 0.15, 0.0), (r['can'], K_TEN), (r['pr'], K_SJ), (r['ve'] + 0.15, 1.0)])
    kS = ease(prog(t, r['sal'] - 0.35, r['e13'] + 0.5))
    kB = lerpk(t, [(r['bal'], 0.0), (r['cu'], K_HAB), (r['mx'] + 0.3, 1.0)])
    kP = linek(t, [(r['s15'] - 0.1, 0.0), (r['pa'], K_ACA + 0.04), (r['fi'] + 0.1, 1.0)])
    kC = ease(prog(t, r['s16'] - 0.1, r['ch'] + 0.25))
    kR = ease(prog(t, r['s17'] + 0.15, r['e17'] - 0.05))
    return kA, kS, kB, kP, kC, kR

def globe_route(t):
    r = RT(); g = globe_cam(t)
    kA, kS, kB, kP, kC, kR = route_k(t)
    tint = lambda t0: 0.5 * ease(prog(t, t0 - 0.1, t0 + 0.4))
    tints = [('Spain', TINT_ES, 0.55), ('Puerto Rico', TINT_V, tint(r['pr'])), ('Venezuela', TINT_V, tint(r['ve'])),
             ('Colombia', TINT_V, 0.5 * ease(prog(kS, 0.2, 0.4))), ('Ecuador', TINT_V, 0.5 * ease(prog(kS, 0.5, 0.65))), ('Peru', TINT_V, 0.5 * ease(prog(kS, 0.7, 0.85))),
             ('Bolivia', TINT_V, 0.5 * ease(prog(kS, 0.9, 1.0))), ('Cuba', TINT_V, tint(r['cu'])), ('Mexico', TINT_V, tint(r['mx'])),
             ('Philippines', TINT_V, tint(r['fi'])), ('China', TINT_V, tint(r['ch'])), ('Macao', TINT_V, tint(r['ch']))]
    img = G.render(g, tints)
    G.draw_route(img, g, G.R_SALV, 0.0, kS, BLUE_T, 1.0, 3, (9, 6), t * 20)
    for rt_, k_ in ((G.R_ATL, kA), (G.R_BALM, kB), (G.R_PAC, kP), (G.R_CHN, kC)):
        G.draw_route(img, g, rt_, 0.0, k_, RED, 1.0, 3)
    G.draw_route(img, g, G.R_RET, 0.0, kR, RED, 1.0, 3, (10, 6), t * 25)
    route_dots(t, g, img)
    # barco en cabeza de la ruta activa
    if t < r['bal']: leg, k = G.R_ATL, kA
    elif t < r['s15'] - 0.1: leg, k = G.R_BALM, kB
    elif t < r['s16'] - 0.1: leg, k = G.R_PAC, kP
    elif t < r['s17'] + 0.15: leg, k = G.R_CHN, kC
    else: leg, k = G.R_RET, kR
    lon, lat = G.at(leg, k); x, y, z = g.p(lon, lat)
    if z > 0.05:
        _, dx = G.heading(g, leg, k)
        A.corbeta(img, x, y - 4, 40, t, 1.0, 0.06 * math.sin(t * 2.2), 1 if dx >= 0 else -1, 1.0)
    if 0.02 < kS < 0.999:
        lo_, la_ = G.at(G.R_SALV, kS); sx, sy, sz = g.p(lo_, la_)
        if sz > 0: pulse(img, sx, sy, t, BLUE_T, 1.0, 4, 26, 0.8, 2, 2); over(img, mcirc([(sx, sy, 5)], 0.6), BLUE_T, 1.0)
    return img, g

def route_dots(t, g, img):
    r = RT()
    for (pl, t0) in ((G.TENERIFE, r['can']), (G.SANJUAN, r['pr']), (G.GUAIRA, r['ve']), (G.HABANA, r['cu']), (G.MEXICO, r['mx']), (G.MANILA, r['fi']), (G.CANTON, r['ch'])):
        x, y, z = g.p(*pl)
        if t > t0 - 0.2 and z > 0.05:
            a = ease(prog(t, t0 - 0.2, t0 + 0.1))
            over(img, mcirc([(x, y, 6)], 0.6), CREAM, a); over(img, mcirc([(x, y, 4)], 0.6), RED, a)
            if t < t0 + 1.2: pulse(img, x, y, t, RED, a * (1 - ease(prog(t, t0 + 0.6, t0 + 1.2))), 6, 40, 0.9, 2, 2)

def place_tag(g, place, text, t, t0, t1, col=INK, sz=18, dx=0, dy=-34):
    if t < t0 - 0.3 or t > t1 + 0.4: return
    x, y, z = g.p(*place)
    if z <= 0.05: return
    a = ease((t - t0 + 0.3) / 0.3) * (1 - ease((t - t1) / 0.4)) * min(1, z * 4)
    tag(min(W - 20 - len(text) * sz * 0.26, max(20 + len(text) * sz * 0.26, x + dx)), y + dy, text, t, t0, a, col, sz)

def route_overlays(t, g):
    r = RT()
    place_tag(g, G.TENERIFE, 'CANARIAS', t, r['can'] - 0.05, r['ve'] + 0.3, INK, 18, -20, 34)
    place_tag(g, G.SANJUAN, 'PUERTO RICO', t, r['pr'] - 0.05, st0(13) + 0.6, INK, 18, 40, -34)
    place_tag(g, G.GUAIRA, 'VENEZUELA', t, r['ve'] - 0.05, r['e13'] - 0.3, INK, 18, 50, 36)
    place_tag(g, G.QUITO, 'SALVANY', t, r['sal'] - 0.05, r['s14'] + 0.6, BLUE_T, 20, 80, 10)
    place_tag(g, G.LIMA, 'SUDAMÉRICA', t, r['sud'] - 0.05, r['s14'] + 0.6, BLUE_T, 16, 70, 40)
    place_tag(g, G.GUAIRA, 'BALMIS', t, r['bal'] - 0.05, r['e14'] + 0.2, RED, 20, 60, -40)
    place_tag(g, G.HABANA, 'CUBA', t, r['cu'] - 0.05, r['pa'], INK, 18, 30, -36)
    place_tag(g, G.MEXICO, 'MÉXICO', t, r['mx'] - 0.05, r['pa'], INK, 18, -10, 40)
    place_tag(g, G.MANILA, 'FILIPINAS', t, r['fi'] - 0.05, r['s17'] + 0.4, INK, 18, 60, 30)
    place_tag(g, G.CANTON, 'CHINA', t, r['ch'] - 0.05, r['s17'] + 0.4, INK, 20, -10, -40)
    if t > r['n26'] - 0.1:
        a = ease((t - r['n26'] + 0.1) / 0.25) * (1 - ease(prog(t, r['e15'] - 0.1, r['e15'] + 0.3)))
        counter(270, 560, 330, '26', 'NIÑOS MEXICANOS', a)

def s4(t):
    img, g = globe_route(t)
    route_overlays(t, g)
    header(t, 'LA RUTA DE LA VACUNA', B[4] + 0.1, RT()['e16'] + 0.3, 22)
    return img

def s5(t):
    r = RT(); T_J = r['e17'] + 0.75
    out = None
    if t < T_J + 0.35:
        img, g = globe_route(t)
        route_overlays(t, g)
        header(t, 'LA RUTA DE LA VACUNA', B[4] + 0.1, r['e16'] + 0.3, 22)
        out = img
        if t < T_J + 0.1:
            al = 1 - ease(prog(t, T_J - 0.3, T_J + 0.1))
            header(t, '1806', r['s17'] + 0.05, T_J - 0.35, 14)
            place_tag(g, G.STHELENA, 'SANTA ELENA', t, linek(K_STH, [(0, r['s17']), (1, r['e17'])]) + 0.2, T_J - 0.3, INK, 15, -20, 30)
            sp('LA VUELTA AL MUNDO', 46, RED, -6, 270, 590, st1(17) + 0.05, 0.97 * al)
    if t > T_J - 0.35:
        img = photo_kb(FOT + 'jenner.jpg', t, T_J - 0.35, B[6] + 0.7, 1.95, 1.70, (0.60, 0.36), (0.60, 0.33))
        a = ease(prog(t, T_J - 0.35, T_J + 0.35)); flash(img, t, T_J - 0.05, 0.3, 0.3)
        out = mix(out, img, a)
        if t > T_J - 0.2:
            al = ease(prog(t, T_J - 0.2, T_J + 0.2))
            credit('ERNEST BOARD · WELLCOME COLLECTION, CC BY 4.0', al)
            header(t, 'EDWARD JENNER', st0(18), B[6] - 0.4, 22)
            t_ej = tw(18, 'ejemplo'); t_fi = tw(18, 'filantropia')
            if t > t_ej - 0.3:
                aq = ease((t - t_ej + 0.3) / 0.3)
                rect(30, 470, 510, 612, None, 0.95 * aq, 0.35)
                ov('«UN EJEMPLO DE', 270, 512, 30, INK, aq, 'c', n=tn('«UN EJEMPLO DE', t, t_ej - 0.1, 16))
                ov('FILANTROPÍA TAN NOBLE»', 270, 566, 30, RED, aq, 'c', n=tn('FILANTROPÍA TAN NOBLE»', t, t_fi - 0.05, 16))
    return out


# ===================================================== S6 · 2020
CITIES = [(-3.70, 40.42), (2.17, 41.39), (-0.38, 39.47), (-5.98, 37.39), (-0.88, 41.65), (-2.93, 43.26), (-8.41, 43.36), (-4.42, 36.72), (-4.72, 41.65),
          (-1.13, 37.99), (2.65, 39.57), (-5.85, 43.36), (-3.60, 37.18), (-6.97, 38.88), (-1.64, 42.81), (-3.80, 43.46), (-8.72, 42.24), (-2.46, 36.84)]
OLIVE = C3(0.30, 0.38, 0.22)
def s6(t):
    t_20 = st0(19); t_ej = tw(19, 'ejercito'); t_co = tw(19, 'covid'); t_op = tw(19, 'operacion'); t_ma = tw(20, 'madrid'); t_is = tw(20, 'isabel')
    T_H = tw(20, 'nombre') - 0.2
    out = None
    if t < T_H + 0.35:
        s = logk(t, [(B[6] - 0.7, 0.40), (st1(19), 0.46), (t_ma + 0.2, 0.85), (T_H + 0.4, 1.05)])
        c = (lerpk(t, [(st1(19), -3.4), (t_ma + 0.2, -3.70)]), lerpk(t, [(B[6] - 0.7, 40.2), (st1(19), 40.1), (t_ma + 0.2, 40.42)]))
        g = M.Geo(c[0], c[1], s)
        img = M.geomap(g, spain=0.55, france=0.25, llv=0.0, relief=1.0)
        for j, (lo, la) in enumerate(CITIES):
            tj = t_ej + j * (t_op - t_ej) / len(CITIES)
            if t > tj - 0.1:
                x, y = g.p(lo, la); a = ease(prog(t, tj - 0.1, tj + 0.15))
                over(img, mcirc([(x, y, 6)], 0.6), CREAM, a); over(img, mcirc([(x, y, 4)], 0.6), OLIVE, a)
                pulse(img, x, y, t, OLIVE, a * 0.8, 5, 28, 1.1, 2, 1)
        vir = 1 - ease(prog(t, st1(19) + 0.05, st1(19) + 0.45))
        if vir > 0.01:
            rs = np.random.RandomState(7)
            for j in range(7):
                vx = (rs.rand() * W + t * (8 + 6 * rs.rand()) * (1 if j % 2 else -1)) % (W + 80) - 40; vy = 200 + rs.rand() * 400 + 8 * math.sin(t + j)
                A.virus(img, vx, vy, 12 + 8 * rs.rand(), t + j, vir * 0.85 * ease(prog(t, B[6] - 0.5 + 0.1 * j, B[6] + 0.3 + 0.1 * j)), None, j)
        if t > t_ma - 0.3:
            x, y = g.p(-3.70, 40.42); a = ease(prog(t, t_ma - 0.3, t_ma))
            over(img, mcirc([(x, y, 9)], 0.6), CREAM, a); over(img, mcirc([(x, y, 6.5)], 0.6), RED, a); pulse(img, x, y, t, RED, a, 8, 60, 1.0, 3, 2)
        out = img
        if t < T_H + 0.1:
            al = 1 - ease(prog(t, T_H - 0.3, T_H + 0.1))
            header(t, '2020', t_20 + 0.05, T_H - 0.35, 14)
            tag(150, 250, 'COVID', t, t_co - 0.05, ease((t - t_co + 0.3) / 0.3) * (1 - ease(prog(t, st1(19), st1(19) + 0.3))), RED, 22)
            sp('OPERACIÓN BALMIS', 46, RED, -6, 270, 330, st1(19) + 0.05, 0.97 * (1 - ease(prog(t, t_ma - 0.4, t_ma))))
            if t > t_ma - 0.3:
                x, y = g.p(-3.70, 40.42); tag(x, y - 46, 'MADRID', t, t_ma - 0.1, ease((t - t_ma + 0.3) / 0.3) * al, RED, 22)
    if t > T_H - 0.35:
        img = A.night_city_bg(); A.hospital(img, 1.0, t, 0.6 + 0.4 * ease(prog(t, T_H, T_H + 0.6)))
        img = Cam(lerp(1.0, 1.10, ease(prog(t, T_H - 0.35, B[7] + 0.7))), 0, 0, 270, 520).apply(img)
        a = ease(prog(t, T_H - 0.35, T_H + 0.35))
        out = mix(out, img, a)
        if t > T_H:
            recre(t, 0.8 * ease(prog(t, T_H, T_H + 0.4)), CREAM)
            ah = ease(prog(t, T_H, T_H + 0.3))
            rect(40, 196, 500, 300, None, 0.95 * ah, 0.35)
            ov('HOSPITAL', 270, 226, 22, INK, ah, 'c', n=tn('HOSPITAL', t, T_H + 0.05, 16))
            ov('ISABEL ZENDAL', 270, 270, 36, RED, ah, 'c', n=tn('ISABEL ZENDAL', t, t_is - 0.1, 16))
            tag(270, 340, 'MADRID', t, T_H + 0.2, ah, INK, 16)
    return out


# ===================================================== S7 · cierre
def s7(t):
    t_q = st0(21); t_su = tw(22, 'suscribete'); t_de = tw(22, 'descubrir')
    lit = [1.0] * 22; grow = [0.0] * 22
    z = lerpk(t, [(B[7] - 0.7, 1.35), (TEND, 1.12)]); wx = lerpk(t, [(B[7] - 0.7, 230.0), (TEND, 270.0)]); wy = 550.0
    img = hold_scene(t, (z, wx, wy), lit, grow, (), True, 1.0)
    aq = ease((t - t_q + 0.2) / 0.3) * (1 - ease((t - t_su + 0.4) / 0.4))
    if aq > 0.003:
        rect(30, 160, 510, 290, None, 0.95 * aq, 0.3)
        ov('¿CONOCÍAS A LOS NIÑOS', 270, 202, 32, RED, aq, 'c', n=tn('¿CONOCÍAS A LOS NIÑOS', t, t_q, 18))
        ov('DE LA VACUNA?', 270, 252, 32, RED, aq, 'c', n=tn('DE LA VACUNA?', t, tw(21, 'vacuna') - 0.3, 18))
    sp('DE BRAZO A BRAZO', 44, RED, -6, 270, 590, st1(21) + 0.05, 0.97)
    if t > t_su - 0.1:
        a = ease((t - t_su + 0.1) / 0.4)
        rect(26, 150, 514, 226, RED, 0.96 * a, 0.35); ov('SUSCRÍBETE', 270, 188, 44, CREAM, a, 'c', n=tn('SUSCRÍBETE', t, t_su, 12))
        if t > t_de - 0.1:
            a2 = ease((t - t_de + 0.1) / 0.4); rect(26, 240, 514, 322, None, 0.95 * a2, 0.3)
            ov('PARA DESCUBRIR MÁS HISTORIAS', 270, 268, 20, INK, a2, 'c', n=tn('PARA DESCUBRIR MÁS HISTORIAS', t, t_de, 18)); ov('COMO ESTA', 270, 302, 28, RED, a2, 'c', n=tn('COMO ESTA', t, tw(22, 'como'), 12))
    recre(t, 0.8 * (1 - ease(prog(t, t_su - 0.3, t_su))), CREAM)
    return img

SC = [s0, s1, s2, s3, s4, s5, s6, s7]
