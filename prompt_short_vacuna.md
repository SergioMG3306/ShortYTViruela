Hola, Claude. Vamos a hacer un Short vertical de historia para mi canal de YouTube («Historia en 16 bits»), siguiendo exactamente el mismo estilo y el mismo motor que los Shorts anteriores (Llívia, los balleneros vascos, la ola de cerveza de Londres, Cervantes).

## Material en el repositorio de GitHub
- `motor_shorts.zip`: el motor completo con el que se hicieron los Shorts anteriores. Descomprímelo, ejecuta `bash motor/setup.sh` (copia el código a `/home/claude/serie/…`, instala dependencias, las fuentes y descarga la voz de Dave) y lee `motor/README_MOTOR.md`. Usa `serie/llivia` como plantilla: copia ese proyecto y adáptalo, no reescribas el motor desde cero.
- `fotos/`: aquí subiré las imágenes que me pidas. Pídemelas al principio, en una sola lista, solo las imprescindibles (3–5), indicando qué buscar y que sean de dominio público o con licencia libre (Wikimedia Commons). Mientras las subo, avanza con el guion, la voz y las escenas que no dependen de ellas.

## Tema: la Expedición Balmis (la vacuna de la viruela que viajó dentro de 22 niños)
Real Expedición Filantrópica de la Vacuna (1803–1806). Puntos de partida, que DEBES verificar con fuentes antes de usarlos:
- Sale de A Coruña el 30 de noviembre de 1803 en la corbeta María Pita, dirigida por el médico Francisco Javier de Balmis.
- No había forma de conservar la vacuna: la llevaron viva, de brazo a brazo, en 22 niños huérfanos que se iban vacunando por parejas durante la travesía.
- Isabel Zendal, rectora del orfanato de A Coruña, cuidó de los niños durante el viaje.
- Canarias, Puerto Rico, Venezuela; allí se divide (Salvany hacia Sudamérica, Balmis hacia Cuba y México); desde México, Balmis cruza el Pacífico a Filipinas con otros niños mexicanos y llega hasta China.
- Edward Jenner, el descubridor de la vacuna, la elogió como un ejemplo de filantropía sin igual.
- Gancho final posible: en 2020 la operación del ejército contra la COVID se llamó «Operación Balmis» y el hospital de pandemias de Madrid lleva el nombre de Isabel Zendal.
Si alguna cifra o fecha no se sostiene en las fuentes, corrígela y avísame. Ojo con afirmaciones repetidas en internet sin fuente clara (por ejemplo, lo que la OMS diga o no de Isabel Zendal).

## Formato y guion
- Vertical 1080×1920, 30 fps, entre 60 y 90 s.
- Empieza directamente con el gancho «¿Sabías que…?» (en voz y con la cabecera grande «¿SABÍAS QUE...?» desde el primer fotograma, sin fundido desde negro).
- Frases cortas y claras para un público amplio (mi audiencia es sobre todo mayor de 55 años, española).
- Cierre: pregunta al espectador + «Suscríbete para descubrir más historias como esta».
- Enséñame el guion antes de generar la voz.

## Estilo visual (igual que los anteriores)
- Estética de collage de papel: placas color crema, letra LM Mono negrita de máquina de escribir que se teclea, acentos en rojo, sellos que caen con golpe, polvo y grano, viñeta.
- Inmersión ante todo: movimiento de cámara en todas las escenas, Ken Burns en fotos y grabados, mapas con fronteras reales y relieve (`ll_map`), recreaciones ilustradas (barco en el mar con `nao`/`storm_sea`, figuras con `person`, velas, partículas), transiciones (wipe y fundido).
- Ideas: mapa animado de la ruta A Coruña → Canarias → Puerto Rico → Caracas → México → Filipinas → China con el barco avanzando; contador de niños y de brazo a brazo (la vacuna «saltando» de un niño a otro como una chispa); la viruela como amenaza (cifras de mortalidad verificadas); el sello final.
- Los datos que salgan en pantalla tienen que coincidir EXACTAMENTE con lo que dice la voz (si dice «veintidós niños», el rótulo pone 22; nada de redondeos distintos).
- Las fotos/grabados, a pantalla completa y al menos 3 segundos, con el pie de crédito pequeño.
- Arte entre y=140 y y=640 (en coordenadas 540×960); los subtítulos van solos abajo.
- Sellos justo después de que termine la frase, nunca encima de una palabra importante; nada de overlays que se queden colgados en las transiciones.

## Sonido y voz
- Voz de Dave (es_ES-davefx con sherpa-onnx), velocidad 0.90, con respellings para nombres difíciles.
- Diseño sonoro por capas: drones, mar y viento, crujidos de madera del barco, golpes en los sellos, tecleo, whooshes en zooms, campanas; ducking bajo la voz. Master a −14 LUFS.

## Proceso y entregables
1. Pide las imágenes y propón el guion. 2. Voz y tiempos. 3. Escenas, revisadas con hojas de contacto antes del render completo. 4. Render, versión ligera (crf 25 + hqdn3d, idealmente < 30 MB, porque los archivos grandes no me dejan descargarlos) y comprobación de −14 LUFS.
- Entrega: el MP4 ligero, título, descripción con fuentes y créditos de las imágenes, hashtags y etiquetas (todo en español), en un `titulo_descripcion.txt` como en los proyectos anteriores.
- Intenta ser eficiente con los créditos: reutiliza el motor, no repitas renders completos sin necesidad.
