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
