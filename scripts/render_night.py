#!/usr/bin/env python3
"""render_night.py ep004 ep005 ep006 ep007   —  renderiza varios episodios seguidos (p. ej. por la noche) y pasa el
control técnico de cada uno. Si uno falla, sigue con el siguiente. Si un episodio ya tiene su .mp4, no lo repite.

Al final escribe render/NOCHE.txt con el resultado: qué archivo *_SUBIR.mp4 subir de cada episodio.
"""
import pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    eps = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not eps: sys.exit(__doc__)
    report = []
    for ep in eps:
        src = ROOT / "anim" / "episodes" / f"{ep}.py"; out = ROOT / "render" / ep; mp4 = out / f"{ep}.mp4"
        if not src.exists(): report.append(f"{ep}: NO EXISTE {src}"); continue
        t = time.time()
        if not mp4.exists():
            print(f"\n=== Renderizando {ep} ({time.strftime('%H:%M')}) ===", flush=True)
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "render_episode.py"), str(src), str(out)])
            if r.returncode or not mp4.exists(): report.append(f"{ep}: FALLO EN EL RENDER (mira la ventana)"); continue
        q = subprocess.run([sys.executable, str(ROOT / "scripts" / "qc_local.py"), str(mp4)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        line = (q.stdout.strip().splitlines() or ["sin resultado"])[-1]
        report.append(f"{ep}: {line}  ({(time.time() - t) / 60:.0f} min)")
        print(report[-1], flush=True)
    txt = "Resultado de la noche (" + time.strftime("%Y-%m-%d %H:%M") + ")\n" + "\n".join(report) + "\n"
    (ROOT / "render").mkdir(exist_ok=True); (ROOT / "render" / "NOCHE.txt").write_text(txt, encoding="utf-8")
    print("\n" + txt)


if __name__ == "__main__":
    main()
