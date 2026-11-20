"""assets.py — modelos 3D externos (p. ej. creados en Mixar y exportados a GLB) dentro de los episodios del kit.

Cada episodio que los usa declara  ASSETS = "assets/mixar/epNNN/manifest.json"  y en su código:
    from assets import use_asset
    roca = use_asset(S, "roca")          # importa, comprueba y devuelve un empty "raíz" para animar con S.key
Manifiesto (lo crea/actualiza scripts/mixar_fetch.py):
{
  "episode": "ep009",
  "assets": {
    "roca": {"file": "roca.glb", "sha256": "…", "objects": ["Roca"], "dims_m": [1.2, 1.0, 0.9],
             "animated": true, "source": "Mixar 4.5.0 (execute_bpy_script)", "license": "propio"}
  }
}
Reglas: el archivo debe existir y coincidir con su sha256; deben estar todos los objetos listados; las medidas
(si se indican) deben cuadrar ±25 %; lo marcado "animated" debe tener fotogramas clave y moverse (verify_animated).
Si algo falla, se lanza AssetError: el render se detiene. Nunca se sustituye por imágenes fijas.
"""
import hashlib, json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


class AssetError(RuntimeError):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def load_manifest(path):
    p = ROOT / path if not os.path.isabs(str(path)) else pathlib.Path(path)
    if not p.exists(): raise AssetError(f"no existe el manifiesto {p}")
    m = json.loads(p.read_text(encoding="utf-8")); m["_dir"] = p.parent
    return m


def check_files(manifest):
    """Comprobación sin Blender: archivos presentes y sin alterar. Devuelve lista de problemas (vacía = OK)."""
    probs = []
    for name, a in manifest.get("assets", {}).items():
        f = manifest["_dir"] / a["file"]
        if not f.exists(): probs.append(f"{name}: falta el archivo {f}"); continue
        if f.stat().st_size < 200: probs.append(f"{name}: archivo sospechosamente pequeño ({f.stat().st_size} bytes)")
        if a.get("sha256") and sha256(f) != a["sha256"]: probs.append(f"{name}: el archivo cambió desde que se registró (sha256)")
        if f.suffix.lower() not in (".glb", ".gltf", ".fbx", ".obj", ".usd", ".usdc"): probs.append(f"{name}: formato no 3D ({f.suffix})")
        if not a.get("objects"): probs.append(f"{name}: el manifiesto no lista los objetos esperados")
    return probs


def use_asset(S, name, manifest=None, location=(0, 0, 0), scale=1.0):
    """Importa el asset `name` en la escena del Stage S, lo verifica y lo cuelga de un empty que se devuelve."""
    import bpy
    man = manifest or getattr(S, "asset_manifest", None)
    if man is None: raise AssetError("el episodio no declaró ASSETS (manifiesto)")
    if name not in man["assets"]: raise AssetError(f"'{name}' no está en el manifiesto")
    a = man["assets"][name]; f = man["_dir"] / a["file"]
    probs = [p for p in check_files({"assets": {name: a}, "_dir": man["_dir"]})]
    if probs: raise AssetError("; ".join(probs))
    before = set(bpy.data.objects)
    ext = f.suffix.lower()
    if ext in (".glb", ".gltf"): r = bpy.ops.import_scene.gltf(filepath=str(f))
    elif ext == ".fbx": r = bpy.ops.import_scene.fbx(filepath=str(f))
    elif ext == ".obj": r = bpy.ops.wm.obj_import(filepath=str(f))
    else: r = bpy.ops.wm.usd_import(filepath=str(f))
    if "FINISHED" not in r: raise AssetError(f"{name}: la importación falló ({r})")
    new = [o for o in bpy.data.objects if o not in before]
    names = {o.name.split(".")[0] for o in new}
    missing = [o for o in a["objects"] if o not in names]
    if missing: raise AssetError(f"{name}: faltan objetos tras importar: {missing} (hay {sorted(names)})")
    root = S.empty(f"asset_{name}", location); root.scale = (scale,) * 3
    for o in new:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    if a.get("dims_m"):
        import mathutils
        pts = [o.matrix_world @ mathutils.Vector(c) for o in new if o.type == "MESH" for c in o.bound_box]
        if not pts: raise AssetError(f"{name}: no contiene mallas")
        dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
        exp = [d * scale for d in a["dims_m"]]
        if any(abs(d - e) > 0.25 * max(e, 1e-3) for d, e in zip(sorted(dims), sorted(exp))):
            raise AssetError(f"{name}: medidas {[round(d, 2) for d in dims]} no cuadran con {exp}")
    S.assets_used = getattr(S, "assets_used", {}); S.assets_used[name] = {"root": root, "objects": new, "animated": a.get("animated", False)}
    return root


def verify_animated(S, n_frames):
    """Tras construir el nivel: todo asset marcado 'animated' debe tener fotogramas clave y moverse de verdad."""
    import bpy
    probs = []
    for name, info in getattr(S, "assets_used", {}).items():
        if not info["animated"]: continue
        root = info["root"]
        keyed = bool(S.fcurves(root)) or any(S.fcurves(o) for o in info["objects"])
        if not keyed: probs.append(f"{name}: marcado como animado pero no tiene fotogramas clave"); continue
        pos = []
        for fr in (1, max(1, n_frames // 2), n_frames):
            S.sc.frame_set(fr); bpy.context.view_layer.update()
            pos.append(tuple(round(v, 4) for v in root.matrix_world.to_translation()) + tuple(round(v, 4) for v in root.matrix_world.to_euler()))
        if len(set(pos)) == 1 and not any(S.fcurves(o) for o in info["objects"]):
            probs.append(f"{name}: tiene claves pero no se mueve en todo el nivel")
    if probs: raise AssetError("; ".join(probs))
