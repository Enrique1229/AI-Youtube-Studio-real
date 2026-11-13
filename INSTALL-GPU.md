# Instalación en un PC con GPU NVIDIA (Windows, PowerShell)

Probado en Windows 11 con una RTX 4050 Laptop (6 GB) de principio a fin (2026-11-13): SDXL genera en 6 GB a ~70-85 s por imagen de 832x1472. Tiempos y límites medidos: `channel/style-bible/engine.md`.
Si Claude Code da `Connection refused`, revisa variables `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_MODEL` que apunten a un intermediario local apagado.
Los comandos de ComfyUI son los de su README oficial (consultado el 2026-11-13).

1. Herramientas: `winget install Git.Git`, `winget install Python.Python.3.12`, `winget install Gyan.FFmpeg`, `winget install OpenJS.NodeJS.LTS`, y `npm install -g @anthropic-ai/claude-code`. Cierra y abre PowerShell.
2. Proyecto: `git clone https://github.com/Enrique1229/AI-Youtube-Studio-real` y dentro: `python3 -m pip install -r requirements.txt` (con `python3`, que es el intérprete que usan los scripts; en Windows puede no ser el mismo que `pip`).
3. Voz (dentro del proyecto): crea `models` y descarga `kokoro-v1.0.onnx` y `voices-v1.0.bin` de https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/ . La fuente de los subtítulos (Inter Display) va en `models/fonts/`: desde Git Bash, `bash scripts/setup_models.sh` descarga las dos cosas.
4. ComfyUI (fuera del proyecto): `git clone https://github.com/comfyanonymous/ComfyUI`, entorno virtual, `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130` (con `--index-url`, no `--extra-index-url`: con el segundo, en Windows pip instaló la versión sin GPU). Comprueba con `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`: debe decir `+cu130 True`, `pip install -r requirements.txt`.
5. Modelo: `sd_xl_base_1.0.safetensors` (6,9 GB) de https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 a `ComfyUI\models\checkpoints\`.
6. Arranca ComfyUI con `python main.py` y déjalo abierto.
7. En el proyecto: `copy studio.config.gpu-sdxl.json studio.config.json`.
8. Abre `claude` en la carpeta del proyecto y escribe `/studio-setup`; después, `Produce 1 Short.` como primera prueba.

Tarjetas NVIDIA serie 10 o anteriores: usa el ComfyUI portable "cu126" de la página de releases en lugar del paso 4.

## Opcional: vídeo generado en planos clave (Wan 2.2 TI2V 5B, Apache-2.0)
Son 17 GB de descarga. En una tarjeta de 6 GB no está garantizado que funcione: `/studio-setup` lo mide.
Con ComfyUI apagado, desde `C:\Users\<tú>\ComfyUI`:

    curl.exe -L -C - -o models\diffusion_models\wan2.2_ti2v_5B_fp16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors
    curl.exe -L -C - -o models\vae\wan2.2_vae.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors
    curl.exe -L -C - -o models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors

Después, en Claude Code: "ejecuta la prueba de vídeo de /studio-setup".
El workflow `templates/comfy/i2v_wan22_5b.json` reproduce la plantilla oficial de ComfyUI; aquí se validó su estructura contra ComfyUI 0.45.0, pero no se ha generado ningún clip con él (no había GPU).
