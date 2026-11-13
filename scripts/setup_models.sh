#!/usr/bin/env bash
# Instala dependencias de Python y descarga el modelo TTS (Kokoro ONNX, ~350 MB) desde Hugging Face.
set -e; cd "$(dirname "$0")/.."
pip install -q -r requirements.txt
mkdir -p models
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s models/$f ] || curl -fL --retry 3 -o models/$f https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/$f
done
# Fuente de subtítulos y thumbnails: Inter Display (SIL OFL 1.1, github.com/rsms/inter, verificada el 2026-11-13).
if [ ! -s models/fonts/InterDisplay-Bold.ttf ]; then
  mkdir -p models/fonts; t=$(mktemp -d)
  curl -fL --retry 3 -o "$t/inter.zip" https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip
  unzip -o -q -j "$t/inter.zip" extras/ttf/InterDisplay-Bold.ttf extras/ttf/InterDisplay-Regular.ttf LICENSE.txt -d models/fonts
  rm -rf "$t"
fi
ls -la models models/fonts
