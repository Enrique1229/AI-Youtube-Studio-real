---
name: analyze-channel
description: Ciclo de aprendizaje del canal. Úsalo cuando el usuario aporte métricas nuevas de YouTube o pida revisar la estrategia ("analiza el canal", "actualiza la estrategia").
---
# /analyze-channel — Analytics → Estrategia

1. Comprueba que `channel/analytics/videos.csv` existe y tiene filas nuevas (columnas en `templates/videos.csv`). Si el usuario pega datos o da un export de YouTube Studio, normalízalos a ese CSV (añade filas, no dupliques `story_id`).
2. `analytics-scientist` → `channel/analytics/insights.md`.
3. `strategy-manager` → propone cambios en `channel/strategy/strategy.md`.
4. Tú (Director) revisas el diff de strategy.md: acepta como máximo 3 cambios, rechaza los que no tengan evidencia suficiente.
5. Informa al usuario en ≤ 10 líneas: qué funciona, qué no, qué cambia en el próximo lote y con qué nivel de confianza.

Con menos de 10 vídeos publicados por formato, trata todo como hipótesis y no cambies el umbral de VPS.
