# Instalación en un PC con GPU NVIDIA (Windows, PowerShell)

Probado en Windows 11 con una RTX 4050 Laptop (6 GB) hasta arrancar ComfyUI con GPU (pasos 1-6, 2026-11-13). Los pasos 7-8 y la generación con SDXL en 6 GB están pendientes de confirmar.
Si Claude Code da `Connection refused`, revisa variables `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_MODEL` que apunten a un intermediario local apagado.
Los comandos de ComfyUI son los de su README oficial (consultado el 2026-11-13).

1. Herramientas: `winget install Git.Git`, `winget install Python.Python.3.12`, `winget install Gyan.FFmpeg`, `winget install OpenJS.NodeJS.LTS`, y `npm install -g @anthropic-ai/claude-code`. Cierra y abre PowerShell.
2. Proyecto: `git clone https://github.com/Enrique1229/AI-Youtube-Studio-real` y dentro: `pip install -r requirements.txt`.
3. Voz (dentro del proyecto): crea `models` y descarga `kokoro-v1.0.onnx` y `voices-v1.0.bin` de https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/ .
4. ComfyUI (fuera del proyecto): `git clone https://github.com/comfyanonymous/ComfyUI`, entorno virtual, `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130` (con `--index-url`, no `--extra-index-url`: con el segundo, en Windows pip instaló la versión sin GPU). Comprueba con `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`: debe decir `+cu130 True`, `pip install -r requirements.txt`.
5. Modelo: `sd_xl_base_1.0.safetensors` (6,9 GB) de https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 a `ComfyUI\models\checkpoints\`.
6. Arranca ComfyUI con `python main.py` y déjalo abierto.
7. En el proyecto: `copy studio.config.gpu-sdxl.json studio.config.json`.
8. Abre `claude` en la carpeta del proyecto y escribe `/studio-setup`; después, `Produce 1 Short.` como primera prueba.

Tarjetas NVIDIA serie 10 o anteriores: usa el ComfyUI portable "cu126" de la página de releases en lugar del paso 4.
