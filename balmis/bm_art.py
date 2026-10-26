"""Ilustraciones propias del Short de la Expedición Balmis: niños, bodega del barco, farol, frasco de linfa,
cubierta, faro, hospital y partículas de virus."""
import math
import numpy as np, cv2
from cv_lib import W, H, F32, C3, INK, RED, CREAM, PAPER, XX, YY, over, mcirc, glow_roi, shadow, lerp, ease, prog, fractal, splat, rot
from cv_lib import _f, _d
from cv_art import mk, paint, outline, sea_img, waves as sea_waves
from cv_artbase import _L, _P, _C, _E, _fm, WOOD, OCHRE, BONE, SKIN, STONE, GOLD

HAIRS = [C3(0.30, 0.20, 0.13), C3(0.16, 0.12, 0.09), C3(0.55, 0.36, 0.18), C3(0.24, 0.17, 0.12), C3(0.62, 0.48, 0.28)]
SHIRTS = [C3(0.93, 0.90, 0.80), C3(0.80, 0.74, 0.60), C3(0.62, 0.68, 0.74), C3(0.86, 0.82, 0.70), C3(0.70, 0.60, 0.48), C3(0.90, 0.86, 0.76)]
PANTS = [C3(0.36, 0.30, 0.24), C3(0.28, 0.30, 0.36), C3(0.46, 0.38, 0.28), C3(0.30, 0.26, 0.22)]

# ------------------------------------------------------------------ niños (sprites cacheados)
def _child_draw(img, x, y, h, v):
    """niño de frente, pies en (x,y); devuelve el punto del brazo (vacuna) relativo a (x,y)."""
    u = h / 10.0; rs = np.random.RandomState(v)
    hair, shirt, pant = HAIRS[v % len(HAIRS)], SHIRTS[(v * 7) % len(SHIRTS)], PANTS[(v * 3) % len(PANTS)]
    hx, hy = x, y - 8.55 * u; shy = y - 7.25 * u; wy = y - 4.4 * u
    ink, leg, shoe, sh_, pa, arm, skin, hr = mk(), mk(), mk(), mk(), mk(), mk(), mk(), mk()
    for sg in (-1, 1):
        hip = (x + 0.5 * u * sg, wy + 0.6 * u); ft = (x + 0.62 * u * sg, y)
        _L(ink, [hip, ft], 1.05 * u + 2); _L(leg, [hip, ft], 1.05 * u)
        _E(ink, ft[0] + 0.2 * u * sg, ft[1], 0.75 * u + 1, 0.36 * u + 1); _E(shoe, ft[0] + 0.2 * u * sg, ft[1], 0.75 * u, 0.36 * u)
    tor = [(x - 1.25 * u, shy), (x + 1.25 * u, shy), (x + 1.05 * u, wy), (x - 1.05 * u, wy)]
    _P(ink, [(px + (1 if px > x else -1), py + (1 if py > shy else -1)) for px, py in tor]); _P(sh_, tor)
    br = [(x - 1.08 * u, wy - 0.3 * u), (x + 1.08 * u, wy - 0.3 * u), (x + 1.25 * u, wy + 1.9 * u), (x - 1.25 * u, wy + 1.9 * u)]
    _P(ink, [(px, py + 1) for px, py in br]); _P(pa, br)
    sl = mk()
    for sg in (-1, 1):
        s0 = (x + 1.1 * u * sg, shy + 0.35 * u); el = (x + 1.45 * u * sg, shy + 1.85 * u); hd = (x + 1.5 * u * sg, wy + 0.35 * u)
        _L(ink, [s0, el, hd], 0.8 * u + 2); _L(arm, [s0, el, hd], 0.8 * u); _C(skin, hd[0], hd[1], 0.4 * u)
        _L(sl, [s0, (x + 1.25 * u * sg, shy + 0.9 * u)], 0.95 * u)          # manga corta
    _C(ink, hx, hy, 1.05 * u + 1.2); _C(skin, hx, hy, 1.05 * u)
    _E(hr, hx, hy - 0.25 * u, 1.12 * u, 0.95 * u, 0, 180, 360)
    if v % 3 == 0: _E(hr, hx - 0.6 * u, hy - 0.4 * u, 0.55 * u, 0.7 * u)
    sh = cv2.GaussianBlur(_fm(ink, 0.0), (0, 0), 2.5); img *= (1 - 0.20 * np.roll(np.roll(sh, 3, 0), 3, 1))[..., None]
    over(img, _fm(ink, 0.45), INK, 0.92)
    paint(img, leg, SKIN * 0.92, 1.0, 0.45); paint(img, shoe, C3(0.20, 0.15, 0.11), 1.0, 0.45); paint(img, pa, pant, 1.0, 0.45)
    paint(img, arm, SKIN, 1.0, 0.45); paint(img, sh_, shirt, 1.0, 0.45); paint(img, sl, shirt * 0.97, 1.0, 0.45); paint(img, skin, SKIN, 1.0, 0.45)
    paint(img, hr, hair, 1.0, 0.45)
    ey = mk(); _C(ey, hx - 0.38 * u, hy + 0.05 * u, 0.12 * u + 0.3); _C(ey, hx + 0.38 * u, hy + 0.05 * u, 0.12 * u + 0.3); paint(img, ey, INK, 0.85, 0.3)
    mo = mk(); _E(mo, hx, hy + 0.5 * u, 0.28 * u, 0.12 * u, 0, 0, 180); paint(img, mo, C3(0.55, 0.25, 0.20), 0.6, 0.3)
    return (1.42 * u, -(y - (shy + 1.0 * u))), (-1.42 * u, -(y - (shy + 1.0 * u)))

