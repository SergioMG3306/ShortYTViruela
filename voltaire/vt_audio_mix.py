# ---------- mezcla final
def rev(x):
    n_ir = int(2.6 * SR); ir_ = (rng.randn(n_ir) * np.exp(-np.arange(n_ir) / SR / 0.75)).astype(np.float32); ir_ = lp(ir_, 5200); ir_ = np.concatenate([np.zeros(int(0.03 * SR), np.float32), ir_])
    y = fftconvolve(x, ir_)[:N]; return y / (np.abs(y).max() + 1e-9)
SL, SR_, L, R, AMB, VOZ, DUCK = AL.SL, AL.SR_, AL.L, AL.R, AL.AMB, AL.VOZ, AL.DUCK
wl = rev(SL); wr_ = rev(SR_)
amb = AMB * DUCK[None, :]
HK = 1 + 0.4 * np.clip((2.3 - tt(N)) / 0.3, 0, 1)
fxL = (L * (0.55 + 0.45 * DUCK) + amb[0]) * HK; fxR = (R * (0.55 + 0.45 * DUCK) + amb[1]) * HK
fxL = fxL + 0.30 * wl * np.abs(SL).max() * 6 * DUCK; fxR = fxR + 0.30 * wr_ * np.abs(SR_).max() * 6 * DUCK
mixL = VOZ * 1.2 + np.tanh(fxL * 1.2) / 1.2 * 0.80; mixR = VOZ * 1.2 + np.tanh(fxR * 1.2) / 1.2 * 0.80
mixL = np.tanh(mixL * 1.0) / np.tanh(1.0); mixR = np.tanh(mixR * 1.0) / np.tanh(1.0)
HG = 1 + 0.2 * np.clip((2.35 - tt(N)) / 0.35, 0, 1); mixL *= HG; mixR *= HG
pk = max(np.abs(mixL).max(), np.abs(mixR).max()); mixL *= 0.92 / pk; mixR *= 0.92 / pk
fade = np.clip(tt(N) / 0.25, 0, 1) * np.clip((TEND + 0.4 - tt(N)) / 2.2, 0, 1); mixL *= fade; mixR *= fade
st = np.stack([mixL, mixR], 1)[:int((TEND + 0.1) * SR)]
wv = wave.open('/home/claude/serie/voltaire/vt_audio_raw.wav', 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
print('ok', round(float(np.sqrt((st ** 2).mean())), 3), 'voz rms', round(float(np.sqrt((VOZ ** 2).mean())), 3))
