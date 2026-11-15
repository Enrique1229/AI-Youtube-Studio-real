#!/usr/bin/env python3
"""audio_gen.py — música ambiental y efectos SINTETIZADOS por este proyecto (numpy).

No usa grabaciones ni modelos de terceros: no hay licencias que gestionar.
Lo llama assemble.py; también se puede probar suelto:
    python3 scripts/audio_gen.py <mood> <segundos> <salida.wav>

Música (edl.music.mood): tension | mystery | melancholy | wonder
Efectos: whoosh | hit | riser | swell | boing | splash | pop | slide_down | tada | creak | paddle | clunk | drain
"""
import sys, zlib
import numpy as np, soundfile as sf

SR = 48000
# Intervalos en semitonos sobre la tónica: dos acordes que se alternan lentamente.
MOODS = {
    "tension": ([0, 1, 7, 12], [0, 6, 7, 13], 0.55),
    "mystery": ([0, 3, 7, 14], [0, 5, 8, 12], 0.45),
    "melancholy": ([0, 3, 7, 10], [-4, 0, 3, 7], 0.35),
    "wonder": ([0, 7, 12, 16], [0, 5, 12, 17], 0.30),
}


def lowpass(x, cutoff):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def fade(x, t_in, t_out):
    n_in, n_out = int(SR * t_in), int(SR * t_out)
    x = x.copy()
    x[:n_in] *= np.linspace(0, 1, n_in) ** 2
    x[-n_out:] *= np.linspace(1, 0, n_out) ** 2
    return x


def norm(x, peak=0.7):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def chord(intervals, root_hz, t, rng):
    out = np.zeros_like(t)
    for i, st in enumerate(intervals):
        f = root_hz * 2 ** (st / 12)
        for det in (-0.15, 0.15):  # dos voces desafinadas por nota: suena a "pad"
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.03, 0.11) * t + rng.uniform(0, 6.28))
            out += lfo * np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6.28)) / (1 + i * 0.5)
    return out


