# Short «Voltaire y la lotería de 1729» (Historia en 16 bits)

Estilo nuevo «cuaderno del matemático», dibujado a 1080×1920 nativo (sin reescalar):
fondo azul noche, tinta dorada que se escribe a pluma, tipografías del XVIII (Playfair Display, Libre Caslon),
grabados virados a azul y oro en marcos dorados, lacres en lugar de sellos y subtítulos con la palabra dicha en oro.

Se reutilizan del motor: la voz de Dave (`tts_vt.py`, copia de `tts_ll.py`), `timing.json`, la librería de audio,
el ducking y la mezcla (`vt_audio_*`).

## Reproducir
1. `bash motor/setup.sh`, `pip install --break-system-packages "sherpa-onnx==1.12.40"` y `pip install --break-system-packages --no-deps num2words`.
2. Copiar esta carpeta a `/home/claude/serie/voltaire` (con `fonts/`) y las fotos a `fotos/`: `voltaire.jpg`, `condamine.jpg`, `turgot.jpg`, `voltaire_grabado.png`.
3. Voz: `python3 tts_vt.py 0.90 0.6`
4. Pruebas: `python3 vt_render.py test 3.9 23.5 46.5` y `python3 vt_render.py sheet hoja.jpg 3.9 23.5 46.5`
5. Eventos y audio: `python3 vt_events.py`; `cat vt_audio_head.py vt_audio_cues.py vt_audio_mix.py > vt_audio.py; python3 vt_audio.py`;
   `ffmpeg -i vt_audio_raw.wav -af "volume=-3.0dB,alimiter=limit=0.93:level=false" vt_audio.wav` (−14 LUFS)
6. Render: `python3 vt_render.py voltaire_master.mp4 vt_audio.wav` (4 procesos) y versión ligera con crf 25 + hqdn3d.
