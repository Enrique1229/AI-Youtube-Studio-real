# QC — story-003 EL NOMBRE TIBIO (SHORT) — 2026-11-13

VERDICT: REJECT
SCORE: 58/100

## Técnico (probe)
- h264 1080x1920, 30 fps, AAC; duración 50.43 s (timing.json 50.443 s): OK, dentro de Short (<60 s). placeholder_images=false, has_audio=true.
- Audio: mean -14.7 dB, max -0.3 dB. Media correcta para móvil; pico muy cerca de 0 dBFS (riesgo de clipping tras recodificación de YouTube). Recomendado limitador a -1 dB. No es error bloqueante.
- SFX: riser a 24.43 s, hit a 27.03 s, coincide con el inicio de s05 ("Ponía Anselmo", 27.048 s). Bien colocado. Música -22 dB bajo voz: razonable (mezcla no verificada de oído).
- Sin errores técnicos de contenedor. El bloqueo es de calidad visual (ver abajo).

## Subtítulos (subtitles.srt, 57 cues)
- Sincronía: los cues coinciden con timing.json (inicio 0.000, último fin 50.023; frases s01..s06 alineadas). OK.
- Ortografía: sin erratas. Se pierde la puntuación (dos puntos, comas) y "Ponía Anselmo" sale sin mayúsculas enfáticas; aceptable.
- Segmentación: cues de 2-3 palabras con cortes malos ("porque en el" / "ese pozo se" / "y mi sombra" / "no habla"; "tac" x3 como cues sueltos de 0.38 s). Legibilidad mediocre. Corrección: agrupar por frase/cláusula, 4-7 palabras. Responsable: editor/subtitulador.

## Puntuación
- Historia / arco: 17/20. Arco completo, giros G1 ~15 s, G2 ~27 s, G3 ~47 s; final cerrado y con gancho ("Grababa el siguiente"). Frase "mi sombra no habla" es buena.
- Hook (3 s): 9/15. Abre con exposición ("Bajé con una lámpara de carburo porque en el pueblo decían..."); la pared brilla a 13 s y los nombres a 17 s. La bible declaraba hook = escalera de nombres. Pobre enganche en 3 s. Corrección: reordenar para abrir con el nombre/la escalera. Responsable: writer.
- Ritmo: 11/15. 16 planos en 50 s (~3 s/plano) con movimiento variado: bien. Todos weight=1, s05 (13 s) con 4 planos y s01 (8 s) con 2 sin ajuste. Ritmo de voz uniforme.
- Continuidad: 6/15. Texto continuo (continuity.md sin contradicciones graves), pero el personaje visual falla: Anselmo aparece como 5 hombres distintos (director-visual.md).
- Visual: 4/20. Veredicto del Director: NO PUBLICABLE. Nombres dorados (centro de la historia) ausentes en todos los planos, lámpara de carburo poco clara, escalera metálica exenta en vez de tallada, 2 planos fuera de estilo, marcos de póster, franja de texto ilegible, escalado 512 a 1080.
- Audio: 6/8. Niveles correctos, pico alto, sfx bien sincronizados.
- Subtítulos: 3/5. Sincronía OK, segmentación pobre.
- Metadata/policy: 2/2 sobre 2. Policy PASS; ficción declarada en descripción; título correcto. Market: WEAK (experimento medible).
Total: 58/100 (<75) y bloqueo visual: REJECT.

## Correcciones (con responsable)
1. Regenerar imágenes: modelo mejor (SDXL/GPU), bloque de personaje corto al inicio del prompt, negativo fijo con "frame, border, poster, text"; mostrar nombres en oro sobre peldaños tallados en la pared y lámpara de carburo visible. Responsable: image-prompt/visual worker (Director aprueba).
2. Consistencia de Anselmo (gorra de lana oscura, chaleco marrón remendado, arnés): corregir scenes/ch01-s01.md "abrigo de lana"; quitar "años 60" o fijarlo en la bible; ajustar chispas en s06. Responsable: scene-planner.
3. Hook: reabrir con la imagen/frase del nombre o la escalera dentro de los primeros 3 s; unificar "en la oscuridad" con ch01.md. Responsable: writer.
4. Subtítulos: reagrupar cues (4-7 palabras, por cláusula). Responsable: editor.
5. Audio: limitador de pico a -1 dB. Responsable: editor/audio.
6. provenance.json: añadir URL de origen del checkpoint SD 1.5. Responsable: Director.
7. Tras regenerar, recalcular pesos en edl.json para s05/s01 y repetir probe y revisión visual. Responsable: editor.

## Disclosure
ai_use_disclosure=false solo válido si el render es ilustración claramente no realista. Con las imágenes actuales (14/16 ilustradas, 2 fuera de estilo) no puedo confirmarlo; tras regenerar, el Director debe revisar que no haya aspecto fotográfico. Si lo hay, poner true.

## NO verificado (queda para revisión humana)
- No he visto ni oído el vídeo: calidad de voz Kokoro (pronunciación, entonación), mezcla real de música/voz/sfx, claridad de los subtítulos en pantalla, movimientos Ken Burns, transiciones y artefactos de imagen finos se apoyan solo en el informe del Director y los archivos.
- Thumbnail (no existe en la entrada).
- Licencias de modelos en origen (solo provenance declarada).
