# AI YouTube Studio — Arquitectura

Estado (2026-11-13): Fases 1-3 ejecutadas. El pipeline completo funciona de extremo a extremo en CPU y los 20 trabajadores están probados (market-validator, solo a través de un agente genérico). Lo que falta para producir con calidad de canal es un motor de imagen mejor (GPU). Resultados de las pruebas: `PILOT-REPORT.md`. Puesta en marcha: `README.md`.

## 0. Decisiones de diseño que se apartan del encargo literal

| Decisión | Motivo |
|---|---|
| El EXECUTIVE DIRECTOR no es un subagente: es la sesión principal de Claude Code (Fable) guiada por `CLAUDE.md` y el skill `produce`. | En Claude Code los subagentes no pueden lanzar otros subagentes; solo la sesión principal puede delegar. |
| Dos pipelines: SHORT (ligero) y LONG (completo). En un Short, el Story Architect escribe una bible compacta que ya incluye personajes y mundo. | Un guion de 150 palabras no justifica 3 agentes de preproducción. Ahorra ~40 % de llamadas por Short. |
| Audience Analyst actúa después de la selección, una vez por lote. | Analizar audiencia de ideas que se van a descartar es gasto puro. |
| El Virality Potential Score lo calcula un script, no el Critic. | El Critic puntúa 11 criterios; la fórmula es determinista, auditable y ajustable por Strategy sin tocar prompts. |
| Modo visual por defecto: imágenes fijas con movimiento de cámara (FFmpeg). El vídeo generativo es opcional. | Es lo único viable sin GPU potente y lo más barato; el vídeo local es lento (minutos por clip de pocos segundos). |

## 1. Skills (procedimientos que sigue el Director)

| Skill | Cuándo |
|---|---|
| `produce` | "Produce N Shorts y M vídeos largos". Las 12 etapas, reglas de coste y formato de entrega. |
| `analyze-channel` | Hay métricas nuevas. Analytics → Strategy → cambios aprobados por el Director. |
| `studio-setup` | Configurar o verificar el motor audiovisual en una máquina. Escribe `engine.md`. |

Un skill es conocimiento de procedimiento cargado bajo demanda: no ocupa contexto hasta que se usa.

## 2. Subagentes (`.claude/agents/`, generados por `scripts/_gen_agents.py`)

| # | Trabajador | Modelo | Lee | Escribe |
|---|---|---|---|---|
| 1 | Executive Director | Fable (sesión principal) | `state.json`, bloques STATUS, reviews con fallo | `selected.json`, estado, informe final |
| 2 | trend-researcher | Sonnet + web | `strategy.md` | `channel/strategy/trends.md` |
| 3 | idea-generator | Sonnet | trends, strategy, ledger resumido | `ideas/<batch>/ideas.json` |
| 4 | content-critic | Sonnet | `ideas.json` | `ideas/<batch>/scores.json` |
| 4b | market-validator | Sonnet + web + `yt_lookup.py` | ideas sobre el umbral, `market.md` | `ideas/<batch>/market.json`, `channel/strategy/market.md` |
| 5 | audience-analyst | Haiku | `selected.json` | campo `audience` |
| 6 | story-architect | Sonnet | `idea.json`, `narrative.md` | `story-bible.md` |
| 7 | character-designer (solo LONG) | Sonnet | sección personajes | `characters.md` |
| 8 | world-builder (solo LONG) | Sonnet | sección mundo | `world.md` |
| 9 | story-writer | Sonnet | bible + resumen del capítulo anterior | `chapters/`, `scenes/`, `continuity.md` |
| 10 | continuity-manager | Sonnet | bible, fichas, capítulos | `reviews/continuity.md` |
| 11 | visual-director | Sonnet | escenas, bloques visuales, `engine.md` | `visual-prompts/shots.json` |
| 12 | voice-director | Haiku | capítulos, `voice.md` | `voice/narration.json` |
| 13 | video-editor | Haiku | shots, duraciones reales de audio | `final/edl.json` |
| 14 | shorts-specialist | Sonnet | bible del largo + capítulos indicados | nueva `stories/<id>/` por short |
| 15 | thumbnail-designer | Sonnet | idea, bloques visuales | `final/thumbnail.json` |
| 16 | youtube-packager | Haiku | idea, duración | `final/metadata.json` |
| 17 | policy-guardian | Sonnet | idea, guion, metadata, similitud | `reviews/policy.md` (PASS/FIX/STOP) |
| 18 | quality-control | Sonnet | `final/`, informe ffprobe, reviews | `reviews/qc.md` (PASS/REJECT, 0-100) |
| 19 | analytics-scientist | Sonnet | agregados de `studio.py analytics` | `channel/analytics/insights.md` |
| 20 | strategy-manager | Sonnet | insights, strategy | `channel/strategy/strategy.md` |

