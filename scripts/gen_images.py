#!/usr/bin/env python3
"""gen_images.py <story-id> [--thumbnail] [--force]  —  visual-prompts/shots.json -> assets/images/<shot>.png

Backends (studio.config.json -> image.backend):
  comfy        ComfyUI por HTTP: POST /prompt, GET /history/<id>, GET /view (API oficial).
  placeholder  Imagen de prueba con Pillow. Solo para probar el pipeline: marca la historia
               como NO entregable (assets/PLACEHOLDER) y `studio.py deliver` la rechaza.
No regenera imágenes que ya existen (borra el archivo para rehacer un plano).
"""
import sys
import comfy
from common import CFG, story, state, load, die

C = CFG["image"]


def placeholder(vals, out, label):
    from PIL import Image, ImageDraw
    import random
    rnd = random.Random(vals["seed"])
    w, h = vals["width"], vals["height"]
    a, b = [tuple(rnd.randint(10, 120) for _ in range(3)) for _ in range(2)]
    im = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(im)
    for y in range(h):
        px.line([(0, y), (w, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * y / h) for i in range(3)))
    for _ in range(12):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(20, 160)
        px.ellipse([x - r, y - r, x + r, y + r], outline=(200, 200, 200), width=3)
    px.text((40, 40), f"PLACEHOLDER {label}", fill=(255, 255, 255))
    im.save(out)


def main(sid, *flags):
    d = story(sid)
    fmt = state(sid)["format"]
    if "--thumbnail" in flags:
        th = load(d / "final" / "thumbnail.json", "lo escribe thumbnail-designer")
        c = th["concepts"][th.get("chosen", 0)]
        shots = [{"id": "thumbnail", "prompt": c["prompt"], "negative": c.get("negative", ""), "seed": c.get("seed", 1),
                  "aspect": "9:16" if fmt == "short" else "16:9"}]
    else:
        shots = load(d / "visual-prompts" / "shots.json", "lo escribe visual-director")
    outdir = d / "assets" / "images"
    outdir.mkdir(parents=True, exist_ok=True)
    if "--force" in flags:  # rehacer todo (p. ej. al pasar de placeholder a un motor real)
        for s_ in shots:
            (outdir / f"{s_['id']}.png").unlink(missing_ok=True)
        if "--thumbnail" not in flags:
            (d / "assets" / "PLACEHOLDER").unlink(missing_ok=True)
    made = 0
    for s in shots:
        out = outdir / f"{s['id']}.png"
        if out.exists():
            continue
        w, h = C["size"][s.get("aspect") or ("9:16" if fmt == "short" else "16:9")]
        vals = {**C.get("params", {}), "prompt": s["prompt"], "negative": s.get("negative", ""), "seed": int(s.get("seed", 1)), "width": w, "height": h}
        if C["backend"] == "comfy":
            comfy.run_workflow(C["workflow"], vals, out, C["timeout_s"])
        elif C["backend"] == "placeholder":
            placeholder(vals, out, s["id"])
            (d / "assets" / "PLACEHOLDER").write_text("imágenes de prueba; no entregable\n")
        else:
            die(f"backend desconocido: {C['backend']}")
        made += 1
    print(f"{made} imágenes nuevas, {len(shots) - made} ya existían ({C['backend']})")


if __name__ == "__main__":
    main(*sys.argv[1:])
