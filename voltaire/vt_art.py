"""Objetos ilustrados del Short de Voltaire (a resolución nativa): bonos, billetes, monedas, bombo de lotería,
balanza, gráfica de valor, socios en silueta, pluma y fondo con cifras flotantes."""
from vt_lib import *

# ------------------------------------------------------------------ fondo con cifras y símbolos flotantes
_rs = np.random.RandomState(12)
GLYPHS = ['1.000', '÷', '<', '=', '1', '100', '+', '×', '0', '7', '9', '3', '½', '%']
FLOAT = [(GLYPHS[_rs.randint(len(GLYPHS))], _rs.rand() * W, _rs.rand() * H, 8 + _rs.rand() * 14, 40 + int(_rs.rand() * 70), _rs.rand() * 6.28) for _ in range(26)]
def math_bg(t, a=1.0):
    img = board()
    for (g, x, y, sp, sz, ph) in FLOAT:
        yy = (y - t * sp) % (H + 200) - 100; xx = x + 14 * math.sin(t * 0.3 + ph)
        text(img, g, xx, yy, sz, GOLD, 0.07 * a, 'playr')
    return img

# ------------------------------------------------------------------ papeles
def _deckle(w, h, n=16, amp=3.0, seed=0):
    rs = np.random.RandomState(seed); pts = []
    for i in range(n + 1): pts.append((-w / 2 + w * i / n, -h / 2 + amp * rs.rand()))
    for i in range(n + 1): pts.append((w / 2 - amp * rs.rand(), -h / 2 + h * i / n))
    for i in range(n + 1): pts.append((w / 2 - w * i / n, h / 2 - amp * rs.rand()))
    for i in range(n + 1): pts.append((-w / 2 + amp * rs.rand(), h / 2 - h * i / n))
    return pts

def _paper(img, cx, cy, w, h, seed, col=PARCH):
    P = [(cx + x, cy + y) for x, y in _deckle(w, h, 18, 4.0, seed)]
    m = mpoly([P]); shadow_m(img, m, 0.55, (8, 12), 12)
    tex = noise(seed + 40, (3, 9, 30)); colm = col * (0.86 + 0.20 * tex[..., None])
    mm = m[..., None]; img[:] = img * (1 - mm) + colm * mm

def bond_sprite(value, w=420, h=300):
    def draw(img, cx, cy):
        _paper(img, cx, cy, w, h, 3)
        for d, th, k in ((14, 3, 0.8), (22, 1, 0.6)):
            over(img, mline([[(cx - w / 2 + d, cy - h / 2 + d), (cx + w / 2 - d, cy - h / 2 + d), (cx + w / 2 - d, cy + h / 2 - d), (cx - w / 2 + d, cy + h / 2 - d), (cx - w / 2 + d, cy - h / 2 + d)]], th), SEPIA, k)
        text(img, 'BONO', cx, cy - h * 0.30, int(h * 0.11), SEPIA, 1.0, 'cas', track=6)
        text(img, 'CIUDAD DE PARÍS', cx, cy - h * 0.17, int(h * 0.075), SEPIA, 0.9, 'casr', track=3)
        text(img, value, cx, cy + h * 0.06, int(h * 0.19), INK, 1.0, 'play')
        over(img, mline([[(cx - w * 0.28, cy + h * 0.22), (cx + w * 0.28, cy + h * 0.22)]], 2), SEPIA, 0.6)
        over(img, mcirc([(cx + w * 0.33, cy + h * 0.30, h * 0.07)]), WAX, 0.9)
    return sprite(('bond', value, w, h), draw)

