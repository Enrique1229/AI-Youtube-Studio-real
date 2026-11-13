#!/usr/bin/env python3
"""tts.py <story-id>  —  voice/narration.json -> voice/narration.wav + durations.json + timing.json

Sintetiza frase a frase (Kokoro ONNX, CPU). timing.json guarda el inicio/fin exacto de cada frase:
de ahí salen los subtítulos, con el texto del guion y sin reconocimiento de voz.
"""
import json, re, sys
import numpy as np, soundfile as sf
from common import CFG, ROOT, story, load, die


def sentences(text):
    parts = re.split(r"(?<=[.!?…;:])\s+", text.strip())
    return [p for p in parts if p]


def main(sid):
    d = story(sid)
    nar = load(d / "voice" / "narration.json", "lo escribe voice-director")
    c = CFG["tts"]
    if c["engine"] != "kokoro-onnx":
        die(f"motor TTS no soportado: {c['engine']}")
    from kokoro_onnx import Kokoro
    k = Kokoro(str(ROOT / c["model"]), str(ROOT / c["voices"]))
    voice = nar.get("voice") if nar.get("voice") in k.get_voices() else c["voice"]
    audio, timing, durations, t, sr = [], [], {}, 0.0, 24000
    for seg in nar["segments"]:
        start, sents = t, []
        for s in sentences(seg["text"]):
            wav, sr = k.create(s, voice=voice, speed=float(seg.get("speed") or c["speed"]), lang=c["lang"])
            wav = np.trim_zeros(wav.astype(np.float32), "b")
            gap = np.zeros(int(sr * 0.12), np.float32)
            sents.append({"text": s, "start": round(t, 3), "end": round(t + len(wav) / sr, 3)})
            audio += [wav, gap]
            t += (len(wav) + len(gap)) / sr
        pause = np.zeros(int(sr * (seg.get("pause_after_ms") or 0) / 1000), np.float32)
        audio.append(pause)
        t += len(pause) / sr
        durations[seg["id"]] = round(t - start, 3)
        timing.append({"id": seg["id"], "start": round(start, 3), "end": round(t, 3), "sentences": sents})
    sf.write(d / "voice" / "narration.wav", np.concatenate(audio), sr)
    (d / "voice" / "durations.json").write_text(json.dumps(durations, indent=1))
    (d / "voice" / "timing.json").write_text(json.dumps(timing, indent=1, ensure_ascii=False))
    print(f"narration.wav {t:.1f}s, {len(durations)} segmentos, voz {voice}")


if __name__ == "__main__":
    main(*sys.argv[1:])
