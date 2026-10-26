import os; os.environ['PAL_DIR'] = '/home/claude/serie/balmis'
import sys; sys.path.insert(0, '/home/claude/serie/cervantes'); sys.path.insert(0, '/home/claude/serie/vascos')
import sys, glob, cv2, numpy as np
ts = sys.argv[2:]; out = sys.argv[1]
ims = []
for t in ts:
    f = cv2.imread('/home/claude/serie/balmis/tf_%06.2f.jpg' % float(t))
    f = cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA)
    cv2.putText(f, t, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    ims.append(f)
rows = []
n = 4
for i in range(0, len(ims), n):
    r = ims[i:i + n]
    while len(r) < n: r.append(np.zeros_like(ims[0]))
    rows.append(np.hstack(r))
cv2.imwrite(out, np.vstack(rows))