Fable solo interviene en: selección de ideas, conflictos entre agentes, decisión de BLOCKED y aprobación de cambios de estrategia.

## 3. Archivos de memoria

| Ámbito | Archivo | Contenido | Quién lo escribe |
|---|---|---|---|
| Canal | `channel/style-bible/{narrative,visual,voice,editing}.md` | Identidad del canal | Director + usuario |
| Canal | `channel/style-bible/engine.md` | Capacidades PROBADAS del motor audiovisual | `studio-setup` |
| Canal | `channel/strategy/strategy.md` | Umbrales, experimentos, packaging | strategy-manager |
| Canal | `channel/strategy/trends.md` | Señales vigentes (caduca a los 7 días) | trend-researcher |
| Canal | `channel/strategy/ideas-ledger.jsonl` | Todas las ideas, aceptadas y rechazadas | `studio.py ledger` |
| Canal | `channel/strategy/policy-checklist.md` | Checklist de monetización con fecha de verificación | Director |
| Canal | `channel/analytics/videos.csv`, `insights.md` | Métricas y patrones | usuario / analytics |
| Canal | `channel/characters/`, `channel/worlds/` | Solo personajes y mundos recurrentes (series) | designers |
| Historia | `stories/story-NNN/state.json` | Etapa, 4 puertas, scores, rondas de corrección | `studio.py` |
| Historia | `story-bible.md`, `characters.md`, `world.md`, `continuity.md` | Memoria propia y aislada de la historia | arquitecto, diseñadores, writer |
| Historia | `reviews/{continuity,policy,qc}.md` | Veredictos y correcciones | puertas |

## 4. Scripts (0 tokens de LLM)

| Script | Función | Estado |
|---|---|---|
| `studio.py` | `new`, `select`, `derive`, `close-batch`, `status`, `set`, `vps`, `ledger`, `similar`, `gate`, `probe`, `deliver`, `analytics` | Probado |
| `tts.py` | `narration.json` → `narration.wav`, `durations.json`, `timing.json` (Kokoro ONNX, CPU) | Probado |
| `gen_images.py` | `shots.json` → imágenes por la API HTTP de ComfyUI; backend `placeholder` solo para pruebas (marca la historia como no entregable) | Probado contra ComfyUI 0.45.0 real |
| `assemble.py` | EDL + imágenes + voz → mp4; reparte la duración según el audio real; escribe `provenance.json` (modelos y licencias) | Probado |
| `subtitles.py` | `timing.json` → `.srt`, `.ass` y vídeo final con subtítulos quemados | Probado |
| `thumbnail.py` | Imagen + texto → `thumbnail.jpg` | Probado |
| `audio_gen.py` | Música ambiental (4 moods) y efectos (whoosh, hit, riser, swell) sintetizados, sin terceros | Probado técnicamente; no evaluado de oído |
| `gen_video.py` | Anima los planos `i2v` con Wan 2.2 TI2V 5B en ComfyUI | Estructura validada contra ComfyUI 0.45.0; sin ejecutar (no había GPU) |
| `yt_lookup.py` | Vistas y suscriptores públicos de YouTube para la puerta de mercado | Probado; no es API oficial, puede romperse |
| `comfy.py` | Cliente de ComfyUI compartido (subida, ejecución, descarga) | Probado contra ComfyUI real |
| `import_metrics.py` | YouTube Analytics API → `videos.csv` | Probado solo contra una API simulada; necesita tus credenciales |
| `check_tools.sh`, `setup_models.sh` | Diagnóstico e instalación del modelo de voz | Probados |

