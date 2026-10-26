# Short «La Expedición Balmis» (Historia en 16 bits)

Proyecto hecho con el motor de `motor_shorts.zip` a partir de la plantilla `serie/llivia`.

## Reproducir
1. `bash motor/setup.sh`, y además:
   `pip install --break-system-packages "sherpa-onnx==1.12.40"` (la 2.0 ya no genera la voz de Dave)
   `pip install --break-system-packages --no-deps num2words`
2. Copiar esta carpeta a `/home/claude/serie/balmis` y las fotos de `fotos/` a `/home/claude/serie/balmis/fotos/`
   con los nombres `balmis.jpg`, `jenner.jpg`, `codice.jpg`, `zendal.jpg`, `mano.jpg` (más `codice_hq.png`, el Códice reescalado).
3. Voz: `python3 tts_bm.py 0.90 0.6` → `voz.wav` + `timing.json`
4. Pruebas: `python3 t_sc.py 4.3 20 45` y `python3 sheet.py hoja.jpg 4.3 20 45`
5. Eventos y audio: `python3 bm_events.py`; `cat bm_audio_head.py bm_audio_cues.py bm_audio_mix.py > bm_audio.py; python3 bm_audio.py`;
   `ffmpeg -i bm_audio_raw.wav -af "volume=-2.3dB,alimiter=limit=0.93:level=false" bm_audio.wav` (−14 LUFS)
6. Render: `python3 bm_render.py balmis_v1.mp4 bm_audio.wav` y versión ligera con crf 25 + hqdn3d.

## Piezas nuevas
- `bm_globe.py`: globo ortográfico con fronteras reales (Natural Earth 50m) y relieve procedural; rutas de la expedición.
- `bm_art.py`: niños (sprites), bodega con farol, corbeta con corte interior, cubierta, Torre de Hércules, frasco de linfa, hospital, virus.
- `bm_map.py`: `ll_map` con relieve de toda la Península (escena de 2020).
