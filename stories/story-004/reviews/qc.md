# QC — story-004 (Short, render v10) — 2026-11-16

VEREDICTO: PASS — puntuación 76/100

## Técnica (medida)
- video.mp4: H.264, 1080x1920, 30 fps, duración 20,000 s. OK para Short vertical.
- Audio AAC mono, 96 kHz. Integrado -16,3 LUFS (rango aceptado -14/-16 con margen), LRA 4,6 LU, true peak -2,2 dBFS (<= -1 dBFS). OK.
- `studio.py probe` daba "final_file no definido" solo porque aún no estaba registrado; se registra al dar PASS.
- Sin errores técnicos detectados.

## Contenido (hoja de contactos v10, 3 fps)
- Rótulo en inglés "IQ LEVEL", banda oscura, color por nivel (rojo, blanco, verde, verde, oro); identidad propia (cumple C2 de policy).
- Cabeza siempre bajo el rótulo en los 5 niveles (según check_framing.py del Director; en la hoja no se ve solapamiento).
- Los 5 gags se leen: hundirse con corona de gotas, salto fallido con chapuzón, tablón, barca, palanca y cauce vacío. Cortes en seco entre niveles, sin barridos con artefactos visibles.
- Sin marca de agua, logotipo ni texto ajeno en ningún fotograma de la hoja (C3 cumplida a esa resolución).

## Metadatos (meta/youtube.json)
- Título, descripción y hashtags en inglés, coherentes con el vídeo (cruzar un río, niveles de IQ). Sin promesas de viralidad.
- Crédito literal "Motion capture: CMU Graphics Lab Motion Capture Database" presente. Música/efectos propios declarados. ai_use_disclosure=false según decisión del Director (dibujo animado claramente no real).
- Short: no requiere capítulos.

## Desglose
- Técnica/audio/vídeo: 24/25
- Legibilidad visual y encuadre: 20/25
- Metadatos y cumplimiento (crédito, idioma): 18/20
- Ritmo y hook (rótulo + acción desde el segundo 0): 8/15
- Originalidad/final (reserva por critic: fórmula de referencia, final sin confirmar bucle): 6/15

## NO verificado (revisión humana)
- Audio real (mezcla, sincronía sfx con chapuzón/palanca): solo medido, no oído.
- Movimiento fluido a 30 fps y cortes a ritmo real: solo vi muestras a 3 fps.
- Bucle último plano -> primer plano (pedido por critic).
- Nivel 2: que "quedarse en el aire" se lea como gag y no como fallo.
- Marca de agua en fotogramas intermedios no incluidos en la hoja.
- director-visual.md describe v6; la revisión de v10 se apoya en el contexto del Director y la hoja v10.
- Decisión "creado para niños" (COPPA) queda al usuario al publicar.

## Recomendaciones no bloqueantes
- Próximo episodio: variar escenario, nº de niveles y orden de IQ (policy C4, critic 3).
