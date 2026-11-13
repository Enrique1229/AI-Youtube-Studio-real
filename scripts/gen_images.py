#!/usr/bin/env python3
"""gen_images.py <story-id> [--thumbnail] [--force]  —  visual-prompts/shots.json -> assets/images/<shot>.png

Backends (studio.config.json -> image.backend):
  comfy        ComfyUI por HTTP: POST /prompt, GET /history/<id>, GET /view (API oficial).
  placeholder  Imagen de prueba con Pillow. Solo para probar el pipeline: marca la historia
               como NO entregable (assets/PLACEHOLDER) y `studio.py deliver` la rechaza.
No regenera imágenes que ya existen (borra el archivo para rehacer un plano).
"""
import json, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from common import CFG, ROOT, story, state, load, die

C = CFG["image"]


def fill(node, vals):
    if isinstance(node, dict):
        return {k: fill(v, vals) for k, v in node.items()}
    if isinstance(node, list):
        return [fill(v, vals) for v in node]
    if isinstance(node, str) and node.startswith("{{") and node.endswith("}}"):
        if node[2:-2] not in vals:
            die(f"el workflow usa el marcador {node} y no está en studio.config.json -> image.params")
        return vals[node[2:-2]]
    return node


def http(path, data=None):
    req = urllib.request.Request(C["comfy_url"] + path, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:  # ComfyUI devuelve 400 con node_errors si el workflow no valida
        die(f"ComfyUI {e.code} en {path}: {e.read().decode(errors='replace')[:1200]}")
    except urllib.error.URLError as e:
        die(f"ComfyUI no responde en {C['comfy_url']} ({e.reason})")


def comfy(vals, out):
    wf = fill(json.loads((ROOT / C["workflow"]).read_text()), vals)
    pid = json.loads(http("/prompt", {"prompt": wf, "client_id": uuid.uuid4().hex}))["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < C["timeout_s"]:
        hist = json.loads(http(f"/history/{pid}"))
        if pid in hist:
            for node in hist[pid].get("outputs", {}).values():
                for img in node.get("images", []):
                    q = urllib.parse.urlencode({k: img[k] for k in ("filename", "subfolder", "type")})
                    out.write_bytes(http(f"/view?{q}"))
                    return
            die(f"ComfyUI terminó sin imágenes: {json.dumps(hist[pid].get('status'))[:400]}")
        time.sleep(2)
    die("ComfyUI: tiempo de espera agotado")


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
            comfy(vals, out)
        elif C["backend"] == "placeholder":
            placeholder(vals, out, s["id"])
            (d / "assets" / "PLACEHOLDER").write_text("imágenes de prueba; no entregable\n")
        else:
            die(f"backend desconocido: {C['backend']}")
        made += 1
    print(f"{made} imágenes nuevas, {len(shots) - made} ya existían ({C['backend']})")


if __name__ == "__main__":
    main(*sys.argv[1:])
