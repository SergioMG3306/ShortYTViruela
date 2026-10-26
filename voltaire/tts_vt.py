"""Capítulo 1 · sintetiza la narración frase a frase (davefx), mide duraciones y genera timing.json + voz.wav.

Pausas pensadas para un ritmo calmado e inmersivo:
  frase → 0.55 s · tras pregunta → 0.80 s · cambio de párrafo +0.8 s · cambio de escena +2.8 s
  La voz empieza a los 3.6 s (apertura en frío con solo ambiente) y deja una cola final de 7 s.
"""
import sys, re, json, time, wave
sys.path.insert(0, '/home/claude/topo')
import numpy as np
import sherpa_onnx
from scipy.signal import resample_poly
import tts_norm as N

N.NAMES.update({'Voltaire': 'Voltér', 'Charles-Marie': 'Charl Marí', 'Condamine': 'Condamín'})

SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 0.90
HERE = '/home/claude/serie/voltaire'
T_START, T_TAIL = float(sys.argv[2]) if len(sys.argv) > 2 else 7.2, 5.0

txt = open(f'{HERE}/narr.txt').read()
SCENES = []      # (titulo, [párrafos])
for blk in re.split(r'^## ', txt, flags=re.M):
    blk = blk.strip()
    if not blk:
        continue
    head, _, body = blk.partition('\n')
    paras = [p.strip().replace('\n', ' ') for p in re.split(r'\n\s*\n', body.strip()) if p.strip()]
    SCENES.append((head.strip(), paras))

SENT = []        # dict(sc, pi, text, first_in_para, first_in_scene)
for si, (head, paras) in enumerate(SCENES):
    for pi, p in enumerate(paras):
        parts = [q.strip() for q in re.split(r'(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿¡])', p) if q.strip()]
        for k, q in enumerate(parts):
            SENT.append(dict(sc=si, pi=pi, text=q, fpara=(k == 0), fscene=(k == 0 and pi == 0)))

d = '/home/claude/topo/voz_model'
cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f"{d}/es_ES-davefx-medium.onnx", tokens=f"{d}/tokens.txt",
                                               data_dir=f"{d}/espeak-ng-data"), num_threads=2))
tts = sherpa_onnx.OfflineTts(cfg)
SR0 = 22050
FR = int(0.010 * SR0)


def rms_frames(a):
    n = len(a) // FR
    return np.sqrt((a[:n * FR].reshape(n, FR) ** 2).mean(1) + 1e-12)


def analyse(a):
    r = rms_frames(a)
    thr = max(0.012, 0.05 * np.percentile(r, 95))
    on = r > thr
    idx = np.where(on)[0]
    s0, s1 = idx[0], idx[-1] + 1
    gaps = []
    i = s0
    while i < s1:
        if not on[i]:
            j = i
            while j < s1 and not on[j]:
                j += 1
            if (j - i) >= 5:
                gaps.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return s0 * 0.01, s1 * 0.01, gaps


def word_times(tokens, spoken, a):
    s0, s1, gaps = analyse(a)
    wts = [max(2.0, len(re.sub(r'[^\wáéíóúñü]', '', sp.lower()))) for sp in spoken]
    punct_idx = [i for i, tk in enumerate(tokens[:-1]) if re.search(r'[,;:—?!]$|—$', tk)]
    pw = [w + (3.0 if i in punct_idx else 0.0) for i, w in enumerate(wts)]
    tot = sum(pw)
    cum = np.cumsum([0] + pw)
    est_end = [s0 + (cum[i + 1] - (3.0 if i in punct_idx else 0.0)) / tot * (s1 - s0) for i in range(len(tokens))]
    anchors = []
    last_g = -1
    for i in punct_idx:
        p = est_end[i] + 0.5 * 3.0 / tot * (s1 - s0)
        best = None
        for gi, (g0, g1) in enumerate(gaps):
            if gi <= last_g:
                continue
            c = 0.5 * (g0 + g1)
            if abs(c - p) < 0.45 and (best is None or abs(c - p) < abs(0.5 * (gaps[best][0] + gaps[best][1]) - p)):
                best = gi
        if best is not None:
            anchors.append((i, gaps[best][0], gaps[best][1])); last_g = best
    times = [None] * len(tokens)
    segs = []
    start_tok, start_t = 0, s0
    for (i, g0, g1) in anchors:
        segs.append((start_tok, i, start_t, g0)); start_tok, start_t = i + 1, g1
    segs.append((start_tok, len(tokens) - 1, start_t, s1))
    for (a_, b_, t0_, t1_) in segs:
        ws = wts[a_:b_ + 1]
        tt = sum(ws)
        c = 0.0
        for k, w in enumerate(ws):
            times[a_ + k] = t0_ + c / tt * (t1_ - t0_)
            c += w
    return s0, s1, times, len(anchors), len(punct_idx)


