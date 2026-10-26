"""Globo terráqueo (proyección ortográfica) con fronteras reales (Natural Earth 50m) y relieve procedural,
en la misma paleta que ll_map. Textura equirectangular cacheada en disco; cámara (lon, lat, R px)."""
import os, json, math
import numpy as np, cv2
from cv_lib import W, H, F32, C3, INK, RED, CREAM, PAPER, XX, YY, over, mcirc, glow_roi, lerp, ease, prog, fractal

TW, TH = 6144, 3072
GEO = '/home/claude/serie/plaga/geo/countries-50m.geojson'
CACHE = '/home/claude/serie/balmis/globe_tex.npz'

def uv(lon, lat): return ((np.asarray(lon) + 180.0) / 360.0 * TW, (90.0 - np.asarray(lat)) / 180.0 * TH)

_G = json.load(open(GEO))
NAMES = []; RINGS = []          # RINGS: (idx, arr lon/lat)
for i, f in enumerate(_G['features']):
    NAMES.append(f['properties']['name']); g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in polys:
        for k, ring in enumerate(p):
            RINGS.append((i, k, np.asarray(ring, np.float64)))
del _G
CID = {n: i + 1 for i, n in enumerate(NAMES)}

# ------------------------------------------------------------------ relieve procedural sobre la geografía real
# (polilínea lon/lat, altura km, semiancho en grados)
RIDGES = [
    ([(-73.0, 11.0), (-71.5, 9.0), (-73.5, 6.0), (-75.5, 4.0), (-77.5, 1.0), (-78.5, -2.0), (-79.0, -5.0), (-77.5, -9.0), (-75.5, -12.0), (-72.0, -15.0),
      (-69.0, -17.0), (-68.5, -20.0), (-68.0, -24.0), (-69.5, -28.0), (-70.0, -33.0), (-71.0, -38.0), (-71.5, -42.0), (-72.5, -47.0), (-73.5, -51.0)], 4.4, 1.6),
    ([(-69.5, -15.5), (-67.5, -18.5), (-66.5, -22.0)], 3.8, 2.6),
    ([(-108.0, 29.0), (-104.5, 24.0), (-103.0, 21.0)], 2.3, 1.3), ([(-101.0, 25.0), (-98.5, 21.0)], 2.0, 0.9), ([(-104.0, 19.6), (-97.0, 19.2)], 2.8, 0.8),
    ([(-101.0, 17.6), (-97.0, 16.6), (-94.5, 16.4)], 2.0, 0.8), ([(-92.0, 15.4), (-89.0, 14.6), (-86.0, 13.5), (-84.5, 10.5), (-82.5, 9.0), (-80.0, 8.4)], 2.0, 0.9),
    ([(-106.0, 35.0), (-106.0, 40.0), (-110.0, 44.0), (-115.0, 49.0), (-120.0, 54.0), (-128.0, 59.0), (-140.0, 62.0)], 3.0, 2.8),
    ([(-119.0, 36.5), (-121.0, 41.0), (-121.5, 46.0)], 2.4, 1.0), ([(-84.0, 34.0), (-80.0, 37.0), (-77.0, 40.0), (-73.0, 43.0), (-69.0, 46.0)], 1.0, 1.6),
    ([(-73.5, 19.0), (-70.5, 19.0)], 1.6, 0.6), ([(-77.5, 20.0), (-75.0, 20.1)], 1.2, 0.4), ([(-77.0, 18.1)], 1.2, 0.4),
    ([(-69.5, 10.3), (-66.0, 10.3), (-63.0, 10.4)], 2.0, 0.6), ([(-65.0, 5.0), (-61.0, 5.0)], 1.5, 2.0), ([(-48.0, -18.0), (-44.0, -21.0)], 1.0, 4.0),
    ([(-1.0, 42.7), (1.0, 42.6), (2.5, 42.5)], 2.6, 0.5), ([(-7.0, 43.0), (-4.0, 43.1)], 1.8, 0.6), ([(-6.5, 40.3), (-3.5, 40.8)], 1.8, 0.5), ([(-5.0, 36.9), (-2.5, 37.2)], 2.2, 0.6),
    ([(6.0, 45.5), (8.0, 46.2), (10.0, 46.5), (14.0, 47.0)], 3.0, 0.9), ([(-8.0, 31.0), (-4.0, 32.5), (0.0, 34.0), (5.0, 35.5)], 2.5, 1.2),
    ([(41.0, 43.0), (46.0, 42.0)], 3.2, 0.8), ([(47.0, 34.0), (52.0, 30.0), (57.0, 27.0)], 2.2, 1.5),
    ([(73.0, 35.0), (78.0, 32.0), (82.0, 30.0), (86.0, 28.0), (90.0, 28.0), (95.0, 29.0)], 6.0, 1.6), ([(80.0, 34.5), (88.0, 33.0), (96.0, 33.5)], 4.6, 4.5),
    ([(75.0, 42.0), (80.0, 42.5), (85.0, 43.0)], 3.5, 1.4), ([(98.0, 27.0), (100.0, 22.0)], 2.5, 1.5), ([(106.0, 17.0), (108.0, 13.0)], 1.5, 0.8),
    ([(110.0, 25.0), (117.0, 26.0)], 1.0, 2.0), ([(121.0, 23.5)], 2.5, 0.6), ([(121.0, 17.5), (121.3, 15.5), (122.5, 13.5), (124.0, 12.0), (125.5, 8.0)], 1.6, 0.7),
    ([(115.0, 3.0)], 1.5, 1.8), ([(97.0, 3.0), (101.0, -1.0), (104.0, -4.0)], 2.0, 0.8), ([(106.5, -7.0), (112.0, -7.8)], 2.0, 0.5),
    ([(138.0, -4.5), (145.0, -6.0)], 3.5, 1.2), ([(39.0, 9.0)], 2.5, 3.0), ([(36.0, -3.0)], 1.8, 3.0), ([(29.0, -29.0), (30.5, -27.0)], 2.0, 1.0),
    ([(146.0, -37.0), (150.0, -33.0), (152.0, -28.0), (147.0, -20.0), (145.0, -16.0)], 1.0, 1.5), ([(60.0, 50.0), (59.0, 58.0), (61.0, 65.0)], 1.2, 1.5),
    ([(8.0, 61.0), (14.0, 65.0), (18.0, 68.0)], 1.5, 2.0), ([(-42.0, 72.0)], 2.6, 9.0), ([(0.0, -82.0)], 2.6, 14.0), ([(137.0, 36.0), (140.0, 38.0)], 2.0, 1.0),
]
HY_E = [0.0, 0.5, 1.1, 1.8, 2.45, 2.9]
HY_C = np.array([[1.00, 1.00, 1.00], [0.92, 0.97, 0.84], [0.86, 0.90, 0.76], [0.84, 0.78, 0.68], [0.93, 0.92, 0.91], [1.03, 1.04, 1.07]], F32)
LAND0 = C3(0.90, 0.86, 0.74); SEA0 = C3(0.58, 0.72, 0.79)

