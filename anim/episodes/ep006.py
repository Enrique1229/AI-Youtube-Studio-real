"""ep006 — Cada nivel de IQ protege un bocadillo de una gaviota. Gaviota y bocadillo construidos con S.obj (sin tocar kit.py)."""
import math
import bpy

TITLE = "Every IQ Level Protects a Sandwich From a Seagull"
R = math.radians
PI = math.pi


# ---------------------------------------------------------------- utilidades
class G:  # gaviota
    pass


def mk_gull(S, x, z=0.0, scale=1.0, parent=None):
    g = G()
    g.root = S.empty("gaviota", (x, 0, z), parent=parent); g.root.scale = (scale,) * 3
    r = g.root
    S.obj("uv_sphere", "cuerpo", "white", (0, 0, 0.42), (0.38, 0.21, 0.21), parent=r)
    S.obj("uv_sphere", "lomo", "gray", (0.05, 0, 0.52), (0.30, 0.20, 0.13), parent=r)
    S.obj("cone", "cola", "gray", (0.46, 0, 0.44), (0.10, 0.07, 0.16), rot=(0, R(90), 0), parent=r)
    S.obj("uv_sphere", "cabeza", "white", (-0.34, 0, 0.68), (0.17, 0.15, 0.16), parent=r)
    g.beak = S.empty("pico", (-0.56, 0, 0.64), parent=r)
    S.obj("cone", "pico_c", "yellow", (-0.54, 0, 0.64), (0.055, 0.05, 0.11), rot=(0, R(-90), 0), parent=r)
    S.obj("uv_sphere", "mancha", "red", (-0.60, 0.0, 0.60), (0.02, 0.025, 0.02), parent=r)
    g.eyes = []
    for sy in (-1, 1):
        e = S.empty("ojo", (-0.42, 0.12 * sy, 0.73), parent=r)
        S.obj("uv_sphere", "ojo_b", "white", (0, 0, 0), (0.085, 0.07, 0.085), parent=e)
        S.obj("uv_sphere", "pupila", "black", (-0.05, 0.015 * sy, -0.005), (0.04, 0.035, 0.045), parent=e)
        g.eyes.append(e)
    for sy in (-1, 1):
        S.obj("cylinder", "pata", "orange", (-0.02, 0.09 * sy, 0.14), (0.018, 0.018, 0.14), parent=r)
        S.obj("cube", "pie", "orange", (-0.07, 0.09 * sy, 0.02), (0.09, 0.05, 0.012), parent=r)
    g.wings = []
    for sy in (-1, 1):
        p = S.empty("ala", (0.02, 0.18 * sy, 0.52), parent=r)
        S.obj("cube", "ala_b", "white", (0.02, 0.30 * sy, 0), (0.24, 0.30, 0.022), parent=p)
        S.obj("cube", "ala_p", "gray", (0.10, 0.54 * sy, 0), (0.18, 0.08, 0.024), parent=p)
        g.wings.append(p)
    wing(S, g, 1, -68)
    return g


def wing(S, g, f, ang, interp="BEZIER"):
    S.key(g.wings[0], f, rot=(R(-ang), 0, 0), interp=interp)
    S.key(g.wings[1], f, rot=(R(ang), 0, 0), interp=interp)
    k = 0.5 if ang < -50 else 1.0
    for w in g.wings: S.key(w, f, scale=(1, k, 1), interp=interp)


