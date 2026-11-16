#!/usr/bin/env python3
"""qc_local.py <video.mp4> [<video2.mp4> ...]  —  control técnico final SIN gastar tokens (lo ejecuta el usuario).

Comprueba cada vídeo: 1080x1920, H.264 yuv420p, AAC, 9-30 s, volumen y pico de audio. Si el pico pasa de -1 dBFS,
crea <nombre>_SUBIR.mp4 con el audio corregido (la imagen no se toca). Si todo está bien, copia a <nombre>_SUBIR.mp4.
Sube siempre el archivo *_SUBIR.mp4.
"""
import json, pathlib, re, shutil, subprocess, sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def peak_and_lufs(path):
    r = run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(p[-1]) if p else None), (float(i[-1]) if i else None)


def check(path):
    path = pathlib.Path(path); problems = []
    if not path.exists(): return [f"no existe {path}"], None
    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,pix_fmt,width,height",
                           "-of", "json", str(path)]).stdout or "{}")
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})
    dur = float(info.get("format", {}).get("duration", 0))
    if (v.get("width"), v.get("height")) != (1080, 1920): problems.append(f"resolución {v.get('width')}x{v.get('height')} (debe ser 1080x1920)")
    if v.get("codec_name") != "h264" or v.get("pix_fmt") != "yuv420p": problems.append(f"vídeo {v.get('codec_name')}/{v.get('pix_fmt')} (debe ser h264/yuv420p)")
    if a.get("codec_name") != "aac": problems.append("sin audio AAC")
    if not 9 <= dur <= 30: problems.append(f"duración {dur:.1f} s (Shorts del canal: 9-30 s)")
    return problems, dur


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    ok_all = True
    for f in sys.argv[1:]:
        f = pathlib.Path(f); problems, dur = check(f)
        out = f.with_name(f.stem + "_SUBIR.mp4")
        if not problems:
            peak, lufs = peak_and_lufs(f)
            if peak is None or peak > -1.0:
                run(["ffmpeg", "-y", "-v", "error", "-i", str(f), "-c:v", "copy", "-af",
                     "loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.7:level=false:attack=2:release=50,volume=-1dB",
                     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)])
                peak, lufs = peak_and_lufs(out); fixed = " (audio corregido)"
            else:
                shutil.copyfile(f, out); fixed = ""
            if peak is not None and peak > -1.0: problems.append(f"pico de audio {peak} dBFS")
        if problems:
            ok_all = False; print(f"FALLO  {f.name}: " + "; ".join(problems))
        else:
            print(f"OK     {f.name}: {dur:.1f} s, volumen {lufs} LUFS, pico {peak} dBFS{fixed}  ->  sube {out.name}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
