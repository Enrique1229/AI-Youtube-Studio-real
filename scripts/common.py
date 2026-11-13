"""Utilidades compartidas por los scripts de medios."""
import _utf8  # noqa: F401  (primero: UTF-8 en Windows)
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "studio.config.json").read_text())


def die(msg):
    sys.exit(f"ERROR: {msg}")


def story(sid):
    d = ROOT / "stories" / sid
    if not d.is_dir():
        die(f"no existe {d}")
    return d


def state(sid):
    return json.loads((story(sid) / "state.json").read_text())


def set_state(sid, **kv):
    p = story(sid) / "state.json"
    st = json.loads(p.read_text())
    st.update(kv)
    p.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n")


def load(path, what):
    if not path.exists():
        die(f"falta {path.relative_to(ROOT)} ({what})")
    return json.loads(path.read_text())


FONTS = ROOT / "models" / "fonts"  # las descarga setup_models.sh; así no dependen del sistema


def font_file(bold=True):
    """Ruta al .ttf de subtitles.font: primero models/fonts, después fontconfig (Linux)."""
    name = CFG["subtitles"]["font"]
    p = FONTS / f"{name.replace(' ', '')}-{'Bold' if bold else 'Regular'}.ttf"
    if p.exists():
        return str(p)
    try:
        fp = subprocess.run(["fc-match", "-f", "%{file}", f"{name}:bold" if bold else name], capture_output=True, text=True).stdout
    except FileNotFoundError:
        fp = ""
    return fp or die(f"no encuentro la fuente {name}: ejecuta `bash scripts/setup_models.sh`")


def frame_size(fmt):
    return (1080, 1920) if fmt == "short" else (1920, 1080)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        die(f"{cmd[0]} falló:\n{r.stderr[-1500:]}")
    return r
