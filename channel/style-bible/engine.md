# Motor audiovisual — capacidades PROBADAS (2026-11-13, Windows 11, RTX 4050 Laptop 6 GB VRAM, 16 GB RAM)
Configuración activa: `studio.config.json` (igual a `studio.config.gpu-sdxl.json`). Este archivo solo declara lo que se ha ejecutado de verdad en esta máquina.

## Probado y funcionando
- Imágenes: ComfyUI 0.45.0 con GPU (PyTorch 2.14.1+cu130), por su API HTTP (`/prompt`, `/history`, `/view`).
  - Modelo: Stable Diffusion XL base 1.0 (`sd_xl_base_1.0.safetensors`). Licencia OpenRAIL++ (Hugging Face, comprobada el 2026-11-13).
  - Workflow: `templates/comfy/txt2img.json`, 25 pasos, cfg 7, euler/normal.
  - Resolución: 832x1472 (9:16) y 1472x832 (16:9). Ambas probadas.
  - Tiempo medido: 69-84 s por imagen (~2,4 s/paso; la primera tarda más por la carga del modelo). Sin errores de memoria: ComfyUI carga el modelo por partes en los 6 GB.
  - Estimación a ese ritmo: Short de 18 planos ≈ 22-25 min de imágenes; largo de 150 planos ≈ 3 h.
  - Calidad observada (3 imágenes): aspecto cinematográfico, paleta y luz respetadas, mano y cara correctas en planos sencillos. Fallos vistos: el "botón sin número" salió con un símbolo dentro; los rótulos pequeños salen como garabatos ilegibles. La consistencia de personaje entre planos NO se ha probado.
- TTS: Kokoro-82M v1.0 vía `kokoro-onnx` en CPU. Licencia Apache-2.0. Voces en español: em_alex, em_santa, ef_dora. 11,9 s de audio en ~8 s (incluye cargar el modelo). Sin etiquetas de emoción: la expresividad solo se controla con puntuación, velocidad y pausas.
- Montaje: FFmpeg. IMÁGENES FIJAS con movimiento: zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, static. Transición: corte. Salida 1080x1920 (short) / 1920x1080 (long), 30 fps, h264/aac. 12 s de vídeo con 3 planos: 24 s de montaje.
- Subtítulos: desde el guion y los tiempos del TTS, quemados con libass. Fuente Inter Display (SIL OFL 1.1) servida desde `models/fonts/` (la descarga `scripts/setup_models.sh`), no del sistema.
- Thumbnail: Pillow (texto sobre imagen), misma fuente.
- Hoja de contactos (`studio.py sheet`) y `studio.py probe`: probados.
- Música y efectos: sintetizados por `scripts/audio_gen.py` (sin terceros). Música ambiental: tension, mystery, melancholy, wonder. Efectos: whoosh, hit, riser, swell. Probados en la mezcla (mystery + whoosh; media -15,8 dB, pico -1,9 dB). Es ambiente, no melodía; no se ha evaluado de oído.

## NO disponible
- Vídeo generativo (i2v/t2v): `video_gen.enabled` = false. Los modelos de Wan 2.2 TI2V 5B no están descargados en esta máquina (17 GB) y no se ha generado ningún clip. Usa siempre `type: "still"`.
- Música de archivo: no hay biblioteca descargada (se puede usar una pista propia indicándola en el EDL).
- FLUX schnell y otros modelos de imagen: no probados.
- SD 1.5 + LCM (`templates/comfy/txt2img_sd15_lcm.json`): se probó solo en CPU en otra máquina; aquí no está el modelo.

## Reglas para prompts de imagen con el motor activo (SDXL base 1.0)
- Inglés, máximo ~60 palabras (el codificador de texto corta a 77 tokens: lo importante, al principio).
- Un solo sujeto y una sola acción por imagen. Evita manos en primer plano, multitudes y cualquier texto, número o rótulo legible (no los dibuja bien).
- Si un objeto debe estar "en blanco" o "sin número", dilo en el prompt y refuérzalo en el negativo (numbers, symbols, digits).
- Mismos bloques visuales fijos de personaje y lugar, en inglés y cortos, en cada plano.

## Requisitos de arranque en esta máquina
- ComfyUI debe estar abierto: en `C:\Users\<tú>\ComfyUI`, `venv\Scripts\python.exe main.py`.
- Los scripts se ejecutan con `python3` y fuerzan UTF-8 en Windows (`scripts/_utf8.py`).
