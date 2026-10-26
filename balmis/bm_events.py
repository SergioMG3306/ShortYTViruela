import sys, json, math
import os; os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
sys.path.insert(0, '/home/claude/serie/balmis'); sys.path.insert(0, '/home/claude/serie/vascos'); sys.path.insert(0, '/home/claude/serie/cervantes')
from multiprocessing import Pool
import numpy as np
import cv_lib as L
import bm_scenes as S
import cv_scenes as CS
from cv_lib import B, TEND
TN, SPS, PHS = {}, {}, {}
_tn0 = S.tn; _sp0 = S.sp; _ph0 = S.photo
def tn(text, t, t0, cps=14.0): TN[(text, round(float(t0), 3), float(cps))] = 1; return _tn0(text, t, t0, cps)
def sp(text, sz, col, ang, x, y, t0, alpha=0.9): SPS[(text, round(float(t0), 3))] = 1; return _sp0(text, sz, col, ang, x, y, t0, alpha)
def photo(name, cx, cy, w, ang, t0, t1, cap=''): PHS[(name, round(float(t0), 3), round(float(t1), 3))] = 1; return _ph0(name, cx, cy, w, ang, t0, t1, cap)
S.tn = tn; CS.tn = tn; S.sp = sp; S.photo = photo
def job(i):
    TN.clear(); SPS.clear(); PHS.clear()
    t = B[i]; t1 = B[i + 1] if i < len(S.SC) - 1 else TEND
    while t < t1 + 0.7:
        L.OV.clear(); L.RC.clear(); L.SP.clear(); L.PH.clear()
        S.SC[i](min(t, TEND - 0.01)); t += 0.2
    return (list(TN), list(SPS), list(PHS))
if __name__ == '__main__':
    with Pool(4) as p: res = p.map(job, range(len(S.SC)))
    out = dict(tn=[], sp=[], ph=[])
    for a, b, c in res:
        out['tn'] += a; out['sp'] += b; out['ph'] += c
    for k in out: out[k] = sorted(set(map(tuple, out[k])), key=lambda x: x[1])
    json.dump(out, open('/home/claude/serie/balmis/events.json', 'w'), ensure_ascii=False, indent=0)
    print('LISTO', {k: len(v) for k, v in out.items()})
