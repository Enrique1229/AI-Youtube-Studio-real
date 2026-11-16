#!/usr/bin/env python3
"""render_episode.py <episodio.py> <carpeta_salida> [--blender RUTA] [--cpu] [--draft] [--eevee] [--only N]

Renderiza todos los niveles de un episodio con Blender y monta el Short final (rótulos, efectos y música).
Por defecto usa la tarjeta gráfica y resolución completa (1080x1920). --draft: 540x960 para revisar rápido.
--eevee: motor EEVEE (mucho más rápido en GPU; aspecto algo distinto). --only N: solo el nivel N, sin montar (para medir tiempos).
Ejemplo en Windows:
  python scripts/render_episode.py anim/episodes/ep001.py render/ep001 --blender "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe"
Sin --blender, busca blender en el PATH o en la carpeta habitual de Windows.
"""
import glob, importlib.util, os, pathlib, shutil, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent


def find_blender(arg):
    if arg: return arg
    if shutil.which("blender"): return shutil.which("blender")
    c = sorted(glob.glob("C:/Program Files/Blender Foundation/Blender */blender.exe"))
    if c: return c[-1]
    sys.exit("ERROR: no encuentro Blender. Pasa la ruta con --blender \"C:/Program Files/Blender Foundation/Blender X.Y/blender.exe\"")


def episode_settings(path):
    """Lee los ajustes del episodio SIN ejecutarlo (el episodio usa bpy, que solo existe dentro de Blender):
    LEVELS (los IQ), CAPTION, CTA, SPEED, TITLE."""
    import ast
    tree = ast.parse(pathlib.Path(path).read_text(encoding="utf-8")); cfg = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == "LEVELS":
                cfg["iqs"] = [ast.literal_eval(el.elts[0]) for el in node.value.elts]
            elif name in ("CAPTION", "CTA", "SPEED", "TITLE"):
                try: cfg[name] = ast.literal_eval(node.value)
                except ValueError: pass
    if "iqs" not in cfg: sys.exit(f"ERROR: {path} no define LEVELS")
    return cfg


def main():
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    ep, out = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
    blender = find_blender(a[a.index("--blender") + 1] if "--blender" in a else None)
    cfg = episode_settings(ep); iqs = cfg["iqs"]
    env = dict(os.environ, STUDIO_DEVICE="CPU" if "--cpu" in a else "GPU", STUDIO_ENGINE="BLENDER_EEVEE" if "--eevee" in a else "CYCLES",
               STUDIO_RES="540x960" if "--draft" in a else "1080x1920", STUDIO_SAMPLES="16" if "--draft" in a else "32")
    out.mkdir(parents=True, exist_ok=True)
    only = int(a[a.index("--only") + 1]) if "--only" in a else None
    for i in ([only] if only else range(1, len(iqs) + 1)):
        lv = out / f"l{i}"; t = time.time()
        r = subprocess.run([blender, "-b", "--python-exit-code", "1", "-P", str(ROOT / "anim" / "run_level.py"), "--", str(ep), str(i), str(lv)],
                           env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(f"ERROR en el nivel {i}")
        info = " ".join(l for l in r.stdout.splitlines() if l.startswith("[kit]"))
        n = len(list(lv.glob("f*.png"))); dt = time.time() - t
        print(f"nivel {i}/{len(iqs)}: {n} fotogramas en {dt:.0f} s ({dt / max(n, 1):.2f} s/fotograma) {info}")
    if only:
        print("Nivel suelto renderizado (sin montaje). Fotogramas en", out / f"l{only}"); return
    final = out / f"{ep.stem}.mp4"
    cmd = [sys.executable, str(ROOT / "scripts" / "anim_build.py"), str(out), str(final), "--speed", str(cfg.get("SPEED", 1.5))]
    if cfg.get("CAPTION") or not any(iqs): cmd += ["--caption", cfg["CAPTION"]] if cfg.get("CAPTION") else ["--no-label"]
    else: cmd += ["--iq", ",".join(map(str, iqs))]
    if cfg.get("CTA"): cmd += ["--cta", cfg["CTA"]]
    subprocess.run(cmd, check=True)
    print("LISTO:", final)


if __name__ == "__main__":
    main()