Los subtítulos no usan reconocimiento de voz: el texto es el del guion y el tiempo de cada frase lo mide el TTS. Dentro de la frase, las palabras se reparten por longitud.
El vídeo generado está implementado pero desactivado (`video_gen.enabled: false`) hasta que `/studio-setup` lo pruebe en una GPU.

## 5. Hooks y automatizaciones

| Mecanismo | Qué hace | Estado |
|---|---|---|
| Hook `SessionStart` | Imprime el estado de las producciones en curso: retomar un lote no cuesta relectura. | Verificado en una sesión real |
| `studio.py select` | Se niega a crear una historia si su VPS no llega al umbral o si no tiene validación de mercado VALIDATED/WEAK (salvo `--force`). | Probado |
| `studio.py deliver` | Se niega a entregar si alguna puerta no es PASS, si no hay vídeo final o si las imágenes son de prueba. | Probado |
| Tarea programada semanal (opcional) | Refrescar `trends.md` y recordar importar métricas. | No creada: decide tú si la quieres |
| Publicación en YouTube | No automatizada, por diseño. | — |

No añado más hooks: cada hook inyecta texto en el contexto y los controles importantes ya son scripts.

## 6. Estructura de carpetas

```
ai-youtube-studio/
├── CLAUDE.md  ARCHITECTURE.md
├── .claude/{agents/ (19), skills/{produce,analyze-channel,studio-setup}, settings.json}
├── studio.config.json   motor, voz, umbrales, licencias
├── scripts/      studio.py tts.py gen_images.py assemble.py subtitles.py thumbnail.py import_metrics.py check_tools.sh setup_models.sh _gen_agents.py
├── templates/    idea, scores, story-bible, character, world, scene, shots, narration, edl, thumbnail, metadata, videos.csv, comfy/ (2 workflows)
├── channel/
│   ├── style-bible/   narrative  visual  voice  editing  engine
│   ├── strategy/      strategy  trends  ideas-ledger.jsonl  policy-checklist
│   ├── analytics/     videos.csv  insights
│   ├── characters/    worlds/          (solo recurrentes)
├── ideas/<batch>/     ideas.json  scores.json  selected.json
├── stories/story-NNN/ state.json idea.json story-bible characters world continuity
│                      chapters/ scenes/ visual-prompts/ voice/ assets/ final/ reviews/
├── shorts/            entregas aprobadas
└── long-videos/       entregas aprobadas
```

## 7. Interfaces entre trabajadores

- Entrada: el Director pasa el id de historia y rutas. Nunca texto pegado.
- Salida: archivos con esquema fijo (`templates/`). Los JSON son el contrato entre agentes y scripts.
- Respuesta al Director, máximo 8 líneas:
  ```
  STATUS: DONE | NEEDS_FIX | BLOCKED
  FILES: ...
  SUMMARY: (2 líneas)
  ISSUES: (con trabajador responsable)
  ```
- Correcciones: la puerta escribe `reviews/<puerta>.md` con archivo:línea, corrección concreta y responsable. El Director reenvía al responsable solo esa ruta.

## 8. Control de tokens

