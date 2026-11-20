#!/usr/bin/env python3
"""fetch_polyhaven.py <id> [<id> ...] [--res 1k|2k] — descarga recursos CC0 de Poly Haven a assets/polyhaven/<id>/.

Tipos: modelos (glTF + texturas), HDRI (cielo con luz real, .hdr) y texturas PBR (color, normal, rugosidad, desplazamiento).
Todo Poly Haven es CC0 (dominio público, uso comercial libre, sin atribución obligatoria). Se anota en
assets/polyhaven/LICENSES.json. No vuelve a descargar lo que ya existe.
"""
import json, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "assets" / "polyhaven"
API = "https://api.polyhaven.com"
UA = {"User-Agent": "klunk-studio-pipeline"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return r.read()


def save(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists(): path.write_bytes(get(url))
    return path


def fetch(aid, res):
    info = json.loads(get(f"{API}/info/{aid}")); files = json.loads(get(f"{API}/files/{aid}")); d = DEST / aid
    kind = {0: "hdri", 1: "texture", 2: "model"}[info["type"]]; got = []
    if kind == "hdri":
        f = files["hdri"][res]["hdr"]; got.append(save(f["url"], d / f"{aid}_{res}.hdr"))
    elif kind == "model":
        g = files["gltf"][res]["gltf"]; got.append(save(g["url"], d / f"{aid}_{res}.gltf"))
        for rel, inc in g.get("include", {}).items(): got.append(save(inc["url"], d / rel))
    else:
        for m in ("Diffuse", "nor_gl", "Rough", "Displacement", "AO"):
            if m in files and res in files[m]:
                f = files[m][res].get("jpg") or files[m][res].get("png"); got.append(save(f["url"], d / pathlib.Path(f["url"]).name))
    lic = DEST / "LICENSES.json"; data = json.loads(lic.read_text()) if lic.exists() else {}
    data[aid] = {"name": info.get("name"), "type": kind, "license": "CC0 1.0 (Poly Haven)", "url": f"https://polyhaven.com/a/{aid}",
                 "authors": list(info.get("authors", {}).keys()), "files": [str(p.relative_to(ROOT)) for p in got]}
    lic.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"OK {aid} ({kind}): {len(got)} archivos, {sum(p.stat().st_size for p in got) / 1e6:.1f} MB")


def main():
    a = sys.argv[1:]; res = a[a.index("--res") + 1] if "--res" in a else "1k"
    ids = [x for x in a if not x.startswith("--") and x != res]
    if not ids: sys.exit(__doc__)
    for aid in ids: fetch(aid, res)


if __name__ == "__main__":
    main()
