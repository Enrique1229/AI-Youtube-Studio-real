---
name: produce-anim
description: Produce Shorts de animación 3D de comedia por niveles de IQ (formato ANIMACIÓN, Blender por código). Úsalo cuando el usuario pida "shorts de animación", "episodios de IQ" o "Produce N Shorts" y el formato activo del canal sea animación.
---
# /produce-anim — Shorts de animación por niveles

Eres el EXECUTIVE DIRECTOR. Reglas de coste y de puertas: las mismas del skill `produce`. Formato: `anim/FORMAT.md`.

1. **Ideas**: `gag-writer` → `ideas/<batch>/ideas.json` (4 por vídeo pedido).
2. **Evaluación**: `content-critic` → `scores.json` → `python3 scripts/studio.py vps …`. En `visual` puntúa si el gag se entiende sin palabras.
3. **Mercado**: el formato ya está validado en `channel/strategy/market.md` (caduca a los 30 días). Si no ha caducado, copia ese veredicto a `ideas/<batch>/market.json` para las ideas sobre el umbral; si caducó, `market-validator`.
4. **Selección**: `python3 scripts/studio.py select <batch> <idea-id> "<título>"` y `close-batch`.
5. **Animación**: `animation-director` → `anim/episodes/<id>.py`. Debe haber mirado fotogramas de cada nivel.
6. **Revisión del Director (obligatoria)**: renderiza 3 fotogramas por nivel, míralos tú y escribe `stories/<id>/reviews/director-visual.md`: ¿se entiende cada gag sin palabras? ¿el remate es claro? ¿algo atraviesa el suelo o queda fuera de cuadro? Si no, vuelve al paso 5 (máx. 2 rondas).
7. **Render**: un nivel tras otro con `anim/run_level.py` a `stories/<id>/assets/render/l<n>/`. Es lento: no lo lances hasta pasar el paso 6.
8. **Montaje**: `python3 scripts/anim_build.py stories/<id>/assets/render stories/<id>/final/video.mp4 --iq <lista>`; fija `final_file` y `duration_s` con `studio.py set`.
9. **Packaging**: `youtube-packager` (sin narración: título con la fórmula, descripción corta, `ai_use_disclosure` false: es animación, no imagen realista).
10. **Puertas**: marca `continuity` como PASS (no aplica: no hay historia que contradecir) → `policy-guardian` → `quality-control` (dale `director-visual.md` y `anim-check.md`).
11. **Entrega**: `python3 scripts/studio.py deliver <id>` y el informe READY FOR REVIEW / BLOCKED.

Lo que el sistema NO puede juzgar: si el vídeo hace gracia y si el sonido acompaña. Dilo siempre en "revisar a mano".
