"""ep005 — Cómo da de comer a un pato cada nivel de IQ. Pato y patitos construidos aquí con S.obj. Comedia amable: ningún animal sufre daño."""
import math
import bpy
from mathutils import Vector

TITLE = "Every IQ Level Feeds a Duck"

SWIM_Z = -0.30      # raíz del pato nadando (superficie del agua z = -0.25)
DOCK_Z = 0.12


# ------------------------------------------------------------------ pato (cuerpo, cabeza, pico, ojos, cuello)
def make_duck(S, name, k=1.0, x=0.0, z=SWIM_Z):
    """Pato amarillo que MIRA hacia -x. d['root'] en la línea de flotación; d['head'] se anima con head()."""
    root = S.empty(name, (x, 0, z)); root.scale = (k, k, k)
    S.obj("uv_sphere", name + "_cuerpo", "yellow", (0, 0, 0.15), (0.34, 0.22, 0.17), parent=root)
    S.obj("cone", name + "_cola", "yellow", (0.33, 0, 0.27), (0.07, 0.05, 0.09), rot=(0, math.radians(55), 0), parent=root)
    for sy in (-1, 1):
        S.obj("uv_sphere", name + "_ala", "gold", (0.04, 0.17 * sy, 0.19), (0.20, 0.05, 0.11), rot=(0, 0, math.radians(8 * sy)), parent=root)
        S.obj("uv_sphere", name + "_pie", "orange", (-0.04, 0.08 * sy, 0.0), (0.08, 0.05, 0.02), parent=root)
    head = S.empty(name + "_cabeza", (-0.24, 0, 0.42), parent=root)
    S.obj("uv_sphere", name + "_craneo", "yellow", (0, 0, 0), (0.14, 0.125, 0.125), parent=head)
    S.obj("cone", name + "_pico", "orange", (-0.17, 0, -0.015), (0.06, 0.035, 0.07), rot=(0, math.radians(-90), 0), parent=head)
    for sy in (-1, 1):
        S.obj("uv_sphere", name + "_ojo", "white", (-0.065, 0.09 * sy, 0.045), (0.045, 0.04, 0.05), parent=head)
        S.obj("uv_sphere", name + "_pupila", "black", (-0.092, 0.095 * sy, 0.048), (0.024, 0.02, 0.028), parent=head)
    neck = S.obj("cylinder", name + "_cuello", "yellow", (-0.18, 0, 0.31), (0.07, 0.07, 0.1), parent=root, vertices=14)
    d = {"root": root, "head": head, "neck": neck, "k": k}
    set_head(S, d, 1)
    return d


def set_head(S, d, f, hx=-0.24, hz=0.42, pitch=0, yaw=0, interp="BEZIER"):
    S.key(d["head"], f, loc=(hx, 0, hz), rot=(0, math.radians(pitch), math.radians(yaw)), interp=interp)
    B = Vector((-0.12, 0, 0.2)); H = Vector((hx, 0, hz - 0.05)); v = H - B
    S.key(d["neck"], f, loc=tuple((B + H) / 2), rot=tuple(v.to_track_quat("Z", "Y").to_euler()), scale=(0.07, 0.07, max(0.02, v.length / 2)), interp=interp)


def peck(S, d, f, hx=-0.24, hz=0.42):
    set_head(S, d, f, hx, hz); set_head(S, d, f + 3, hx - 0.14, hz - 0.20, -55); set_head(S, d, f + 6, hx, hz)


def duck_pos(S, d, f, x, z=None, yaw=None, roll=0, sq=None, interp="BEZIER", y=0.0):
    z = SWIM_Z if z is None else z
    S.key(d["root"], f, loc=(x, y, z), rot=(math.radians(roll), 0, math.radians(0 if yaw is None else yaw)), interp=interp)
    if sq is not None:
        k = d["k"]; S.key(d["root"], f, scale=(k * sq[0], k * sq[1], k * sq[2]), interp=interp)


