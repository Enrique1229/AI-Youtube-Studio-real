"""ep001 — Cómo cruza el río cada nivel de IQ. Personaje y gags propios."""
import math

TITLE = "Cada nivel de IQ cruzando un río"


def l1(S):  # -450: camina tan seguro… y al agua. Solo queda el sombrero.
    a = S.actor(x=-4.4); S.wait(6); a.blink()
    a.hop_to(-3.7); a.hop_to(-3.0, z=0.12); a.hop_to(-2.3, z=0.12); a.hop_to(-1.8, z=0.12)
    f = S.f; a.fall_in_water(); a.drop_hat_floating(f + 9); S.wait(22); return a


def l2(S):  # -80: coge carrerilla para saltarlo… y se queda a medias.
    a = S.actor(x=-3.0); S.wait(4); a.think(14)
    a.walk_to(-5.2, sound=None); a.tilt(-12); S.wait(6); a.shiver(8, 6)           # retrocede y se prepara
    S.cue("whoosh"); a.hop_to(-3.9, h=0.25, dur=4, sound=None); a.hop_to(-2.6, z=0.12, h=0.25, dur=4, sound=None); a.hop_to(-1.8, z=0.12, h=0.25, dur=4, sound=None)
    S.cue("boing"); a.hop_to(0.2, z=0.6, h=1.6, dur=12, sound=None)                # gran salto… corto
    a.arms_to(150); a.look(0, -0.05); a.blink(S.f + 2); S.wait(7); S.cue("slide_down")
    S.key(a.root, S.f, loc=(0.2, 0, 0.6)); S.key(a.root, S.f + 7, loc=(0.2, 0, -1.9)); S.f += 4; S.splash(0.2, big=1.4); S.wait(26); return a


def l3(S):  # +120: un tablón que se comba y tambalea; llega y celebra.
    plank = S.obj("cube", "tablon", "wood", (0, 0, 0.14), (2.5, 0.22, 0.04), smooth=False)
    a = S.actor(x=-4.2); S.wait(4); a.think(12)
    xs = [-3.3, -2.3, -1.3, -0.3, 0.7, 1.7, 2.7, 3.6]
    for i, x in enumerate(xs):
        onp = -2.4 < x < 2.4; sag = -0.28 * (1 - (x / 2.4) ** 2) if onp else 0.0; f0 = S.f
        a.hop_to(x, z=(0.18 + sag) if onp else 0.0, h=0.4, dur=7)
        S.key(plank, f0 + 9, loc=(0, 0, 0.14 + sag * 0.9), rot=(0, math.radians(4 if i % 2 else -4), 0), interp="BACK")
        a.tilt(14 if i % 2 else -14, f0 + 9)
        if onp: S.cue("creak", f0 + 9, vol=-10)
    S.key(plank, S.f + 4, loc=(0, 0, 0.14), rot=(0, 0, 0), interp="ELASTIC"); a.tilt(0); a.cheer(); S.wait(6); return a


def l4(S):  # +900: una barca hinchable; se sienta, rema con calma y saluda.
    boat = S.empty("barca", (-1.45, 0, -0.16))
    S.obj("uv_sphere", "casco", "red", (0, 0, -0.08), (1.10, 0.62, 0.20), parent=boat)
    S.obj("torus", "borde", "red", (0, 0, 0.06), (1.0, 0.56, 1.0), parent=boat, major_radius=1.0, minor_radius=0.09)
    a = S.actor(x=0.0); a.root.parent = boat
    hip = a.sit(f=1, knee=25); a.root.location = (0.15, 0.12, 0.12 - hip + 0.05)
    for sh in a.arms: S.key(sh, 1, rot=(math.radians(-55), 0, 0))
    for el in a.elbows: S.key(el, 1, rot=(math.radians(-50), 0, 0))
    S.f = 1; remo = a.hold_stick("remo", "wood", 1.45, (0.10, -0.80, -0.45), side=1, free=True)
    n = 84
    for i, fr in enumerate(range(1, n + 1, 6)):
        t_ = (fr - 1) / (n - 1); e_ = t_ * t_ * (3 - 2 * t_)
        S.key(boat, fr, loc=(-1.45 + 3.15 * e_, 0, -0.16 + (0.04 if i % 2 else -0.02)), rot=(0, math.radians(3 if i % 2 else -3), 0))
        if fr < 50 or fr > 82:                                           # palada: brazos adelante y atrás
            for sh in a.arms: S.key(sh, fr, rot=(math.radians(-75 if i % 2 else -30), 0, 0))
            a.tilt(6 if i % 2 else -4, fr)
            a.aim_stick(remo, fr, (-0.45, -0.75, -0.50) if i % 2 else (0.45, -0.75, -0.42))  # pala dentro del agua, por fuera del borde
        if i % 2: S.cue("paddle", fr, vol=-10)
    if a.has_hat:                                                        # saluda con la mano libre (y el sombrero si lo lleva)
        hz = a.hat_z; S.key(a.hat, 50, loc=(0, 0, hz), rot=(0, 0, 0)); S.key(a.hat, 58, loc=(0.25, -0.2, hz + 0.37), rot=(0, math.radians(-40), 0), interp="BACK")
        S.key(a.hat, 70, loc=(0.25, -0.2, hz + 0.37), rot=(0, math.radians(-40), 0)); S.key(a.hat, 80, loc=(0, 0, hz), interp="BACK")
    a.aim_stick(remo, 50, (0.15, -0.75, -0.25)); S.key(a.arms[0], 50, rot=(math.radians(-30), 0, 0)); S.key(a.arms[0], 56, rot=(0, math.radians(150), 0), interp="BACK")
    for k, fr in enumerate(range(58, 76, 4)): S.key(a.elbows[0], fr, rot=(0, math.radians(-25 if k % 2 else 25), 0))
    S.key(a.arms[0], 80, rot=(math.radians(-55), 0, 0)); a.face(-45, 50, turn=4); a.blink(64)
    S.cue("pop", 56, vol=-6); S.f = n + 6; return a


def l5(S):  # +5469: tira de una palanca, el río se vacía y cruza andando, silbando.
    base = S.obj("cube", "base", "metal", (-3.6, 0.9, 0.1), (0.25, 0.25, 0.1), smooth=False)
    piv = S.empty("pivote", (-3.6, 0.9, 0.2)); S.obj("cylinder", "palanca", "metal", (0, 0, 0.45), (0.05, 0.05, 0.45), parent=piv)
    S.obj("uv_sphere", "pomo", "red", (0, 0, 0.95), (0.13, 0.13, 0.13), parent=piv)
    a = S.actor(x=-4.6); S.wait(4); a.think(16); a.hop_to(-3.9, h=0.3, dur=6)
    a.arms_to(110); S.key(piv, S.f, rot=(0, math.radians(-30), 0)); S.wait(5); S.cue("clunk")
    S.key(piv, S.f, rot=(0, math.radians(40), 0), interp="BACK"); a.arms_to(20, S.f + 2); S.wait(6)
    S.cue("drain"); S.key(S.water, S.f, loc=(0, 0, -1.75)); S.key(S.water, S.f + 34, loc=(0, 0, -2.75)); a.look(0.04, -0.03); a.blink(S.f + 10); S.wait(36); a.look(0, 0)
    a.walk_to(-2.6); a.hop_to(-1.6, z=-1.1, h=0.4, dur=9); a.walk_to(1.6, steps=4); a.hop_to(2.9, z=0.0, h=1.5, dur=11); a.cheer(); S.wait(6); return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