def ticket_sprite(label, w=330, h=190, small=False):
    def draw(img, cx, cy):
        pts = []
        n = 10 if small else 16
        for i in range(n + 1): pts.append((cx - w / 2 + w * i / n, cy - h / 2 + (2.5 if i % 2 else 0)))
        for i in range(n + 1): pts.append((cx + w / 2 - (2.5 if i % 2 else 0), cy - h / 2 + h * i / n))
        for i in range(n + 1): pts.append((cx + w / 2 - w * i / n, cy + h / 2 - (2.5 if i % 2 else 0)))
        for i in range(n + 1): pts.append((cx - w / 2 + (2.5 if i % 2 else 0), cy + h / 2 - h * i / n))
        m = mpoly([pts]); shadow_m(img, m, 0.5, (4, 7) if small else (7, 11), 4 if small else 10)
        over(img, m, C3(0.96, 0.92, 0.80))
        d = max(4, int(h * 0.07))
        over(img, mline([[(cx - w / 2 + d, cy - h / 2 + d), (cx + w / 2 - d, cy - h / 2 + d), (cx + w / 2 - d, cy + h / 2 - d), (cx - w / 2 + d, cy + h / 2 - d), (cx - w / 2 + d, cy - h / 2 + d)]], 2 if not small else 1), VERM, 0.8)
        if not small:
            text(img, 'BILLETE', cx, cy - h * 0.27, int(h * 0.12), VERM, 1.0, 'cas', track=5)
            text(img, label, cx, cy + h * 0.08, int(h * 0.27), INK, 1.0, 'play')
        else:
            text(img, label, cx, cy, int(h * 0.42), INK, 1.0, 'play')
    return sprite(('ticket', label, w, h, small), draw)

def coin_sprite(r=34, tilt=0.6):
    def draw(img, cx, cy): coin(img, cx, cy, r, 1.0, tilt)
    return sprite(('coin', r, tilt), draw)

# ------------------------------------------------------------------ bombo de la lotería
def drum(img, cx, cy, R, t, a=1.0, spin=1.0):
    if a <= 0.003: return
    leg = mpoly([[(cx - R * 0.9, cy + R * 1.45), (cx - R * 0.75, cy + R * 1.45), (cx - 6, cy), (cx + 6, cy), (cx + R * 0.75, cy + R * 1.45), (cx + R * 0.9, cy + R * 1.45), (cx + 10, cy - 10), (cx - 10, cy - 10)]])
    shadow_m(img, leg, 0.4 * a, (8, 12), 10); over(img, leg, C3(0.32, 0.20, 0.11), a)
    ang = t * 2.2 * spin
    m = mcirc([(cx, cy, R)]); shadow_m(img, m, 0.5 * a, (10, 16), 16); over(img, m, C3(0.20, 0.13, 0.08), a)
    rs = np.random.RandomState(4)
    for j in range(16):
        r = R * (0.25 + 0.6 * rs.rand()); th = ang * (0.6 + 0.4 * rs.rand()) + rs.rand() * 6.28
        x, y = cx + r * math.cos(th), cy + r * math.sin(th) + R * 0.15
        blit(img, ticket_sprite('', 70, 40, True), x, y, a, 1.0, math.degrees(th) * 0.7)
    over(img, mcirc([(cx, cy, R * 0.98)]) - mcirc([(cx, cy, R * 0.90)]), GOLD, a)
    sp = []
    for k in range(8):
        th = ang + k * math.pi / 4; sp.append([(cx + R * 0.12 * math.cos(th), cy + R * 0.12 * math.sin(th)), (cx + R * 0.93 * math.cos(th), cy + R * 0.93 * math.sin(th))])
    over(img, mline(sp, 5), GOLD * 0.9, a); over(img, mcirc([(cx, cy, R * 0.13)]), GOLDL, a)
    over(img, mring([(cx, cy, R * 0.6)], 3), GOLD * 0.7, a)
    glow(img, cx - R * 0.4, cy - R * 0.45, R * 0.7, C3(1, 0.9, 0.6), 0.10 * a, 2.0)
    hx, hy = cx + R * 1.05 * math.cos(ang * 0.5), cy + R * 1.05 * math.sin(ang * 0.5)
    over(img, mline([[(cx, cy), (hx, hy)]], 8), C3(0.32, 0.20, 0.11), a); over(img, mcirc([(hx, hy, 14)]), GOLD, a)

