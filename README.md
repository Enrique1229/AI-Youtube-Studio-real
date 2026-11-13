# AI YouTube Studio — puesta en marcha

Sistema de producción de un canal de YouTube de ficción con IA, dirigido desde Claude Code.
Diseño: `ARCHITECTURE.md`. Resultados de las pruebas: `PILOT-REPORT.md`.

## Uso
Abre Claude Code en esta carpeta y escribe, por ejemplo: `Produce 3 Shorts y 1 vídeo largo.`
Los vídeos aprobados aparecen en `shorts/` y `long-videos/`. Nada se publica solo.

## Instalación en tu máquina
1. Python 3.10+ y FFmpeg.
2. `bash scripts/setup_models.sh` — dependencias y modelo de voz (~350 MB).
3. ComfyUI (github.com/comfyanonymous/ComfyUI): clónalo, instala su `requirements.txt` y arráncalo (`python main.py`).
4. Descarga un checkpoint a `ComfyUI/models/checkpoints/` y ajusta `studio.config.json → image`:
   - `workflow`: `templates/comfy/txt2img.json` sirve para cualquier checkpoint SD 1.5 o SDXL.
   - `params.ckpt`, `params.steps`, `params.cfg`, `size` (SDXL: 832x1472 y 1472x832) y `license`.
5. `bash scripts/check_tools.sh` — todo debe salir OK.
6. En Claude Code: `/studio-setup` para probar el motor y reescribir `channel/style-bible/engine.md`.

## Decisiones que son tuyas
- Idioma y voz del narrador: `channel/style-bible/narrative.md`, `voice.md` y `studio.config.json → tts`.
- Estilo visual: `channel/style-bible/visual.md`.
- Umbrales de calidad: `studio.config.json → vps_threshold`.

## Después de publicar
`python3 scripts/studio.py set <story-id> youtube_id <ID>`; más adelante, `scripts/import_metrics.py` (ver su cabecera) y `/analyze-channel`.
