"""Mapa en relieve con fronteras reales (Natural Earth 10m), adaptado de ll_map a toda la Península (Short de Balmis).
Proyección equirectangular local (lat0 = 40.2) con cámara (lon, lat, s = px por km)."""
import os, json, math
import numpy as np, cv2
from cv_lib import W, H, F32, C3, INK, RED, CREAM, XX, YY, over, mcirc, glow_roi, _f, lerp, ease, prog

LAT0 = 40.2
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 110.57
LLV_C = (1.9680, 42.4625)          # centro del contorno de Llívia
PUIG = (1.9275, 42.4315)
PERP = (2.8948, 42.6986)

# ------------------------------------------------------------------ datos
_G = json.load(open('/home/claude/serie/geo10/ne10.geojson'))
RINGS = []          # (name, arr lon/lat, bbox)
for f in _G['features']:
    n = f['properties']['NAME']; geom = f['geometry']
    if geom is None: continue
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for p in polys:
        a = np.asarray(p[0], np.float64)
        bb = (a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max())
        if bb[1] < -20 or bb[0] > 30 or bb[3] < 25 or bb[2] > 64: continue
        RINGS.append((n, a, bb))
del _G
LLV_RING = [r for (n, r, b) in RINGS if n == 'Spain' and len(r) == 12][0]
SPAIN_MAIN = max([r for (n, r, b) in RINGS if n == 'Spain'], key=len)
FR_MAIN = max([r for (n, r, b) in RINGS if n == 'France'], key=len)

# frontera hispano-francesa (vértices compartidos)
_fs = set(map(tuple, np.round(FR_MAIN, 6)))
_sh = np.array([tuple(np.round(p, 6)) in _fs for p in SPAIN_MAIN])
_runs = []; cur = []
for p, s_ in zip(SPAIN_MAIN, _sh):
    if s_: cur.append(p)
    elif cur: _runs.append(np.array(cur)); cur = []
if cur: _runs.append(np.array(cur))
BORDER_ES_FR = [r for r in _runs if len(r) > 3]

# frontera anterior a 1659 (aprox.: Corbières, al norte del Rosellón; el Fenolledés ya era francés)
OLD_B = [(1.735, 42.575), (1.80, 42.615), (1.88, 42.665), (1.98, 42.700), (2.08, 42.690), (2.18, 42.705), (2.30, 42.715), (2.42, 42.735),
         (2.55, 42.760), (2.66, 42.800), (2.78, 42.835), (2.90, 42.865), (3.00, 42.880), (3.10, 42.895)]

# ------------------------------------------------------------------ cámara
class Geo:
    def __init__(s, lon, lat, sc, cx=270.0, cy=400.0): s.lon, s.lat, s.s, s.cx, s.cy = lon, lat, sc, cx, cy
    def p(s, lon, lat): return (s.cx + (lon - s.lon) * KX * s.s, s.cy + (s.lat - lat) * KY * s.s)
    def P(s, a):
        a = np.asarray(a, np.float64)
        return np.stack([s.cx + (a[:, 0] - s.lon) * KX * s.s, s.cy + (s.lat - a[:, 1]) * KY * s.s], 1)
    def lat_at_y(s, y): return s.lat - (y - s.cy) / (KY * s.s)
    def visible(s, bb, pad=60):
        x0, y0 = s.p(bb[0], bb[3]); x1, y1 = s.p(bb[1], bb[2])
        return not (x1 < -pad or x0 > W + pad or y1 < -pad or y0 > H + pad)

def _fill(m, q):
    cv2.fillPoly(m, [np.round(q * 16).astype(np.int64).astype(np.int32)], 255, cv2.LINE_AA, shift=4)

def _clipq(q):
    return np.clip(q, -20000, 20000)

def mask_of(geo, names=None, rings=None):
    m = np.zeros((H, W), np.uint8)
    src = rings if rings is not None else [r for (n, r, b) in RINGS if (names is None or n in names) and geo.visible(b)]
    for r in src: _fill(m, _clipq(geo.P(r)))
    return m.astype(F32) / 255

def lines_of(geo, rings, th=1.0, closed=True):
    m = np.zeros((H, W), np.uint8)
    for r in rings:
        q = _clipq(geo.P(r))
        cv2.polylines(m, [np.round(q * 16).astype(np.int32)], closed, 255, max(1, int(round(th))), cv2.LINE_AA, shift=4)
    return m.astype(F32) / 255

