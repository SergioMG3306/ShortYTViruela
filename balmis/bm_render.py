import sys, subprocess, math
import os; os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
sys.path.insert(0, '/home/claude/serie/balmis'); sys.path.insert(0, '/home/claude/serie/vascos'); sys.path.insert(0, '/home/claude/serie/cervantes')
from cv_lib import *
import cv_lib as L
import bm_scenes as S

TRANS = {1: 'dis', 2: 'wipe', 3: 'wipe', 4: 'dis', 6: 'wipe', 7: 'dis'}
TW = 0.7
TWS = {}
_n = fractal(41, (40, 90, 200)); NOISE = ((_n - _n.min()) / (_n.max() - _n.min())).astype(F32)
_rg = np.random.RandomState(77); GR = [(_rg.randn(FH, FW).astype(F32) * 0.017)[..., None] for _ in range(3)]
_mt = np.random.RandomState(31); MX = _mt.rand(46) * W; MY = _mt.rand(46) * H; MS = 5 + _mt.rand(46) * 9; MP = _mt.rand(46) * 6.28

def scene_at(t): return max(j for j in range(len(S.SC)) if t >= B[j])
def grab():
    o = (list(L.OV), list(L.RC), list(L.SP), list(L.PH)); L.OV.clear(); L.RC.clear(); L.SP.clear(); L.PH.clear(); return o
def scaled(lists, k):
    ovl, rcl, spl, phl = lists
    return ([o[:5] + (o[5] * k,) + o[6:] for o in ovl], [r[:5] + (r[5] * k,) + r[6:] for r in rcl], [s_[:7] + (s_[7] * k,) for s_ in spl], [p[:8] + (p[8] * k,) for p in phl])
def blend(a, b, p, kind):
    p = ease(p)
    if kind == 'dis': return a * (1 - p) + b * p
    if kind == 'beer':
        xs = np.arange(W, dtype=F32)
        lvl = (H + 40) * (1 - min(1, p * 2)) if p < 0.5 else (H + 40) * ((p - 0.5) * 2) * 1.0
        wav = 10 * np.sin(xs * 0.03 + p * 20) + 6 * np.sin(xs * 0.11 - p * 31)
        if p < 0.5:
            top = (lvl + wav)[None, :]; m = np.clip(YY - top + 0.5, 0, 1); base = a
        else:
            top = (lvl + wav)[None, :]; m = np.clip(YY - top + 0.5, 0, 1); base = b
        dep = np.clip((YY - top) / 300.0, 0, 1)[..., None]
        beer = C3(0.36, 0.19, 0.07) * (1 - dep) + C3(0.17, 0.09, 0.045) * dep
        beer = beer * (0.9 + 0.12 * (0.5 + 0.5 * np.sin(XX * 0.05 + YY * 0.08 - p * 30)))[..., None]
        out = base * (1 - m[..., None]) + beer * m[..., None]
        foam = np.clip(1 - np.abs(YY - top - 7) / 9.0, 0, 1)
        out = out * (1 - 0.95 * foam[..., None]) + C3(0.90, 0.80, 0.60) * 0.95 * foam[..., None]
        bub = ((np.sin(XX * 0.9 + p * 40) * np.sin(YY * 0.7 - p * 60) > 0.94) * m).astype(F32)
        return out * (1 - 0.5 * bub[..., None]) + C3(0.95, 0.88, 0.70) * 0.5 * bub[..., None]
    if kind == 'wipe':
        thr = lerp(-0.12, 1.12, p); m = np.clip((thr - NOISE) / 0.05, 0, 1); edge = np.clip(1 - np.abs(NOISE - thr) / 0.022, 0, 1)
        out = a * (1 - m[..., None]) + b * m[..., None]; return out * (1 - 0.55 * edge[..., None])
    off = (1 - p) * H; bs = cv2.warpAffine(b, np.float32([[1, 0, 0], [0, 1, off]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    m = (YY >= off).astype(F32); shd = np.clip(1 - (off - YY) / 46.0, 0, 1) * (YY < off)
    return a * (1 - 0.40 * shd[..., None]) * (1 - m[..., None]) + bs * m[..., None]

def frame(t, fi):
    L.OV.clear(); L.RC.clear(); L.SP.clear(); L.PH.clear(); S.LN.clear()
    i = scene_at(t); lists = None
    tb = None
    for bi in TRANS:
        if abs(t - B[bi]) < TWS.get(bi, TW): tb = bi; break
    if tb is None:
        a = S.SC[i](t).astype(F32)
    else:
        tw_ = TWS.get(tb, TW); p = (t - (B[tb] - tw_)) / (2 * tw_)
        A = S.SC[tb - 1](t).astype(F32); la = grab(); Bn = S.SC[tb](t).astype(F32); lb = grab()
        a = blend(A, Bn, p, TRANS[tb]); pe = ease(p)
        if TRANS[tb] == 'beer': la = scaled(la, max(0.0, 1 - 2.5 * p)); lb = scaled(lb, min(1.0, max(0.0, 2.5 * p - 1.5)))
        else: la = scaled(la, 1 - pe); lb = scaled(lb, pe)
        L.OV.extend(la[0] + lb[0]); L.RC.extend(la[1] + lb[1]); L.SP.extend(la[2] + lb[2]); L.PH.extend(la[3] + lb[3])
    img = np.clip(a, 0, None)
    # motas de polvo flotando
    xs = (MX + 6 * np.sin(t * 0.5 + MP)) % W; ys = (MY - MS * t * 0.6) % H
    splat(img, xs, ys, np.tile(C3(1.0, 0.95, 0.85), (46, 1)), 1.0, 0.16)
    hi = np.clip(img - 0.80, 0, None); img = img + 0.45 * cv2.GaussianBlur(hi, (0, 0), 8)
    img = np.where(img < 0.85, img, 0.85 + 0.15 * np.tanh((img - 0.85) / 0.15)).astype(F32)
    img = img * VIG * (0.99 + 0.012 * math.sin(t * 7.3))
    fade = ease((TEND - t) / 1.6); img = img * fade
    fr = cv2.resize(np.clip(img, 0, 1), (FW, FH), interpolation=cv2.INTER_CUBIC)
    fr = fr + GR[fi % 3]
    draw_ov(fr, t)
    S.draw_lines(fr)
    if t > 1.0 and t < TEND - 3.0: caption(fr, t)
    return np.clip(fr, 0, 1)

def _job(fi): return (frame(fi / 30.0, fi) * 255).astype(np.uint8).tobytes()

def render(out, audio=None, t0=0.0, t1=None, workers=4):
    from multiprocessing import Pool
    t1 = TEND if t1 is None else t1; f0 = int(t0 * 30); f1 = int(t1 * 30)
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{FW}x{FH}', '-r', '30', '-i', '-']
    if audio: cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '224k', '-t', f'{TEND:.2f}']
    cmd += ['-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for n, d in enumerate(pool.imap(_job, range(f0, f1), chunksize=6)):
            pr.stdin.write(d)
            if n % 150 == 0: print(f0 + n, flush=True)
    pr.stdin.close(); pr.wait(); print('LISTO', flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        import time
        for t in [float(x) for x in sys.argv[2:]]:
            t_ = time.time(); f = frame(t, int(t * 30)); cv2.imwrite(f'/home/claude/serie/balmis/tf_{t:06.2f}.jpg', (f[:, :, ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90]); print(t, round(time.time() - t_, 2), flush=True)
    else:
        render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
