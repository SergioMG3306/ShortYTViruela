"""Base gráfica del Short de Voltaire: dibujo nativo a 1080×1920 (sin reescalado), estilo «cuaderno del matemático»:
fondo azul noche, tinta dorada que se escribe a pluma, tipografías del XVIII, grabados virados a azul y oro."""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
F32 = np.float32
YY, XX = np.mgrid[0:H, 0:W].astype(F32)
FD = '/home/claude/serie/voltaire/fonts/'
FONTS = dict(play='Playfair-Bold.ttf', playk='Playfair-Black.ttf', playr='Playfair-Regular.ttf', cas='Caslon-Bold.ttf', casr='Caslon-Regular.ttf',
             casi='Caslon-Italic.ttf', fell='Fell-Regular.ttf', felli='Fell-Italic.ttf', gar='Garamond-SemiBold.ttf')

def C3(a, b, c): return np.array((a, b, c), F32)
NAVY = C3(0.050, 0.068, 0.110); NAVY2 = C3(0.090, 0.115, 0.175); GOLD = C3(0.88, 0.70, 0.36); GOLDL = C3(0.99, 0.88, 0.58)
IVORY = C3(0.95, 0.91, 0.82); VERM = C3(0.86, 0.30, 0.22); INK = C3(0.10, 0.08, 0.07); PARCH = C3(0.93, 0.87, 0.74); WAX = C3(0.62, 0.08, 0.07)
SEPIA = C3(0.36, 0.22, 0.12); TEAL = C3(0.42, 0.66, 0.72)

def cl(x, a=0.0, b=1.0): return min(b, max(a, x))
def prog(t, a, b): return cl((t - a) / (b - a)) if b != a else float(t >= a)
def ease(x): x = cl(x); return x * x * (3 - 2 * x)
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def win(t, a, b, fi=0.35, fo=0.35): return ease((t - a) / fi) * (1 - ease((t - b) / fo))

def lerpk(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1: return v0 + (v1 - v0) * ease((t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]

def noise(seed, cells, shape=(H, W)):
    rs = np.random.RandomState(seed); out = np.zeros(shape, F32); amp = 1.0; tot = 0
    for c in cells:
        a = rs.rand(max(2, shape[0] // c), max(2, shape[1] // c)).astype(F32)
        out += cv2.resize(a, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC) * amp; tot += amp; amp *= 0.6
    return out / tot

# ------------------------------------------------------------------ fondos
_BG = {}
def board(kind='navy'):
    """fondo azul noche con fibra de papel, retícula de cuaderno muy tenue y viñeta."""
    if kind in _BG: return _BG[kind].copy()
    g = np.clip(YY / H, 0, 1)[..., None]
    img = NAVY2 * (1 - g) + NAVY * g
    fib = noise(5, (6, 14, 40, 120)); img = img * (0.88 + 0.22 * fib[..., None])
    rs = np.random.RandomState(9); speck = cv2.GaussianBlur(rs.rand(H, W).astype(F32), (0, 0), 0.8); img += (speck[..., None] - 0.5) * 0.025
    if kind == 'navy':
        grid = (((XX % 54) < 1.4) | ((YY % 54) < 1.4)).astype(F32)
        img = img * (1 - 0.06 * grid[..., None]) + GOLD * 0.06 * grid[..., None]
    d = np.sqrt(((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H * 0.45) / (H * 0.70)) ** 2)
    img *= np.clip(1.08 - 0.55 * d ** 2, 0.35, 1.1)[..., None]
    _BG[kind] = np.clip(img, 0, 1).astype(F32); return _BG[kind].copy()

def parchment_bg():
    if 'parch' in _BG: return _BG['parch'].copy()
    f = noise(17, (4, 10, 30, 90, 240))
    img = PARCH * (0.82 + 0.26 * f[..., None])
    stain = noise(23, (60, 160)); img *= (1 - 0.12 * np.clip((stain - 0.55) * 4, 0, 1))[..., None]
    d = np.sqrt(((XX - W / 2) / (W * 0.7)) ** 2 + ((YY - H / 2) / (H * 0.66)) ** 2)
    img *= np.clip(1.05 - 0.6 * d ** 2.2, 0.3, 1)[..., None]
    _BG['parch'] = np.clip(img, 0, 1).astype(F32); return _BG['parch'].copy()

# ------------------------------------------------------------------ composición
def over(img, m, col, a=1.0):
    if a <= 0.001: return
    mm = (m * a)[..., None]; img[:] = img * (1 - mm) + np.asarray(col, F32) * mm

def over_roi(img, m, col, x0, y0, a=1.0):
    """pega una máscara pequeña m en (x0,y0) (esquina)."""
    h, w = m.shape; xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb or a <= 0.001: return
    mm = (m[ya - y0:yb - y0, xa - x0:xb - x0] * a)[..., None]
    col = np.asarray(col, F32)
    if col.ndim == 3: col = col[ya - y0:yb - y0, xa - x0:xb - x0]
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - mm) + col * mm

def glow(img, cx, cy, r, col, k=1.0, power=2.0):
    x0 = int(max(0, cx - r)); x1 = int(min(W, cx + r + 1)); y0 = int(max(0, cy - r)); y1 = int(min(H, cy + r + 1))
    if x0 >= x1 or y0 >= y1 or r < 1 or k <= 0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(F32); d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    img[y0:y1, x0:x1] += (np.clip(1 - d, 0, 1) ** power)[..., None] * (np.asarray(col, F32) * k)

def shadow_m(img, m, k=0.4, off=(8, 12), bl=10.0):
    s = cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, off[0]], [0, 1, off[1]]]), (W, H)), (0, 0), bl); img *= (1 - k * s)[..., None]

