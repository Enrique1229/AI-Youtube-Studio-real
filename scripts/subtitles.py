#!/usr/bin/env python3
"""subtitles.py <story-id>  —  voice/timing.json -> final/subtitles.srt + .ass, y los quema en final/video.mp4

El texto es el del guion (exacto). El tiempo de cada frase es exacto (lo midió tts.py); dentro de
la frase, las palabras se reparten en proporción a su longitud. Fija final_file en state.json.
"""
import sys
from common import CFG, ROOT, FONTS, story, state, set_state, load, frame_size, run


WEAK_END = set("el la los las un una unos unas de del al a en con por para que y o e ni su sus mi mis tu tus se me te lo le no".split())


def chunks(words, cfg):
    """Trozos de 2-4 palabras que no terminan en artículo, preposición o conjunción y no dejan una palabra suelta."""
    cur = []
    for i, w in enumerate(words):
        full = cur and (len(cur) >= cfg["max_words"] or len(" ".join(cur + [w])) > cfg["max_chars"])
        if full and cur[-1].lower().strip("¿¡«»\"") in WEAK_END and len(cur) > 1:
            carry = cur.pop()  # la palabra débil pasa al trozo siguiente
            yield cur
            cur = [carry]
        elif full:
            yield cur
            cur = []
        cur.append(w)
        last = i == len(words) - 1
        if w[-1] in ".;:!?…" or (w[-1] == "," and len(cur) > 1) or last:
            yield cur
            cur = []


def cues(timing, cfg):
    for seg in timing:
        for s in seg["sentences"]:
            words = s["text"].split()
            wt = [len(w) + (3 if w[-1] in ".,;:!?…" else 1) for w in words]
            per = (s["end"] - s["start"]) / sum(wt)
            t, i = s["start"], 0
            for ch in chunks(words, cfg):
                dur = sum(wt[i:i + len(ch)]) * per
                yield t, t + dur, " ".join(ch).strip(",.;:")
                t, i = t + dur, i + len(ch)


def ts(t, sep):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", sep) if sep == "," else f"{h}:{m:02d}:{s:05.2f}"


def main(sid):
    d = story(sid)
    fmt = state(sid)["format"]
    W, H = frame_size(fmt)
    cfg = CFG["subtitles"]
    cs = list(cues(load(d / "voice" / "timing.json", "lo escribe tts.py"), cfg))
    (d / "final" / "subtitles.srt").write_text(
        "".join(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{txt}\n\n" for i, (a, b, txt) in enumerate(cs, 1)))
    size, marg = (int(H * 0.05), int(H * 0.30)) if fmt == "short" else (int(H * 0.065), int(H * 0.08))
    ass = d / "final" / "subtitles.ass"
    ass.write_text(
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        f"Style: D,{cfg['font']},{size},&H00FFFFFF,&H00000000,&H80000000,1,1,{max(size // 12, 3)},2,2,60,60,{marg}\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
        + "".join(f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},D,{txt.upper() if fmt == 'short' else txt}\n" for a, b, txt in cs))
    out = d / "final" / "video.mp4"
    if cfg.get("burn", {}).get(fmt, True):
        # Rutas relativas a ROOT y con "/": en Windows, "C:\..." rompe la sintaxis de filtros de ffmpeg.
        vf = f"ass={ass.relative_to(ROOT).as_posix()}" + (f":fontsdir={FONTS.relative_to(ROOT).as_posix()}" if FONTS.is_dir() else "")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(d / "final" / "video_nosub.mp4"), "-vf", vf,
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "copy", str(out)], cwd=ROOT)
    else:  # relato: sin subtítulos quemados; el .srt se sube a YouTube como pista de subtítulos
        import shutil
        shutil.copyfile(d / "final" / "video_nosub.mp4", out)
    set_state(sid, final_file=out.relative_to(ROOT).as_posix(), stage="assembled")
    print(f"{out.name} con {len(cs)} subtítulos")


if __name__ == "__main__":
    main(*sys.argv[1:])
