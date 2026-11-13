#!/usr/bin/env python3
"""assemble.py <story-id>  —  final/edl.json + imágenes + narration.wav -> final/video_nosub.mp4

La duración de cada plano sale del audio real (voice/durations.json): los planos de un mismo
segmento de audio se reparten su duración según `weight`. Los campos in/out del EDL se ignoran.

Audio: voz normalizada + música + efectos.
  music: null | {"mood": "tension|mystery|melancholy|wonder", "level_db": -22}   (sintetizada, audio_gen.py)
         | {"file": "assets/music/pista.mp3", "license": "...", "level_db": -22}  (archivo tuyo)
  sfx:   [{"type": "whoosh|hit|riser|swell", "shot": "<id de shot>", "level_db": -14}]
         El efecto empieza con el plano; `riser` TERMINA donde empieza el plano (anticipa un giro).
"""
import datetime, json, sys, tempfile, pathlib
import soundfile as sf
import audio_gen
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
    clips, frames_done, t_audio, shot_start, n_clips = [], 0, 0.0, {}, 0
    for seg in dur:  # orden del audio
        t_audio += dur[seg]
        target = round(t_audio * fps) - frames_done  # sin deriva acumulada
        ws = [float(e.get("weight", 1)) for e in groups[seg]]
        for i, e in enumerate(groups[seg]):
            n = target - sum(round(target * w / sum(ws)) for w in ws[:-1]) if i == len(ws) - 1 else round(target * ws[i] / sum(ws))
            n = max(n, 1)
            img = d / "assets" / "images" / f"{e['shot']}.png"
            clip = d / "assets" / "clips" / f"{e['shot']}.mp4"
            out = tmp / f"{len(clips):04d}.mp4"
            if clip.exists():  # clip generado (gen_video.py): se adapta a la duración del plano
                need = n / fps
                cdur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip)]).stdout.strip() or 0)
                slow = min(max(need / cdur, 1.0), 1.6) if cdur > 0 else 1.0  # como mucho 1,6x más lento; el resto, último fotograma
                vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setpts={slow:.4f}*PTS,"
                      f"fps={fps},tpad=stop_mode=clone:stop_duration={need:.3f},format=yuv420p")
                run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-an", "-vf", vf, "-frames:v", str(n),
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps), str(out)])
                n_clips += 1
            else:
                if not img.exists():
                    die(f"falta la imagen {img.name}")
                zexp, x, y = (s.format(z=z, n=n) for s in MOTION.get(e.get("motion", "zoom_in"), MOTION["zoom_in"]))
                vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                      f"zoompan=z='{zexp}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={fps},format=yuv420p")
                run(["ffmpeg", "-y", "-v", "error", "-i", str(img), "-vf", vf, "-frames:v", str(n),
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps), str(out)])
            shot_start[e["shot"]] = frames_done / fps
            clips.append(out)
            frames_done += n
    total = frames_done / fps
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))

    # ---- audio: voz + música + efectos ----
    music = edl.get("music") or {}
    gen_music, gen_sfx = audio_gen.build(d, edl, total)
    mpath = gen_music or (d / music["file"] if music.get("file") and (d / music["file"]).exists() else None)
    if music.get("file") and not mpath:
        die(f"el EDL pide la música {music['file']} y no existe")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(d / "voice" / "narration.wav")]
    chains, labels, idx = ["[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[voz]"], ["[voz]"], 2
    if mpath:
        cmd += ["-stream_loop", "-1", "-i", str(mpath)]
        chains.append(f"[{idx}:a]aresample=48000,volume={music.get('level_db', -22)}dB[mus]")
        labels.append("[mus]")
        idx += 1
    used_sfx = []
    for i, s in enumerate(edl.get("sfx") or []):
        if s.get("shot") not in shot_start:
            die(f"sfx {i}: el shot {s.get('shot')} no está en el timeline")
        start = shot_start[s["shot"]]
        if s["type"] == "riser":
            start = max(0.0, start - sf.info(str(gen_sfx[i])).duration)
        ms = int(start * 1000)
        cmd += ["-i", str(gen_sfx[i])]
        chains.append(f"[{idx}:a]aresample=48000,adelay={ms}:all=1,volume={s.get('level_db', -14)}dB[fx{i}]")
        labels.append(f"[fx{i}]")
        used_sfx.append({"type": s["type"], "shot": s["shot"], "at_s": round(start, 2)})
        idx += 1
    chains.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.8:level=0[a]")
    out = d / "final" / "video_nosub.mp4"
    cmd += ["-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[a]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", str(out)]
    run(cmd)

    placeholder = (d / "assets" / "PLACEHOLDER").exists()
    music_prov = None
    if gen_music:
        music_prov = {"source": "sintetizada por scripts/audio_gen.py", "mood": music["mood"], "license": "propia, sin terceros"}
    elif mpath:
        music_prov = {"source": music["file"], "license": music.get("license", "SIN ANOTAR")}
    prov = {"generated": datetime.date.today().isoformat(),
            "voice": {k: CFG["tts"].get(k) for k in ("engine", "model", "license")},
            "images": {"backend": "placeholder" if placeholder else CFG["image"]["backend"],
                       "workflow": CFG["image"]["workflow"], "params": CFG["image"].get("params"),
                       "source": CFG["image"].get("source"),
                       "license": "n/a (imágenes de prueba)" if placeholder else CFG["image"].get("license")},
            "video_clips": {"count": n_clips, "workflow": CFG["video_gen"]["workflow"], "license": CFG["video_gen"]["license"]} if n_clips else None,
            "music": music_prov,
            "sfx": {"source": "sintetizados por scripts/audio_gen.py", "license": "propia, sin terceros", "cues": used_sfx} if used_sfx else None,
            "editing": "FFmpeg"}
    (d / "final" / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
    set_state(sid, duration_s=round(total, 1))
    print(f"{out.name}: {total:.1f}s, {len(clips)} planos ({n_clips} con vídeo generado), música: {music_prov['source'] if music_prov else 'no'}, efectos: {len(used_sfx)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
