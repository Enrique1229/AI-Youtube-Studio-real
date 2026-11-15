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


def l4(S):  # +900: una barca; rema tranquilo y saluda con el sombrero.
    boat = S.empty("barca", (-1.9, 0, -0.16))
    S.obj("uv_sphere", "casco", "red", (0, 0, 0), (1.05, 0.55, 0.32), parent=boat)
    S.obj("cube", "banco", "wood", (0, 0, 0.16), (0.8, 0.4, 0.03), parent=boat, smooth=False)
    remo = S.obj("cube", "remo", "wood", (0, -0.62, 0.3), (0.05, 0.05, 0.75), rot=(0.9, 0, 0), parent=boat, smooth=False)
    a = S.actor(x=0.0); a.root.parent = boat; a.root.location = (0, 0, 0.18)
    n = 84
    for i, fr in enumerate(range(1, n + 1, 6)):
        t = (fr - 1) / (n - 1); e = t * t * (3 - 2 * t)
        S.key(boat, fr, loc=(-1.9 + 3.6 * e, 0, -0.16 + (0.04 if i % 2 else -0.02)), rot=(0, math.radians(3 if i % 2 else -3), 0))
        S.key(remo, fr, rot=(0.9, math.radians(35 if i % 2 else -35), 0)); a.arms_to(35 if i % 2 else -20, fr)
        if i % 2: S.cue("paddle", fr, vol=-10)
    hz = a.hat_z; S.key(a.hat, 50, loc=(0, 0, hz), rot=(0, 0, 0)); S.key(a.hat, 58, loc=(0.25, -0.2, hz + 0.37), rot=(0, math.radians(-40), 0), interp="BACK")
    S.key(a.hat, 70, loc=(0.25, -0.2, hz + 0.37), rot=(0, math.radians(-40), 0)); S.key(a.hat, 80, loc=(0, 0, hz), rot=(0, 0, 0), interp="BACK")
    S.cue("pop", 58, vol=-6); a.blink(64); S.f = n + 6; S.follow_obj = boat; return a


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