# ------------------------------------------------------------------ relieve (procedural, sobre la geografía real)
A0, A1, B0, B1 = -10.0, 4.6, 35.6, 44.2; RES = 1.0
TW_ = int((A1 - A0) * KX / RES); TH_ = int((B1 - B0) * KY / RES)
def _tex(lon, lat): return ((lon - A0) * KX / RES, (B1 - lat) * KY / RES)
RIDGES = [  # (polilínea lon/lat, altura km, semiancho km)
    ([(-5.5, 41.5), (-4.2, 40.6), (-3.5, 40.0), (-3.0, 39.0)], 0.75, 150.0),
    ([(-1.8, 43.2), (-0.5, 42.85), (0.7, 42.7), (1.7, 42.55), (2.9, 42.45)], 2.6, 20.0),
    ([(-7.2, 42.9), (-6.0, 43.0), (-4.8, 43.1), (-3.5, 43.05), (-2.5, 43.0)], 2.0, 18.0),
    ([(-8.0, 42.4), (-7.2, 42.2)], 1.1, 35.0),
    ([(-3.0, 42.0), (-2.2, 41.5), (-1.6, 40.9), (-1.0, 40.3), (-0.7, 39.9)], 1.8, 30.0),
    ([(-7.0, 40.2), (-5.8, 40.3), (-4.5, 40.5), (-3.6, 40.9), (-2.8, 41.2)], 2.2, 18.0),
    ([(-5.2, 39.5), (-4.0, 39.4)], 1.1, 18.0),
    ([(-7.0, 38.0), (-5.5, 38.2), (-4.0, 38.4), (-2.8, 38.4)], 1.0, 20.0),
    ([(-5.4, 36.7), (-4.5, 36.9), (-3.3, 37.05), (-2.5, 37.2), (-1.5, 37.8), (-0.5, 38.5)], 2.6, 22.0),
    ([(1.0, 41.3), (2.3, 41.9)], 1.0, 12.0),
    ([(-7.6, 40.3)], 1.6, 20.0),
]
VALLEYS = [  # (polilínea, semiancho km, nivel km)
    ([(-2.5, 42.5), (-1.5, 41.9), (-0.6, 41.5), (0.5, 41.0), (0.8, 40.7)], 30.0, 0.25),
    ([(-3.5, 37.9), (-4.8, 37.8), (-5.9, 37.4), (-6.3, 36.9)], 35.0, 0.08),
    ([(-8.0, 39.5), (-9.0, 38.8)], 45.0, 0.08),
]

def _noise(shape, cell, seed):
    rs = np.random.RandomState(seed); gh = max(2, int(shape[0] / cell) + 2); gw = max(2, int(shape[1] / cell) + 2)
    return cv2.resize(rs.rand(gh, gw).astype(F32), (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)

def _dist_to(pl):
    m = np.full((TH_, TW_), 255, np.uint8)
    q = np.array([_tex(*p) for p in pl])
    cv2.polylines(m, [np.round(q * 16).astype(np.int32)], False, 0, 1, cv2.LINE_8, shift=4)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5) * RES

def _dist_pt(p):
    m = np.full((TH_, TW_), 255, np.uint8); q = _tex(*p); cv2.circle(m, (int(q[0]), int(q[1])), 1, 0, -1)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5) * RES

def _build():
    shape = (TH_, TW_); env = np.zeros(shape, F32)
    for pl, h, w in RIDGES:
        d = _dist_to(pl) if len(pl) > 1 else _dist_pt(pl[0]); env = np.maximum(env, h * np.exp(-(d / w) ** 2) + 0.35 * h * np.exp(-(d / (2.5 * w)) ** 2))
    rid = np.zeros(shape, F32); tot = 0
    for k, (cell_km, amp) in enumerate([(30, 1.0), (14, 0.8), (7, 0.55), (3.5, 0.35), (1.8, 0.18), (0.9, 0.08)]):
        n = _noise(shape, cell_km / RES, 100 + k); rid += amp * (1 - np.abs(2 * n - 1)) ** 2; tot += amp
    rid /= tot
    el = env * (0.50 + 0.80 * rid)
    for pl, w, lvl in VALLEYS:
        d = _dist_to(pl); b = np.exp(-(d / w) ** 2)
        el = el * (1 - b) + np.minimum(el, lvl + 0.10 * rid) * b
    # bordes suaves de la textura
    wx = np.clip(np.minimum(np.arange(TW_), TW_ - 1 - np.arange(TW_)) / 40.0, 0, 1); wy = np.clip(np.minimum(np.arange(TH_), TH_ - 1 - np.arange(TH_)) / 40.0, 0, 1)
    el *= (wy[:, None] * wx[None, :]).astype(F32)
    el = cv2.GaussianBlur(el, (0, 0), 0.8)
    gy, gx = np.gradient(el * 2.6, RES)
    nz = 1.0 / np.sqrt(gx ** 2 + gy ** 2 + 1); nx = -gx * nz; ny = -gy * nz
    alt = math.radians(42); lx, ly, lz = -math.cos(alt) * 0.7071, -math.cos(alt) * 0.7071, math.sin(alt)
    sh = (nx * lx + ny * ly + nz * lz) / lz
    return el.astype(F32), np.clip(sh, 0.40, 1.40).astype(F32)