# ------------------------------------------------------------------ balanza
def balance(img, cx, cy, L, tilt, a=1.0, left=None, right=None, labels=('', ''), lab_a=1.0, base=True):
    """balanza con brazo de semilongitud L; tilt>0 baja el platillo derecho. left/right(img, x, y): contenido de cada platillo."""
    if a <= 0.003: return
    if base:
        post = mpoly([[(cx - 9, cy), (cx + 9, cy), (cx + 12, cy + L * 1.55), (cx - 12, cy + L * 1.55)]]); over(img, post, GOLD * 0.75, a)
        foot = mpoly([[(cx - L * 0.45, cy + L * 1.62), (cx + L * 0.45, cy + L * 1.62), (cx + L * 0.2, cy + L * 1.50), (cx - L * 0.2, cy + L * 1.50)]])
        shadow_m(img, foot, 0.4 * a, (8, 10), 10); over(img, foot, GOLD * 0.8, a)
    P = rot([(cx - L, cy), (cx + L, cy)], tilt, (cx, cy))
    over(img, mline([P], 12), GOLD, a); over(img, mcirc([(cx, cy, 20)]), GOLDL, a)
    for k, (bx, by) in enumerate(P):
        py = by + L * 0.62
        over(img, mline([[(bx, by), (bx - L * 0.36, py)], [(bx, by), (bx + L * 0.36, py)]], 2), GOLD, 0.9 * a)
        pan = np.zeros((H, W), np.uint8); cv2.ellipse(pan, (int(bx * 16), int(py * 16)), (int(L * 0.42 * 16), int(L * 0.08 * 16)), 0, 0, 180, 255, -1, cv2.LINE_AA, shift=4)
        over(img, pan.astype(F32) / 255, GOLD * 0.75, a)
        fn = left if k == 0 else right
        if fn: fn(img, bx, py)
        if labels[k]:
            lw = text_w(labels[k], int(L * 0.13), 'casi') / 2 + 40
            text(img, labels[k], min(W - lw, max(lw, bx)), py + L * 0.22, int(L * 0.13), IVORY, a * lab_a, 'casi')
    return P

# ------------------------------------------------------------------ gráfica de valor que cae
def value_chart(img, x0, y0, x1, y1, k, a=1.0):
    if a <= 0.003: return
    over(img, mline([[(x0, y0), (x0, y1), (x1, y1)]], 4), IVORY, 0.8 * a)
    text(img, 'valor', x0 + 20, y0 - 30, 40, IVORY, 0.85 * a, 'casi', anchor='l')
    n = 60; pts = []
    for i in range(n + 1):
        u = i / n; v = 0.12 + 0.10 * math.sin(u * 9) * (1 - u) + 0.72 * ease(prog(u, 0.25, 0.9))
        pts.append((x0 + 10 + (x1 - x0 - 30) * u, y0 + (y1 - y0) * v))
    m = int(n * k)
    if m >= 1:
        over(img, mline([pts[:m + 1]], 7), VERM, a)
        ex, ey = pts[m]; glow(img, ex, ey, 40, VERM, 0.6 * a, 2.0)
        if k > 0.85:
            over(img, mpoly([[(ex - 18, ey - 10), (ex + 18, ey - 10), (ex, ey + 18)]]), VERM, a * ease(prog(k, 0.85, 1.0)))

