import os; os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
import sys; sys.path.insert(0, '/home/claude/serie/cervantes'); sys.path.insert(0, '/home/claude/serie/vascos')
import sys, time
sys.path.insert(0, '/home/claude/serie/balmis')
import bm_scenes as S
import cv_lib as L
import cv2, numpy as np
if not hasattr(S, 'SC'):
    S.SC = [getattr(S, "s%d" % i, lambda t: np.zeros((S.H, S.W, 3), np.float32)) for i in range(8)]
import bm_render as R
R.S = S
for t in [float(x) for x in sys.argv[1:]]:
    t_ = time.time()
    try:
        f = R.frame(t, int(t * 30))
    except Exception as e:
        import traceback; traceback.print_exc(); continue
    cv2.imwrite(f'tf_{t:06.2f}.jpg', (f[:, :, ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88]); print(t, round(time.time() - t_, 2), flush=True)
