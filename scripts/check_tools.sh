#!/usr/bin/env bash
# Informe de herramientas disponibles. No instala nada.
cd "$(dirname "$0")/.."
ok(){ printf "OK    %s\n" "$1"; }; no(){ printf "FALTA %s\n" "$1"; }
for t in ffmpeg ffprobe python3; do command -v $t >/dev/null && ok $t || no $t; done
if command -v nvidia-smi >/dev/null; then ok "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)"; else no "GPU NVIDIA (sin ella: solo imágenes fijas + FFmpeg, TTS en CPU)"; fi
curl -s -m 2 "${COMFY_URL:-http://127.0.0.1:8188}/system_stats" >/dev/null 2>&1 && ok "ComfyUI en ${COMFY_URL:-http://127.0.0.1:8188}" || no "ComfyUI (no responde en ${COMFY_URL:-http://127.0.0.1:8188})"
for m in PIL kokoro_onnx soundfile; do python3 -c "import $m" 2>/dev/null && ok "python:$m" || no "python:$m"; done
[ -s models/kokoro-v1.0.onnx ] && ok "modelo TTS" || no "modelo TTS (bash scripts/setup_models.sh)"
B=$(python3 -c "import json;print(json.load(open('studio.config.json'))['image']['backend'])")
L=$(python3 -c "import json;print(json.load(open('studio.config.json'))['image']['license'])"); echo "      licencia imágenes: $L"
[ "$B" = placeholder ] && no "image.backend=placeholder: los vídeos NO son entregables (configura ComfyUI)" || ok "image.backend=$B"
grep -q "NO CONFIGURADO" channel/style-bible/engine.md && no "engine.md sin configurar (/studio-setup)" || ok "engine.md"
exit 0
