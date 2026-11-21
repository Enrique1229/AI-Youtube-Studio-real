#!/usr/bin/env python3
"""audio_gen.py — música ambiental y efectos SINTETIZADOS por este proyecto (numpy).

No usa grabaciones ni modelos de terceros: no hay licencias que gestionar.
Lo llama assemble.py; también se puede probar suelto:
    python3 scripts/audio_gen.py <mood> <segundos> <salida.wav>

Música (edl.music.mood): tension | mystery | melancholy | wonder
Efectos: whoosh | hit | riser | swell | boing | splash | pop | slide_down | tada | creak | paddle | clunk | drain | horn | door
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


def _note(freq, dur, kind="pluck"):
    t = np.arange(int(SR * dur)) / SR
    if kind == "bass":   # tuba/bajo: redondo y corto
        return (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) + 0.15 * np.sin(2 * np.pi * 3 * freq * t)) * np.exp(-t * 6) * np.minimum(1, t * 200)
    if kind == "chord":  # acorde corto a contratiempo
        return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)) * np.exp(-t * 16) * np.minimum(1, t * 300)
    return (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t * 30) + 0.2 * np.sin(2 * np.pi * 2 * freq * t)) * np.exp(-t * 9) * np.minimum(1, t * 400)


def comedy_music(seconds, seed):
    """Música original alegre y marcada para comedia: bajo 'um-pa', acordes a contratiempo, melodía saltarina y percusión.
    Cada semilla da otro tempo, tonalidad, progresión y melodía. Sintetizada aquí: sin derechos de terceros."""
    rng = np.random.default_rng(seed)
    bpm = int(rng.choice([126, 132, 138, 144, 152])); beat = 60 / bpm
    root = 110.0 * 2 ** (int(rng.integers(0, 7)) / 12)                                  # tónica (La2 a Mi3)
    prog = [[0, 5, 7, 0], [0, 9, 5, 7], [0, 7, 9, 5], [0, 5, 0, 7]][int(rng.integers(0, 4))]  # grados en semitonos por compás
    minor = {9}                                                                         # el vi es menor
    scale = [0, 2, 4, 7, 9, 12, 14, 16]                                                 # pentatónica mayor (dos octavas)
    motifs = [[int(rng.integers(0, len(scale))) if rng.random() > 0.25 else None for _ in range(8)] for _ in range(2)]
    form = [0, 0, 1, 0]
    n = int(SR * seconds) + SR; out = np.zeros(n)
    def put(sig, at, gain):
        k = int(at * SR)
        if k < n: out[k:k + len(sig)] += sig[:max(0, n - k)] * gain
    kick_t = np.arange(int(SR * 0.16)) / SR; kick = np.sin(2 * np.pi * (110 * np.exp(-kick_t * 28) + 42) * kick_t) * np.exp(-kick_t * 18)
    sn_t = np.arange(int(SR * 0.11)) / SR; snare = rng.standard_normal(len(sn_t)) * np.exp(-sn_t * 34)
    hh_t = np.arange(int(SR * 0.035)) / SR; hat = np.diff(rng.standard_normal(len(hh_t) + 1)) * np.exp(-hh_t * 110)
    bar, t0 = 0, 0.0
    while t0 < seconds:
        deg = prog[bar % 4]; third = 3 if deg in minor else 4; base = root * 2 ** (deg / 12)
        for b in range(4):
            at = t0 + b * beat
            if b % 2 == 0:
                put(_note(base / 2 * (1.0 if b == 0 else 1.498), beat * 0.9, "bass"), at, 0.55); put(kick, at, 0.6)
            else:
                for st in (0, third, 7): put(_note(base * 2 ** (st / 12), beat * 0.5, "chord"), at, 0.16)
                put(snare, at, 0.16)
            for h in (0, 0.5): put(hat, at + h * beat, 0.10 if h else 0.06)
        m = motifs[form[bar % 4]]
        for i, deg_i in enumerate(m):
            if deg_i is not None: put(_note(base * 2 * 2 ** (scale[deg_i] / 12) if scale[deg_i] < 12 else base * 2 ** (scale[deg_i] / 12), beat * 0.45), t0 + i * beat / 2, 0.30)
        bar += 1; t0 += 4 * beat
    out = out[:int(SR * seconds)]
    return norm(fade(np.tanh(out * 1.3), 0.03, min(0.6, seconds / 6)), 0.7)


def _pizz(freq, dur, bright=1.0):
    """Cuerda pulsada (pizzicato) por Karplus-Strong: ataque seco y cola corta."""
    n = int(SR * dur); per = max(2, int(SR / freq)); rng = np.random.default_rng(int(freq * 7))
    buf = rng.uniform(-1, 1, per); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % per]; buf[i % per] = 0.5 * (buf[i % per] + buf[(i + 1) % per]) * (0.985 + 0.012 * bright)
    return fade(out * np.exp(-np.arange(n) / SR * 6), 0.001, 0.03)


def sneaky_music(seconds, seed):
    """Música original de comedia 'a escondidas', tempo tranquilo (~84-94 BPM, como la referencia analizada):
    bajo pizzicato que camina, chasquidos de dedos en 2 y 4, bombo suave, acordes pulsados a contratiempo y un
    motivo juguetón que va y viene. Cada semilla cambia tempo, tonalidad, línea de bajo y motivo. Sin terceros."""
    rng = np.random.default_rng(seed)
    bpm = int(rng.choice([84, 88, 90, 94])); beat = 60 / bpm; sw = beat * 0.08            # ligero swing
    root = 73.42 * 2 ** (int(rng.integers(0, 7)) / 12)                                    # Re2..La2
    prog = [[0, 0, 5, 7], [0, 3, 5, 7], [0, 5, 3, 7], [0, 8, 7, 7]][int(rng.integers(0, 4))]
    scale = [0, 2, 3, 5, 7, 8, 11, 12, 14, 15]                                             # menor armónica: tono pícaro
    walk = [[0, 7, 3, 6], [0, 3, 5, 6], [0, 12, 7, 11]][int(rng.integers(0, 3))]          # bajo caminante con cromatismo
    motif = [int(rng.integers(0, len(scale))) if rng.random() > 0.35 else None for _ in range(8)]
    n = int(SR * seconds) + SR; out = np.zeros(n)
    def put(sig, at, gain):
        k = int(at * SR)
        if 0 <= k < n: out[k:k + len(sig)] += sig[:max(0, n - k)] * gain
    kt = np.arange(int(SR * 0.18)) / SR; kick = np.sin(2 * np.pi * (90 * np.exp(-kt * 30) + 45) * kt) * np.exp(-kt * 16)
    st_ = np.arange(int(SR * 0.06)) / SR; snap = lowpass(rng.standard_normal(len(st_)), 6000) * np.exp(-st_ * 70) * 3
    snap = snap - lowpass(snap, 1200)                                                      # chasquido: solo agudos
    sh_ = np.arange(int(SR * 0.05)) / SR; shaker = (rng.standard_normal(len(sh_)) - lowpass(rng.standard_normal(len(sh_)), 4000)) * np.exp(-sh_ * 60)
    bar, t0 = 0, 0.0
    while t0 < seconds:
        deg = prog[bar % 4]; base = root * 2 ** (deg / 12)
        for b in range(4):
            at = t0 + b * beat + (sw if b % 2 else 0)
            put(_pizz(base * 2 ** (walk[b] / 12), beat * 0.8), at, 0.75)
            if b in (0, 2): put(kick, at, 0.45)
            if b in (1, 3): put(snap, at, 0.35)
            put(shaker, at + beat / 2, 0.06)
            if b in (1, 3):
                for stp in (0, 3, 7): put(_pizz(base * 4 * 2 ** (stp / 12), beat * 0.35, 0.5), at + beat / 2, 0.10)
        if bar % 2 == 1 or rng.random() < 0.3:                                              # el motivo, no todo el rato
            for i, d in enumerate(motif):
                if d is not None: put(_pizz(base * 4 * 2 ** (scale[d] / 12), beat * 0.4), t0 + i * beat / 2 + (sw if i % 2 else 0), 0.30)
        bar += 1; t0 += 4 * beat
    out = out[:int(SR * seconds)]
    return norm(fade(np.tanh(out * 1.2), 0.02, min(0.6, seconds / 6)), 0.7)


def ambience(seconds, seed, birds=True):
    """Ambiente de parque: aire suave + pájaros ocasionales (chirridos sintetizados)."""
    rng = np.random.default_rng(seed); n = int(SR * seconds)
    air = lowpass(rng.standard_normal(n), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * np.arange(n) / SR / 5.3)) * 2
    out = air
    if birds:
        t_ = 0.4
        while t_ < seconds - 0.5:
            f0 = rng.uniform(2800, 4800); m = int(rng.integers(2, 5))
            for k in range(m):
                d = rng.uniform(0.05, 0.11); tt = np.arange(int(SR * d)) / SR
                ch = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.35 * np.sin(np.pi * tt / d))) / SR) * np.sin(np.pi * tt / d) ** 2
                kk = int((t_ + k * (d + 0.03)) * SR); out[kk:kk + len(ch)] += ch[:max(0, n - kk)] * 0.25
            t_ += rng.uniform(1.2, 3.0)
    return norm(out, 0.5)


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
    if kind == "step":       # paso: golpe corto y seco
        t = np.arange(int(SR * 0.09)) / SR
        return norm(np.sin(2 * np.pi * (160 - 600 * t) * t) * np.exp(-t * 55) + 0.4 * lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 80) * 3, 0.5)
    if kind == "boing":      # muelle de dibujos ("doiiing"): tono nasal con vibrato que se apaga y formante que barre
        dur = 0.75; t = np.arange(int(SR * dur)) / SR
        f0 = 118 * (1 + 0.10 * np.exp(-t * 5) * np.sin(2 * np.pi * 13 * t)) * (1 + 0.25 * np.exp(-t * 18))
        ph = np.cumsum(f0) / SR; fc = 380 + 1500 * np.exp(-t * 4.0) * (0.55 + 0.45 * np.sin(2 * np.pi * 13 * t + 0.6))
        x = np.zeros_like(t)
        for k in range(1, 26):
            x += np.exp(-((k * f0 - fc) / 260.0) ** 2) * np.sin(2 * np.pi * k * ph) / (1 + 0.05 * k)
        return norm(fade(x * np.exp(-t * 3.2), 0.002, 0.12), 0.85)
    if kind in ("huh", "oof", "laugh", "sigh", "hmm", "yay"):     # voz del personaje sin palabras (síntesis por formantes)
        def vowel(f0, dur, F, bw=110, jitter=0.0):
            t = np.arange(int(SR * dur)) / SR; f = np.interp(t, np.linspace(0, dur, len(f0)), f0) if hasattr(f0, "__len__") else np.full_like(t, f0)
            f = f * (1 + jitter * np.sin(2 * np.pi * 5.5 * t)); ph = np.cumsum(f) / SR; x = np.zeros_like(t)
            for k in range(1, 40):
                a = sum(np.exp(-((k * f - Fi) / bw) ** 2) * g for Fi, g in F)
                x += a * np.sin(2 * np.pi * k * ph) / (1 + 0.04 * k)
            return x + 0.04 * lowpass(rng.standard_normal(len(t)), 3000)
        if kind == "huh":    # "¿eh?": sube el tono
            x = vowel([170, 175, 260], 0.32, [(650, 1.0), (1150, 0.6), (2500, 0.2)]) * np.sin(np.pi * np.linspace(0, 1, int(SR * 0.32))) ** 0.6
        elif kind == "oof":  # "¡uf!": golpe que saca el aire
            x = vowel([210, 150], 0.22, [(400, 1.0), (800, 0.5), (2400, 0.1)]) * np.exp(-np.linspace(0, 5, int(SR * 0.22)))
        elif kind == "hmm":  # "mmm" pensando / molesto (boca cerrada)
            x = vowel([140, 132, 145], 0.55, [(250, 1.0), (2200, 0.05)], bw=80, jitter=0.01) * np.sin(np.pi * np.linspace(0, 1, int(SR * 0.55))) ** 0.4
        elif kind == "sigh": # suspiro de alivio: aire que cae
            n = int(SR * 0.8); t = np.arange(n) / SR; nz = rng.standard_normal(n)
            x = (lowpass(nz, 1800) - 0.6 * lowpass(nz, 300)) * np.sin(np.pi * t / 0.8) ** 1.5 * 2.5
            x += 0.35 * vowel([180, 120], 0.8, [(600, 1.0), (1000, 0.4)]) * np.sin(np.pi * t / 0.8) ** 2
        elif kind == "yay":  # "¡bien!": vocal abierta que sube
            x = vowel([220, 300, 330], 0.4, [(800, 1.0), (1300, 0.7), (2600, 0.3)], jitter=0.02) * np.sin(np.pi * np.linspace(0, 1, int(SR * 0.4))) ** 0.5
        else:                # risa: "ja-ja-ja-ja"
            parts = []
            for i, f0 in enumerate((260, 245, 235, 220)):
                h = vowel([f0, f0 * 0.93], 0.11, [(850, 1.0), (1250, 0.7), (2600, 0.2)]); h *= np.sin(np.pi * np.linspace(0, 1, len(h))) ** 0.7
                parts += [h, np.zeros(int(SR * 0.045))]
            x = np.concatenate(parts)
        return norm(fade(x, 0.005, 0.04), 0.75)
    if kind == "wahwah":     # trombón triste ("fracaso"): tres notas que bajan y la última tiembla
        out = []
        for i, (f0, d) in enumerate(((233, 0.28), (220, 0.28), (208, 0.28), (196, 0.9))):
            t = np.arange(int(SR * d)) / SR; f = f0 * (1 + (0.03 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0) - (0.06 * t if i == 3 else 0))
            ph = np.cumsum(f) / SR; x = np.zeros_like(t); fc = 900 + 500 * np.sin(np.pi * np.minimum(t / 0.15, 1))
            for k in range(1, 30): x += np.exp(-((k * f - fc) / 500) ** 2) * np.sin(2 * np.pi * k * ph) / k ** 0.6
            out.append(x * np.minimum(1, t / 0.02) * (np.exp(-t * 1.2) if i == 3 else 1))
        return norm(fade(np.concatenate(out), 0.005, 0.2), 0.7)
    if kind == "horn":       # bocina de autobús: dos tonos cuadrados (sol y si) filtrados, ~0,6 s
        dur = 0.6; t = np.arange(int(SR * dur)) / SR
        sq = lambda f: np.sign(np.sin(2 * np.pi * f * t))
        x = lowpass(sq(311.0) + 0.9 * sq(392.0) + 0.05 * rng.standard_normal(len(t)), 1700)
        env = np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.07)
        return norm(fade(x * env, 0.004, 0.05), 0.85)
    if kind == "door":       # "pssh" de puertas neumáticas: ruido de aire que cae, ~0,5 s
        dur = 0.5; t = np.arange(int(SR * dur)) / SR; n_ = rng.standard_normal(len(t))
        hiss = (lowpass(n_, 6500) - lowpass(n_, 1200)) * np.exp(-t * 6.5) * np.minimum(1, t / 0.006)
        tick = np.sin(2 * np.pi * 120 * t) * np.exp(-t * 60) * 0.35
        return norm(fade(hiss * 3 + tick, 0.002, 0.08), 0.8)
    if kind == "whoosh":     # zas: ruido de aire que pasa (banda que sube y baja)
        dur = 0.45; t = np.arange(int(SR * dur)) / SR; n_ = rng.standard_normal(len(t))
        lo = lowpass(n_, 3200) - lowpass(n_, 500); env = np.sin(np.pi * t / dur) ** 2.2
        return norm(fade(lo * env * 3, 0.01, 0.05), 0.75)
    if kind == "splash":     # chapuzón: ruido que se abre y se apaga
        t = np.arange(int(SR * 0.9)) / SR
        x = lowpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 5.5) + 0.6 * lowpass(rng.standard_normal(len(t)), 600) * np.exp(-t * 3) * 4
        x += 0.5 * np.sin(2 * np.pi * 70 * t) * np.exp(-t * 12)
        return norm(fade(x, 0.002, 0.2), 0.9)
    if kind == "ignite":     # cerilla que se enciende: raspado + soplo de llama
        t = np.arange(int(SR * 0.7)) / SR; n_ = rng.standard_normal(len(t))
        scratch = (n_ - lowpass(n_, 2500)) * np.exp(-t * 30) * 1.5
        whoosh = lowpass(rng.standard_normal(len(t)), 900) * np.sin(np.pi * np.minimum(t / 0.6, 1)) * 3
        return norm(fade(scratch + whoosh, 0.002, 0.1), 0.8)
    if kind == "pop":
        t = np.arange(int(SR * 0.12)) / SR
        return norm(np.sin(2 * np.pi * (900 - 4000 * t) * t) * np.exp(-t * 40), 0.8)
    if kind == "slide_down":  # silbato de émbolo que cae ("fiuuu"): tono puro con vibrato y soplo
        dur = 0.9; t = np.arange(int(SR * dur)) / SR
        f = (1500 * np.exp(-t * 2.2) + 260) * (1 + 0.012 * np.sin(2 * np.pi * 6.5 * t))
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.15 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        breath = lowpass(rng.standard_normal(len(t)), 4000) * 0.35
        return norm(fade((tone + breath) * np.minimum(1, t / 0.03) * np.exp(-t * 0.8), 0.01, 0.15), 0.7)
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
    if kind == "bell":       # campana: parciales inarmónicos que se apagan + golpe seco (el volumen da débil/fuerte)
        t = np.arange(int(SR * 1.8)) / SR
        x = sum(am * np.sin(2 * np.pi * fr * t) * np.exp(-t * d) for fr, am, d in ((660, 1.0, 2.2), (1320, 0.6, 3.0), (1780, 0.45, 3.8), (2330, 0.3, 5.0), (3100, 0.15, 7.0)))
        x = x + 0.6 * np.exp(-t * 60) * lowpass(rng.standard_normal(len(t)), 4000)
        return norm(fade(x, 0.001, 0.4), 0.8)
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