def flap(S, g, f0, n, per=3, up=55, down=-20):
    for i in range(n // per + 1):
        wing(S, g, f0 + i * per, up if i % 2 == 0 else down)


def eyes(S, g, f, k):
    for e in g.eyes: S.key(e, f, scale=(k, k, k))


def gpos(S, g, f, x, z, interp="BEZIER"):
    S.key(g.root, f, loc=(x, 0, z), interp=interp)


def turn(S, g, f, right):
    S.key(g.root, f, rot=(0, 0, PI if not right else 0)); S.key(g.root, f + 3, rot=(0, 0, 0 if not right else PI))


def hop_g(S, g, f, x0, x1, h=0.2, n=6):
    gpos(S, g, f, x0, 0); gpos(S, g, f + n // 2, (x0 + x1) / 2, h); gpos(S, g, f + n, x1, 0)
    S.cue("pop", f + n, vol=-14)


def mk_sand(S):
    s = S.empty("bocata", (0, 0, 5)); s.scale = (1.3,) * 3
    S.obj("cube", "pan1", "khaki", (0, 0, -0.045), (0.17, 0.11, 0.035), parent=s, smooth=False)
    S.obj("cube", "jamon", "pink", (0.005, 0, -0.008), (0.175, 0.115, 0.012), parent=s, smooth=False)
    S.obj("cube", "lechuga", "lime", (0, 0, 0.012), (0.18, 0.12, 0.012), parent=s, smooth=False)
    S.obj("cube", "tomate", "red", (0, 0, 0.03), (0.15, 0.1, 0.01), parent=s, smooth=False)
    S.obj("cube", "pan2", "khaki", (0, 0, 0.062), (0.17, 0.11, 0.035), parent=s, smooth=False)
    return s


def follow(obj, target, f_on, f_off=None):
    c = obj.constraints.new("COPY_LOCATION"); c.target = target
    c.influence = 0.0; c.keyframe_insert("influence", frame=max(1, f_on - 1))
    c.influence = 1.0; c.keyframe_insert("influence", frame=f_on)
    if f_off:
        c.influence = 1.0; c.keyframe_insert("influence", frame=f_off - 1)
        c.influence = 0.0; c.keyframe_insert("influence", frame=f_off)
    return c


def grip(S, a, side=1):
    return S.empty("agarre", (0, -0.005, -a._dims["fa"] - 0.07), parent=a.elbows[side])


def arm(S, a, f, x=0, y=0, el=0, side=1):
    S.key(a.arms[side], f, rot=(R(x), R(y), 0)); S.key(a.elbows[side], f, rot=(R(-12 + el), 0, 0))


def hold_front(S, a, f):   # sandwich delante
    arm(S, a, f, x=-70, el=-45)


def to_mouth(S, a, f):
    arm(S, a, f, x=-105, el=-85)


def up_arm(S, a, f):
    arm(S, a, f, y=-150, el=0)


def rest_arm(S, a, f):
    arm(S, a, f, 0, 0, 0)


def wpos(S, obj, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return tuple(obj.matrix_world.translation)


def stage_start(S, x_man, x_gull, land=12, size=1.0):
    """Fotograma 1: la gaviota ya vuela hacia el bocadillo que el hombre lleva en la mano."""
    a = S.actor(x=x_man)
    sand = mk_sand(S); follow(sand, grip(S, a), 1)
    hold_front(S, a, 1)
    g = mk_gull(S, x_gull, 0.0, size)
    gpos(S, g, 1, x_gull + 3.2, 2.7); gpos(S, g, land - 3, x_gull + 0.3, 0.7); gpos(S, g, land, x_gull, 0.0)
    flap(S, g, 1, land - 2, per=3); wing(S, g, land - 1, 62); wing(S, g, land + 4, -68)
    eyes(S, g, land, 1.0); eyes(S, g, land + 4, 1.5)
    S.cue("whoosh", 1, vol=-8); S.cue("pop", land, vol=-8)
    return a, sand, g


def fly_away(S, g, f, to=(5.5, 4.5), n=34, carry_turn=True):
    if carry_turn: turn(S, g, f, True)
    x0, z0 = S.sc.frame_current, 0
    flap(S, g, f, n, per=3)
    S.key(g.root, f + n // 2, loc=(to[0] - 3.5, 0, to[1] * 0.45))
    S.key(g.root, f + n, loc=(to[0], 0, to[1]))


# ---------------------------------------------------------------- niveles
def l1(S):  # -400: lo esconde en el sombrero; la gaviota se lleva sombrero y bocadillo
    a, sand, g = stage_start(S, -4.6, -3.2)
    hz = a.hat_z
    H = S.empty("copa", (0, 0, hz), parent=a.body); H.scale = (0.62,) * 3
    S.obj("cylinder", "ala", "navy", (0, 0, 0), (0.36, 0.36, 0.025), parent=H)
    S.obj("cylinder", "copa_c", "black", (0, 0, 0.26), (0.20, 0.20, 0.26), parent=H)
    S.obj("cylinder", "cinta", "red", (0, 0, 0.08), (0.205, 0.205, 0.04), parent=H)
    slot = S.empty("hueco", (0, 0, 0.22), parent=H)
    # f14-26: se quita el sombrero, mete el bocadillo y se lo pone
    S.key(H, 12, loc=(0, 0, hz)); S.key(H, 17, loc=(-0.25, 0, hz + 0.55), interp="BACK"); S.key(H, 27, loc=(-0.25, 0, hz + 0.55)); S.key(H, 31, loc=(0, 0, hz), interp="BOUNCE")
    arm(S, a, 12, x=-70, el=-45); up_arm(S, a, 19); arm(S, a, 28, y=-70, el=-30); rest_arm(S, a, 40)
    S.key(sand, 18, scale=(1.3,) * 3); S.key(sand, 26, scale=(0.62,) * 3)
    follow(sand, slot, 27)
    S.cue("pop", 27, vol=-4); S.cue("clunk", 31, vol=-10)
    a.blink(36); a.look(0.03, 0.0, 40)
    # la gaviota inclina la cabeza y se acerca, pausa del hombre
    S.key(g.root, 22, rot=(0, R(8), 0)); S.key(g.root, 40, rot=(0, R(-8), 0)); S.key(g.root, 50, rot=(0, 0, 0))
    hop_g(S, g, 46, -3.2, -3.6, 0.12, 6); hop_g(S, g, 56, -3.6, -4.0, 0.12, 6)
    a.look(0, 0, 50); a.blink(60)
    # salta y se lleva el sombrero
    xh, yh, zh = wpos(S, H, 80)
    gx, gz = xh + 0.56, zh - 0.64
    gpos(S, g, 66, -4.0, 0.0); gpos(S, g, 69, -4.0, -0.04)
    flap(S, g, 70, 10, per=2)
    gpos(S, g, 76, gx, gz)
    S.cue("whoosh", 70, vol=-6)
    follow(H, g.beak, 76)
    eyes(S, g, 76, 1.2)
    turn(S, g, 78, True)
    flap(S, g, 76, 40, per=3)
    S.key(g.root, 90, loc=(-1.2, 0, 3.0)); S.key(g.root, 112, loc=(3.0, 0, 5.0))
    up_arm(S, a, 80); S.cue("boing", 80, vol=-6)
    rest_arm(S, a, 102); a.look(0.04, 0.06, 90)
    S.f = 102; a.shiver(10, 8); a.blink(S.f)
    S.wait(18)
    return a


def l2(S):  # -90: salta con el bocadillo en alto; la gaviota se lo quita en el aire
    a, sand, g = stage_start(S, -4.6, -3.3)
    up_arm(S, a, 6)
    base_f = [16, 28, 40]
    zs = {}
    for f0 in base_f:
        S.key(a.root, f0, loc=(-4.6, 0, 0.0)); S.key(a.root, f0 + 6, loc=(-4.6, 0, 0.65)); S.key(a.root, f0 + 12, loc=(-4.6, 0, 0.0)); S.cue("boing", f0, vol=-6)
        S.key(g.root, f0 + 6, rot=(0, R(-10), 0)); S.key(g.root, f0 + 12, rot=(0, R(10), 0))
    apex = base_f[2] + 6
    # la gaviota se agacha y se lanza
    gpos(S, g, 38, -3.3, 0.0); gpos(S, g, 41, -3.3, -0.05)
    sx, sy, sz = wpos(S, sand, apex)
    flap(S, g, 42, 8, per=2)
    gx, gz = sx + 0.56, sz - 0.64
    gpos(S, g, apex, gx, gz)
    eyes(S, g, apex, 1.5)
    follow(sand, g.beak, apex)
    S.cue("whoosh", 42, vol=-6)
    turn(S, g, apex + 1, True)
    flap(S, g, apex, 40, per=3)
    S.key(g.root, apex + 16, loc=(-1.0, 0, 3.4)); S.key(g.root, apex + 40, loc=(4.0, 0, 5.0))
    # él cae con la mano vacía
    S.key(a.root, apex + 1, loc=(-4.6, 0, 0.62)); S.key(a.root, apex + 7, loc=(-4.6, 0, 0.0))
    a.blink(apex + 8); a.look(0.04, 0.06, apex + 6)
    S.f = apex + 20; a.shiver(8, 8)
    rest_arm(S, a, S.f + 4)
    S.wait(30)
    return a


def l3(S):  # 110: se lo come de tres bocados; se atraganta, se golpea el pecho y traga a tiempo
    a, sand, g = stage_start(S, -4.6, -3.2)
    S.key(sand, 12, scale=(1.3,) * 3)
    bites = [(22, 0.68), (38, 0.36), (54, 0.001)]
    for f, k in bites:
        hold_front(S, a, f - 10); to_mouth(S, a, f - 2); a.tilt(-8, f - 2); to_mouth(S, a, f + 1)
        S.key(sand, f + 1, scale=(1.3 * k,) * 3, interp="CONSTANT"); S.cue("pop", f + 1, vol=-4)
        hold_front(S, a, f + 6); a.tilt(0, f + 6)
        S.key(g.root, f, rot=(0, R(10 if k > 0.5 else -10), 0))
        eyes(S, g, f, 1.5 if k > 0.5 else 1.8)
    S.key(sand, 21, scale=(1.3,) * 3); S.key(sand, 37, scale=(1.3 * 0.68,) * 3); S.key(sand, 53, scale=(1.3 * 0.36,) * 3)
    # atragantamiento
    S.f = 62; a.shiver(12, 16); a.blink(S.f)
    for i, f in enumerate(range(72, 90, 4)):
        arm(S, a, f, x=-40 if i % 2 else -20, y=0, el=-100 if i % 2 else -70); S.cue("hit", f, vol=-8)
    a.tilt(-12, 84); a.tilt(0, 92)
    S.cue("slide_down", 90, vol=-8)
    S.key(a.arms[0], 1, rot=(0, 0, 0)); S.key(a.arms[0], 88, rot=(0, 0, 0)); up_arm(S, a, 96); S.key(a.arms[0], 96, rot=(0, R(150), 0))
    S.key(g.root, 90, rot=(0, 0, 0))
    wing(S, g, 94, -90); eyes(S, g, 96, 1.0)
    turn(S, g, 102, True)
    flap(S, g, 108, 30, per=3)
    gpos(S, g, 100, -3.2, 0.0); gpos(S, g, 108, -3.2, -0.02); gpos(S, g, 124, -0.5, 2.6); gpos(S, g, 140, 4.0, 4.5)
    S.cue("tada", 98, vol=-8)
    S.f = 128
    return a


def l4(S):  # 800: lo tapa con una campana; la gaviota levanta la campana y se lleva el bocadillo
    a, sand, g = stage_start(S, -4.8, -3.0)
    dome = S.empty("campana", (-4.05, 0, 4.0))
    S.obj("uv_sphere", "domo", "metal", (0, 0, 0.0), (0.42, 0.32, 0.34), parent=dome)
    S.obj("uv_sphere", "pomo", "gold", (0, 0, 0.35), (0.07, 0.07, 0.07), parent=dome)
    # lo baja al suelo, la campana cae encima
    hold_front(S, a, 2); arm(S, a, 12, x=-45, el=-20); a.tilt(18, 14); a.tilt(0, 28)
    sloc = (-4.05, 0, 0.06)
    S.key(sand, 14, loc=sloc, scale=(1.3,) * 3)
    c = sand.constraints[0]
    c.influence = 1.0; c.keyframe_insert("influence", frame=13); c.influence = 0.0; c.keyframe_insert("influence", frame=14)
    S.key(sand, 14, loc=sloc)
    rest_arm(S, a, 26)
    S.key(dome, 1, loc=(-4.05, 0, 9.0)); S.key(dome, 24, loc=(-4.05, 0, 0.0)); S.key(dome, 27, loc=(-4.05, 0, 0.14)); S.key(dome, 30, loc=(-4.05, 0, 0.0))
    S.key(dome, 66, loc=(-4.05, 0, 0.0)); S.key(dome, 67, loc=(-4.05, 0, 0.0))
    S.cue("clunk", 26, vol=-2)
    S.key(a.arms[0], 1, rot=(0, 0, 0)); S.key(a.arms[0], 26, rot=(0, 0, 0)); up_arm(S, a, 30); S.key(a.arms[0], 30, rot=(0, R(150), 0)); a.blink(34)
    # la gaviota picotea la campana
    for k, f in enumerate((40, 48, 56)):
        gpos(S, g, f, -3.0 if k == 0 else -3.45, 0.0)
        S.key(g.root, f + 2, loc=(-3.45, 0, 0.1)); S.key(g.root, f + 4, loc=(-3.45, 0, 0.0))
        S.key(dome, f + 2, rot=(0, R(-8), 0)); S.key(dome, f + 5, rot=(0, R(5), 0)); S.key(dome, f + 8, rot=(0, 0, 0))
        S.cue("clunk", f + 2, vol=-8)
    gpos(S, g, 40, -3.0, 0.0); gpos(S, g, 46, -3.45, 0.0)
    # agarra el pomo y levanta la campana
    knob = S.empty("pomo_t", (0, 0, 0.42), parent=dome)
    kx, ky, kz = wpos(S, knob, 66)
    gpos(S, g, 62, -3.45, 0.0); flap(S, g, 62, 10, per=2)
    gpos(S, g, 68, kx + 0.56, kz - 0.64)
    follow(dome, g.beak, 68)
    S.key(dome, 66, rot=(0, 0, 0))
    eyes(S, g, 68, 1.5)
    gpos(S, g, 78, -3.4, 1.4)
    a.look(0.0, 0.05, 70)
    S.f = 74; a.shiver(8, 8)
    rest_arm(S, a, 74)
    # suelta la campana a un lado y se lanza al bocadillo
    S.key(g.root, 82, loc=(-2.4, 0, 1.8))
    c2 = dome.constraints[-1]
    c2.influence = 1.0; c2.keyframe_insert("influence", frame=82); c2.influence = 0.0; c2.keyframe_insert("influence", frame=83)
    S.key(dome, 83, loc=(-2.4, 0, 0.8)); S.key(dome, 92, loc=(-1.9, 0, 0.12), interp="BOUNCE")
    S.key(dome, 92, rot=(0, R(10), 0)); S.cue("clunk", 92, vol=-4)
    wing(S, g, 84, 40); flap(S, g, 84, 30, per=3)
    gpos(S, g, 90, -4.05 + 0.56, 0.1 + 0.0 - 0.1)
    follow(sand, g.beak, 91)
    turn(S, g, 93, True)
    S.key(g.root, 108, loc=(-1.0, 0, 3.0)); S.key(g.root, 126, loc=(4.0, 0, 4.5))
    S.cue("whoosh", 86, vol=-6)
    a.blink(92); a.look(0.04, 0.0, 94)
    arm(S, a, 96, y=-100, el=0)
    S.f = 98; a.shiver(8, 8)
    S.wait(30)
    return a


def l5(S):  # 5469: planta un espejo; la gaviota ve a otra gaviota con bocadillo, se asusta y se va; él come y saluda
    a = S.actor(x=-5.6)
    sand = mk_sand(S); follow(sand, grip(S, a), 1); hold_front(S, a, 1)
    xm = -4.15
    M = S.empty("espejo", (xm, 0.1, 0.0)); M.rotation_euler = (R(-90), 0, 0)
    S.obj("cube", "marco", "gold", (0, 0.02, 0.92), (0.58, 0.02, 0.70), parent=M, smooth=False)
    S.obj("cube", "luna", "foam", (0, 0.0, 0.92), (0.50, 0.015, 0.62), parent=M, smooth=False)
    for sx in (-1, 1):
        S.obj("cylinder", "pata_e", "wood", (0.3 * sx, 0.1, 0.12), (0.03, 0.03, 0.12), parent=M)
    return _l5_build(S, a, sand, M, xm)


def _l5_build(S, a, sand, M, xm):
    # el empty M está tumbado (rot x -90): se levanta con el "gesto de plantarlo"
    # reflejo en un empty independiente que sigue la posición del espejo
    ref = S.empty("reflejo", (xm - 0.0, 0.05, 0.0))
    ig = mk_gull(S, 0.0, 0.0, 0.0, parent=ref)
    ig.root.scale = (0.001,) * 3
    hip_f = 20
    # gaviota real
    g = mk_gull(S, -2.6, 0.0)
    gpos(S, g, 1, -0.6, 2.7); gpos(S, g, 9, -2.3, 0.7); gpos(S, g, 12, -2.6, 0.0)
    flap(S, g, 1, 10, per=3); wing(S, g, 11, 62); wing(S, g, 16, -68)
    eyes(S, g, 12, 1.0); eyes(S, g, 16, 1.5)
    S.cue("whoosh", 1, vol=-8); S.cue("pop", 12, vol=-8)
    # el hombre planta el espejo (f14-26): se agacha y lo levanta
    a.tilt(20, 14); S.key(M, 14, rot=(R(-90), 0, 0)); S.key(M, 24, rot=(0, 0, 0), interp="BACK"); S.cue("clunk", 24, vol=-4)
    a.tilt(0, 28)
    # reflejo: aparece cuando el espejo está de pie; imita a la gaviota (simétrico)
    S.key(ref, 23, loc=(xm - 0.0, 0.05, 0.40)); S.key(ref, 24, loc=(xm - 0.0, 0.05, 0.40))
    sc = 0.55
    S.key(ig.root, 23, scale=(0.001,) * 3); S.key(ig.root, 25, scale=(sc, 0.05, sc))
    ig.root.rotation_euler = (0, 0, PI); S.key(ig.root, 23, rot=(0, 0, PI))
    S.key(ig.root, 25, loc=(0.0, -0.0, 0.0))
    isand = mk_sand(S); isand.parent = ig.root; isand.location = (-0.66, 0, 0.58); isand.scale = (0.55, 0.9, 0.55)
    # él se sienta (f26-36)
    for lg in a.legs: S.key(lg, 26, rot=(0, 0, 0))
    for kn in a.knees: S.key(kn, 26, rot=(0, 0, 0))
    S.key(a.root, 26, loc=(-5.6, 0, 0.0))
    hip = a.sit(f=36, knee=25)
    S.key(a.root, 36, loc=(-5.6, 0, 0.08 - hip))
    S.cue("slide_down", 32, vol=-12)
    a.blink(40)
    # la gaviota ve su reflejo: se infla, se acerca a saltitos, se alarma
    S.key(g.root, 28, rot=(0, R(-8), 0)); S.key(g.root, 34, rot=(0, R(8), 0)); S.key(g.root, 40, rot=(0, 0, 0))
    eyes(S, g, 30, 1.9)
    hop_g(S, g, 44, -2.6, -3.0, 0.14, 6); hop_g(S, g, 54, -3.0, -3.3, 0.14, 6)
    S.key(g.root, 60, scale=(1.0,) * 3); S.key(g.root, 63, scale=(1.18,) * 3)
    wing(S, g, 58, 50); wing(S, g, 66, -68)
    S.key(ig.root, 58, scale=(sc, 0.05, sc)); S.key(ig.root, 63, scale=(sc * 1.18, 0.06, sc * 1.18))
    S.key(ig.root, 66, scale=(sc, 0.05, sc))
    S.key(g.root, 66, scale=(1.0,) * 3)
    S.cue("hit", 62, vol=-12)
    # se asusta: ojos enormes, hacia atrás y se va volando ileso
    eyes(S, g, 66, 2.1)
    gpos(S, g, 62, -3.3, 0.0); gpos(S, g, 70, -2.9, 0.25); gpos(S, g, 74, -2.7, 0.0)
    turn(S, g, 76, True)
    flap(S, g, 76, 40, per=3)
    gpos(S, g, 76, -2.7, 0.0); gpos(S, g, 90, -0.8, 2.6); gpos(S, g, 112, 4.5, 4.8)
    S.cue("whoosh", 78, vol=-6)
    # reflejo: sorprendido también (se encoge y desaparece del plano)
    eyes(S, ig, 66, 1.7)
    # él come
    to_mouth(S, a, 92); hold_front(S, a, 84)
    S.key(sand, 84, scale=(1.3,) * 3)
    to_mouth(S, a, 96); S.key(sand, 97, scale=(0.8,) * 3, interp="CONSTANT"); S.cue("pop", 97, vol=-4)
    hold_front(S, a, 104); a.tilt(0, 104)
    to_mouth(S, a, 112); S.key(sand, 113, scale=(0.4,) * 3, interp="CONSTANT"); S.cue("pop", 113, vol=-4)
    hold_front(S, a, 120)
    # saluda al espejo; el reflejo le devuelve el saludo con el ala
    S.key(a.arms[0], 1, rot=(0, 0, 0)); S.key(a.arms[0], 118, rot=(0, 0, 0)); S.key(a.arms[0], 122, rot=(0, R(150), 0), interp="BACK")
    for k, f in enumerate(range(124, 140, 4)):
        S.key(a.elbows[0], f, rot=(0, R(-25 if k % 2 else 25), 0))
        wing(S, ig, f, 55 if k % 2 == 0 else -20)
    S.cue("tada", 124, vol=-8); a.face(-30, 120)
    a.blink(130)
    S.f = 140
    S.wait(8)
    return a


ONSCREEN = "Every IQ level protects a sandwich"   # texto fijo arriba (reto)
LEVELS = [(-400, l1), (-90, l2), (110, l3), (800, l4), (5469, l5)]
