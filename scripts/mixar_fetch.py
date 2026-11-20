#!/usr/bin/env python3
"""mixar_fetch.py <epNNN> <nombre> <archivo_exportado> --objects Obj1,Obj2 [--dims 1.2,1,0.9] [--animated] [--source "..."]

Mixar solo exporta a Descargas (o a carpetas fijas). Este script COPIA el archivo exportado a
assets/mixar/<epNNN>/, calcula su sha256 y lo registra en assets/mixar/<epNNN>/manifest.json.
<archivo_exportado> puede ser una ruta o solo el nombre (se busca en la carpeta Descargas del usuario).
Se niega a trabajar sobre los episodios protegidos (ep001-ep008).
"""
import json, pathlib, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "anim"))
from assets import sha256  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTECTED = {f"ep{n:03d}" for n in range(1, 9)}


def main():
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    ep, name, src = a[0], a[1], pathlib.Path(a[2])
    if ep in PROTECTED: sys.exit(f"ERROR: {ep} está protegido (episodios 1-8 publicados o cerrados)")
    if not src.exists(): src = pathlib.Path.home() / "Downloads" / a[2]
    if not src.exists(): sys.exit(f"ERROR: no encuentro {a[2]} (ni como ruta ni en Descargas)")
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    objects = [o for o in (opt("--objects") or "").split(",") if o]
    if not objects: sys.exit("ERROR: indica --objects con los nombres de objeto que debe contener")
    d = ROOT / "assets" / "mixar" / ep; d.mkdir(parents=True, exist_ok=True)
    dst = d / src.name; shutil.copy2(src, dst)
    mp = d / "manifest.json"
    man = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {"episode": ep, "assets": {}}
    man["assets"][name] = {"file": dst.name, "sha256": sha256(dst), "objects": objects,
                           "dims_m": [float(x) for x in opt("--dims").split(",")] if opt("--dims") else None,
                           "animated": "--animated" in a, "source": opt("--source") or "Mixar", "license": "propio"}
    mp.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK {name}: {dst.relative_to(ROOT)} ({dst.stat().st_size} bytes) registrado en {mp.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
