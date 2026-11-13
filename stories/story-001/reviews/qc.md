# QC story-001 (SHORT) - El botón sin número
VERDICT: REJECT
SCORE: 62/100

## Desglose
- Historia/giro: 17/20 - cierre limpio ("el edificio donde nunca nací"), pistas resueltas (continuity DONE).
- Hook (3 s): 9/10 - primera frase "Pulsé el botón que no tiene número, entre el siete y el ocho" (0-3,3 s) + temblor y radio; engancha en texto. Visual no verificable.
- Ritmo: 8/10 - 18 planos de 3-4 pesos, 55,3 s (<60 s); ~125 palabras, ritmo alto pero ajustado.
- Continuidad: 9/10 - sin contradicciones abiertas.
- Audio: 8/10 - mean -16,0 dB, max -1,5 dB (sin clipping, algo cerca de 0). Sin música ni SFX (edl: music null, sfx []): plano sonoro.
- Vídeo técnico: 3/15 - 1080x1920, 30 fps, h264/aac, 55,33 s OK, PERO checks.placeholder_images = true (imágenes de prueba, "no entregable").
- Subtítulos: 8/10 - sincronizados con timing.json, ortografía correcta; fragmentos de 2-3 palabras ("Neón", "una tele") muy cortados, legibles pero nerviosos; último subtítulo termina 55,197 vs vídeo 55,333.
- Metadata: 0/5 efectivo - policy en FIX (checklist de divulgación sintética ambiguo).
(Suma con penalización por bloqueo técnico: 62.)

## Errores técnicos (bloqueantes)
1. Imágenes y thumbnail son placeholder (probe checks.placeholder_images=true; assets/PLACEHOLDER). Sin imágenes reales con licencia verificada no es entregable.
2. Puerta policy en FIX (reviews/policy.md), pendiente de re-revisión.
3. No consta reseña del critic en reviews/ (solo continuity.md y policy.md): puerta 1 sin evidencia en disco.

## Correcciones
- Director/operador: generar imágenes reales con motor de licencia comercial verificada, anotarla en engine.md, reensamblar vídeo y thumbnail.
- editor: anotar licencias (imagen, TTS Kokoro Apache-2.0, música ninguna) en edl.json; considerar SFX/ambiente leve (ascensor, radio) para variedad sonora.
- metadata-writer: upload_checklist -> "Marcar 'contenido alterado o sintético': SÍ".
- subtitle/editor: agrupar subtítulos en frases de 4-6 palabras donde el timing lo permita.
- Re-ejecutar policy y confirmar reseña del critic antes de nuevo QC.

## NO verificado (queda para revisión humana)
Calidad visual real de planos/thumbnail, coherencia imagen-narración, sincronía audiovisual percibida, calidad/prosodia de la voz, mezcla subjetiva, legibilidad de subtítulos quemados, encuadre en móvil.
