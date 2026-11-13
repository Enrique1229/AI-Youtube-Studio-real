#!/usr/bin/env python3
"""assemble.py <story-id>  —  final/edl.json + imágenes + narration.wav -> final/video_nosub.mp4

La duración de cada plano sale del audio real (voice/durations.json): los planos de un mismo
segmento de audio se reparten su duración según `weight`. Los campos in/out del EDL se ignoran.
"""
import datetime, json, sys, tempfile, pathlib
from common import CFG, story, state, set_state, load, frame_size, run, die

MOTION = {  # (expresión de zoom, x, y)
    "zoom_in": ("1+{z}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_out": ("1+{z}-{z}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan_left": ("1+{z}", "(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"),
    "pan_right": ("1+{z}", "(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"),
    "pan_up": ("1+{z}", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/{n})"),
    "pan_down": ("1+{z}", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*on/{n}"),
    "static": ("1", "0", "0"),
}


def main(sid):
    d = story(sid)
    edl = load(d / "final" / "edl.json", "lo escribe video-editor")
    dur = load(d / "voice" / "durations.json", "lo escribe tts.py")
    W, H = frame_size(state(sid)["format"])
    fps, z = CFG["video"]["fps"], CFG["video"]["zoom"]
    groups = {}
    for e in edl["timeline"]:
        if e["audio"] not in dur:
            die(f"el EDL referencia el audio {e['audio']} que no existe en durations.json")
        groups.setdefault(e["audio"], []).append(e)
    missing = set(dur) - set(groups)
    if missing:
        die(f"segmentos de audio sin plano en el EDL: {sorted(missing)}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="asm_"))
    clips, frames_done, t_audio = [], 0, 0.0
    for seg in dur:  # orden del audio
        t_audio += dur[seg]
        target = round(t_audio * fps) - frames_done  # sin deriva acumulada
        ws = [float(e.get("weight", 1)) for e in groups[seg]]
        for i, e in enumerate(groups[seg]):
            n = target - sum(round(target * w / sum(ws)) for w in ws[:-1]) if i == len(ws) - 1 else round(target * ws[i] / sum(ws))
            n = max(n, 1)
            img = d / "assets" / "images" / f"{e['shot']}.png"
            if not img.exists():
                die(f"falta la imagen {img.name}")
            zexp, x, y = (s.format(z=z, n=n) for s in MOTION.get(e.get("motion", "zoom_in"), MOTION["zoom_in"]))
            vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                  f"zoompan=z='{zexp}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={fps},format=yuv420p")
            out = tmp / f"{len(clips):04d}.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-i", str(img), "-vf", vf, "-frames:v", str(n),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps), str(out)])
            clips.append(out)
            frames_done += n
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    out = d / "final" / "video_nosub.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(d / "voice" / "narration.wav")]
    music = (edl.get("music") or {}).get("file")
    mpath = d / music if music else None
    if mpath and mpath.exists():
        lvl = edl["music"].get("level_db", -22)
        cmd += ["-stream_loop", "-1", "-i", str(mpath), "-filter_complex",
                f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];[2:a]volume={lvl}dB[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(out)]
    run(cmd)
    placeholder = (d / "assets" / "PLACEHOLDER").exists()
    prov = {"generated": datetime.date.today().isoformat(),
            "voice": {k: CFG["tts"].get(k) for k in ("engine", "model", "license")},
            "images": {"backend": "placeholder" if placeholder else CFG["image"]["backend"],
                       "workflow": CFG["image"]["workflow"], "params": CFG["image"].get("params"),
                       "license": "n/a (imágenes de prueba)" if placeholder else CFG["image"].get("license")},
            "music": edl.get("music"), "editing": "FFmpeg"}
    (d / "final" / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
    set_state(sid, duration_s=round(frames_done / fps, 1))
    print(f"{out.name}: {frames_done / fps:.1f}s, {len(clips)} planos, música: {'sí' if mpath and mpath.exists() else 'no'}")


if __name__ == "__main__":
    main(*sys.argv[1:])