def music(mood, seconds, seed):
    a, b, noise_amt = MOODS.get(mood, MOODS["mystery"])
    rng = np.random.default_rng(seed)
    root = 55.0 * 2 ** (int(rng.integers(0, 8)) / 12)  # tónica grave distinta por historia
    t = np.arange(int(SR * seconds)) / SR
    mix = 0.5 + 0.5 * np.sin(2 * np.pi * t / float(rng.uniform(14, 22)) - np.pi / 2)  # alterna los acordes
    pad = (1 - mix) * chord(a, root, t, rng) + mix * chord(b, root, t, rng)
    sub = 0.5 * np.sin(2 * np.pi * root / 2 * t)
    air = lowpass(rng.standard_normal(len(t)), 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
    x = lowpass(pad, 1800) + sub + noise_amt * 6 * air
    return norm(fade(x, min(2.0, seconds / 4), min(2.5, seconds / 4)), 0.6)


def sfx(kind, seed):
    rng = np.random.default_rng(seed)
    if kind == "hit":
        t = np.arange(int(SR * 1.4)) / SR
        x = np.sin(2 * np.pi * 48 * t * (1 + 0.6 * np.exp(-t * 18))) * np.exp(-t * 3.5)
        x += 0.5 * lowpass(rng.standard_normal(len(t)), 700) * np.exp(-t * 14) * 8
        return norm(fade(x, 0.002, 0.2), 0.9)
    if kind == "riser":
        t = np.arange(int(SR * 2.6)) / SR
        sweep = np.sin(2 * np.pi * (160 * t + (900 / 2.6) * t ** 2 / 2))
        x = (sweep * 0.5 + lowpass(rng.standard_normal(len(t)), 3500) * 3) * (t / 2.6) ** 2.5
        return norm(fade(x, 0.05, 0.03), 0.8)
    if kind == "swell":
        t = np.arange(int(SR * 3.0)) / SR
        x = chord([0, 7, 12], 82.4, t, rng) * np.sin(np.pi * t / 3.0) ** 2
        return norm(lowpass(x, 1200), 0.7)
    if kind == "boing":      # muelle: tono que sube y vibra
        t = np.arange(int(SR * 0.32)) / SR
        f = 180 + 520 * (t / 0.32) ** 0.6 + 40 * np.sin(2 * np.pi * 28 * t)
        return norm(fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7), 0.003, 0.05), 0.8)
    if kind == "splash":     # chapuzón: ruido que se abre y se apaga
        t = np.arange(int(SR * 0.9)) / SR
        x = lowpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 5.5) + 0.6 * lowpass(rng.standard_normal(len(t)), 600) * np.exp(-t * 3) * 4
        x += 0.5 * np.sin(2 * np.pi * 70 * t) * np.exp(-t * 12)
        return norm(fade(x, 0.002, 0.2), 0.9)
    if kind == "pop":
        t = np.arange(int(SR * 0.12)) / SR
        return norm(np.sin(2 * np.pi * (900 - 4000 * t) * t) * np.exp(-t * 40), 0.8)
    if kind == "slide_down":  # silbido que cae: "se viene abajo"
        t = np.arange(int(SR * 0.6)) / SR
        f = 1400 * np.exp(-t * 3.2) + 180
        return norm(fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)), 0.01, 0.1), 0.7)
    if kind == "tada":       # arpegio mayor: éxito
        out = np.zeros(int(SR * 0.9))
        for i, st in enumerate((0, 4, 7, 12)):
            t = np.arange(int(SR * 0.5)) / SR; f = 523.25 * 2 ** (st / 12)
            n = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 5)
            k = int(SR * 0.09 * i); out[k:k + len(n)] += n[:len(out) - k]
        return norm(out, 0.8)
    if kind == "creak":      # madera que cruje
        t = np.arange(int(SR * 0.22)) / SR
        return norm(np.sign(np.sin(2 * np.pi * (90 + 60 * t) * t)) * lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 9), 0.6)
    if kind == "paddle":     # remo en el agua
        t = np.arange(int(SR * 0.35)) / SR
        return norm(fade(lowpass(rng.standard_normal(len(t)), 1400) * np.sin(np.pi * t / 0.35) ** 2, 0.02, 0.08), 0.6)
    if kind == "clunk":      # palanca
        t = np.arange(int(SR * 0.25)) / SR
        return norm(np.sin(2 * np.pi * 140 * t) * np.exp(-t * 22) + 0.5 * lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 45) * 4, 0.9)
    if kind == "drain":      # el agua se va por el desagüe
        t = np.arange(int(SR * 1.5)) / SR
        f = 900 * np.exp(-t * 1.6) + 120
        x = lowpass(rng.standard_normal(len(t)), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f / 30) / SR)) + 0.3 * np.sin(2 * np.pi * np.cumsum(f) / SR)
        return norm(fade(x * (1 - t / 1.5) ** 0.5, 0.05, 0.3), 0.7)
    t = np.arange(int(SR * 0.8)) / SR  # whoosh
    x = lowpass(rng.standard_normal(len(t)), 2500) * np.sin(np.pi * t / 0.8) ** 3
    return norm(x, 0.7)


def seed_of(text):
    return zlib.crc32(text.encode())


def build(story_dir, edl, seconds):
    """Genera los wav que pide el EDL. Devuelve (ruta_música|None, {índice_sfx: ruta})."""
    out_m, out_s = None, {}
    m = edl.get("music") or {}
    if m.get("mood"):
        d = story_dir / "assets" / "music"
        d.mkdir(parents=True, exist_ok=True)
        out_m = d / f"bed-{m['mood']}.wav"
        sf.write(out_m, music(m["mood"], seconds, seed_of(story_dir.name + m["mood"])), SR)
    for i, s in enumerate(edl.get("sfx") or []):
        d = story_dir / "assets" / "sfx"
        d.mkdir(parents=True, exist_ok=True)
        out_s[i] = d / f"{i:02d}-{s['type']}.wav"
        sf.write(out_s[i], sfx(s["type"], seed_of(story_dir.name + str(i))), SR)
    return out_m, out_s


if __name__ == "__main__":
    mood, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    sf.write(out, music(mood, secs, 1) if mood in MOODS else sfx(mood, 1), SR)
    print(out)
