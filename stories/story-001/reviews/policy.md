# Policy review — story-001 (SHORT) — 2026-11-13
VERDICT: FIX

Fuentes: idea.json, chapters/ch01.md, final/metadata.json, final/edl.json, final/thumbnail.json, `studio.py similar` (0.05), policy-checklist.md, engine.md.
Nota: el checklist se basa en prensa, no en las páginas oficiales de YouTube; lo que sigue son dudas, no reglas confirmadas.

| # | Punto | Resultado |
|---|-------|-----------|
| 1 | Similitud léxica < 0.3 | OK: 0.05. Primer vídeo del canal; solo el lote de ideas en el ledger. Sin plantilla repetida comprobable aún. |
| 2 | Valor original | OK: historia propia, sin obra ajena detectada. |
| 3 | Título/descr./thumbnail vs. vídeo | Texto OK (botón entre 7 y 8, época, piso propio). BLOQUEA: las imágenes del vídeo y el thumbnail son placeholder (ver 6). |
| 4 | Ficción presentada como ficción | OK: descripción dice "Ficción original... no describe hechos reales". |
| 5 | Personas reales/marcas/copyright | OK: ninguna. |
| 6 | Licencias | FALLA: assets/PLACEHOLDER = "imágenes de prueba; no entregable"; engine.md: backend de imagen = placeholder, ComfyUI solo probado contra servidor simulado. No hay modelo de imagen con licencia comercial verificada. TTS Kokoro Apache-2.0 OK. Música: null (OK). edl.json no anota licencias (el checklist lo pide). |
| 7 | Divulgación sintético | DUDA: voz e imágenes IA con apariencia realista; recomendable marcar "contenido alterado o sintético". metadata.upload_checklist dice "si aplica": hacerlo explícito. Revisar política oficial. |
| 8 | Apto anunciantes | OK: sin violencia/lenguaje/temas sensibles. |
| 9 | No dirigido a niños | OK: personaje infantil (niña) es parte del giro, no público infantil; marcar "no es para niños" ya está. |
| 10 | Variedad vs 3 anteriores | N/A: no hay anteriores. Vigilar en la serie (ascensor/época como plantilla repetida). |
| 11 | Tono | OK: inquietante, no manipulador ni con apariencia de tragedia real. |

## Correcciones
- (Bloqueante, Director/operador, no un subagente) Generar imágenes reales con un motor de licencia comercial verificada y anotarla en engine.md; re-ensamblar vídeo y thumbnail. Hasta entonces `deliver` no debe ejecutarse.
- (metadata-writer) Cambiar upload_checklist a "Marcar 'contenido alterado o sintético': SÍ (voz e imágenes IA realistas)".
- (editor) Anotar en edl.json licencias de modelo de imagen, TTS (Kokoro Apache-2.0) y música (ninguna).
- Re-revisar policy tras regenerar imágenes (la similitud y el texto no requieren cambios).