# ------------------------------------------------------------------ socios en silueta (tricornio y casaca)
def socio_sprite(v, h=230):
    def draw(img, cx, cy):
        u = h / 10.0; rs = np.random.RandomState(v); y = cy + h / 2
        body = [(cx - 1.9 * u, y - 4.2 * u), (cx - 1.4 * u, y - 7.3 * u), (cx + 1.4 * u, y - 7.3 * u), (cx + 1.9 * u, y - 4.2 * u), (cx + 2.3 * u, y - 3.0 * u), (cx - 2.3 * u, y - 3.0 * u)]
        legs = [[(cx - 0.8 * u, y - 3.1 * u), (cx - 0.9 * u, y)], [(cx + 0.8 * u, y - 3.1 * u), (cx + 0.9 * u, y)]]
        col = C3(0.13, 0.12, 0.13) * (0.9 + 0.2 * rs.rand())
        m = mpoly([body]) ; m = np.maximum(m, mline(legs, 0.8 * u)); m = np.maximum(m, mcirc([(cx, y - 8.3 * u, 1.05 * u)]))
        hat = [(cx - 1.9 * u, y - 8.9 * u), (cx + 1.9 * u, y - 8.9 * u), (cx + 1.3 * u, y - 9.4 * u), (cx, y - 10.0 * u), (cx - 1.3 * u, y - 9.4 * u)]
        m = np.maximum(m, mpoly([hat])); m = np.maximum(m, mcirc([(cx + (1 if v % 2 else -1) * 0.9 * u, y - 7.9 * u, 0.55 * u)]))
        shadow_m(img, m, 0.45, (6, 10), 10)
        rim = np.clip(m - cv2.warpAffine(m, np.float32([[1, 0, 3], [0, 1, 3]]), (W, H)), 0, 1)
        over(img, m, col); over(img, rim, GOLD, 0.9)
    return sprite(('socio', v, h), draw)

# ------------------------------------------------------------------ pluma de ave
def quill(img, x, y, a=1.0, t=0.0, L=230):
    if a <= 0.003: return
    sw = 4 * math.sin(t * 9)
    ang = math.radians(-58 + sw * 0.4); ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v): return (x + u * ca - v * sa, y + u * sa + v * ca)
    vane = [P(L * 0.22, 0)] + [P(L * (0.22 + 0.78 * k), L * 0.13 * math.sin(math.pi * k) ** 0.7) for k in np.linspace(0, 1, 14)] + \
           [P(L * (0.22 + 0.78 * k), -L * 0.07 * math.sin(math.pi * k) ** 0.8) for k in np.linspace(1, 0, 14)]
    m = mpoly([vane]); shadow_m(img, m, 0.4 * a, (10, 14), 10); over(img, m, C3(0.93, 0.90, 0.84), a)
    bar = mline([[P(L * (0.3 + 0.07 * j), 0), P(L * (0.34 + 0.07 * j), L * 0.10)] for j in range(9)], 1); over(img, bar, C3(0.70, 0.66, 0.60), 0.6 * a)
    over(img, mline([[P(0, 0), P(L, 0)]], 3), GOLD * 0.8, a)
    over(img, mpoly([[P(0, 0), P(L * 0.12, -4), P(L * 0.12, 4)]]), INK, a)

def scribbles(img, x0, y0, w, rows, k, a=1.0, col=SEPIA, seed=3, lh=46):
    """renglones de escritura a mano que avanzan con k∈[0,1]; devuelve la punta (para la pluma)."""
    rs = np.random.RandomState(seed); lines = []; tip = None; tot = rows; done = k * tot
    for r in range(rows):
        if done <= r: break
        frac = min(1.0, done - r); wr = w * (0.75 + 0.25 * rs.rand()); xs = np.arange(0, wr * frac, 2.0)
        if len(xs) < 2: continue
        ph = rs.rand() * 6
        ys = y0 + r * lh + 5 * np.sin(xs * 0.35 + ph) * (0.6 + 0.4 * np.sin(xs * 0.07)) + 2.5 * np.sin(xs * 1.3)
        lines.append(list(zip(x0 + xs, ys))); tip = (x0 + xs[-1], ys[-1])
    if lines: over(img, mline(lines, 3), col, 0.85 * a)
    return tip