_RP = '/home/claude/serie/balmis/relief.npz'
if os.path.exists(_RP):
    _z = np.load(_RP); EL, SH = _z['el'], _z['sh']
else:
    EL, SH = _build(); np.savez(_RP, el=EL, sh=SH)
MIPS = [(EL, SH)]
for _ in range(5):
    e, s_ = MIPS[-1]; MIPS.append((cv2.pyrDown(e), cv2.pyrDown(s_)))

def relief_at(geo):
    sc = RES * geo.s; k = 0
    while k < len(MIPS) - 1 and sc * (2 ** k) < 0.6: k += 1
    e, s_ = MIPS[k]; f = 2 ** k
    M = np.float32([[sc * f, 0, geo.cx + (A0 - geo.lon) * KX * geo.s], [0, sc * f, geo.cy + (geo.lat - B1) * KY * geo.s]])
    fl = cv2.INTER_CUBIC if sc * f > 1.5 else cv2.INTER_LINEAR
    el = cv2.warpAffine(e, M, (W, H), flags=fl, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0)
    sh = cv2.warpAffine(s_, M, (W, H), flags=fl, borderMode=cv2.BORDER_CONSTANT, borderValue=1.0)
    return el, sh

HY_E = [0.0, 0.5, 1.1, 1.8, 2.45, 2.9]
HY_C = np.array([[1.00, 1.00, 1.00], [0.92, 0.97, 0.84], [0.86, 0.90, 0.76], [0.84, 0.78, 0.68], [0.93, 0.92, 0.91], [1.03, 1.04, 1.07]], F32)
def hyps(el):
    out = np.empty(el.shape + (3,), F32)
    for c in range(3): out[..., c] = np.interp(el, HY_E, HY_C[:, c])
    return out

LAND0 = C3(0.90, 0.86, 0.74); SEA0 = C3(0.58, 0.72, 0.79)
TINT_ES = C3(0.97, 0.62, 0.48); TINT_FR = C3(0.52, 0.66, 0.92)
BLUE_D = C3(0.15, 0.32, 0.62)
GRAIN = (0.93 + 0.10 * _f)[..., None].astype(F32)

def _tint(img, m, col, a):
    if a <= 0: return
    lum = (img.mean(2) / float(LAND0.mean()))[..., None]
    mm = (m * a)[..., None]; img[:] = img * (1 - mm) + (lum * col) * mm

