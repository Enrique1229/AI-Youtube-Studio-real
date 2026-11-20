#!/usr/bin/env python3
"""anim_build.py <carpeta_del_episodio_renderizado> <salida.mp4> [--title "…"]

Une los niveles renderizados (l1, l2… con sus PNG y level.json), añade el rótulo de IQ y mezcla los sonidos
que el kit anotó en cada fotograma. Los IQ se leen del episodio vía level.json + argumento --iq.
Uso típico:  python scripts/anim_build.py render/ep001 final/ep001.mp4 --iq -450,-80,120,900,5469 [--speed 1.5]
"""
import json, pathlib, subprocess, sys, tempfile
import numpy as np, soundfile as sf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import audio_gen as A

FONT_CANDIDATES = ["models/fonts/InterDisplay-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]


AUDIO_LIB = pathlib.Path(__file__).resolve().parent.parent / "assets" / "audio"


def lib_files(kind, name=None):
    """assets/audio/music/*.mp3|wav|ogg  ·  assets/audio/sfx/<tipo>*.wav|mp3|ogg (p. ej. splash1.wav, splash2.mp3)."""
    d = AUDIO_LIB / kind
    if not d.exists(): return []
    fs = [f for f in sorted(d.iterdir()) if f.suffix.lower() in (".wav", ".mp3", ".ogg", ".flac", ".m4a")]
    if name: fs = [f for f in fs if f.stem.lower().rstrip("0123456789_- ") == name.lower()]
    return fs


def decode(path, seconds=None, loop=False):
    """Archivo de audio -> numpy mono a A.SR (con FFmpeg). Bucle y fundidos si se pide una duración."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(A.SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    if seconds:
        n = int(seconds * A.SR)
        if loop and len(x) < n: x = np.tile(x, n // max(1, len(x)) + 1)
        x = x[:n]; x = A.fade(x, 0.05, min(1.0, seconds / 8))
    peak = np.abs(x).max() or 1.0
    return (x / peak * 0.7).astype(np.float32)


def main():
    args = sys.argv[1:]
    src, out = pathlib.Path(args[0]), pathlib.Path(args[1])
    caption = args[args.index("--caption") + 1] if "--caption" in args else None      # formato POV / mini-historia: premisa fija arriba
    no_label = "--no-label" in args                                                   # objetos vivos / mini-historias: sin rótulo
    topline = args[args.index("--title") + 1] if "--title" in args else None          # niveles: el reto escrito encima del rótulo de IQ
    cta = args[args.index("--cta") + 1] if "--cta" in args else None                  # p. ej. "follow for more" en el último segundo
    if "--iq" in args: iqs = [int(x) for x in args[args.index("--iq") + 1].split(",")]
    else: iqs = [0] * len([d for d in src.iterdir() if d.is_dir() and d.name.startswith("l") and d.name[1:].isdigit()])
    speed = float(args[args.index("--speed") + 1]) if "--speed" in args else 1.5   # 1.5 = versión rápida (estándar del canal)
    root = pathlib.Path(__file__).resolve().parent.parent
    font = next(str(p) for p in ((root / f if not f.startswith(("/", "C:")) else pathlib.Path(f)) for f in FONT_CANDIDATES) if p.exists()).replace("\\", "/").replace(":", "\\:")
    lang = json.loads((root / "studio.config.json").read_text(encoding="utf-8")).get("language", "en")
    LABEL = {"es": "NIVEL DE IQ"}.get(lang, "IQ LEVEL")                                # idioma del canal
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="anim_")); clips, durs, cues, t0 = [], [], [], 0.0
    X = float(args[args.index("--xfade") + 1]) if "--xfade" in args else 0.22          # barrido entre niveles (s)
    order = sorted(iqs)
    for i, iq in enumerate(iqs, 1):
        d = src / f"l{i}"; meta = json.loads((d / "level.json").read_text())
        # rótulo: recuadro blanco "IQ:" y debajo el número con contorno; color por posición (rojo el peor, oro el mejor)
        num = f"{'+ ' if iq > 0 else '- '}{abs(iq)}"
        color = "0xE53935" if iq == order[0] else ("0xFFC107" if iq == order[-1] else ("0x43A047" if iq > 0 else "white"))
        # rótulo propio del canal: banda oscura translúcida, "NIVEL DE IQ" pequeño y el número grande con barra de color
        if no_label:
            vf = "scale=1080:1920:flags=lanczos,format=yuv420p"
        elif caption:
            import textwrap
            cap = "\n".join(textwrap.wrap(caption, 24)).replace("'", "\u2019").replace(":", "\\:")
            vf = (f"scale=1080:1920:flags=lanczos,drawtext=fontfile='{font}':text='{cap}':fontcolor=black:fontsize=58:"
                  f"line_spacing=8:text_align=C:box=1:boxcolor=white@0.97:boxborderw=22:x=(w-text_w)/2:y=60,format=yuv420p")
        else:
          pre = ""
          if topline:                                                                   # reto en una línea ARRIBA del rótulo (no lo mueve)
            tl = topline.replace("'", "\u2019").replace(":", "\\:")
            pre = (f"drawtext=fontfile='{font}':text='{tl}':fontcolor=black:fontsize=44:"
                   f"box=1:boxcolor=white@0.95:boxborderw=14:x=(w-text_w)/2:y=46,")
          vf = (f"scale=1080:1920:flags=lanczos,{pre}drawbox=x=300:y=140:w=480:h=170:color=black@0.55:t=fill,"
              f"drawbox=x=300:y=300:w=480:h=10:color={color}@1:t=fill,"
              f"drawtext=fontfile='{font}':text='{LABEL}':fontcolor=0xFFE082:fontsize=38:x=(w-text_w)/2:y=156,"
              f"drawtext=fontfile='{font}':text='{num}':fontcolor={color}:borderw=4:bordercolor=black:fontsize=92:x=(w-text_w)/2:y=200,format=yuv420p")
        clip = tmp / f"l{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(meta["fps"] * speed), "-i", str(d / "f%04d.png"), "-vf", vf,
                        "-c:v", "libx264", "-crf", "18", "-r", "30", str(clip)], check=True)
        dur = meta["frames"] / meta["fps"] / speed
        start = t0 - (X if i > 1 else 0)                                                  # el barrido solapa el final del anterior
        clips.append(clip); durs.append(dur)
        if i > 1: cues.append({"t": max(0, start - 0.12), "type": "whoosh", "vol": -2})
        cues += [dict(c, t=c["t"] / speed + start) for c in meta["cues"]]; t0 = start + dur
    # vídeo: niveles unidos con un barrido lateral rápido (xfade)
    inputs = sum((["-i", str(c)] for c in clips), []); fc, prev, off = [], "[0:v]", 0.0
    for i in range(1, len(clips)):
        off += durs[i - 1] - X; lab = f"[v{i}]"
        fc.append(f"{prev}[{i}:v]xfade=transition=slideleft:duration={X}:offset={off:.3f}{lab}"); prev = lab; off = off
    vid = tmp / "video.mp4"
    if fc:
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "18", "-r", "30", str(vid)], check=True)
    else: vid = clips[0]
    # audio: música (estilo referencia: tranquila y pícara) + ambiente de parque + efectos bien presentes
    n = int(t0 * A.SR) + A.SR; mix = np.zeros(n, np.float32)
    mdb = float(args[args.index("--music-db") + 1]) if "--music-db" in args else -12.0
    style = args[args.index("--music") + 1] if "--music" in args else "sneaky"
    lib_music = lib_files("music")
    if lib_music:                                                                       # música real (Biblioteca de audio de YouTube, etc.)
        pick = lib_music[A.seed_of(out.stem) % len(lib_music)]; bed = decode(pick, t0 + 0.5, loop=True)
        print(f"música: {pick.name}")
    else: bed = (A.sneaky_music if style == "sneaky" else A.comedy_music)(t0 + 0.5, A.seed_of(out.stem))
    mix[:len(bed)] += bed[:n].astype(np.float32) * 10 ** (mdb / 20)
    amb = A.ambience(t0 + 0.5, A.seed_of(out.stem) + 1); mix[:len(amb)] += amb[:n].astype(np.float32) * 10 ** (-24 / 20)
    cache = {}
    for c in cues:
        if c["type"] not in cache:                                                       # efecto real si existe; si no, sintético
            real = lib_files("sfx", c["type"]); cache[c["type"]] = [decode(f) for f in real] or [A.sfx(c["type"], A.seed_of(c["type"]))]
        opts = cache[c["type"]]; w = opts[int(c["t"] * 1000) % len(opts)]                 # varía entre tomas si hay varias
        k = int(c["t"] * A.SR); g = 10 ** ((c.get("vol", 0) - 1) / 20); mix[k:k + len(w)] += w[:max(0, n - k)] * g
    mix = np.tanh(mix * 1.3) * 0.85
    sf.write(tmp / "audio.wav", mix, A.SR)
    out.parent.mkdir(parents=True, exist_ok=True)
    if cta:                                                                           # llamada a la acción en el último segundo y medio
        vid2 = tmp / "video_cta.mp4"; c_ = cta.replace("'", "\u2019").replace(":", "\\:")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vid), "-vf",
                        f"drawtext=fontfile='{font}':text='{c_}':fontcolor=white:fontsize=72:box=1:boxcolor=black@0.85:boxborderw=24:"
                        f"x=(w-text_w)/2:y=h*0.78:enable='gte(t,{max(0, t0 - 1.6):.2f})',format=yuv420p",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(vid2)], check=True); vid = vid2
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vid), "-i", str(tmp / "audio.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.7:level=false:attack=2:release=50,volume=-1dB", "-t", f"{t0:.3f}", str(out)], check=True)
    print(f"{out}: {t0:.1f} s, {len(iqs)} niveles, {len(cues)} sonidos")


if __name__ == "__main__":
    main()
