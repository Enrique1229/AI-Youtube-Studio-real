# QC story-005 (Short anim, "A Match Warms Up an Ice Cube (Together Forever)") - 2026-11-16
Veredicto: PASS - calidad 80/100

## Tecnica (final/video.mp4, probe + ffprobe + ebur128)
- 1080x1920, H.264 yuv420p, 30 fps: OK.
- AAC 48 kHz mono, presente: OK.
- Duracion 17,6 s (rango 15-25): OK.
- True peak -2,0 dBFS (limite <= -1): OK. Max volume -2,1 dB. Integrado -16,8 LUFS, LRA 3,7: razonable para Short.
- probe checks: placeholder_images false, resolution_ok, has_audio, duration_ok: todo OK.
- Errores tecnicos: ninguno detectado.

## Contenido (contact-sheet-v2.jpg, 3 fps)
- Hook: cubito tiritando en primer plano con cejas preocupadas desde el fotograma 0; necesidad clara. Funciona, aunque ~4 s en plano casi estatico es el punto mas flojo del ritmo.
- Narrativa legible sin palabras: tirita, cerilla se enciende, cubito se derrite, charco con ojos, gota salta y abraza, llama se apaga, nube con dos caras sube, cerilla negra queda. Arco completo, remate claro.
- Caras grandes y legibles en casi todos los planos; cabeza de cerilla entera salvo un fotograma con la punta de la llama asomando en el borde (menor, ya anotado en anim-check).
- CTA "follow for more" visible en los ultimos ~1,6 s, legible, sin tapar caras. Sin marca de agua ajena ni texto extra.
- Nube algo gris (ya anotado por el Director); aceptable.
- Diferencias frente a la referencia R2 mantenidas (sin contagio, peluca, pareja, calavera): condicion D de policy OK.

## Metadatos (meta/youtube.json vs idea.json)
- Titulo, descripcion, hashtags en ingles; coherentes con el video; sin promesas de viralidad. OK.
- Descripcion declara "Fiction made with AI-assisted tools" pero ai_use_disclosure=false: ligera incoherencia (no bloqueante). Recomendacion: decision del Director/usuario; por prudencia (hielo/charco con transmision realista) valorar true.
- Audiencia made-for-kids sin decidir (policy condicion C): decision del usuario en la subida.

## Desglose
- Historia/remate 18/20, hook 13/20, ritmo/montaje 15/20, visual/continuidad 17/20, audio/tecnica 17/20 = 80.

## NO verificado (revision humana)
- No he oido el audio: sincronia de SFX/musica con la accion, timbre y ausencia de clicks.
- No he visto el video en movimiento: fluidez de cortes secos, parpadeos, calidad de transmision del hielo.
- Solo veo 3 fps; artefactos breves entre muestras no detectables.
- provenance.json/edl.json (policy condicion B) no revisados por no estar en mi entrada.
- Clasificacion final de YouTube (made for kids) y divulgacion IA.