def geomap(geo, spain=0.35, france=0.30, ceded=None, llv=1.0, relief=1.0, border_hl=0.0, old_b=0.0, extra_es=None):
    """ceded: None o k∈[0,1] (barrido norte→sur que pasa el Rosellón/Cerdaña a Francia)."""
    land = mask_of(geo)
    el, sh = relief_at(geo)
    sh = 1 + (sh - 1) * relief
    img = LAND0 * GRAIN * hyps(el * relief) * sh[..., None]
    # mar
    if land.min() < 0.99:
        sea = np.broadcast_to(SEA0, (H, W, 3)) * GRAIN
        d = cv2.distanceTransform((land < 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        rip = np.clip(1 - np.abs(((d - 3) % 11) - 5.5) / 1.2, 0, 1) * (d > 2) * np.clip(1 - d / 60, 0, 1)
        sea = sea * (1 - 0.10 * rip[..., None]) + 0.0
        sea = sea * (1 - 0.12 * np.clip(1 - d / 8, 0, 1))[..., None]
        img = sea * (1 - land[..., None]) + img * land[..., None]
    es = mask_of(geo, ('Spain',)); fr = mask_of(geo, ('France',))
    fr = np.clip(fr - es, 0, 1)
    if ceded is not None:
        cm = np.zeros((H, W), np.uint8)
        poly = OLD_B + [(3.6, 42.9), (3.6, 41.9), (1.735, 41.9)]
        _fill(cm, _clipq(geo.P(poly))); cm = cm.astype(F32) / 255 * fr
        y_front = geo.p(0, lerp(42.98, 42.30, ceded))[1]
        sw = np.clip((y_front - YY) / 5.0, 0, 1)
        es = np.clip(es + cm * (1 - sw), 0, 1); fr = np.clip(fr - cm * (1 - sw), 0, 1)
    if extra_es is not None: es = np.clip(es + extra_es, 0, 1); fr = np.clip(fr - extra_es, 0, 1)
    _tint(img, es, TINT_ES, spain); _tint(img, fr, TINT_FR, france)
    # contornos de países
    vis = [r for (n, r, b) in RINGS if geo.visible(b)]
    th = 1.0 if geo.s < 3 else (1.6 if geo.s < 20 else 2.2)
    over(img, lines_of(geo, vis, th), INK, 0.45)
    if border_hl > 0: over(img, lines_of(geo, BORDER_ES_FR, max(2.0, th * 1.6), False), RED * 0.75, border_hl)
    if old_b > 0:
        m = np.zeros((H, W), np.uint8); q = geo.P(OLD_B)
        L_ = np.cumsum(np.r_[0, np.hypot(*np.diff(q, axis=0).T)])
        for d0 in np.arange(0, L_[-1], 14):
            d1 = min(L_[-1], d0 + 8); a_ = np.interp([d0, d1], L_, q[:, 0]); b_ = np.interp([d0, d1], L_, q[:, 1])
            cv2.line(m, (int(a_[0] * 16), int(b_[0] * 16)), (int(a_[1] * 16), int(b_[1] * 16)), 255, max(2, int(th * 1.6)), cv2.LINE_AA, shift=4)
        over(img, m.astype(F32) / 255, RED * 0.75, old_b)
    if llv > 0:
        lm = mask_of(geo, rings=[LLV_RING])
        _tint(img, lm, C3(0.95, 0.50, 0.40), 0.75 * llv)
        lo = lines_of(geo, [LLV_RING], max(1.5, min(4.0, geo.s / 12)))
        over(img, lo, RED * 0.85, llv)
    return img

def dot(img, geo, lon, lat, col=INK, r=5, a=1.0):
    x, y = geo.p(lon, lat)
    over(img, mcirc([(x, y, r + 2)], 0.6), CREAM, a); over(img, mcirc([(x, y, r)], 0.6), col, a)
    return x, y

# ------------------------------------------------------------------ 33 pueblos de la Cerdaña francesa
def _km(a): return np.stack([(np.asarray(a)[:, 0] - LLV_C[0]) * KX, (LLV_C[1] - np.asarray(a)[:, 1]) * KY], 1).astype(np.float32)
_FK = _km(FR_MAIN).reshape(-1, 1, 2); _LK = _km(LLV_RING).reshape(-1, 1, 2)
_rs = np.random.RandomState(21); VILL = []
while len(VILL) < 33:
    lon = 1.80 + 0.36 * _rs.rand(); lat = 42.385 + 0.17 * _rs.rand()
    p = _km(np.array([[lon, lat]]))[0]; p = (float(p[0]), float(p[1]))
    if cv2.pointPolygonTest(_FK, p, True) < 0.6: continue
    if cv2.pointPolygonTest(_LK, p, True) > -0.9: continue
    if any(math.hypot((lon - a) * KX, (lat - b) * KY) < 2.3 for a, b in VILL): continue
    VILL.append((lon, lat))
VILL.sort(key=lambda q: (q[0] - LLV_C[0]) ** 2 + (q[1] - LLV_C[1]) ** 2)

def villages(img, geo, t_flips, t=0.0, a=1.0):
    """t_flips[j]: instante en que el pueblo j pasa a Francia (azul)."""
    r = max(2.6, min(6.0, 2.2 + geo.s * 0.22))
    reds, blues = [], []
    for j, (lon, lat) in enumerate(VILL):
        x, y = geo.p(lon, lat); rr = r
        if t_flips[j] <= t < t_flips[j] + 0.25: rr = r * (1 + 0.8 * math.sin(math.pi * (t - t_flips[j]) / 0.25))
        (blues if t >= t_flips[j] else reds).append((x, y, rr))
    allp = reds + blues
    if not allp: return
    over(img, mcirc([(x, y, rr + 1.6) for x, y, rr in allp], 0.6), CREAM, a)
    if reds: over(img, mcirc(reds, 0.6), RED, a)
    if blues: over(img, mcirc(blues, 0.6), BLUE_D, a)

# carretera Puigcerdà → Llívia (cruza territorio francés)
ROAD = [(1.9286, 42.4325), (1.9340, 42.4370), (1.9400, 42.4412), (1.9470, 42.4455), (1.9545, 42.4495), (1.9620, 42.4545), (1.9690, 42.4590), (1.9760, 42.4620)]
