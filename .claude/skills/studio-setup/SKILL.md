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

## Vídeo generado (opcional, plan A: local)
Solo si el usuario lo pide o `video_gen.enabled` debe activarse. Modelo: Wan 2.2 TI2V 5B (Apache-2.0); la documentación oficial dice que cabe en 8 GB con el offloading de ComfyUI. En tarjetas de menos memoria puede ir muy lento o fallar: hay que medirlo.
1. Comprueba que existen en ComfyUI: `models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors`, `models/vae/wan2.2_vae.safetensors`, `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` (enlaces en INSTALL-GPU.md). Si falta alguno, dilo y para.
2. Reinicia ComfyUI para que liste los modelos nuevos.
3. Prueba: en una historia con imágenes, marca UN plano como `"type": "i2v"` con `motion_prompt`, pon `video_gen.enabled` a true y ejecuta `python3 scripts/gen_video.py <id> --test`. Anota tiempo y si hubo error de memoria.
4. Si falla por memoria: baja `video_gen.size` (p. ej. 384x672) y `video_gen.length` (25 o 33) y repite UNA vez. Si sigue fallando, deja `video_gen.enabled` en false y escríbelo en engine.md.
5. Si funciona: mira el clip (extrae 3 fotogramas con ffmpeg y ábrelos). Si es aceptable, deja `enabled` true, y escribe en engine.md: modelo, resolución, fotogramas, tiempo por clip y `max_per_short` razonable para ese tiempo (objetivo: menos de 30 min de vídeo generado por Short).
