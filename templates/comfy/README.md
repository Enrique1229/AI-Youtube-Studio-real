# Workflows de ComfyUI (formato API)

`txt2img.json` es el workflow por defecto de ComfyUI (tomado de `script_examples/basic_api_example.py` del repositorio oficial)
con marcadores `{{prompt}}`, `{{negative}}`, `{{seed}}`, `{{width}}`, `{{height}}`. El checkpoint (`ckpt_name`) debe existir
en tu `ComfyUI/models/checkpoints/`. Probado el 2026-11-13 con SDXL base 1.0 en una RTX 4050 de 6 GB (ver `channel/style-bible/engine.md`).

Para otro modelo (FLUX schnell, Wan image-to-video…): carga en ComfyUI la plantilla oficial del modelo, comprueba que genera,
exporta con "File → Export (API)", guarda aquí el JSON y sustituye los valores por los marcadores. Para i2v añade `{{image}}`
(nombre del archivo ya subido a ComfyUI). Luego apunta `studio.config.json → image.workflow` a ese archivo.
