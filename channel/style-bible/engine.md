# Motor audiovisual — capacidades PROBADAS (2026-11-13, contenedor cloud: 4 CPU, 15 GB RAM, sin GPU)
Configuración activa: `studio.config.json`. Este archivo solo declara lo que se ha ejecutado de verdad.

## Probado y funcionando
- TTS: Kokoro-82M v1.0 vía `kokoro-onnx` en CPU. Licencia Apache-2.0. Voces en español: em_alex, em_santa, ef_dora. 55 s de audio en ~4 s. Sin etiquetas de emoción: la expresividad solo se controla con puntuación, velocidad y pausas.
- Imágenes: ComfyUI 0.45.0 en modo `--cpu`, por su API HTTP (`/prompt`, `/history`, `/view`).
  - `templates/comfy/txt2img.json` (workflow por defecto de ComfyUI): probado con Stable Diffusion 1.5, 20 pasos, 512x896.
  - `templates/comfy/txt2img_sd15_lcm.json` (SD 1.5 + LCM LoRA, 6 pasos, cfg 1.5): ~1 min 55 s por imagen de 512x896 en CPU. ES EL ACTIVO.
  - Licencias: SD 1.5 CreativeML OpenRAIL-M; LCM LoRA OpenRAIL++.
  - Calidad: SD 1.5 a 512 px es floja para un canal (poco detalle, manos y caras débiles, no respeta bien prompts largos). Sirve para validar el pipeline, no como estándar de producción.
- Montaje: FFmpeg. Solo IMÁGENES FIJAS con movimiento: zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, static. Transición: corte. Salida 1080x1920 (short) / 1920x1080 (long), 30 fps. Las imágenes de 512 px se escalan: se nota.
- Subtítulos: desde el guion y los tiempos del TTS, quemados con libass.
- Thumbnail: Pillow (texto sobre imagen).

## NO disponible
- Vídeo generativo (i2v/t2v): no implementado. Usa siempre `type: "still"`.
- Música y SFX: no hay biblioteca. `music: null`.
- Modelos de imagen mejores (SDXL, FLUX schnell): requieren GPU; no probados aquí.

## Reglas para prompts de imagen con el motor activo (SD 1.5)
- Inglés, máximo ~60 palabras (el codificador de texto corta a 77 tokens: lo importante, al principio).
- Un solo sujeto y una sola acción por imagen. Evita manos en primer plano, texto, números y multitudes.
- Mismos bloques visuales fijos de personaje y lugar en cada plano.