def main():
    out, audios = [], []
    t = time.time()
    for i, s in enumerate(SENT):
        tokens = s['text'].split()
        spoken = N.speak_tokens(tokens)
        said = ' '.join(spoken)
        said = re.sub(r'\s*,\s*', ', ', said)
        said = re.sub(r',\s*,', ',', said).strip()
        said = said.replace('quinientos mil libras', 'quinientas mil libras')
        a = np.array(tts.generate(said, sid=0, speed=SPEED).samples, dtype=np.float32)
        s0, s1, times, na, npn = word_times(tokens, spoken, a)
        audios.append(a)
        out.append(dict(s, said=said, s0=s0, s1=s1, times=times, anch=(na, npn)))
        if i % 10 == 0:
            print(i, len(SENT), round(time.time() - t, 1), flush=True)
    cur = T_START
    for i, o in enumerate(out):
        if i == 0:
            start = T_START
        else:
            gap = 0.75 if out[i - 1]['text'].endswith('?') else 0.50
            if o['fscene']:
                gap += 0.7
            elif o['fpara']:
                gap += 0.6
            start = cur + gap
        o['T0'] = start
        o['T1'] = start + (o['s1'] - o['s0'])
        cur = o['T1']
    sent_t, words = [], []
    for i, o in enumerate(out):
        sent_t.append([o['T0'], o['T1'], o['text']])
        for w, tm in zip(o['text'].split(), o['times']):
            words.append([w, o['T0'] + (tm - o['s0']), i])
    scene_first = [next(i for i, o in enumerate(out) if o['sc'] == k) for k in range(len(SCENES))]
    total = out[-1]['T1'] + T_TAIL
    json.dump(dict(sent_t=sent_t, words=words, scene_first=scene_first, scene_names=[h for h, _ in SCENES],
                   para=[[o['sc'], o['pi'], o['fpara']] for o in out], total=total),
              open(f'{HERE}/timing.json', 'w'), ensure_ascii=False)
    SR = 44100
    voz = np.zeros(int(total * SR), np.float32)
    for o, a in zip(out, audios):
        seg = resample_poly(a, 2, 1).astype(np.float32)
        s0, s1 = int(o['s0'] * SR), int(o['s1'] * SR)
        body = seg[s0:s1]
        rms = np.sqrt((body ** 2).mean() + 1e-9)
        seg = seg * (0.11 / rms)
        i0 = int(o['T0'] * SR) - s0
        lo = max(0, i0)
        voz[lo:lo + len(seg) - (lo - i0)] += seg[lo - i0:][:len(voz) - lo]
    peak = np.abs(voz).max()
    voz = np.tanh(voz * 1.6) / np.tanh(1.6)
    voz = voz / np.abs(voz).max() * 0.85
    w = wave.open(f'{HERE}/voz.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((voz * 32767).astype(np.int16).tobytes()); w.close()
    bad = [(i, o['anch']) for i, o in enumerate(out) if o['anch'][0] < o['anch'][1]]
    print('frases', len(out), 'total', round(total, 1), 'fin voz', round(out[-1]['T1'], 1), 'pico', peak)
    print('sin anclar completamente:', len(bad), 'de', len(out))
    for k, f in enumerate(scene_first):
        print(k, SCENES[k][0], 'frase', f, 't=', round(out[f]['T0'], 1))


main()
