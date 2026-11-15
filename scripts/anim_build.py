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


def main():
    args = sys.argv[1:]
    src, out = pathlib.Path(args[0]), pathlib.Path(args[1])
    iqs = [int(x) for x in args[args.index("--iq") + 1].split(",")]
    speed = float(args[args.index("--speed") + 1]) if "--speed" in args else 1.5   # 1.5 = versión rápida (estándar del canal)
    root = pathlib.Path(__file__).resolve().parent.parent
    font = next(str(p) for p in ((root / f if not f.startswith(("/", "C:")) else pathlib.Path(f)) for f in FONT_CANDIDATES) if p.exists()).replace("\\", "/").replace(":", "\\:")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="anim_")); clips, cues, t0 = [], [], 0.0
    for i, iq in enumerate(iqs, 1):
        d = src / f"l{i}"; meta = json.loads((d / "level.json").read_text())
        label = f"IQ  {'+' if iq > 0 else ''}{iq}"; color = "0xE53935" if iq < 0 else ("0xFBC02D" if iq < 500 else "0x2E7D32")
        vf = (f"scale=1080:1920:flags=lanczos,drawbox=x=270:y=150:w=540:h=118:color=white@0.94:t=fill,"
              f"drawtext=fontfile='{font}':text='{label}':fontcolor={color}:fontsize=70:x=(w-text_w)/2:y=172,format=yuv420p")
        clip = tmp / f"l{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(meta["fps"] * speed), "-i", str(d / "f%04d.png"), "-vf", vf,
                        "-c:v", "libx264", "-crf", "18", "-r", "30", str(clip)], check=True)
        clips.append(clip); cues.append({"t": t0, "type": "whoosh", "vol": -12})
        cues += [dict(c, t=c["t"] / speed + t0) for c in meta["cues"]]; t0 += meta["frames"] / meta["fps"] / speed
    (tmp / "list.txt").write_text("".join(f"file '{c.as_posix()}'\n" for c in clips))
    # pista de audio: música ambiental + cada efecto en su instante
    n = int(t0 * A.SR) + A.SR; mix = np.zeros(n, np.float32)
    bed = A.music("wonder", t0 + 1, 11); mix[:len(bed)] += bed[:n] * 10 ** (-20 / 20)
    cache = {}
    for c in cues:
        w = cache.setdefault(c["type"], A.sfx(c["type"], A.seed_of(c["type"])))
        k = int(c["t"] * A.SR); g = 10 ** ((c.get("vol", 0) - 4) / 20); mix[k:k + len(w)] += w[:max(0, n - k)] * g
    mix = np.tanh(mix * 1.1) * 0.8
    sf.write(tmp / "audio.wav", mix, A.SR)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-i", str(tmp / "audio.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{t0:.3f}", str(out)], check=True)
    print(f"{out}: {t0:.1f} s, {len(iqs)} niveles, {len(cues)} sonidos")


if __name__ == "__main__":
    main()
