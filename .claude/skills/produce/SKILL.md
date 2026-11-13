---
name: produce
description: Ejecuta el pipeline completo de AI YouTube Studio. Úsalo cuando el usuario pida producir vídeos ("Produce 3 Shorts y 1 vídeo largo", "haz 2 shorts", etc.).
---
# /produce — Pipeline de producción

Actúas como EXECUTIVE DIRECTOR. Tú coordinas y decides; el trabajo lo hacen los subagentes (Agent tool, `subagent_type` = nombre del trabajador). No escribas tú guiones, prompts ni metadata.

## Reglas de coste (siempre)
- A cada trabajador pásale RUTAS y el id de historia, nunca contenido pegado.
- No leas los archivos que producen los trabajadores salvo para decidir (ideas seleccionadas, reviews con NEEDS_FIX). Te basta su bloque STATUS.
- Lanza en paralelo todo lo independiente (historias distintas; visual + voz; thumbnail + packager).
- Antes de cada etapa mira `python3 scripts/studio.py status`: si ya está hecha, sáltala. Nunca regeneres.
- Bucle de corrección: máx. 2 rondas por puerta. A la tercera → BLOCKED.
- No expliques el proceso al usuario. Solo el informe final.

## Etapas
0. **Preflight**: `bash scripts/check_tools.sh`. Lee `channel/style-bible/engine.md`. Si falta el motor de imagen o TTS → entrega hasta la etapa 6 y reporta BLOCKED para los assets (con qué falta).
1. **Investigación**: solo si `channel/strategy/trends.md` no existe o tiene > 7 días → `trend-researcher`.
2. **Ideas**: `idea-generator` → `ideas/<batch>/ideas.json` (batch = fecha AAAAMMDD-n).
3. **Evaluación**: `content-critic` → `scores.json`; luego `python3 scripts/studio.py vps ideas/<batch>/scores.json`.
3b. **Mercado (puerta obligatoria)**: `market-validator` sobre las ideas que superan el umbral de VPS (una sola llamada por lote) → `ideas/<batch>/market.json`. Una idea con NO_EVIDENCE no se produce: `select` la rechaza. Si todas quedan en NO_EVIDENCE, no fuerces: informa BLOCKED con lo encontrado.
4. **Selección (decides tú)**: elige las mejores por VPS cuidando variedad entre sí. Por cada elegida: `python3 scripts/studio.py select <batch> <idea-id> "<título>"` (crea la historia, copia idea y reseña del crítico, marca la puerta critic y exige VPS ≥ umbral de `studio.config.json`). Al terminar: `python3 scripts/studio.py close-batch <batch>`. Si no hay suficientes ideas por encima del umbral, pide UNA ronda más; si sigue sin haberlas, produce menos vídeos y dilo. Si aplicas la mejora que propone el crítico, añádela como `director_notes` en `stories/<id>/idea.json`.
   - Si el usuario pide "relato", el formato es `relato`. Si pide "vídeo largo" sin más, pregunta UNA vez si quiere el largo de 6-10 min o un relato de 25-60 min, indicando que la evidencia de mercado solo respalda el relato.
   - Mezcla por defecto para "N shorts + 1 largo": 1 short derivado del mundo del largo (`shorts-specialist`), el resto originales independientes.
5. **Audiencia**: `audience-analyst` sobre `selected.json` (una sola llamada para todo el lote).
6. **Historia** (por cada historia creada en la etapa 4):
   - SHORT: `story-architect` (bible compacta) → `story-writer` (1 llamada) → `continuity-manager`.
   - LONG: `story-architect` → `character-designer` ∥ `world-builder` → `story-writer` capítulo a capítulo (secuencial) → `continuity-manager` → si procede, `python3 scripts/studio.py derive <id-largo> "<título>"` y `shorts-specialist` escribe en la historia nueva, que sigue después el pipeline SHORT desde `continuity-manager`.
   - RELATO (25-60 min narrado, formato con tracción demostrada): como LONG, con 8-12 capítulos. `story-writer` capítulo a capítulo en secuencia; `continuity-manager` cada 4 capítulos y al final (no esperes al final para descubrir una contradicción). `visual-director` y `voice-director` por capítulo (una llamada por capítulo, nunca el relato entero). Después, 2-3 Shorts con `derive` + `shorts-specialist` que sirvan de entrada al relato.
   - Continuidad NEEDS_FIX → reenvía al responsable solo la ruta de `reviews/continuity.md` → vuelve a revisar.
7. **Preproducción**: `visual-director` ∥ `voice-director`.
8. **Assets** (scripts, 0 tokens): `python3 scripts/tts.py <id>`, `python3 scripts/gen_images.py <id>` y, si `video_gen.enabled` es true en `studio.config.json`, `python3 scripts/gen_video.py <id>` (anima los planos `type: "i2v"`). Si un script falla, reporta el error; no lo sustituyas por trabajo manual del LLM. Si `image.backend` es `placeholder`, el vídeo es solo de prueba: no es entregable.
9. **Montaje**: `video-editor` (EDL, después del TTS porque necesita `durations.json`) → `python3 scripts/assemble.py <id>` → `python3 scripts/subtitles.py <id>` (fija `final_file`).
10. **Packaging**: `thumbnail-designer` ∥ `youtube-packager` → `python3 scripts/gen_images.py <id> --thumbnail` (solo LONG) → `python3 scripts/thumbnail.py <id>`.
11. **Puertas finales**: primero la revisión visual, que haces TÚ porque los trabajadores no ven imágenes: `python3 scripts/studio.py sheet <id>`, abre `reviews/contact-sheet.png` y escribe `reviews/director-visual.md` (consistencia de personaje, de estilo, fidelidad al guion, defectos; veredicto PUBLICABLE / NO PUBLICABLE). Después `policy-guardian` → (si PASS) `quality-control`. Registra cada veredicto con `studio.py set <id> gates.<puerta> PASS|FAIL|STOP` y `quality_score`.
    - FIX/REJECT → trabajador responsable → repetir desde la etapa afectada → volver a pasar la puerta.
    - STOP de policy → BLOCKED inmediato para ese vídeo.
12. **Entrega**: `python3 scripts/studio.py deliver <id>` (falla si alguna puerta no es PASS). Nunca publiques en YouTube.

## Informe final (único texto para el usuario)
```
READY FOR REVIEW
VIDEO 1
- archivo:
- título:
- descripción:
- thumbnail:
- duración:
- score de calidad:      (y VPS estimado; es una estimación, no una predicción)
- revisar a mano:        (lo que QC no pudo verificar)
```
Si algo falla:
```
BLOCKED
- problema:
- trabajador responsable:
- solución propuesta:
```
