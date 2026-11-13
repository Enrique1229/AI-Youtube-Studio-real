# Informe del piloto — 2026-11-13

Entorno: contenedor en la nube, 4 CPU, 15 GB RAM, sin GPU.

## Resultado
| Historia | Tipo | Estado | Motivo |
|---|---|---|---|
| story-001 "El botón sin número" | Short 55 s | BLOCKED (QC 61/100) | Imágenes no publicables: SD 1.5 a 512 px no mantiene personaje ni estilo. Guion, voz, montaje, subtítulos y política: correctos. |
| story-002 "El pozo de los nombres" | Largo | En escritura, 2 de 4 capítulos | Prueba técnica: su idea (VPS 66,6) no llega al umbral de 70 y se forzó solo para probar el pipeline largo. Decide si continuarla o borrarla. |
| story-003 "El nombre tibio" | Short derivado de story-002 | Guion escrito | Pendiente de continuidad y producción. |

Ningún vídeo se entrega como READY FOR REVIEW.

## Qué quedó verificado
- Los 19 trabajadores ejecutaron su tarea real al menos una vez. En esta sesión se invocaron a través de un agente genérico que leía su definición; aparte, una sesión real de Claude Code abierta en el proyecto confirmó que carga los 19 agentes, los 3 skills y el hook de inicio. Falta ver un `/produce` completo lanzado como skill.
- Las 4 puertas actuaron: el crítico descartó 11 de 12 ideas; continuidad encontró una pista sin resolver y el guionista la corrigió en una ronda; policy bloqueó las imágenes de prueba y aprobó tras regenerarlas; QC rechazó por calidad visual.
- El umbral frenó el vídeo largo: dos rondas de ideas (8 ideas) quedaron en 53-67 frente a un umbral de 70.
- ComfyUI 0.45.0 real: los dos workflows generan imágenes desde `gen_images.py`.
- `deliver` se negó en los tres casos probados: puertas pendientes, imágenes de prueba, QC en FAIL.

## Tiempos medidos (CPU)
- Voz: 55 s de audio en ~4 s.
- Imagen: ~1 min 55 s por imagen (SD 1.5 + LCM, 6 pasos, 512x896). 18 imágenes: ~35 min. Sin LCM, 20 pasos: ~5 min sin competencia de CPU.
- Montaje + subtítulos de un Short: menos de 1 minuto.

## Coste en tokens (medido, con reservas)
- 18 ejecuciones de trabajadores para el Short, incluida la ronda de corrección y la repetición de las dos puertas finales. Cada una reportó entre 79 000 y 99 000 tokens acumulados.
- Esa cifra suma el contexto base del agente genérico usado en la prueba, releído en cada paso. Con los agentes propios (herramientas restringidas) debería ser bastante menor; no está medido.
- El investigador de tendencias es el más caro por las búsquedas web; se ejecuta como mucho una vez cada 7 días.

## Lecciones aplicadas al sistema durante el piloto
1. Bloques visuales de personaje y lugar siempre en inglés.
2. El editor no escribe tiempos: los calcula el script desde el audio real.
3. Selección de ideas, historias derivadas y cierre de lote pasaron a ser comandos (`select`, `derive`, `close-batch`).
4. Cada vídeo guarda `provenance.json` con modelos y licencias.
5. Revisión visual obligatoria del Director con hoja de contactos (`studio.py sheet`): ningún trabajador ve imágenes.
6. `ai_use_disclosure` explícito en la metadata.

## Pendiente
- Repetir `/studio-setup` en la máquina con GPU (RTX 4050 Laptop, 6 GB) y validar SDXL con el estilo de ilustración.
- Regenerar las imágenes de story-001 allí y volver a pasar QC.
- Calibrar los umbrales de VPS: el crítico es severo y 70 para largos puede ser inalcanzable en la práctica; no hay datos para decidirlo.
- Música y efectos; vídeo generativo; métricas reales.

---
# Segunda ronda — 2026-11-13 (tarde)

## Evidencia de mercado (búsqueda pública de YouTube, `scripts/yt_lookup.py`)
Detalle y cifras en `channel/strategy/market.md`. En resumen:
- Shorts de ficción de misterio/sci-fi con IA (formato principal del plan): mucha oferta y casi ninguna tracción. 27 Shorts muestreados, la mayoría con menos de 1.000 vistas; decenas de canales clónicos de 3 a 539 suscriptores. Veredicto WEAK.
- Vídeos de 6-10 min del mismo formato: 4-1.264 vistas en la muestra. Veredicto NO_EVIDENCE.
- Lo que sí muestra tracción es otro formato: relato de ciencia ficción narrado de 25-60 min, tipo audiolibro (canales de hasta 170 K suscriptores; vídeos recientes con 70-230 K vistas; en español, Nebula SciFi con 15,9 K suscriptores).
- Las vistas no prueban monetización, y ese formato tiene sus propios riesgos (relatos reutilizados, clones sin vistas).

## Añadido al sistema
- Quinta puerta, `market`: `market-validator` + `yt_lookup.py`; `select` rechaza ideas sin comparables.
- Música ambiental y efectos sintetizados (`audio_gen.py`), mezclados y limitados a -1,7 dB de pico.
- Vídeo generado en planos clave (`gen_video.py`, Wan 2.2 TI2V 5B). El ComfyUI real aceptó el grafo completo salvo los tres archivos de modelo ausentes; la subida de imagen y la recogida de vídeo se ejecutaron de verdad. Nunca se ha generado un clip.
- Subtítulos: los trozos ya no terminan en artículo o preposición.
- Umbral del largo: 70 → 65 (provisional).

## Short "El nombre tibio" (story-003) con los agentes reales
- Resultado: BLOCKED. QC 58/100. Política PASS a la segunda (pidió justificar la derivación y la validación de mercado). Sin errores técnicos.
- Motivos: el protagonista cambia de aspecto en cada plano; los nombres grabados no aparecen; arranque con exposición; subtítulos mal cortados (corregido después).
- El estilo de ilustración mantuvo la paleta en 14 de 16 planos: mejora clara frente al piloto realista.

## Coste real por trabajador (agentes propios)
| Trabajador | Tokens |
|---|---|
| story-architect | 16.565 |
| continuity-manager | 17.746 |
| visual-director | 20.345 (+20.192 en la corrección) |
| voice-director | 15.290 |
| video-editor | 17.975 (+17.559 en la corrección) |
| thumbnail-designer | 15.251 |
| youtube-packager | 13.578 |
| policy-guardian | 19.786 + 26.223 |
| quality-control | 24.028 |
Total medido en este Short: ~245.000 tokens en 12 ejecuciones (incluye dos rondas de corrección). No incluye ideas, crítico, mercado, audiencia ni guionista, que aquí se ejecutaron con el agente genérico (79.000-99.000 cada uno, cifra inflada). Estimación para un Short completo con agentes propios: 330.000-400.000 tokens. El validador de mercado y el investigador de tendencias son los más caros por las búsquedas web.

## Pendiente (solo se puede cerrar en la máquina con GPU)
- `/studio-setup` con SDXL en la RTX 4050 (6 GB): tiempo por imagen y calidad con el estilo de ilustración.
- Prueba de vídeo generado (17 GB de modelos): puede no funcionar en 6 GB.
- Consistencia de personaje: no resuelta. Es el principal motivo de rechazo en los dos Shorts.
- Decisión del usuario sobre el formato, a la vista de la evidencia de mercado.