1. Modelo por dificultad: Haiku para transformaciones (voz, EDL, metadata, audiencia), Sonnet para creación y juicio, Fable solo para decidir.
2. Contexto mínimo: cada agente tiene su lista de "Entrada"; no explora. El writer lee la bible y el resumen del capítulo anterior, no los capítulos anteriores.
3. Tope de tamaño en cada salida (bible ≤ 40/120 líneas, trends ≤ 60, insights ≤ 50, strategy ≤ 80).
4. El Director no lee el trabajo, solo los bloques STATUS; el contenido va de disco a disco.
5. Lo determinista va a scripts: score, similitud, estado, sondeo técnico, agregados de analytics.
6. Caché en disco: trends 7 días; ledger evita regenerar o reevaluar ideas; `state.json` evita repetir etapas.
7. Embudo: se generan 4 ideas baratas por vídeo y solo las aprobadas llegan a las etapas caras.
8. Límite de 2 rondas de corrección por puerta.
9. Paralelismo donde no hay dependencia (no ahorra tokens, sí tiempo).

Pendiente de medir: el coste real por Short y por largo se conocerá tras el primer lote; se anotará en `strategy.md`.

## 9. Pipeline

```
orden → preflight → [trends si caducó] → ideas ×4 → critic → VPS (script) ── puerta 1: critic
      → market-validator (canales reales comparables) ── puerta 2: market
      → selección (Director)
      → audiencia (1 llamada)
      → SHORT: architect → writer ─────────────────────────┐
        LONG:  architect → characters ∥ world → writer×cap ┤→ continuity ── puerta 3
               └→ shorts-specialist (derivados)            ┘
      → visual ∥ voz → TTS → imágenes [→ vídeo] → EDL → montaje → subtítulos
      → thumbnail ∥ packaging
      → revisión visual (Director) → policy ── puerta 4 → QC ── puerta 5 → deliver → READY FOR REVIEW
fallo en una puerta → responsable → corrección → misma puerta (máx. 2) → BLOCKED
```

VPS = Σ pesos × nota/10 − penalizaciones. Pesos: hook 20, curiosidad 15, retención 15, originalidad 12, final 10, visual 8, emoción 8, serie 6, diferenciación 6. Penalización: dificultad hasta 5, riesgo de repetición hasta 10. Es una estimación de potencial, no una predicción; los pesos se recalibran cuando haya métricas reales.

## 10. Herramientas gratuitas / locales

Licencias leídas en los metadatos de Hugging Face el 2026-11-13; el resto, en la fuente que se indica.

| Capa | Opción | Licencia / límite verificado | Probado aquí |
|---|---|---|---|
| Voz | Kokoro-82M (kokoro-onnx) | Apache-2.0. Voces es: em_alex, em_santa, ef_dora | Sí, CPU |
| Voz | Chatterbox (Resemble) | MIT | No |
| Voz | XTTS-v2 (Coqui) | Coqui Public Model License (no comercial): descartada | — |
| Imagen | ComfyUI + Stable Diffusion 1.5 (+ LCM LoRA) | CreativeML OpenRAIL-M / OpenRAIL++ | Sí, CPU, ~2 min/imagen, calidad baja |
| Imagen | SDXL base 1.0 | OpenRAIL++ | No (GPU) |
| Imagen | FLUX.1 schnell | Apache-2.0 | No (GPU) |
| Imagen | FLUX.1 dev | Licencia no comercial: descartada | — |
| Imagen | DreamShaper (Lykon) | "other", sin aclarar: no usar hasta leerla | — |
| Vídeo | Wan 2.2 (TI2V-5B, I2V/T2V-A14B) | Apache-2.0; docs.comfy.org: soporte nativo en ComfyUI y "The Wan2.2 5B version should fit well on 8GB vram" | No (GPU) |
| Vídeo | LTX-Video | "other", sin aclarar: no usar hasta leerla | — |
| Subtítulos | Guion + tiempos del TTS | Sin dependencias | Sí |
| Subtítulos | faster-whisper (alternativa) | MIT | Funciona en CPU; no se usa |
| Edición | FFmpeg | — | Sí |
| Música | Biblioteca de audio de YouTube | "copyright-safe"; las pistas Creative Commons exigen atribución. Descarga manual | No integrada |
| Texto local | Qwen3-4B (GGUF Q4, llama.cpp) | Apache-2.0 | Sí: ver abajo |
| Tendencias | YouTube Data API v3 | Por defecto: 100 llamadas `search.list` al día y 10 000 unidades diarias para el resto | No integrada |
| Analytics | YouTube Analytics API, informe "Top videos" | Máximo 200 vídeos por consulta; el CTR de miniatura no está entre sus métricas | Solo simulada |

