import os; os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
import sys; sys.path.insert(0, '/home/claude/serie/cervantes'); sys.path.insert(0, '/home/claude/serie/vascos')
import sys, time
sys.path.insert(0, '/home/claude/serie/balmis')
import bm_render as R, bm_scenes as S, cv_lib as L
import numpy as np
tt = []; bad = 0
t = 0.0
while t < L.TEND:
    t0 = time.time()
    try: R.frame(t, int(t * 30))
    except Exception as e:
        import traceback; print('ERR at', t); traceback.print_exc(); bad += 1
        if bad > 3: break
    tt.append(time.time() - t0); t += 0.5
print('frames', len(tt), 'mean %.2f max %.2f' % (np.mean(tt), np.max(tt)), 'est total min (2 workers): %.1f' % (np.mean(tt) * L.TEND * 30 / 2 / 60))