def _noise(shape, cell, seed):
    rs = np.random.RandomState(seed); gh = max(2, int(shape[0] / cell) + 2); gw = max(2, int(shape[1] / cell) + 2)
    return cv2.resize(rs.rand(gh, gw).astype(F32), (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)

def _build():
    # máscaras e identificadores de país
    ids = np.zeros((TH, TW), np.uint16); land = np.zeros((TH, TW), np.uint8); lines = np.zeros((TH, TW), np.uint8)
    for (i, k, r) in RINGS:
        u, v = uv(r[:, 0], r[:, 1]); q = np.stack([u, v], 1)
        if k == 0:
            cv2.fillPoly(ids, [np.round(q).astype(np.int32)], int(i + 1))
            cv2.fillPoly(land, [np.round(q * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        else:
            cv2.fillPoly(ids, [np.round(q).astype(np.int32)], 0); cv2.fillPoly(land, [np.round(q * 16).astype(np.int32)], 0, cv2.LINE_AA, shift=4)
        cv2.polylines(lines, [np.round(q * 16).astype(np.int32)], True, 255, 2, cv2.LINE_AA, shift=4)
    landf = land.astype(F32) / 255
    # relieve a media resolución
    h2, w2 = TH // 2, TW // 2; ppd = w2 / 360.0
    env = np.zeros((h2, w2), F32)
    for pl, hk, wd in RIDGES:
        m = np.full((h2, w2), 255, np.uint8)
        q = np.array([((lo + 180) * ppd, (90 - la) * ppd) for lo, la in pl])
        if len(q) == 1: cv2.circle(m, (int(q[0, 0]), int(q[0, 1])), 1, 0, -1)
        else: cv2.polylines(m, [np.round(q * 16).astype(np.int32)], False, 0, 1, cv2.LINE_8, shift=4)
        d = cv2.distanceTransform(m, cv2.DIST_L2, 5) / ppd
        env = np.maximum(env, hk * np.exp(-(d / wd) ** 2) + 0.30 * hk * np.exp(-(d / (2.6 * wd)) ** 2))
    rid = np.zeros((h2, w2), F32); tot = 0
    for k, (cell, amp) in enumerate([(60, 1.0), (28, 0.8), (13, 0.55), (6, 0.35), (3, 0.18)]):
        n = _noise((h2, w2), cell, 300 + k); rid += amp * (1 - np.abs(2 * n - 1)) ** 2; tot += amp
    rid /= tot
    l2 = cv2.resize(landf, (w2, h2), interpolation=cv2.INTER_AREA)
    el = (env * (0.45 + 0.85 * rid) + 0.35 * rid ** 1.5) * cv2.GaussianBlur(l2, (0, 0), 1.5)
    el = cv2.GaussianBlur(el, (0, 0), 0.8)
    gy, gx = np.gradient(el * 6.0, 13.0 / 6.0)
    nz = 1.0 / np.sqrt(gx ** 2 + gy ** 2 + 1); nx = -gx * nz; ny = -gy * nz
    alt = math.radians(40); lx, ly, lz = -math.cos(alt) * 0.7071, -math.cos(alt) * 0.7071, math.sin(alt)
    sh = np.clip((nx * lx + ny * ly + nz * lz) / lz, 0.45, 1.35).astype(F32)
    el = cv2.resize(el, (TW, TH), interpolation=cv2.INTER_CUBIC); sh = cv2.resize(sh, (TW, TH), interpolation=cv2.INTER_CUBIC)
    hy = np.empty((TH, TW, 3), F32)
    for c in range(3): hy[..., c] = np.interp(el, HY_E, HY_C[:, c])
    grain = (0.94 + 0.08 * cv2.resize(_noise((TH // 4, TW // 4), 3, 7), (TW, TH)))[..., None]
    img = LAND0 * grain * hy * sh[..., None]
    # mar con ondas junto a la costa
    d = cv2.distanceTransform((land < 128).astype(np.uint8), cv2.DIST_L2, 3)
    rip = np.clip(1 - np.abs(((d - 3) % 10) - 5) / 1.1, 0, 1) * (d > 2) * np.clip(1 - d / 48, 0, 1)
    deep = np.clip(d / 260.0, 0, 1)
    sea = SEA0 * grain * (1 - 0.10 * rip[..., None]) * (1 - 0.12 * np.clip(1 - d / 7, 0, 1))[..., None] * (1 - 0.10 * deep[..., None])
    img = sea * (1 - landf[..., None]) + img * landf[..., None]
    # retícula y contornos
    gm = np.zeros((TH, TW), np.uint8)
    for lo in range(-180, 181, 15): x = int((lo + 180) / 360 * TW); cv2.line(gm, (x, 0), (x, TH), 255, 2)
    for la in range(-75, 76, 15): y = int((90 - la) / 180 * TH); cv2.line(gm, (0, y), (TW, y), 255, 2)
    img = img * (1 - 0.10 * (gm.astype(F32) / 255)[..., None]) + INK * 0.10 * (gm.astype(F32) / 255)[..., None]
    lf = (lines.astype(F32) / 255)[..., None]
    img = img * (1 - 0.50 * lf) + INK * 0.50 * lf
    tex = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    np.savez(CACHE, tex=tex, ids=ids)
    return tex, ids

if os.path.exists(CACHE):
    _z = np.load(CACHE); TEX, IDS = _z['tex'], _z['ids']
else:
    TEX, IDS = _build()
MIPS = [(TEX, IDS)]
for _ in range(4):
    t_, i_ = MIPS[-1]; MIPS.append((cv2.pyrDown(t_), i_[::2, ::2].copy()))

# ------------------------------------------------------------------ cámara
D2R = math.pi / 180
class Globe:
    def __init__(s, lon, lat, R, cx=270.0, cy=400.0): s.lon, s.lat, s.R, s.cx, s.cy = lon, lat, R, cx, cy
    def p(s, lon, lat):
        """(x, y, z) en pantalla; z>0 = cara visible."""
        l = (lon - s.lon) * D2R; f = lat * D2R; f0 = s.lat * D2R
        z = math.sin(f0) * math.sin(f) + math.cos(f0) * math.cos(f) * math.cos(l)
        x = s.R * math.cos(f) * math.sin(l); y = s.R * (math.cos(f0) * math.sin(f) - math.sin(f0) * math.cos(f) * math.cos(l))
        return s.cx + x, s.cy - y, z
    def P(s, a):
        a = np.asarray(a, np.float64); l = (a[:, 0] - s.lon) * D2R; f = a[:, 1] * D2R; f0 = s.lat * D2R
        z = math.sin(f0) * np.sin(f) + math.cos(f0) * np.cos(f) * np.cos(l)
        x = s.R * np.cos(f) * np.sin(l); y = s.R * (math.cos(f0) * np.sin(f) - math.sin(f0) * np.cos(f) * np.cos(l))
        return np.stack([s.cx + x, s.cy - y, z], 1)

_BG = {}
def backdrop():
    if 'bg' not in _BG:
        g = np.clip(YY / H, 0, 1)[..., None]
        _BG['bg'] = (PAPER * (C3(0.80, 0.74, 0.64) * (1 - g) + C3(0.66, 0.60, 0.52) * g)).astype(F32)
    return _BG['bg']

def render(g, tints=None, bg=None):
    """tints: lista de (nombre_país, color, alpha)."""
    x = (XX - g.cx) / g.R; y = -(YY - g.cy) / g.R; rho2 = x * x + y * y
    inside = rho2 < 1.0
    z = np.sqrt(np.clip(1 - rho2, 0, 1)).astype(F32)
    f0 = g.lat * D2R
    lat = np.arcsin(np.clip(z * math.sin(f0) + y * math.cos(f0), -1, 1)) / D2R
    lon = g.lon + np.arctan2(x, z * math.cos(f0) - y * math.sin(f0)) / D2R
    need = g.R * D2R                               # px de pantalla por grado en el centro
    k = 0
    while k < len(MIPS) - 1 and (TW / 360.0) / (2 ** (k + 1)) >= need * 1.05: k += 1
    tex, ids = MIPS[k]; th, tw_ = tex.shape[:2]
    mu = ((lon + 180.0) % 360.0) / 360.0 * tw_; mv = (90.0 - lat) / 180.0 * th
    mu = mu.astype(F32); mv = np.clip(mv, 0, th - 1.001).astype(F32)
    img = cv2.remap(tex, mu, mv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP).astype(F32) / 255
    if tints:
        idm = cv2.remap(ids, mu, mv, cv2.INTER_NEAREST, borderMode=cv2.BORDER_WRAP)
        lum = (img.mean(2) / float(LAND0.mean()))[..., None]
        for (name, col, a) in tints:
            if a <= 0.01: continue
            m = cv2.GaussianBlur((idm == CID[name]).astype(F32), (0, 0), 0.7)
            mm = (m * a)[..., None]; img = img * (1 - mm) + lum * np.asarray(col, F32) * mm
    # sombreado esférico suave
    if g.R < 3000:
        shade = (0.80 + 0.20 * z ** 0.6)[..., None]; img = img * shade
        glow = np.clip(1 - np.sqrt((XX - (g.cx - 0.35 * g.R)) ** 2 + (YY - (g.cy - 0.40 * g.R)) ** 2) / (0.9 * g.R), 0, 1) ** 2
        img = img + 0.06 * glow[..., None]
    if inside.all(): return img
    b = backdrop().copy() if bg is None else bg.copy()
    r = np.sqrt(rho2) * g.R
    sh = np.clip(1 - (r - g.R + 4) / 26.0, 0, 1) * (r > g.R - 4)
    b *= (1 - 0.35 * sh)[..., None]
    halo = np.clip(1 - np.abs(r - g.R - 5) / 6.0, 0, 1)
    b = b * (1 - 0.35 * halo[..., None]) + CREAM * 0.35 * halo[..., None]
    a = np.clip(g.R - r + 0.5, 0, 1)[..., None].astype(F32)
    out = b * (1 - a) + img * a
    edge = np.clip(1 - np.abs(r - g.R) / 1.3, 0, 1)
    over(out, edge, INK, 0.65)
    return out

# ------------------------------------------------------------------ rutas
def densify(pts, step=0.6):
    out = [pts[0]]
    for (a, b) in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for j in range(1, n + 1): out.append((a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n))
    a = np.array(out, np.float64)
    # longitud real (gran círculo) acumulada
    lo, la = a[:, 0] * D2R, a[:, 1] * D2R
    v = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
    d = np.r_[0, np.arccos(np.clip((v[1:] * v[:-1]).sum(1), -1, 1))]
    return a, np.cumsum(d) / max(1e-9, d.sum())

def at(route, k):
    a, c = route; k = min(max(k, 0.0), 1.0); i = int(np.searchsorted(c, k))
    if i <= 0: return tuple(a[0])
    if i >= len(c): return tuple(a[-1])
    u = (k - c[i - 1]) / max(1e-9, c[i] - c[i - 1]); return tuple(a[i - 1] + (a[i] - a[i - 1]) * u)

def draw_route(img, g, route, k0, k1, col, a=1.0, th=3.0, dash=None, phase=0.0):
    """dibuja el tramo [k0,k1] de la ruta; solo la parte visible del globo."""
    if a <= 0.01 or k1 <= k0: return
    pts, c = route
    sel = (c >= k0) & (c <= k1)
    q = list(pts[sel])
    if k0 > 0: q = [np.array(at(route, k0))] + q
    q = q + [np.array(at(route, k1))]
    S = g.P(np.array(q))
    m = np.zeros((H, W), np.uint8)
    seg = []; acc = 0.0
    for i in range(len(S)):
        if S[i, 2] > 0.02:
            seg.append(S[i, :2])
        else:
            if len(seg) > 1: _stroke(m, seg, th, dash, phase)
            seg = []
    if len(seg) > 1: _stroke(m, seg, th, dash, phase)
    mm = cv2.GaussianBlur(m.astype(F32) / 255, (0, 0), 0.6)
    over(img, cv2.GaussianBlur(mm, (0, 0), 2.2), CREAM, 0.55 * a)
    over(img, mm, col, a)

def _stroke(m, seg, th, dash, phase):
    q = np.array(seg)
    if dash is None:
        cv2.polylines(m, [np.round(q * 16).astype(np.int32)], False, 255, max(1, int(round(th))), cv2.LINE_AA, shift=4); return
    L_ = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
    on, off = dash
    d0 = -phase % (on + off)
    while d0 < L_[-1]:
        d1 = min(L_[-1], d0 + on)
        if d1 > 0:
            xa = np.interp([max(0, d0), d1], L_, q[:, 0]); ya = np.interp([max(0, d0), d1], L_, q[:, 1])
            cv2.line(m, (int(xa[0] * 16), int(ya[0] * 16)), (int(xa[1] * 16), int(ya[1] * 16)), 255, max(1, int(round(th))), cv2.LINE_AA, shift=4)
        d0 += on + off

def heading(g, route, k, dk=0.004):
    x0, y0, _ = g.p(*at(route, max(0, k - dk))); x1, y1, _ = g.p(*at(route, min(1, k + dk)))
    return math.atan2(y1 - y0, x1 - x0), x1 - x0

# lugares (lon, lat)
CORUNA = (-8.40, 43.37); TENERIFE = (-16.25, 28.47); SANJUAN = (-66.11, 18.47); GUAIRA = (-66.93, 10.60)
HABANA = (-82.36, 23.13); VERACRUZ = (-96.13, 19.20); MEXICO = (-99.13, 19.43); ACAPULCO = (-99.88, 16.85)
MANILA = (120.98, 14.60); MACAO = (113.55, 22.19); CANTON = (113.26, 23.13); STHELENA = (-5.72, -15.95); LISBOA = (-9.14, 38.72); MADRID = (-3.70, 40.42)
BOGOTA = (-74.07, 4.71); QUITO = (-78.50, -0.22); LIMA = (-77.04, -12.05); CARTAGENA = (-75.51, 10.39)

# longitudes "desenrolladas" hacia el oeste para que la vuelta al mundo sea continua
def W_(p, k=1): return (p[0] - 360.0 * k, p[1])
R_ATL = densify([CORUNA, (-11.5, 39.0), (-14.5, 31.0), TENERIFE, (-22.0, 25.0), (-35.0, 21.5), (-50.0, 19.5), (-62.0, 18.8), SANJUAN, (-66.4, 15.0), GUAIRA])
R_SALV = densify([GUAIRA, (-70.0, 12.4), (-74.5, 11.2), CARTAGENA, (-74.8, 8.0), BOGOTA, (-76.6, 2.4), QUITO, (-79.0, -4.0), (-78.6, -8.0), LIMA, (-72.0, -15.5), (-66.2, -17.4)])
R_BALM = densify([GUAIRA, (-70.0, 13.0), (-75.0, 16.5), (-79.5, 20.6), (-81.0, 22.2), HABANA, (-85.5, 22.5), (-89.0, 22.0), (-93.0, 20.3), VERACRUZ, (-97.6, 19.4), MEXICO])
R_PAC = densify([MEXICO, (-99.6, 18.0), ACAPULCO, (-110.0, 14.5), (-130.0, 13.5), (-155.0, 13.2), (-180.0, 13.2), (-200.0, 13.4), (-215.5, 13.3), (-232.0, 12.9), (-235.8, 12.6), (-237.5, 13.5), W_(MANILA)])
R_CHN = densify([W_(MANILA), (-240.0, 16.0), (-243.5, 19.5), W_(MACAO), W_(CANTON)])
R_RET = densify([W_(MACAO), (-249.0, 15.0), (-251.5, 6.0), (-253.0, 0.0), (-254.5, -6.5), (-265.0, -14.0), (-290.0, -27.0), (-320.0, -36.5), (-341.5, -35.0), (-350.0, -28.0),
                 W_(STHELENA), (-373.0, -2.0), (-381.0, 15.0), (-382.0, 30.0), (-372.0, 37.5), W_(LISBOA)], 0.8)