**Modelo de texto local, evaluación real (Qwen3-4B en 4 CPU):** la tarea de metadata devolvió JSON válido con 5 títulos dentro del límite, pero tardó 274 s (medido con la CPU compartida con ComfyUI; sin competencia será más rápido, no medido). En la tarea de normalizar la narración falló: eliminó toda la puntuación (que es lo que da la prosodia al TTS), ignoró la segmentación pedida y dejó el JSON truncado. Conclusión: en CPU no sustituye a Haiku; no se integra. Reevaluar con GPU y un modelo de 7-14 B.

Configuración según hardware:

| Hardware | Qué se puede producir |
|---|---|
| Sin GPU (este contenedor) | Todo el pipeline, con imágenes SD 1.5 de 512 px a ~2 min cada una. Un Short de 18 planos: ~35 min de imágenes. Un largo de 150 planos: ~5 h. Calidad visual insuficiente para un canal. |
| GPU 8-12 GB | SDXL o FLUX schnell a resolución nativa en segundos por imagen. Punto de partida recomendado. |
| GPU 16-24 GB | Lo anterior + clips Wan 2.2 en planos clave (requiere implementar el workflow de vídeo). |

## 11. Lo que no se puede automatizar del todo

1. Publicar en YouTube y marcar "AI use" al subir: manual por diseño.
2. Ver y oír el vídeo: Quality Control revisa archivos e informes técnicos, no percibe el resultado. Artefactos visuales, voz rara o un ritmo que no funciona solo los detecta tu revisión.
3. Calidad de imagen: depende de tener GPU y de elegir modelo. Con CPU el sistema funciona pero el resultado no es publicable.
4. Vídeo generado: implementado sobre la plantilla oficial de Wan 2.2 5B, pero sin ejecutar nunca. La documentación oficial habla de 8 GB; en 6 GB hay que medirlo. Si no funciona, queda la opción de un ComfyUI remoto (`image.comfy_url`).
5. Consistencia visual de personajes entre planos: se mitiga (bloque visual fijo, seed), no se garantiza.
6. Métricas: la API exige crear un proyecto en Google Cloud y autorizar con tu cuenta; el CTR hay que copiarlo a mano.
7. Música: el sistema sintetiza ambiente y efectos, pero no compone melodías. Para música de verdad hay que descargar pistas y anotar su licencia.
7b. Mercado: `yt_lookup.py` da vistas y suscriptores, nunca ingresos ni estado de monetización.
8. Monetización: el Guardian reduce riesgo, no garantiza la aprobación. La norma de YouTube cita expresamente los "image slideshows" y las plantillas de IA; la defensa es narrativa propia y variedad real.
9. Viralidad: no predecible. Los umbrales de VPS son arbitrarios hasta que haya métricas con las que calibrarlos.

## 12. Plan por fases

| Fase | Entregable | Estado |
|---|---|---|
| 1. Andamiaje | Agentes, skills, memoria, plantillas, `studio.py`, puertas | Hecha |
| 2. Motor audiovisual | Voz, imágenes por ComfyUI, montaje, subtítulos, thumbnail | Hecha en CPU; pendiente repetir `/studio-setup` en una máquina con GPU |
| 3. Piloto | 1 Short de extremo a extremo y prueba de los 19 trabajadores | Hecha: ver `PILOT-REPORT.md` |
| 4. Producción | Primer lote "3 Shorts + 1 largo" con un modelo de imagen de calidad | Pendiente de GPU y de tus decisiones (idioma, voz, estilo) |
| 5. Aprendizaje | `analyze-channel` con métricas reales; recalibrar pesos y umbrales del VPS | Con ≥ 10 vídeos publicados por formato |

