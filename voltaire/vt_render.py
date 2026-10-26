"""Render del Short de Voltaire a 1080×1920 nativo: escenas, transiciones (tinta y fundido), acabado y subtítulos."""
import sys, subprocess, time
sys.path.insert(0, '/home/claude/serie/voltaire')
from vt_lib import *
import vt_scenes as S

TRANS = {1: 'ink', 2: 'dis', 3: 'ink', 4: 'dis', 5: 'ink', 6: 'dis', 7: 'ink'}
TW = 0.5
_n = noise(41, (40, 90, 200, 400)); NOISE = ((_n - _n.min()) / (_n.max() - _n.min())).astype(F32)
_n2 = noise(43, (12, 30)); NOISE = (0.85 * NOISE + 0.15 * (_n2 - _n2.min()) / (_n2.max() - _n2.min())).astype(F32)

def scene_at(t): return max(j for j in range(len(S.SC)) if t >= B[j])

def blend(a, b, p, kind):
    p = ease(p)
    if kind == 'dis': return a * (1 - p) + b * p
    thr = lerp(-0.1, 1.1, p); m = np.clip((thr - NOISE) / 0.04, 0, 1); edge = np.clip(1 - np.abs(NOISE - thr) / 0.018, 0, 1)
    out = a * (1 - m[..., None]) + b * m[..., None]
    return out * (1 - 0.6 * edge[..., None]) + GOLDL * 0.9 * edge[..., None] * (1 - 0.6 * edge[..., None]) + 0.25 * cv2.GaussianBlur(edge, (0, 0), 6)[..., None] * GOLD

def frame(t, fi):
    i = scene_at(t); tb = None
    for bi in TRANS:
        if abs(t - B[bi]) < TW: tb = bi; break
    if tb is None: img = S.SC[i](t)
    else:
        p = (t - (B[tb] - TW)) / (2 * TW)
        img = blend(S.SC[tb - 1](t), S.SC[tb](t), p, TRANS[tb])
    img = finish(img, fi)
    img = img * ease((TEND - t) / 1.6)
    if 0.4 < t < TEND - 3.0: caption(img, t)
    return np.clip(img, 0, 1)

def _job(fi): return (frame(fi / 30.0, fi) * 255 + 0.5).astype(np.uint8).tobytes()

def render(out, audio=None, workers=4):
    from multiprocessing import Pool
    f1 = int(TEND * 30)
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-']
    if audio: cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '224k', '-t', f'{TEND:.2f}']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for n, d in enumerate(pool.imap(_job, range(f1), chunksize=4)):
            pr.stdin.write(d)
            if n % 150 == 0: print(n, flush=True)
    pr.stdin.close(); pr.wait(); print('LISTO', flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        for t in [float(x) for x in sys.argv[2:]]:
            t_ = time.time(); f = frame(t, int(t * 30))
            cv2.imwrite(f'/home/claude/serie/voltaire/tf_{t:06.2f}.jpg', (f[:, :, ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92]); print(t, round(time.time() - t_, 2), flush=True)
    elif sys.argv[1] == 'sheet':
        out = sys.argv[2]; ts = sys.argv[3:]; ims = []
        for t in ts:
            f = cv2.imread('/home/claude/serie/voltaire/tf_%06.2f.jpg' % float(t)); f = cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA)
            cv2.putText(f, t, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2); ims.append(f)
        rows = []
        for i in range(0, len(ims), 4):
            r = ims[i:i + 4]
            while len(r) < 4: r.append(np.zeros_like(ims[0]))
            rows.append(np.hstack(r))
        cv2.imwrite(out, np.vstack(rows))
    else:
        render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
