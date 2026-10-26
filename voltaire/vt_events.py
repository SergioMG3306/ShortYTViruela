"""Recorre todas las escenas y guarda los eventos de sonido (pluma, lacres) en events.json."""
import sys, json
sys.path.insert(0, '/home/claude/serie/voltaire')
from multiprocessing import Pool
import vt_lib as L
import vt_scenes as S

def job(i):
    L.EV = {}
    t = max(0.0, L.B[i] - 0.5); t1 = L.B[i + 1] + 0.5
    while t < t1:
        S.SC[i](min(t, L.TEND - 0.01)); t += 0.1
    return list(L.EV.items())

if __name__ == '__main__':
    with Pool(4) as p: res = p.map(job, range(len(S.SC)))
    ev = {}
    for r in res:
        for k, v in r: ev[tuple(k)] = v
    out = dict(pen=sorted([[k[1], k[2], v] for k, v in ev.items() if k[0] == 'pen'], key=lambda x: x[1]),
               seal=sorted([[k[1], k[2]] for k, v in ev.items() if k[0] == 'seal'], key=lambda x: x[1]))
    json.dump(out, open('/home/claude/serie/voltaire/events.json', 'w'), ensure_ascii=False, indent=0)
    print('LISTO', {k: len(v) for k, v in out.items()})