_SPR = {}
def child_sprite(h, v):
    k = (int(h), v % 30)
    if k in _SPR: return _SPR[k]
    x0, y0 = 270, 480 + int(h * 0.45)
    blk = np.zeros((H, W, 3), F32); wht = np.ones((H, W, 3), F32)
    armR, armL = _child_draw(blk, x0, y0, h, v); _child_draw(wht, x0, y0, h, v)
    al = np.clip(1 - (wht - blk).mean(2), 0, 1)
    col = np.where(al[..., None] > 1e-3, blk / np.maximum(al[..., None], 1e-3), 0)
    ys, xs = np.where(al > 0.01); ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    spr = (col[ya:yb, xa:xb].astype(F32), al[ya:yb, xa:xb].astype(F32), x0 - xa, y0 - ya, armR, armL)
    _SPR[k] = spr; return spr

def blit(img, spr, x, y, a=1.0):
    col, al, ox, oy = spr[:4]; h, w = al.shape
    X0 = int(round(x - ox)); Y0 = int(round(y - oy))
    xa, ya, xb, yb = max(0, X0), max(0, Y0), min(W, X0 + w), min(H, Y0 + h)
    if xa >= xb or ya >= yb: return
    m = (al[ya - Y0:yb - Y0, xa - X0:xb - X0] * a)[..., None]
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - m) + col[ya - Y0:yb - Y0, xa - X0:xb - X0] * m

def child(img, x, y, h, v, a=1.0, t=0.0, bob=1.0):
    spr = child_sprite(h, v); dy = bob * 1.2 * math.sin(t * 2.1 + v * 1.7)
    blit(img, spr, x, y + dy, a)
    (rx, ry), (lx, ly) = spr[4], spr[5]
    return (x + rx, y + dy + ry), (x + lx, y + dy + ly)

def pustule(img, x, y, k, a=1.0):
    """granos de la vacuna en el brazo (k: 0..1 crecimiento)."""
    if k <= 0: return
    over(img, mcirc([(x, y, 2.6 * k + 0.6), (x + 2.2, y + 2.5, 1.9 * k + 0.4)], 0.5), C3(0.78, 0.25, 0.18), a)
    over(img, mcirc([(x - 0.5, y - 0.5, 1.0 * k)], 0.4), C3(1.0, 0.85, 0.70), a * 0.8)

def spark(img, x, y, t, a=1.0, r=1.0):
    glow_roi(img, x, y, 34 * r, C3(1.0, 0.72, 0.30), 0.55 * a, 2.0)
    glow_roi(img, x, y, 10 * r, C3(1.0, 0.95, 0.80), 0.9 * a, 1.6)
    for j in range(4):
        an = t * 7 + j * 1.57; L_ = (7 + 3 * math.sin(t * 13 + j)) * r
        m = mk(); _L(m, [(x - L_ * math.cos(an), y - L_ * math.sin(an)), (x + L_ * math.cos(an), y + L_ * math.sin(an))], 1); paint(img, m, C3(1.0, 0.92, 0.7), 0.7 * a, 0.6)

