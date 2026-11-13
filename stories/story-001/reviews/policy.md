# Policy review (2a revision) — story-001 (SHORT) — 2026-11-13
VERDICT: PASS

Fuentes: idea.json, chapters/ch01.md, final/metadata.json, final/provenance.json, final/edl.json, final/thumbnail.json, `studio.py similar --story story-001` (0.07), policy-checklist.md, engine.md; muestreo visual de thumbnail.jpg y ch01-s05-a.png.
Cambios desde la 1a revisión: imágenes regeneradas con ComfyUI real (SD 1.5 + LCM LoRA); sin marcador PLACEHOLDER; provenance.json completo; upload_checklist corregido.

| # | Punto | Resultado |
|---|-------|-----------|
| 1 | Similitud < 0.3 | OK: 0.07 (lo más cercano es una idea del lote, buzo/presa, otro concepto). Primer vídeo: sin plantilla repetida comprobable. |
| 2 | Valor original | OK: historia, giro y personajes propios; sin obra ajena. |
| 3 | Título/descr./thumbnail vs. vídeo | OK: título (botón entre 7 y 8) = primer verso del guion; descripción y thumbnail "SIN NÚMERO" (botón liso) coinciden con lo que se ve y se cuenta; sin promesas falsas. |
| 4 | Ficción como ficción | OK: descripción y ai_disclosure dicen ficción original, IA, sin hechos reales. |
| 5 | Personas reales/marcas/copyright | OK: ninguna; personajes inventados. |
| 6 | Licencias | OK: Kokoro Apache-2.0; SD 1.5 CreativeML OpenRAIL-M + LCM LoRA OpenRAIL++ (uso comercial permitido con restricciones de uso que esta historia no incumple); música null. Licencias constan en provenance.json y engine.md. No he podido reverificar en Hugging Face desde aquí: me baso en lo anotado. Hay imágenes reales hechas el 2026-11-13 (18:51–19:24), 18 PNG. |
| 7 | Divulgación | OK: las imágenes (p. ej. familia cenando) tienen aspecto fotográfico realista y metadata.ai_use_disclosure=true; upload_checklist dice "AI use: Sí". Marcar en Studio al subir. |
| 8 | Apto anunciantes | OK: sin violencia, lenguaje ni temas sensibles. |
| 9 | No dirigido a niños | OK: "no es para niños" en checklist; la niña es parte del giro. |
| 10 | Variedad vs 3 anteriores | N/A (primer vídeo). |
| 11 | Tono | OK: inquietante, sin manipulación ni apariencia de tragedia real. |
| 12 | Arco narrativo | OK: planteamiento (botón), escalada (3 épocas) y giro/cierre (edificio donde nunca nació, botón se borra). No es sucesión de imágenes sueltas. |

## Dudas (no son reglas confirmadas)
- Riesgo de canal, no de este vídeo: imágenes fijas con zoom + TTS es el perfil que la política de contenido inauténtico describe como riesgo; aquí lo mitiga la narrativa propia. La calidad visual (SD 1.5 a 512 px) es asunto de QC.
- edl.json sigue sin anotar licencias (el checklist las pide en engine.md/edl.json; engine.md y provenance.json las cubren). Opcional para el editor, no bloqueante.
- Vigilar en la serie (ascensor + época por episodio) que no se convierta en plantilla repetida (punto 10 y política de "misma situación, mismo resultado").

## Correcciones
Ninguna bloqueante. Gate policy: PASS.
