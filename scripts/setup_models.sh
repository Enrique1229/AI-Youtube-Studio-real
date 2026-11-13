#!/usr/bin/env bash
# Instala dependencias de Python y descarga el modelo TTS (Kokoro ONNX, ~350 MB) desde Hugging Face.
set -e; cd "$(dirname "$0")/.."
pip install -q -r requirements.txt
mkdir -p models
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s models/$f ] || curl -fL --retry 3 -o models/$f https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/$f
done
ls -la models