def glide(S, d, f0, f1, x0, x1, z=None, yaw=0, y=0.0, y1=None):
    """Nada de x0 a x1 con balanceo suave."""
    n = max(1, (f1 - f0) // 4); y1 = y if y1 is None else y1
    for i in range(n + 1):
        t = i / n; f = f0 + (f1 - f0) * t
        duck_pos(S, d, int(f), x0 + (x1 - x0) * t, (SWIM_Z if z is None else z) + 0.015 * (1 if i % 2 else -1), yaw, roll=2.5 * (1 if i % 2 else -1), interp="LINEAR", y=y + (y1 - y) * t)


def idle_bob(S, d, f0, f1, x, z=None, yaw=0, y=0.0):
    glide(S, d, f0, f1, x, x, z, yaw, y=y)


def waddle(S, d, f0, f1, x0, x1, z, yaw=0, y=0.0):
    """Anda sobre el muelle: pasitos con balanceo."""
    n = max(2, (f1 - f0) // 3)
    for i in range(n + 1):
        t = i / n
        duck_pos(S, d, int(f0 + (f1 - f0) * t), x0 + (x1 - x0) * t, z + 0.025 * (i % 2), yaw, roll=9 * (1 if i % 2 else -1), interp="LINEAR", y=y)


def hop_duck(S, d, f0, f1, p0, p1, h, yaw=0, land_sq=True, y0=0.0, y1=0.0):
    n = max(3, f1 - f0)
    for i in range(0, n + 1, 2):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t; z = p0[1] + (p1[1] - p0[1]) * t + 4 * h * t * (1 - t)
        duck_pos(S, d, f0 + i, x, z, yaw, interp="LINEAR", y=y0 + (y1 - y0) * t)
    duck_pos(S, d, f1, p1[0], p1[1], yaw, y=y1)
    if land_sq:
        k = d["k"]; S.key(d["root"], f1, scale=(k * 1.2, k * 1.1, k * 0.8)); S.key(d["root"], f1 + 4, scale=(k, k, k), interp="BACK")
    S.cue("pop", f0 + 1, vol=-8)


# ------------------------------------------------------------------ utilidades de actor/objetos
def grip_of(S, a, side=0):
    fa = a._dims["fa"]
    return S.empty("agarre", (0, -0.005, -fa - 0.07), parent=a.elbows[side])


def carry(S, o, grip, f0, f1):
    for fr in range(f0, f1 + 1):
        S.sc.frame_set(fr); bpy.context.view_layer.update()
        S.key(o, fr, loc=tuple(grip.matrix_world.translation), rot=(0, 0, 0), interp="LINEAR")


def arc(S, o, f0, f1, p0, p1, h, spin=0.0):
    n = f1 - f0
    for i in range(0, n + 1, 1):
        t = i / n
        p = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t + 4 * h * t * (1 - t))
        S.key(o, f0 + i, loc=p, rot=(0, spin * t, 0), interp="LINEAR")


def loaf(S, scale=1.0):
    o = S.obj("uv_sphere", "hogaza", "khaki", (0, 0, -5), (0.26 * scale, 0.13 * scale, 0.12 * scale))
    S.obj("uv_sphere", "corte", "cream", (0, -0.07 * scale, 0.05 * scale), (0.18 * scale, 0.06 * scale, 0.05 * scale), parent=o)
    return o


def crumb(S, p=(0, 0, -5), r=0.04):
    return S.obj("uv_sphere", "miga", "cream", p, (r, r, r * 0.8), segments=10, ring_count=6)


def hide(S, o, f):
    S.key(o, f, scale=tuple(o.scale)); S.key(o, f + 1, scale=(0.001, 0.001, 0.001))


def wave(S, a, f0, f1):
    S.key(a.arms[0], f0, rot=(0, 0, 0)); S.key(a.arms[0], f0 + 5, rot=(0, math.radians(150), 0), interp="BACK")
    for i, fr in enumerate(range(f0 + 6, f1, 5)):
        S.key(a.elbows[0], fr, rot=(0, math.radians(25 if i % 2 else -25), 0))


def crouch_pose(S, a, f, th=75, kn=130, lean=14, x=None):
    T, Sh = a._dims["thigh"], a._dims["shin"]
    drop = (T + Sh) - (T * math.cos(math.radians(th)) + Sh * math.cos(math.radians(kn - th)))
    for lg in a.legs: S.key(lg, f, rot=(math.radians(-th), 0, 0))
    for kk in a.knees: S.key(kk, f, rot=(math.radians(kn), 0, 0))
    S.key(a.pivot, f, rot=(math.radians(lean), 0, 0))
    S.key(a.root, f, loc=(a.x if x is None else x, 0, a.z - drop))


def stand_pose(S, a, f):
    for lg in a.legs: S.key(lg, f, rot=(0, 0, 0))
    for kk in a.knees: S.key(kk, f, rot=(0, 0, 0))
    S.key(a.pivot, f, rot=(0, 0, 0)); S.key(a.root, f, loc=(a.x, 0, a.z))


# ------------------------------------------------------------------ niveles
def l1(S):  # -420: lanza la hogaza entera; cae junto al pato (salpicadura), el pato se aleja ileso y él saluda a la nada.
    a = S.actor(x=-3.3); a.face(75, 1, turn=1); a.x = -3.3
    d = make_duck(S, "pato", x=-2.05, z=SWIM_Z)
    b = loaf(S); g = grip_of(S, a, 0)
    # fotograma 1: hogaza sobre la cabeza (siembra el remate), baja a la mano mientras el pato mira
    S.key(a.arms[0], 1, rot=(math.radians(-170), 0, 0)); S.key(a.elbows[0], 1, rot=(0, 0, 0))
    S.key(a.arms[0], 8, rot=(math.radians(-75), 0, 0)); S.key(a.elbows[0], 8, rot=(math.radians(-50), 0, 0))
    S.key(a.arms[0], 15, rot=(math.radians(-75), 0, 0))
    S.key(a.arms[0], 19, rot=(math.radians(55), 0, 0), interp="BACK"); S.key(a.elbows[0], 19, rot=(0, 0, 0)); a.tilt(-10, 19)
    S.key(a.arms[0], 24, rot=(math.radians(-110), 0, 0), interp="BACK"); S.key(a.elbows[0], 24, rot=(math.radians(-20), 0, 0)); a.tilt(8, 24)
    S.key(a.arms[0], 40, rot=(math.radians(-110), 0, 0)); a.tilt(0, 36)
    carry(S, b, g, 1, 23)
    idle_bob(S, d, 1, 24, -2.05, y=-0.55)
    set_head(S, d, 1); set_head(S, d, 10, pitch=8); set_head(S, d, 18, hx=-0.27, hz=0.44, pitch=12)
    arc(S, b, 24, 33, tuple(g.matrix_world.translation) if False else (-2.7, 0, 0.85), (-1.5, -0.5, -0.2), 0.55, spin=4.5)   # cae delante del pato
    S.cue("whoosh", 22, vol=-8)
    S.f = 33; S.splash(-1.5, y=-0.5, big=1.0); S.splashes = []; S.cue("splash", 33)   # sin primer plano: el actor debe seguir en cuadro
    S.key(b, 34, loc=(-1.5, -0.5, -0.22)); S.key(b, 90, loc=(0.4, -0.5, -0.22))
    # el pato se sobresalta (salto atrás) y se aleja ileso
    glide(S, d, 24, 33, -2.05, -2.05, y=-0.55)
    duck_pos(S, d, 35, -2.2, SWIM_Z + 0.25, 0, sq=(0.9, 0.9, 1.2), y=-0.55); duck_pos(S, d, 39, -2.15, SWIM_Z, 0, sq=(1, 1, 1), y=-0.55)
    set_head(S, d, 35, hx=-0.2, hz=0.5, pitch=-10); set_head(S, d, 40)
    duck_pos(S, d, 44, -2.15, SWIM_Z, 180, y=-0.55)                                  # media vuelta
    glide(S, d, 44, 90, -2.15, 2.3, yaw=180, y=-0.55)
    set_head(S, d, 60, hx=-0.24, hz=0.42, yaw=0); set_head(S, d, 66, yaw=140); set_head(S, d, 85, yaw=140)   # mira atrás, indignado
    # él: sigue mirando, luego saluda feliz a la nada
    a.face(-30, 40, turn=5)
    a.blink(52)
    wave(S, a, 60, 138)
    S.cue("tada", 60, vol=-10)
    S.f = 140
    return a


def l2(S):  # -60: desmigaja con cuidado; un soplo de viento se lleva las migas; las persigue y casi cae del muelle.
    a = S.actor(x=-3.0); a.face(75, 1, turn=1); a.x = -3.0
    d = make_duck(S, "pato", x=-2.05)
    b = loaf(S); g = grip_of(S, a, 0)
    for sh in a.arms: S.key(sh, 1, rot=(math.radians(-60), 0, 0))
    for el in a.elbows: S.key(el, 1, rot=(math.radians(-70), 0, 0))
    # desmigar: manos juntas, vaivén
    for i, fr in enumerate(range(1, 30, 4)):
        S.key(a.arms[0], fr, rot=(math.radians(-60 - (8 if i % 2 else -8)), 0, 0)); S.key(a.arms[1], fr, rot=(math.radians(-60 + (8 if i % 2 else -8)), 0, 0))
    S.key(a.arms[0], 32, rot=(math.radians(-45), 0, 0)); S.key(a.arms[1], 32, rot=(math.radians(-45), 0, 0))
    carry(S, b, g, 1, 30)
    for fr, s in ((8, 0.8), (16, 0.6), (24, 0.4), (30, 0.001)):
        S.key(b, fr, scale=(s, s, s)) if False else None
    bs = tuple(b.scale)
    for fr, m in ((1, 1.0), (10, 0.75), (20, 0.5), (30, 0.3), (31, 0.001)): S.key(b, fr, scale=tuple(v * m for v in bs))
    cr = []
    px = [-2.55, -2.45, -2.35, -2.25, -2.15, -2.05, -2.40]
    for i, x in enumerate(px):
        c = crumb(S); cr.append(c); f0 = 6 + i * 3; cs0 = tuple(c.scale)
        S.key(c, f0 - 1, loc=(-2.7, 0, -5), scale=(0.001,) * 3)
        S.key(c, f0, loc=(-2.7, 0, 0.75), scale=cs0)
        S.key(c, f0 + 6, loc=(x, 0.0, DOCK_Z + 0.03 + (0.02 if i > 3 else 0)), interp="BOUNCE")
    S.cue("pop", 10, vol=-12); S.cue("pop", 18, vol=-12)
    idle_bob(S, d, 1, 36, -2.05, y=-0.55)
    set_head(S, d, 1); set_head(S, d, 12, pitch=10); set_head(S, d, 24, pitch=10)
    glide(S, d, 36, 52, -2.05, -2.05, y=-0.55); idle_bob(S, d, 52, 150, -2.05, y=-0.55)
    a.face(-30, 34, turn=4); a.arms_to(0, 34)
    # soplo de viento
    S.cue("whoosh", 50, vol=-2)
    streaks = []
    for i in range(4):
        st = S.obj("cube", "racha", "white", (-4, 0.5, 0.6 + i * 0.35), (0.55, 0.012, 0.012), smooth=False)
        S.key(st, 49 + i, loc=(-3.6, 0.5, 0.45 + i * 0.4)); S.key(st, 63 + i, loc=(3.0, 0.5, 0.45 + i * 0.4), interp="LINEAR"); S.key(st, 64 + i, loc=(3.0, 0.5, -6))
        S.key(st, 48 + i, loc=(-3.6, 0.5, -6))
    for i, c in enumerate(cr):
        f0 = 52 + i; xs = px[i]
        arc(S, c, f0, f0 + 20, (xs, 0, DOCK_Z + 0.03), (3.2 + 0.15 * i, 0, 0.5 + 0.1 * i), 0.7 + 0.12 * i)
        S.key(c, f0 + 21, loc=(5, 0, 5))
    for i in range(6): set_head(S, d, 54 + i * 3, pitch=(-25 if i % 2 else 20), hx=-0.24, hz=0.44, yaw=(30 if i % 2 else -30), interp="LINEAR")
    set_head(S, d, 76)
    # persecución y casi caída
    a.hop_to(-2.6, dur=6, h=0.3); a.hop_to(-2.15, dur=6, h=0.3)
    f = S.f
    a.hop_to(-1.8, z=DOCK_Z, dur=6, h=0.3)
    f = S.f
    S.key(a.root, f, loc=(-1.8, 0, DOCK_Z), rot=(0, 0, math.radians(75)))
    # tambaleo al borde: molinillo de brazos
    for i, fr in enumerate(range(f, f + 28, 4)):
        a.tilt(32 if i % 2 == 0 else 14, fr)
        S.key(a.arms[0], fr, rot=(0, math.radians(150 if i % 2 else 60), 0)); S.key(a.arms[1], fr, rot=(0, math.radians(-60 if i % 2 else -150), 0))
        S.key(a.root, fr, loc=(-1.8 + 0.06 * (i % 2), 0, DOCK_Z))
    S.cue("slide_down", f + 4, vol=-8)
    f += 28
    S.key(a.root, f, loc=(-1.8, 0, DOCK_Z)); a.tilt(-12, f + 3); a.arms_to(20, f + 3); a.tilt(0, f + 10)
    a.blink(f + 6)
    # el pato lo mira, sin migas
    set_head(S, d, f - 2, pitch=0); set_head(S, d, f + 6, hx=-0.22, hz=0.45, yaw=-35); set_head(S, d, f + 14, yaw=35); set_head(S, d, f + 22)
    S.f = f + 28
    return a


def l3(S):  # +130: agachado e inmóvil con una miga en la palma; el pato duda, avanza, picotea; él casi llora de emoción.
    a = S.actor(x=-2.35); a.face(75, 1, turn=1); a.x = -2.35; a.z = DOCK_Z
    d = make_duck(S, "pato", x=-0.9)
    g = grip_of(S, a, 0); c = crumb(S, r=0.05)
    crouch_pose(S, a, 1)
    S.key(a.arms[0], 1, rot=(math.radians(-70), 0, 0)); S.key(a.elbows[0], 1, rot=(math.radians(-25), 0, 0))
    S.key(a.arms[1], 1, rot=(math.radians(-20), 0, 0))
    S.key(a.arms[0], 150, rot=(math.radians(-70), 0, 0)); S.key(a.elbows[0], 150, rot=(math.radians(-25), 0, 0))
    carry(S, c, g, 1, 98)
    # el pato: mira, duda, retrocede, vuelve a avanzar
    glide(S, d, 1, 24, -0.9, -0.9, y=-0.3)
    glide(S, d, 24, 44, -0.9, -0.75, y=-0.3)
    set_head(S, d, 1); set_head(S, d, 12, hx=-0.27, hz=0.44, pitch=10); set_head(S, d, 30, yaw=25); set_head(S, d, 40, yaw=-25); set_head(S, d, 48)
    glide(S, d, 44, 58, -0.75, -0.85, y=-0.3)
    glide(S, d, 58, 90, -0.85, -1.3, y=-0.3)
    set_head(S, d, 66, hx=-0.27, hz=0.45, pitch=5); set_head(S, d, 80, hx=-0.30, hz=0.50, pitch=15)
    # pico bajo la mano -> picotazo
    set_head(S, d, 88, hx=-0.32, hz=0.55, pitch=15); set_head(S, d, 93, hx=-0.38, hz=0.62, pitch=-20, interp="LINEAR")
    set_head(S, d, 97, hx=-0.30, hz=0.5, pitch=0); hide(S, c, 94); S.cue("pop", 94, vol=-6)
    set_head(S, d, 104, hx=-0.2, hz=0.5, pitch=20); set_head(S, d, 110, hx=-0.24, hz=0.42)
    glide(S, d, 90, 150, -1.3, -1.3, y=-0.3)
    # él: inmóvil... luego lágrimas y manos al pecho
    a.blink(70)
    a.look(0, -0.03, 90)
    for k, sy in enumerate((-1, 1)):
        S.sc.frame_set(100); bpy.context.view_layer.update()
        hp = a.head.matrix_world.translation
        for j in range(3):
            t = S.obj("uv_sphere", "lagrima", "foam", (hp.x, hp.y, -5), (0.035, 0.03, 0.05))
            f0 = 100 + j * 12 + k * 4
            ex = hp.x + 0.12 + 0.03 * j; ey = hp.y - 0.16 + 0.0 * j
            ts = tuple(t.scale); S.key(t, f0 - 1, loc=(ex, ey, -5), scale=(0.001,) * 3)
            S.key(t, f0, loc=(ex, ey, hp.z - 0.02), scale=ts); S.key(t, f0 + 10, loc=(ex + 0.02, ey, hp.z - 0.45), interp="LINEAR")
            S.key(t, f0 + 11, scale=(0.001,) * 3)
            if k == 1: break
    for i, fr in enumerate(range(100, 146, 6)):
        S.key(a.pivot, fr, rot=(math.radians(14 + (3 if i % 2 else -3)), 0, 0))
    S.key(a.arms[1], 100, rot=(math.radians(-20), 0, 0)); S.key(a.arms[1], 108, rot=(math.radians(-110), 0, 0)); S.key(a.elbows[1], 108, rot=(math.radians(-110), 0, 0))
    S.cue("tada", 98, vol=-12)
    S.f = 148
    return a


def l4(S):  # +850: reguero de migas que sube por su pierna hasta el regazo; el pato lo sigue y se sienta encima.
    a = S.actor(x=-3.4); a.face(75, 1, turn=1); a.x = -3.4; a.z = DOCK_Z
    hip = a.sit(f=1, knee=25)
    S.key(a.root, 1, loc=(-3.4, 0, DOCK_Z - hip + 0.05))
    for el in a.elbows: S.key(el, 1, rot=(math.radians(-15), 0, 0))
    for sh in a.arms: S.key(sh, 1, rot=(math.radians(-20), 0, 0))
    d = make_duck(S, "pato", x=-1.5)
    tr = [(-1.78, 0, DOCK_Z + 0.03), (-1.98, 0, DOCK_Z + 0.03), (-2.18, 0, DOCK_Z + 0.03), (-2.38, 0, DOCK_Z + 0.03), (-2.58, 0, DOCK_Z + 0.03),
          (-2.80, -0.22, 0.30), (-3.00, -0.22, 0.46), (-3.20, -0.22, 0.50)]
    cs = []
    for p in tr:
        c = crumb(S, p); cs.append(c)
    # el pato nada hasta el borde, sube de un salto y sigue el reguero picoteando
    idle_bob(S, d, 1, 10, -1.5, y=-0.5)
    set_head(S, d, 1); set_head(S, d, 8, hx=-0.27, hz=0.44, pitch=10)
    glide(S, d, 10, 28, -1.5, -1.65, y=-0.5)
    hop_duck(S, d, 28, 38, (-1.65, SWIM_Z), (-1.85, DOCK_Z + 0.03), 0.45, y0=-0.5, y1=0.0)
    xs = [-1.98, -2.18, -2.38, -2.58]
    f = 40
    for i, x in enumerate(xs):
        waddle(S, d, f, f + 6, (-1.82 if i == 0 else xs[i - 1]), x, DOCK_Z + 0.03)
        peck(S, d, f + 6); hide(S, cs[i + 1], f + 9); S.cue("pop", f + 9, vol=-10)
        f += 12
    hide(S, cs[0], 43)
    # sube por la pierna: a la rodilla y al regazo
    hop_duck(S, d, f, f + 8, (xs[-1], DOCK_Z + 0.03), (-2.80, 0.30), 0.18, y1=-0.22); peck(S, d, f + 8); hide(S, cs[5], f + 11)
    f += 14
    hop_duck(S, d, f, f + 8, (-2.80, 0.30), (-3.0, 0.46), 0.15, y0=-0.22, y1=-0.22); peck(S, d, f + 8); hide(S, cs[6], f + 11)
    f += 14
    hop_duck(S, d, f, f + 7, (-3.0, 0.46), (-3.2, 0.50), 0.15, y0=-0.22, y1=-0.22); hide(S, cs[7], f + 7)
    f += 9
    k = d["k"]
    S.key(d["root"], f, scale=(k, k, k)); S.key(d["root"], f + 5, scale=(k * 1.15, k * 1.1, k * 0.7), interp="BACK"); S.key(d["root"], f + 9, scale=(k * 1.05, k * 1.0, k * 0.85))
    S.cue("tada", f + 4, vol=-10)
    set_head(S, d, f, hx=-0.24, hz=0.42); set_head(S, d, f + 8, hx=-0.2, hz=0.38, pitch=10)
    a.face(-20, f - 6, turn=8)                      # él mira al pato, quieto
    a.blink(f + 12); a.look(-0.03, -0.03, f + 4)
    S.f = f + 30
    return a


def l5(S):  # +5100: se pone la hogaza de sombrero y se queda quieto; el pato salta a su cabeza y tres patitos hacen torre; guiño.
    a = S.actor(x=-3.2); a.face(75, 1, turn=1); a.x = -3.2
    b = loaf(S, 1.0); g = grip_of(S, a, 0)
    # frame 1: baja el pan desde la mano hasta la cabeza
    S.sc.frame_set(1); bpy.context.view_layer.update()
    hz = a._dims["sh_z"] + a._dims["neck"] + 0.20 + 0.20     # coronilla aprox.
    ha = a.hat_z if a.has_hat else hz
    S.key(a.arms[0], 1, rot=(math.radians(-85), 0, 0)); S.key(a.elbows[0], 1, rot=(math.radians(-60), 0, 0))
    S.key(a.arms[0], 12, rot=(math.radians(-170), 0, 0)); S.key(a.elbows[0], 12, rot=(0, 0, 0))
    S.key(a.arms[0], 20, rot=(math.radians(-170), 0, 0))
    S.key(a.arms[0], 26, rot=(0, 0, 0), interp="BACK"); S.key(a.elbows[0], 26, rot=(math.radians(-12), 0, 0))
    carry(S, b, g, 1, 17)
    S.sc.frame_set(20); bpy.context.view_layer.update()
    top = tuple(a.head.matrix_world.translation); topz = top[2] + 0.23 + (0.15 if a.has_hat else 0)
    for fr in (17, 18, 19, 20): S.key(b, fr, loc=(top[0], top[1], topz + 0.04 + (20 - fr) * 0.0), rot=(0, 0, 0)) if fr > 17 else None
    S.key(b, 18, loc=(top[0], top[1], topz + 0.1)); S.key(b, 20, loc=(top[0], top[1], topz + 0.06), interp="BACK")
    S.key(b, 120, loc=(top[0], top[1], topz + 0.06))
    S.cue("pop", 19, vol=-8)
    tx = top[0]
    base = topz + 0.06 + 0.04          # asiento del pato sobre el pan
    d0 = make_duck(S, "pato", x=-2.05)
    ks = 0.42
    kids = [make_duck(S, "patito%d" % i, k=ks, x=-1.6 + 0.35 * i) for i in range(3)]
    idle_bob(S, d0, 1, 16, -2.05, y=-0.5); set_head(S, d0, 1); set_head(S, d0, 10, hx=-0.27, hz=0.44, pitch=10)
    glide(S, d0, 16, 34, -2.05, -1.75, y=-0.5)
    for i, kd in enumerate(kids):
        glide(S, kd, 1, 34, -1.6 + 0.35 * i, -1.6 + 0.35 * i - 0.4, y=-0.5)
    hop_duck(S, d0, 34, 43, (-1.75, SWIM_Z), (-1.82, DOCK_Z + 0.03), 0.4, y0=-0.5)
    waddle(S, d0, 44, 58, -1.82, -2.55, DOCK_Z + 0.03)
    # salta a la cabeza (quieto él)
    hop_duck(S, d0, 62, 76, (-2.55, DOCK_Z + 0.03), (tx, base), 0.85)
    S.cue("tada", 77, vol=-8)
    a.blink(80); a.look(0.02, 0.03, 78)
    # patitos: suben al muelle en fila y se apilan
    for i, kd in enumerate(kids):
        f0 = 40 + i * 6
        xq = -1.82 + 0.0
        hop_duck(S, kd, f0 + 4, f0 + 12, (-2.0 + 0.35 * i - 0.4 + 0.4, SWIM_Z), (-1.85 + 0.2 * i, DOCK_Z + 0.02), 0.2, y0=-0.5)
    # desfile en fila hasta los pies y trepan uno a uno
    heights = [base + 0.34 * 1.0, base + 0.34 + 0.2, base + 0.34 + 0.4]
    for i, kd in enumerate(kids):
        fw = 58 + i * 4
        waddle(S, kd, fw, fw + 12, -1.85 + 0.2 * i, -2.5 + 0.2 * (2 - i) * 0 + 0.0, DOCK_Z + 0.02)
        fh = 82 + i * 12
        hop_duck(S, kd, fh, fh + 9, (-2.5, DOCK_Z + 0.02), (tx, heights[i]), 0.55 + 0.2 * i)
        S.cue("pop", fh + 9, vol=-8)
        set_head(S, kd, fh + 9, hx=-0.2, hz=0.42, pitch=10)
    # guiño de perfil a cámara
    fw = 82 + 3 * 12 + 14
    a.face(40, fw - 12, turn=8)
    lid = a.lids[1]; lx, ly, lz = a._lid; rz = a._lid_rest
    S.key(lid, fw, scale=(lx, ly, lz)); S.key(lid, fw + 2, scale=(lx, ly, rz)); S.key(lid, fw + 12, scale=(lx, ly, rz)); S.key(lid, fw + 14, scale=(lx, ly, lz))
    S.cue("pop", fw + 2, vol=-6)
    for dd in [d0] + kids:
        pass
    S.f = fw + 28
    return a


ONSCREEN = "Every IQ level feeds a duck"   # texto fijo arriba (reto)
LEVELS = [(-420, l1), (-60, l2), (130, l3), (850, l4), (5100, l5)]