def arc_pt(p0, p1, k, lift=60):
    x = lerp(p0[0], p1[0], k); y = lerp(p0[1], p1[1], k) - lift * 4 * k * (1 - k)
    return x, y

def spark_trail(img, p0, p1, k, t, a=1.0, lift=60):
    if a <= 0.01: return
    xs, ys = [], []
    for j in range(14):
        kk = k - j * 0.025
        if kk < 0: break
        x, y = arc_pt(p0, p1, kk, lift); xs.append(x); ys.append(y)
    if xs:
        cols = np.tile(C3(1.0, 0.75, 0.35), (len(xs), 1)) * np.linspace(1, 0.15, len(xs))[:, None]
        splat(img, np.array(xs), np.array(ys), cols * a, 2.2, 0.9)
    x, y = arc_pt(p0, p1, k, lift); spark(img, x, y, t, a, 0.8)

# ------------------------------------------------------------------ bodega del barco
_BG = {}
def hold_bg():
    if 'hold' in _BG: return _BG['hold'].copy()
    g = np.clip(YY / H, 0, 1)[..., None]
    img = (C3(0.24, 0.16, 0.10) * (1 - g) + C3(0.14, 0.09, 0.06) * g).astype(F32)
    pl = ((YY % 26) < 1.6).astype(F32); over(img, pl, C3(0.08, 0.05, 0.03), 0.7)
    grain = fractal(61, (3, 8, 30)); img *= (0.85 + 0.25 * grain[..., None])
    rs = np.random.RandomState(5)
    for k in range(40):
        y0 = int(rs.rand() * H // 26) * 26; x0 = rs.rand() * W
        m = mk(); _L(m, [(x0, y0 + 1), (x0, y0 + 25)], 1); paint(img, m, C3(0.08, 0.05, 0.03), 0.5)
    # cuadernas (costillas del casco)
    for x0 in (40, 270, 500):
        m = mk(); _P(m, [(x0 - 14, 0), (x0 + 14, 0), (x0 + 18, H), (x0 - 18, H)]); paint(img, m, C3(0.30, 0.20, 0.12), 1.0); outline(img, m, 0.6, 0.6, 1.0)
        over(img, _fm(m) * (fractal(62, (4, 12)) > 0.6), C3(0.20, 0.13, 0.08), 0.4)
    bm_ = mk(); _P(bm_, [(0, 150), (W, 150), (W, 176), (0, 176)]); paint(img, bm_, C3(0.32, 0.22, 0.13), 1.0); outline(img, bm_, 0.6, 0.6, 1.0)
    fl = mk(); _P(fl, [(0, 640), (W, 640), (W, H), (0, H)]); paint(img, fl, C3(0.26, 0.17, 0.10), 1.0)
    over(img, ((YY > 640) & (((XX + (YY - 640) * 0.35) % 60) < 1.5)).astype(F32), C3(0.10, 0.06, 0.04), 0.6)
    _BG['hold'] = np.clip(img, 0, 1).astype(F32); return _BG['hold'].copy()

def lantern(img, x, y, t, a=1.0, swing=1.0):
    ang = 9 * swing * math.sin(t * 1.3)
    top = (x, 176); bx, by = rot([(x, y)], ang, top)[0]
    m = mk(); _L(m, [top, (bx, by - 22)], 2); paint(img, m, INK, a)
    glow_roi(img, bx, by, 260, C3(1.0, 0.70, 0.32), 0.38 * a * (1 + 0.05 * math.sin(t * 11)), 1.6)
    b = mk(); _P(b, rot([(x - 12, y - 18), (x + 12, y - 18), (x + 9, y + 16), (x - 9, y + 16)], ang, top)); paint(img, b, C3(1.0, 0.86, 0.50), a); outline(img, b, a, 0.8, 1.0)
    c = mk(); _P(c, rot([(x - 15, y - 26), (x + 15, y - 26), (x + 12, y - 18), (x - 12, y - 18)], ang, top)); _P(c, rot([(x - 12, y + 16), (x + 12, y + 16), (x + 10, y + 22), (x - 10, y + 22)], ang, top))
    paint(img, c, C3(0.18, 0.15, 0.12), a)
    glow_roi(img, bx, by, 26, C3(1.0, 0.95, 0.75), 0.8 * a, 1.5)
    return bx, by

# ------------------------------------------------------------------ frasco de linfa entre cristales
def vial(img, x, y, s, a=1.0, fill=1.0, crack=0.0, ang=0.0):
    pts = lambda P_: rot([(x + px * s, y + py * s) for px, py in P_], ang, (x, y))
    g = mk(); _P(g, pts([(-9, -30), (9, -30), (9, 26), (6, 32), (-6, 32), (-9, 26)]))
    shadow(img, _fm(g), 0.3 * a, (3, 4), 3.0); paint(img, g, C3(0.86, 0.92, 0.94), 0.55 * a)
    if fill > 0.01:
        lv = lerp(28, -18, fill); l = mk(); _P(l, pts([(-7, lv), (7, lv), (7, 25), (5, 30), (-5, 30), (-7, 25)]))
        paint(img, l, lerp(C3(0.70, 0.62, 0.50), C3(0.96, 0.78, 0.36), fill), a)
    k = mk(); _P(k, pts([(-11, -38), (11, -38), (11, -30), (-11, -30)])); paint(img, k, C3(0.50, 0.34, 0.20), a)
    outline(img, g, a, 0.8, 1.0)
    hl = mk(); _L(hl, pts([(-5, -24), (-5, 20)]), max(1, 1.6 * s)); paint(img, hl, C3(1, 1, 1), 0.5 * a, 0.8)
    if crack > 0:
        c = mk(); _L(c, pts([(-9, -8), (-2, -2), (-5, 6), (4, 12), (9, 20)][:2 + int(3 * min(1, crack))]), 1); paint(img, c, INK, a * min(1, crack * 2))

# ------------------------------------------------------------------ faro (Torre de Hércules, silueta)
def tower(img, x, y, s, a=1.0, t=0.0, beam=0.0):
    m = mk(); _P(m, [(x - 22 * s, y), (x + 22 * s, y), (x + 17 * s, y - 120 * s), (x - 17 * s, y - 120 * s)])
    _P(m, [(x - 13 * s, y - 120 * s), (x + 13 * s, y - 120 * s), (x + 11 * s, y - 150 * s), (x - 11 * s, y - 150 * s)])
    _P(m, [(x - 8 * s, y - 150 * s), (x + 8 * s, y - 150 * s), (x + 6 * s, y - 166 * s), (x - 6 * s, y - 166 * s)])
    paint(img, m, C3(0.16, 0.16, 0.19), a)
    if beam > 0:
        an = t * 1.4; L_ = 300
        for sg in (-1, 1):
            b = mk(); _P(b, [(x, y - 158 * s), (x + sg * L_ * abs(math.cos(an)), y - 158 * s - 30), (x + sg * L_ * abs(math.cos(an)), y - 158 * s + 30)]); paint(img, b, C3(1.0, 0.93, 0.7), 0.16 * beam * a, 4.0)
        glow_roi(img, x, y - 158 * s, 40 * s, C3(1.0, 0.92, 0.65), 0.9 * beam * a, 1.6)

def headland(img, a=1.0):
    m = mk(); _P(m, [(-10, 360), (40, 338), (90, 330), (140, 344), (180, 362), (190, 380), (-10, 380)]); paint(img, m, C3(0.12, 0.12, 0.14), a)

# ------------------------------------------------------------------ cubierta (amanecer) para «a bordo»
def deck_bg(t):
    if 'deck' not in _BG:
        base = sea_img(400, 0.55)
        fg = base.copy(); al = np.zeros((H, W), F32)
        def lay(m, col, k=1.0):
            mm = _fm(m); fg[:] = fg * (1 - (mm * k)[..., None]) + col * (mm * k)[..., None]; al[:] = np.maximum(al, mm * k)
        dk = mk(); _P(dk, [(-10, 560), (W + 10, 560), (W + 10, H), (-10, H)]); lay(dk, C3(0.50, 0.36, 0.22))
        over(fg, ((YY > 560) & ((XX % 38) < 1.6)).astype(F32), C3(0.25, 0.17, 0.10), 0.7)
        rl = mk(); _P(rl, [(-10, 452), (W + 10, 452), (W + 10, 464), (-10, 464)]); lay(rl, C3(0.40, 0.27, 0.16))
        for x0 in range(10, W, 46):
            p_ = mk(); _P(p_, [(x0 - 3, 464), (x0 + 3, 464), (x0 + 3, 560), (x0 - 3, 560)]); lay(p_, C3(0.38, 0.25, 0.15))
        ms = mk(); _P(ms, [(400, 140), (418, 140), (420, 560), (398, 560)]); lay(ms, C3(0.36, 0.24, 0.14))
        e = mk(); _P(e, [(-10, 452), (W + 10, 452), (W + 10, 464), (-10, 464)]); _P(e, [(400, 140), (418, 140), (420, 560), (398, 560)]); outline(fg, e, 0.7, 0.6, 1.0)
        al = np.clip(al + cv2.GaussianBlur(_fm(e, 0.0), (0, 0), 1.0), 0, 1)
        _BG['deck'] = (np.clip(base, 0, 1).astype(F32), np.clip(fg, 0, 1).astype(F32), al.astype(F32))
    base, fg, al = _BG['deck']
    img = base.copy(); sea_waves(img, t, 400, 0.7, 40, 9)
    m = al[..., None]; return img * (1 - m) + fg * m

# ------------------------------------------------------------------ 2020: partículas de virus y hospital
def virus(img, x, y, r, t, a=1.0, col=None, k=0):
    col = C3(0.78, 0.22, 0.18) if col is None else col
    sp = mk()
    for j in range(12):
        an = j * math.pi / 6 + t * 0.4 + k
        x0, y0 = x + r * math.cos(an), y + r * math.sin(an); x1, y1 = x + 1.35 * r * math.cos(an), y + 1.35 * r * math.sin(an)
        _L(sp, [(x0, y0), (x1, y1)], max(1, r * 0.10)); _C(sp, x1, y1, r * 0.13)
    paint(img, sp, col * 0.8, a)
    b = mk(); _C(b, x, y, r); shadow(img, _fm(b), 0.25 * a, (3, 4), 3.0); paint(img, b, col, a); outline(img, b, a, 0.6, 1.0)
    hl = mk(); _C(hl, x - r * 0.35, y - r * 0.35, r * 0.3); paint(img, hl, C3(1, 1, 1), 0.25 * a, 2.0)

def night_city_bg():
    if 'city' in _BG: return _BG['city'].copy()
    g = np.clip((YY - 140) / 520.0, 0, 1)[..., None]
    img = (C3(0.10, 0.14, 0.26) * (1 - g) + C3(0.70, 0.46, 0.36) * g).astype(F32)
    rs = np.random.RandomState(3); m = mk()
    x = -10
    while x < W + 10:
        w = 20 + rs.rand() * 40; h = 40 + rs.rand() * 110; _P(m, [(x, 560), (x + w, 560), (x + w, 560 - h), (x, 560 - h)]); x += w + 2
    paint(img, m, C3(0.20, 0.20, 0.27), 1.0)
    win_ = [(rs.rand() * W, 450 + rs.rand() * 100, 1.2) for _ in range(70)]
    over(img, mcirc(win_, 0.3) * _fm(m), C3(1.0, 0.85, 0.5), 0.7)
    gr = mk(); _P(gr, [(-10, 640), (W + 10, 640), (W + 10, H), (-10, H)]); paint(img, gr, C3(0.24, 0.24, 0.26), 1.0)
    _BG['city'] = np.clip(img, 0, 1).astype(F32); return _BG['city'].copy()

def hospital(img, a=1.0, t=0.0, lights=1.0):
    """pabellón moderno, ancho y bajo, con fachada acristalada."""
    b = mk(); _P(b, [(20, 640), (520, 640), (520, 470), (20, 470)]); shadow(img, _fm(b), 0.4 * a, (6, 8), 6.0); paint(img, b, C3(0.86, 0.86, 0.84), a)
    tp = mk(); _P(tp, [(10, 470), (530, 470), (530, 452), (10, 452)]); paint(img, tp, C3(0.62, 0.64, 0.66), a); outline(img, tp, a, 0.6, 1.0)
    gl = mk()
    for i in range(12):
        x0 = 36 + i * 40
        _P(gl, [(x0, 492), (x0 + 30, 492), (x0 + 30, 560), (x0, 560)])
    paint(img, gl, lerp(C3(0.30, 0.40, 0.50), C3(0.98, 0.90, 0.62), lights), a)
    dr = mk(); _P(dr, [(230, 640), (310, 640), (310, 580), (230, 580)]); paint(img, dr, lerp(C3(0.25, 0.32, 0.40), C3(1.0, 0.92, 0.70), lights), a)
    outline(img, b, a, 0.7, 1.0)
    # cruz roja
    cx, cy = 440, 600; c = mk(); _P(c, [(cx - 6, cy - 18), (cx + 6, cy - 18), (cx + 6, cy + 18), (cx - 6, cy + 18)]); _P(c, [(cx - 18, cy - 6), (cx + 18, cy - 6), (cx + 18, cy + 6), (cx - 18, cy + 6)])
    w_ = mk(); _P(w_, [(cx - 24, cy - 24), (cx + 24, cy - 24), (cx + 24, cy + 24), (cx - 24, cy + 24)]); paint(img, w_, C3(0.97, 0.97, 0.95), a); paint(img, c, RED, a)
    if lights > 0: glow_roi(img, 270, 530, 300, C3(1.0, 0.85, 0.55), 0.18 * lights * a, 1.6)

# ------------------------------------------------------------------ corbeta María Pita (adaptada de la nao de vs_scenes)
def corbeta(img, x, y, L_, t, a=1.0, roll=0.0, facing=1, sails=1.0, cut=0.0, kids_lit=None):
    """casco con tres palos y velas cuadras; cut>0 abre una ventana en el casco con los 22 niños dentro."""
    u = L_ / 100.0
    def P(px, py):
        ca, sa = math.cos(roll), math.sin(roll); qx, qy = px * u * facing, py * u
        return (x + qx * ca - qy * sa, y + qx * sa + qy * ca)
    def PP(pts): return [P(*q) for q in pts]
    hull = [(-50, -16), (-38, -12), (30, -12), (48, -20), (52, -14), (42, 2), (28, 9), (-30, 9), (-46, 0)]
    m = mk(); _P(m, PP(hull)); shadow(img, _fm(m), 0.2 * a, (2, 3), 2.0); paint(img, m, WOOD * 0.95, a)
    cs = mk(); _P(cs, PP([(-50, -16), (-50, -26), (-30, -25), (-30, -12)])); paint(img, cs, WOOD * 1.2, a)
    bd = mk(); _L(bd, PP([(-46, -4), (44, -4)]), max(1, 2 * u)); paint(img, bd, C3(0.86, 0.80, 0.62), a)
    for j in range(7):
        pt = mk(); px = -26 + j * 9; _P(pt, PP([(px, -3), (px + 3.4, -3), (px + 3.4, 0), (px, 0)])); paint(img, pt, C3(0.12, 0.09, 0.07), a)
    masts = [(-18, 70), (6, 82), (30, 58)]
    for k, (mx, mh) in enumerate(masts):
        mm = mk(); _L(mm, PP([(mx, -12), (mx, -12 - mh)]), max(1, 1.6 * u)); paint(img, mm, WOOD * 0.7, a)
        if sails > 0:
            sm = mk(); bw = 14 + 3 * k
            for (y0, y1, s) in ((-12 - mh * 0.92, -12 - mh * 0.68, 0.7), (-12 - mh * 0.64, -12 - mh * 0.38, 0.85), (-12 - mh * 0.34, -12 - mh * 0.06, 1.0)):
                bul = 3 * math.sin(t * 2 + k)
                _P(sm, PP([(mx - bw * s, y0), (mx + bw * s, y0), (mx + bw * s + bul, y1), (mx - bw * s + bul, y1)]))
            paint(img, sm, BONE, a * sails); outline(img, sm, a * sails, 0.5, 0.8)
    fx, fy = -50, -26
    for j, col in enumerate((RED, C3(0.95, 0.78, 0.18), RED)):
        fl = mk(); w0 = 3.2 if j != 1 else 4.0; yo = (0, 3.2, 7.2)[j]; wv = math.sin(t * 6 + j) * 1.5
        _P(fl, PP([(fx, fy - 12 + yo), (fx - 16, fy - 12 + yo + wv), (fx - 16, fy - 12 + yo + w0 + wv), (fx, fy - 12 + yo + w0)])); paint(img, fl, col, a)
    ml = mk(); _L(ml, PP([(fx, -16), (fx, fy - 13)]), max(1, 1.2 * u)); paint(img, ml, WOOD * 0.7, a)
    outline(img, cv2.max(m, cs), a, 0.8, 0.9)
    if cut > 0.01:
        win_ = [(-36, -10.5), (40, -10.5), (40, 6.5), (-34, 6.5)]
        w = mk(); _P(w, PP(win_)); paint(img, w, C3(0.16, 0.10, 0.06), a * cut)
        cx_, cy_ = P(2, -2); glow_roi(img, cx_, cy_, 60 * u, C3(1.0, 0.70, 0.32), 0.45 * a * cut, 1.6)
        for row, (yy, hh) in enumerate(((0.5, 10.0), (6.0, 12.5))):
            for i in range(11):
                px = -31 + i * 6.6 + (3.3 if row == 0 else 0)
                kx, ky = P(px, yy); kid = 11 * row + i
                spr = scaled_child(hh * u, kid); blit(img, spr, kx, ky, a * cut)
                if kids_lit is not None and kids_lit[kid] > 0:
                    glow_roi(img, kx + 1.4 * hh * u * 0.142 * facing, ky - hh * u * 0.6, 7 * u, C3(1.0, 0.75, 0.3), 0.6 * kids_lit[kid] * a * cut, 1.6)
        e = mk(); _P(e, PP(win_)); outline(img, e, a * cut, 0.9, 1.0)

_BASE = {}
def scaled_child(h, v):
    """sprite del niño a cualquier altura: se dibuja una vez grande y se reduce."""
    v = v % 30
    if v not in _BASE: _BASE[v] = child_sprite(200, v)
    col, al, ox, oy, armR, armL = _BASE[v]; k = max(0.05, h / 200.0)
    hh, ww = al.shape; nw, nh = max(2, int(round(ww * k))), max(2, int(round(hh * k)))
    return (cv2.resize(col, (nw, nh), interpolation=cv2.INTER_AREA), cv2.resize(al, (nw, nh), interpolation=cv2.INTER_AREA), ox * k, oy * k,
            (armR[0] * k, armR[1] * k), (armL[0] * k, armL[1] * k))

def kid(img, x, y, h, v, a=1.0, t=0.0, bob=1.0):
    spr = scaled_child(h, v); dy = bob * 0.012 * h * math.sin(t * 2.1 + v * 1.7)
    blit(img, spr, x, y + dy, a)
    (rx, ry), (lx, ly) = spr[4], spr[5]
    return (x + rx, y + dy + ry), (x + lx, y + dy + ly)

def storm_sea(t, wild=1.0, dark=0.7):
    """mar picado con cielo tormentoso (copiado de vs_scenes.storm_sea)."""
    img = sea_img(330, 0.0)
    g = np.clip(YY / 330.0, 0, 1)[..., None]
    sky = C3(0.16, 0.18, 0.24) * (1 - g) + C3(0.36, 0.38, 0.42) * g
    m = (YY < 330).astype(F32)[..., None]
    img = img * (1 - m * dark) + sky * m * dark
    img[330:] *= C3(0.55, 0.62, 0.68)
    sea_waves(img, t * (1 + wild), 330, 1.0, int(70 + 80 * wild), 5)
    xs = np.arange(W, dtype=F32)
    for k in range(4):
        yb = 380 + k * 70; amp = (10 + 12 * k) * wild
        yy = yb + amp * np.sin(xs * (0.018 - 0.002 * k) + t * (1.6 + 0.3 * k) + k)
        mm = np.clip(YY - yy[None, :], 0, 1) * np.clip(yy[None, :] + 60 - YY, 0, 1)
        over(img, mm, C3(0.20, 0.30, 0.36), 0.5)
        crest = np.clip(1 - np.abs(YY - yy[None, :]) / 2.5, 0, 1) * (np.sin(xs * 0.05 + t * 3 + k)[None, :] > 0.2)
        over(img, crest, C3(0.85, 0.90, 0.92), 0.7)
    return img

def front_wave(img, t, y0, amp=10.0, a=1.0, col=C3(0.22, 0.32, 0.38)):
    xs = np.arange(W, dtype=F32)
    yy = y0 + amp * np.sin(xs * 0.021 + t * 2.2) + 0.5 * amp * np.sin(xs * 0.047 - t * 1.4)
    mm = np.clip(YY - yy[None, :], 0, 1)
    over(img, mm, col, a)
    crest = np.clip(1 - np.abs(YY - yy[None, :]) / 2.2, 0, 1) * (np.sin(xs * 0.06 + t * 3)[None, :] > -0.2)
    over(img, crest, C3(0.86, 0.91, 0.93), 0.75 * a)
