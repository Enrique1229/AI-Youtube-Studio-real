---
name: studio-setup
description: Verifica e instala el motor audiovisual local (ComfyUI, TTS, Whisper, FFmpeg) y escribe channel/style-bible/engine.md. Úsalo al configurar una máquina nueva o cuando /produce reporte que falta una herramienta.
---
# /studio-setup — Motor audiovisual

1. `bash scripts/check_tools.sh` y anota GPU/VRAM.
2. Elige la configuración según hardware (tabla en `ARCHITECTURE.md` §10). Sin GPU: imágenes fijas + movimiento por FFmpeg, TTS en CPU.
3. ANTES de integrar cualquier modelo o nodo: verifica en su repositorio/model card oficial (a) que existe, (b) que ComfyUI lo soporta en la versión instalada, (c) que la licencia permite uso comercial, (d) VRAM requerida. Anota fuente y fecha. Si no puedes verificarlo, no lo integres.
4. Prueba real: genera 1 imagen, 1 audio de 10 s y 1 vídeo de prueba con `scripts/assemble.py`. Solo lo que haya funcionado se declara.
5. Escribe `channel/style-bible/engine.md` con SOLO capacidades probadas: modelo, licencia, resolución, tiempo por imagen/clip, duración máx. de clip, límites.
6. Exporta los workflows de ComfyUI en formato API a `templates/comfy/` (los usa `scripts/gen_images.py`).