S16 = 16
def P16(pts): return np.round(np.asarray(pts, np.float64) * S16).astype(np.int32)
def mpoly(polys, blur=0.0):
    m = np.zeros((H, W), np.uint8)
    for p in polys: cv2.fillPoly(m, [P16(p)], 255, cv2.LINE_AA, shift=4)
    m = m.astype(F32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m
def mcirc(items, blur=0.0):
    m = np.zeros((H, W), np.uint8)
    for (x, y, r) in items: cv2.circle(m, (int(round(x * S16)), int(round(y * S16))), int(round(max(r, 0.1) * S16)), 255, -1, cv2.LINE_AA, shift=4)
    m = m.astype(F32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m
def mline(lines, th=3.0, blur=0.0):
    m = np.zeros((H, W), np.uint8)
    for pts in lines: cv2.polylines(m, [P16(pts)], False, 255, max(1, int(round(th))), cv2.LINE_AA, shift=4)
    m = m.astype(F32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m
def mring(items, th=3.0):
    m = np.zeros((H, W), np.uint8)
    for (x, y, r) in items: cv2.circle(m, (int(round(x * S16)), int(round(y * S16))), int(round(r * S16)), 255, max(1, int(round(th))), cv2.LINE_AA, shift=4)
    return m.astype(F32) / 255
def rot(pts, ang, c):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    return [((x - c[0]) * ca - (y - c[1]) * sa + c[0], (x - c[0]) * sa + (y - c[1]) * ca + c[1]) for x, y in pts]

# ------------------------------------------------------------------ texto
_FO = {}; _TS = {}
def font(name, sz):
    k = (name, sz)
    if k not in _FO: _FO[k] = ImageFont.truetype(FD + FONTS[name], sz)
    return _FO[k]

def text_mask(text, sz, fname='play', track=0):
    """máscara de texto (alto ≈ 1.5·sz), cacheada. Devuelve (m, ancho real)."""
    k = (text, sz, fname, track)
    if k in _TS: return _TS[k]
    f = font(fname, sz)
    if track:
        ws = [f.getlength(ch) + track for ch in text]; tw = int(sum(ws)) + 4
    else:
        tw = int(f.getlength(text)) + 4
    pad = int(sz * 0.35); h = int(sz * 1.55)
    im = Image.new('L', (tw + 2 * pad, h), 0); d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch, w_ in zip(text, ws): d.text((x, int(sz * 0.15)), ch, font=f, fill=255); x += w_
    else:
        d.text((pad, int(sz * 0.15)), text, font=f, fill=255)
    m = np.asarray(im, F32) / 255
    _TS[k] = (m, tw, pad); return _TS[k]

def text(img, s, x, y, sz, col=IVORY, a=1.0, fname='play', anchor='c', reveal=None, pen=True, track=0, shadow=0.0, glowk=0.0):
    """dibuja texto centrado verticalmente en y. reveal∈[0,1]: escritura a pluma de izquierda a derecha."""
    if a <= 0.003 or not s: return
    m, tw, pad = text_mask(s, sz, fname, track); h, w = m.shape
    x0 = int(round(x - pad - (tw / 2 if anchor == 'c' else (tw if anchor == 'r' else 0)))); y0 = int(round(y - h / 2))
    mm = m
    edge = None
    if reveal is not None:
        if reveal <= 0: return
        if reveal < 1:
            xe = pad + tw * reveal; ramp = np.clip((xe - np.arange(w, dtype=F32)) / max(6.0, sz * 0.25), 0, 1)[None, :]
            mm = m * ramp; edge = (x0 + xe, y0 + h * 0.55)
    if shadow > 0: over_roi(img, cv2.GaussianBlur(mm, (0, 0), sz * 0.06), C3(0, 0, 0), x0 + int(sz * 0.04), y0 + int(sz * 0.07), shadow * a)
    if glowk > 0: over_roi(img, cv2.GaussianBlur(mm, (0, 0), sz * 0.18), col, x0, y0, glowk * a)
    over_roi(img, mm, col, x0, y0, a)
    if edge is not None and pen: glow(img, edge[0], edge[1], sz * 0.55, GOLDL, 0.55 * a, 2.0)

def text_w(s, sz, fname='play', track=0): return text_mask(s, sz, fname, track)[1]

# ------------------------------------------------------------------ objetos
def plate(img, x0, y0, x1, y1, a=1.0, col=None, border=GOLD, sh=0.45):
    """placa: rectángulo con filete dorado doble."""
    if a <= 0.003: return
    col = NAVY * 0.85 if col is None else col
    m = mpoly([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]])
    shadow_m(img, m, sh * a, (6, 10), 14); over(img, m, col, 0.93 * a)
    over(img, mline([[(x0 + 8, y0 + 8), (x1 - 8, y0 + 8), (x1 - 8, y1 - 8), (x0 + 8, y1 - 8), (x0 + 8, y0 + 8)]], 2), border, a)
    over(img, mline([[(x0 + 15, y0 + 15), (x1 - 15, y0 + 15), (x1 - 15, y1 - 15), (x0 + 15, y1 - 15), (x0 + 15, y0 + 15)]], 1), border, 0.6 * a)

def header(img, t, s, t0, t1, sz=64, col=GOLDL, cps=18.0):
    a = win(t, t0 - 0.05, t1, 0.3, 0.45)
    if a <= 0.003: return
    plate(img, 70, 96, 1010, 250, a)
    text(img, s, 540, 173, sz, col, a, 'play', reveal=prog(t, t0, t0 + max(0.25, len(s) / cps)))

def ticket(img, cx, cy, w, h, ang, label, sub, a=1.0, col=PARCH, ink=INK, num=None):
    """billete de lotería del XVIII: papel con borde dentado, orla y textos."""
    if a <= 0.003: return
    pts = []
    n = 14
    for i in range(n + 1): pts.append((-w / 2 + w * i / n, -h / 2 + (3 if i % 2 else 0)))
    for i in range(n + 1): pts.append((w / 2 - (3 if i % 2 else 0), -h / 2 + h * i / n))
    for i in range(n + 1): pts.append((w / 2 - w * i / n, h / 2 - (3 if i % 2 else 0)))
    for i in range(n + 1): pts.append((-w / 2 + (3 if i % 2 else 0), h / 2 - h * i / n))
    P = rot([(cx + px, cy + py) for px, py in pts], ang, (cx, cy))
    m = mpoly([P]); shadow_m(img, m, 0.5 * a, (6, 10), 10); over(img, m, col, a)
    b = rot([(cx - w / 2 + 12, cy - h / 2 + 12), (cx + w / 2 - 12, cy - h / 2 + 12), (cx + w / 2 - 12, cy + h / 2 - 12), (cx - w / 2 + 12, cy + h / 2 - 12), (cx - w / 2 + 12, cy - h / 2 + 12)], ang, (cx, cy))
    over(img, mline([b], 2), ink, 0.75 * a)
    if abs(ang) < 0.5:
        text(img, label, cx, cy - h * 0.12, int(h * 0.30), ink, a, 'play')
        if sub: text(img, sub, cx, cy + h * 0.24, int(h * 0.14), ink, 0.85 * a, 'casr', track=2)
        if num: text(img, num, cx - w / 2 + 34, cy - h / 2 + 30, int(h * 0.10), VERM, a, 'casr', anchor='l')

def coin(img, cx, cy, r, a=1.0, tilt=0.0):
    ry = r * (1 - 0.65 * tilt)
    m = np.zeros((H, W), np.uint8); cv2.ellipse(m, (int(cx * S16), int(cy * S16)), (int(r * S16), int(ry * S16)), 0, 0, 360, 255, -1, cv2.LINE_AA, shift=4); m = m.astype(F32) / 255
    if tilt > 0:
        e = np.zeros((H, W), np.uint8); cv2.ellipse(e, (int(cx * S16), int((cy + r * 0.12) * S16)), (int(r * S16), int(ry * S16)), 0, 0, 360, 255, -1, cv2.LINE_AA, shift=4)
        over(img, e.astype(F32) / 255, GOLD * 0.55, a)
    over(img, m, GOLD, a)
    i = np.zeros((H, W), np.uint8); cv2.ellipse(i, (int(cx * S16), int(cy * S16)), (int(r * 0.78 * S16), int(ry * 0.78 * S16)), 0, 0, 360, 255, max(1, int(r * 0.07)), cv2.LINE_AA, shift=4)
    over(img, i.astype(F32) / 255, GOLD * 0.65, a)
    glow(img, cx - r * 0.35, cy - ry * 0.35, r * 0.6, C3(1, 0.95, 0.8), 0.25 * a, 2.0)

def wax_seal(img, cx, cy, r, t, t0, letter='V', a=1.0):
    """lacre rojo que cae y se aplasta (sustituye a los sellos de goma de la serie)."""
    d = t - t0
    if d < 0 or a <= 0.003: return
    s = 1 + 0.6 * (1 - eo(d / 0.18)); al = a * min(1, d / 0.06)
    rs = np.random.RandomState(int(cx + cy)); ang = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    rr = r * s * (1 + 0.08 * np.sin(5 * ang + rs.rand() * 6) + 0.04 * np.sin(11 * ang + rs.rand() * 6))
    pts = list(zip(cx + rr * np.cos(ang), cy + rr * np.sin(ang)))
    m = mpoly([pts]); shadow_m(img, m, 0.55 * al, (5, 8), 8); over(img, m, WAX, al)
    over(img, mring([(cx, cy, r * s * 0.72)], max(2, r * 0.07)), WAX * 0.65, al)
    glow(img, cx - r * 0.3 * s, cy - r * 0.35 * s, r * 0.7 * s, C3(1, 0.5, 0.4), 0.22 * al, 2.0)
    text(img, letter, cx, cy + r * 0.04 * s, int(r * 0.95 * s), WAX * 0.55, al, 'play')

# ------------------------------------------------------------------ grabados (virados a azul y oro)
_IM = {}
def duotone(path, k=0.85):
    key = (path, k)
    if key in _IM: return _IM[key]
    a = np.asarray(Image.open(path).convert('RGB'), F32) / 255
    lum = a @ np.array([0.30, 0.59, 0.11], F32)
    lo, hi = np.percentile(lum, 2), np.percentile(lum, 98); lum = np.clip((lum - lo) / max(1e-3, hi - lo), 0, 1)
    ramp = np.array([[0.035, 0.05, 0.09], [0.12, 0.17, 0.28], [0.45, 0.42, 0.40], [0.86, 0.72, 0.48], [1.0, 0.95, 0.84]], F32)
    xs = np.linspace(0, 1, len(ramp)); dt = np.stack([np.interp(lum, xs, ramp[:, c]) for c in range(3)], -1).astype(F32)
    out = dt * k + a * (1 - k)
    _IM[key] = out; return out

def photo_kb(path, t, t0, t1, z0, z1, c0, c1, k=0.85, box=None):
    """imagen a pantalla completa (o en el rectángulo box) con Ken Burns, virada a azul y oro."""
    src = duotone(path, k); hh, ww = src.shape[:2]
    bx0, by0, bx1, by1 = box if box else (0, 0, W, H); bw, bh = bx1 - bx0, by1 - by0
    q = ease(prog(t, t0, t1)); z = lerp(z0, z1, q); cx = lerp(c0[0], c1[0], q) * ww; cy = lerp(c0[1], c1[1], q) * hh
    s = max(bw / ww, bh / hh) * z
    M = np.float32([[s, 0, (bx0 + bw / 2) - s * cx], [0, s, (by0 + bh / 2) - s * cy]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA if s < 0.6 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def gilt_frame(img, x0, y0, x1, y1, a=1.0, oval=False):
    """marco dorado tallado (bisel claro/oscuro) alrededor de un rectángulo u óvalo."""
    if oval:
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
        def ell(r_add, th):
            m = np.zeros((H, W), np.uint8); cv2.ellipse(m, (int(cx * S16), int(cy * S16)), (int((rx + r_add) * S16), int((ry + r_add) * S16)), 0, 0, 360, 255, th, cv2.LINE_AA, shift=4); return m.astype(F32) / 255
        outer = ell(26, 40); shadow_m(img, outer, 0.5 * a, (8, 14), 16)
        over(img, outer, GOLD * 0.8, a); over(img, ell(16, 8), GOLDL, 0.8 * a); over(img, ell(34, 5), GOLD * 0.5, a); over(img, ell(6, 4), GOLD * 0.45, a)
        return
    def rect_l(d, th):
        return mline([[(x0 - d, y0 - d), (x1 + d, y0 - d), (x1 + d, y1 + d), (x0 - d, y1 + d), (x0 - d, y0 - d)]], th)
    outer = rect_l(22, 40); shadow_m(img, outer, 0.5 * a, (8, 14), 16)
    over(img, outer, GOLD * 0.8, a); over(img, rect_l(14, 6), GOLDL, 0.8 * a); over(img, rect_l(36, 4), GOLD * 0.5, a); over(img, rect_l(4, 4), GOLD * 0.45, a)

def framed_photo(img, path, t, t0, t1, z0, z1, c0, c1, box, a=1.0, oval=False, k=0.85):
    if a <= 0.003: return
    ph = photo_kb(path, t, t0, t1, z0, z1, c0, c1, k, box)
    x0, y0, x1, y1 = box
    if oval:
        m = np.zeros((H, W), np.uint8); cv2.ellipse(m, (int((x0 + x1) / 2 * S16), int((y0 + y1) / 2 * S16)), (int((x1 - x0) / 2 * S16), int((y1 - y0) / 2 * S16)), 0, 0, 360, 255, -1, cv2.LINE_AA, shift=4); m = m.astype(F32) / 255
    else:
        m = mpoly([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]])
    mm = (m * a)[..., None]; img[:] = img * (1 - mm) + ph * mm
    gilt_frame(img, x0, y0, x1, y1, a, oval)

# ------------------------------------------------------------------ cámara y acabado
def cam(img, z=1.0, dx=0.0, dy=0.0, cx=W / 2, cy=H / 2, ang=0.0):
    M = cv2.getRotationMatrix2D((cx, cy), ang, z); M[:, 2] += (dx, dy)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

_rg = np.random.RandomState(77); GRAIN = [(cv2.GaussianBlur(_rg.randn(H, W).astype(F32), (0, 0), 0.7) * 0.010)[..., None] for _ in range(2)]
_d = np.sqrt(((XX - W / 2) / (W * 0.80)) ** 2 + ((YY - H / 2) / (H * 0.74)) ** 2)
VIG = np.clip(1 - 0.32 * _d ** 2.4, 0.5, 1)[..., None].astype(F32)
def finish(img, fi):
    img = img * VIG
    hi = np.clip(img - 0.78, 0, None); img = img + 0.35 * cv2.GaussianBlur(hi, (0, 0), 14)
    img = img + GRAIN[(fi // 2) % 2]
    return np.clip(img, 0, 1)

# ------------------------------------------------------------------ tiempos de la voz (timing.json)
import json, unicodedata
TJ = json.load(open('/home/claude/serie/voltaire/timing.json'))
ST = TJ['sent_t']; WD = TJ['words']; TEND = TJ['total']
SW = [[] for _ in ST]
for _w, _t, _si in WD: SW[_si].append((_w, _t))
_sf = TJ['scene_first']
B = [0.0] + [ST[_sf[i]][0] - 1.0 for i in range(1, len(_sf))] + [TEND]
B[4] = ST[_sf[4]][0] - 0.35; B[6] = ST[_sf[6]][0] - 0.4      # dejan respirar los lacres antes del cambio de escena
def _nz(x): return ''.join(c for c in unicodedata.normalize('NFD', x.lower()) if unicodedata.category(c) != 'Mn' and c.isalnum())
def tw(si, prefix, nth=0):
    p = _nz(prefix); k = 0
    for (w, t, s_) in WD:
        if s_ == si and _nz(w).startswith(p):
            if k == nth: return t
            k += 1
    raise KeyError((si, prefix, nth))
def st0(si): return ST[si][0]
def st1(si): return ST[si][1]

# ------------------------------------------------------------------ eventos para el audio (pluma, lacres, monedas…)
EV = None
def ev(kind, key, t0, dur=0.0):
    if EV is not None: EV[(kind, str(key), round(float(t0), 3))] = round(float(dur), 3)

def write(img, t, s, x, y, sz, col, t0, cps=16.0, a=1.0, fname='play', anchor='c', glowk=0.0, shadow=0.0, pen=True, track=0):
    """texto escrito a pluma desde t0 a cps caracteres/s (registra el sonido de la pluma)."""
    if a <= 0.003 or t < t0: return
    dur = max(0.2, len(s) / cps); ev('pen', s, t0, dur)
    text(img, s, x, y, sz, col, a, fname, anchor, reveal=prog(t, t0, t0 + dur), pen=pen, track=track, shadow=shadow, glowk=glowk)

def header(img, t, s, t0, t1, sz=64, col=GOLDL, cps=18.0):
    a = win(t, t0 - 0.05, t1, 0.3, 0.45)
    if a <= 0.003: return
    plate(img, 70, 96, 1010, 250, a)
    write(img, t, s, 540, 173, sz, col, t0, cps, a)

def seal(img, t, t0, cx, cy, r, letter='V', a=1.0):
    if t < t0 or a <= 0.003: return
    ev('seal', letter, t0); wax_seal(img, cx, cy, r, t, t0, letter, a)

# ------------------------------------------------------------------ sprites cacheados (dibujo una vez, luego se pega)
_SP = {}
def sprite(key, draw):
    """draw(img, cx, cy) dibuja el objeto centrado en (540, 960) de un lienzo completo; se extrae color + alfa y se recorta."""
    if key in _SP: return _SP[key]
    blk = np.zeros((H, W, 3), F32); wht = np.ones((H, W, 3), F32)
    draw(blk, 540, 960); draw(wht, 540, 960)
    al = np.clip(1 - (wht - blk).mean(2), 0, 1)
    col = np.where(al[..., None] > 1e-3, blk / np.maximum(al[..., None], 1e-3), 0)
    ys, xs = np.where(al > 0.004)
    if len(ys) == 0: _SP[key] = None; return None
    ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    _SP[key] = (np.clip(col[ya:yb, xa:xb], 0, 1.5).astype(F32), al[ya:yb, xa:xb].astype(F32), 540 - xa, 960 - ya); return _SP[key]

def blit(img, spr, cx, cy, a=1.0, scale=1.0, ang=0.0):
    if spr is None or a <= 0.003 or scale <= 0.01: return
    col, al, ox, oy = spr
    if abs(scale - 1) > 1e-3 or abs(ang) > 1e-3:
        h, w = al.shape; D = int(math.hypot(w, h) * scale) + 4
        ox, oy = float(ox), float(oy); M = cv2.getRotationMatrix2D((ox, oy), float(ang), float(scale)); M[0, 2] += D / 2 - ox; M[1, 2] += D / 2 - oy
        col = cv2.warpAffine(col, M, (D, D), flags=cv2.INTER_LINEAR); al = cv2.warpAffine(al, M, (D, D), flags=cv2.INTER_LINEAR); ox = oy = D / 2
    h, w = al.shape; x0 = int(round(cx - ox)); y0 = int(round(cy - oy))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb: return
    m = (al[ya - y0:yb - y0, xa - x0:xb - x0] * a)[..., None]
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - m) + col[ya - y0:yb - y0, xa - x0:xb - x0] * m

# ------------------------------------------------------------------ subtítulos (banda oscura, palabra dicha en oro)
CAP_SZ = 58; CAP_Y = 1420; CAP_MAXW = 860
def _chunks(si):
    ws = SW[si]; out = []; cur = []; ln = 0
    for i, (w, t) in enumerate(ws):
        cur.append((w, t)); ln += len(w) + 1
        if i == len(ws) - 1 or ln > 44 or (w[-1] in ',:;' and ln > 18): out.append(cur); cur = []; ln = 0
    return out
CH = [_chunks(i) for i in range(len(ST))]
def caption(img, t):
    for si, (t0, t1, _) in enumerate(ST):
        if not (t0 - 0.2 <= t <= t1 + 0.6): continue
        chs = CH[si]; ci = 0
        for k, c in enumerate(chs):
            if c[0][1] - 0.15 <= t: ci = k
        c = chs[ci]; end = (chs[ci + 1][0][1] - 0.15) if ci + 1 < len(chs) else (t1 + 0.6)
        al = min(1, (t - (c[0][1] - 0.2)) / 0.15) * min(1, (end - t) / 0.25)
        if al <= 0.01: return
        f = font('cas', CAP_SZ); sp = f.getlength(' ')
        lines = [[]]; lw = [0.0]
        for (w, tw_) in c:
            ww = f.getlength(w)
            if lines[-1] and lw[-1] + sp + ww > CAP_MAXW: lines.append([]); lw.append(0.0)
            lw[-1] += (sp if lines[-1] else 0) + ww; lines[-1].append((w, tw_, ww))
        LH = CAP_SZ * 1.32; hh = len(lines) * LH + 40; wmax = max(lw) + 80
        x0, x1 = 540 - wmax / 2, 540 + wmax / 2; y0 = CAP_Y - hh / 2; y1 = CAP_Y + hh / 2
        m = mpoly([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], 1.0); shadow_m(img, m, 0.45 * al, (0, 8), 14); over(img, m, NAVY * 0.55, 0.90 * al)
        over(img, mline([[(x0 + 20, y0), (x1 - 20, y0)]], 3), GOLD, 0.95 * al)
        cur = max([j for j, (w, tw_) in enumerate(c) if tw_ <= t + 0.04] or [-1])
        j = 0
        for li, ln_ in enumerate(lines):
            x = 540 - lw[li] / 2; y = y0 + 20 + LH * (li + 0.5)
            for (w, tw_, ww) in ln_:
                col = GOLDL if j == cur else (IVORY if j < cur else IVORY * 0.42)
                text(img, w, x, y, CAP_SZ, col, al, 'cas', anchor='l'); x += ww + sp; j += 1
        return
